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
}
