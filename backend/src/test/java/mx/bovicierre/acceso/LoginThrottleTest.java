package mx.bovicierre.acceso;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class LoginThrottleTest {
    static final class MutableClock extends Clock {
        Instant now = Instant.parse("2026-10-12T10:00:00Z");
        @Override public ZoneOffset getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(java.time.ZoneId zone) { return this; }
        @Override public Instant instant() { return now; }
    }

    @Test void bloqueaTrasDiezFallosDelMismoUsuarioYExpiraConLaVentana() {
        var clock = new MutableClock(); var t = new LoginThrottle(clock);
        for (int i = 0; i < LoginThrottle.MAX_PER_LOGIN; i++) { assertEquals(0, t.retryAfter("demo.caja", "ip" + i)); t.failed("Demo.Caja ", "ip" + i); }
        long wait = t.retryAfter("demo.caja", "otra-ip");
        assertTrue(wait > 0 && wait <= LoginThrottle.WINDOW.toSeconds(), "espera " + wait);
        assertEquals(0, t.retryAfter("demo.admin", "otra-ip"), "otro usuario no queda bloqueado");
        clock.now = clock.now.plus(LoginThrottle.WINDOW).plusSeconds(1);
        assertEquals(0, t.retryAfter("demo.caja", "otra-ip"));
    }

    @Test void limitaPorOrigenAunqueRoteElUsuario() {
        var t = new LoginThrottle(new MutableClock());
        for (int i = 0; i < LoginThrottle.MAX_PER_ORIGIN; i++) t.failed("usuario" + i, "10.0.0.9|null");
        assertTrue(t.retryAfter("nuevo", "10.0.0.9|null") > 0);
        assertEquals(0, t.retryAfter("nuevo", "10.0.0.8|null"));
    }

    @Test void exitoReiniciaElContadorDelUsuario() {
        var clock = new MutableClock(); var t = new LoginThrottle(clock);
        for (int i = 0; i < LoginThrottle.MAX_PER_LOGIN - 1; i++) t.failed("demo.admin", "a" + i);
        t.succeeded("demo.admin");
        t.failed("demo.admin", "b");
        assertEquals(0, t.retryAfter("demo.admin", "c"));
        clock.now = clock.now.plus(Duration.ofSeconds(1));
        assertEquals(0, t.retryAfter("inexistente", "c"), "usuario inexistente sin fallos no se bloquea");
    }

    @Test void topeDeSesionesAnonimasPorOrigen() {
        var clock = new MutableClock(); var t = new LoginThrottle(clock);
        for (int i = 0; i < LoginThrottle.MAX_ANONYMOUS_SESSIONS; i++) assertTrue(t.anonymousSession("o1"));
        assertFalse(t.anonymousSession("o1"));
        assertTrue(t.anonymousSession("o2"));
        assertEquals(0, t.retryAfter("demo.admin", "o1"), "el tope de sesiones no bloquea el login");
        clock.now = clock.now.plus(LoginThrottle.WINDOW).plusSeconds(1);
        assertTrue(t.anonymousSession("o1"));
    }

    @Test void elOrigenIgnoraXForwardedForDelClienteYUsaLaIpDeCaddy() {
        var spoofed = new org.springframework.mock.web.MockHttpServletRequest();
        spoofed.setRemoteAddr("172.18.0.5"); spoofed.addHeader("X-Forwarded-For", "1.2.3." + System.nanoTime() % 255);
        spoofed.addHeader("X-Real-IP", "203.0.113.7");
        assertEquals("203.0.113.7", LoginThrottle.origin(spoofed), "rotar X-Forwarded-For no cambia el origen");
        var direct = new org.springframework.mock.web.MockHttpServletRequest(); direct.setRemoteAddr("10.0.0.9");
        direct.addHeader("X-Forwarded-For", "9.9.9.9");
        assertEquals("10.0.0.9", LoginThrottle.origin(direct));
    }

    @Test void laMemoriaQuedaAcotadaYLasClavesExistentesSiguenContando() {
        var t = new LoginThrottle(new MutableClock());
        for (int i = 0; i < LoginThrottle.MAX_KEYS; i++) t.failed("u" + i, "203.0.113.7");
        int full = t.trackedKeys();
        for (int i = 0; i < 1000; i++) t.failed("nuevo" + i, "203.0.113.7");
        assertTrue(t.trackedKeys() <= LoginThrottle.MAX_KEYS, "sin crecimiento ilimitado: " + t.trackedKeys());
        assertEquals(full, t.trackedKeys());
        assertTrue(t.retryAfter("cualquiera", "203.0.113.7") > 0, "el origen existente sigue bloqueado");
    }
}
