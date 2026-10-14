package mx.bovicierre.acceso;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/**
 * Limita intentos fallidos de login por usuario y por origen dentro de una ventana deslizante.
 * Estado en memoria del proceso: suficiente para el despliegue de una instancia; no se comparte entre réplicas.
 * Se consulta antes de verificar la contraseña para no gastar bcrypt en un ataque y responde igual exista o no el usuario.
 */
@Component
public class LoginThrottle {
    static final int MAX_PER_LOGIN = 10;
    static final int MAX_PER_ORIGIN = 50;
    static final int MAX_ANONYMOUS_SESSIONS = 600;
    static final Duration WINDOW = Duration.ofMinutes(15);
    static final int MAX_KEYS = 50_000;
    static final int OVERFLOW_BUCKETS = 4_096;
    private final ConcurrentHashMap<String, Deque<Instant>> failures = new ConcurrentHashMap<>();
    private final Clock clock;

    public LoginThrottle() { this(Clock.systemUTC()); }
    LoginThrottle(Clock clock) { this.clock = clock; }

    /** Segundos hasta poder reintentar; 0 si está permitido. */
    public long retryAfter(String login, String origin) {
        return Math.max(wait(key("u", login), MAX_PER_LOGIN), wait(key("o", origin), MAX_PER_ORIGIN));
    }

    /**
     * Origen del cliente: X-Real-IP que fija Caddy con su {client_ip} (sobrescribe lo que envíe el cliente; el backend
     * sólo es alcanzable a través de Caddy). Nunca X-Forwarded-For crudo: el cliente lo controla y evadiría el límite.
     */
    public static String origin(jakarta.servlet.http.HttpServletRequest request) {
        String real = request.getHeader("X-Real-IP");
        return real == null || real.isBlank() || real.length() > 64 ? request.getRemoteAddr() : real.trim();
    }

    public void failed(String login, String origin) {
        Instant now = clock.instant();
        for (String k : new String[]{key("u", login), key("o", origin)}) track(k, now);
    }

    /**
     * Memoria acotada sin fallar en abierto: con el mapa lleno (tras limpiar lo vencido), una clave nueva cuenta en uno
     * de OVERFLOW_BUCKETS compartidos. Colisionar endurece el límite para quien comparte cubeta; nunca lo desactiva.
     */
    private String resolve(String k) {
        if (failures.containsKey(k) || failures.size() < MAX_KEYS) return k;
        failures.entrySet().removeIf(e -> !e.getKey().startsWith("x:") && pruneAndEmpty(e.getValue()));
        return failures.size() < MAX_KEYS ? k : "x:" + k.charAt(0) + Math.floorMod(k.hashCode(), OVERFLOW_BUCKETS);
    }

    private boolean pruneAndEmpty(Deque<Instant> q) { synchronized (q) { prune(q); return q.isEmpty(); } }

    private void track(String k, Instant now) {
        Deque<Instant> q = failures.computeIfAbsent(resolve(k), ignored -> new ArrayDeque<>());
        synchronized (q) { prune(q); q.addLast(now); }
    }

    int trackedKeys() { return failures.size(); }

    /** Registra una sesión anónima nueva del origen; false si superó el tope de la ventana (hallazgo SF-03). */
    public boolean anonymousSession(String origin) {
        String k = key("s", origin);
        if (wait(k, MAX_ANONYMOUS_SESSIONS) > 0) return false;
        track(k, clock.instant());
        return true;
    }

    public void succeeded(String login) { failures.remove(key("u", login)); }

    private long wait(String k, int max) {
        Deque<Instant> q = failures.get(failures.containsKey(k) ? k : resolve(k));
        if (q == null) return 0;
        synchronized (q) {
            prune(q);
            if (q.size() < max) return 0;
            return Math.max(1, Duration.between(clock.instant(), q.peekFirst().plus(WINDOW)).toSeconds());
        }
    }

    private void prune(Deque<Instant> q) {
        Instant limit = clock.instant().minus(WINDOW);
        while (!q.isEmpty() && !q.peekFirst().isAfter(limit)) q.removeFirst();
    }

    private static String key(String kind, String value) { return kind + ":" + (value == null ? "" : value.trim().toLowerCase(Locale.ROOT)); }
}
