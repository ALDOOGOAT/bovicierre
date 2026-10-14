package mx.bovicierre.acceso;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.HttpSessionCsrfTokenRepository;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.shared.ApiException;

@RestController
@RequestMapping("/api/v1")
public class SessionController {
    private final AccessService access;
    private final BCryptPasswordEncoder encoder;
    private final HttpSessionSecurityContextRepository contexts;
    private final HttpSessionCsrfTokenRepository csrf;
    private final String dummyHash;
    private final mx.bovicierre.shared.NodeHealth health;
    private final LoginThrottle throttle;
    public SessionController(AccessService access, BCryptPasswordEncoder encoder,HttpSessionSecurityContextRepository contexts,HttpSessionCsrfTokenRepository csrf,mx.bovicierre.shared.NodeHealth health,LoginThrottle throttle) {
        this.throttle=throttle; this.health=health; this.access=access; this.encoder=encoder; this.contexts=contexts; this.csrf=csrf;
        this.dummyHash=encoder.encode(UUID.randomUUID().toString());
    }
    static final int ANONYMOUS_SESSION_SECONDS = 300;
    static final int AUTHENTICATED_SESSION_SECONDS = 1800;
    @GetMapping("/sesion/csrf") ResponseEntity<Map<String,String>> csrf(CsrfToken token,HttpServletRequest request,HttpServletResponse response,Authentication authentication) {
        boolean fresh=request.getSession(false)==null;
        if (fresh && !throttle.anonymousSession(LoginThrottle.origin(request))) {
            response.setHeader("Retry-After","60"); throw new ApiException(429,"AUTH429","Demasiadas sesiones nuevas desde este origen.");
        }
        String value=token.getToken(); // genera y guarda el token: crea la sesión si no existía
        boolean anonymous=authentication==null || authentication instanceof org.springframework.security.authentication.AnonymousAuthenticationToken;
        var session=request.getSession(false);
        if (session!=null && anonymous) session.setMaxInactiveInterval(ANONYMOUS_SESSION_SECONDS); // SF-03: sesión sin login caduca pronto
        return ResponseEntity.ok().cacheControl(org.springframework.http.CacheControl.noStore()).body(Map.of("token",value,"headerName",token.getHeaderName()));
    }
    @PostMapping("/sesion/login") ResponseEntity<Void> login(@Valid @RequestBody Login input,HttpServletRequest request,HttpServletResponse response) {
        if (input.contrasena().getBytes(java.nio.charset.StandardCharsets.UTF_8).length>72) throw new ApiException(400,"BV400","La contraseña excede 72 bytes UTF-8.");
        String origin=LoginThrottle.origin(request);
        long wait=throttle.retryAfter(input.login(),origin);
        if (wait>0) { response.setHeader("Retry-After",String.valueOf(wait)); throw new ApiException(429,"AUTH429","Demasiados intentos. Espera antes de volver a intentar."); }
        var user=access.login(input.login());
        String hash=user == null ? dummyHash : user.get("hash_contrasena").toString().replaceFirst("^\\{bcrypt\\}", "");
        if (!encoder.matches(input.contrasena(),hash) || user == null || !"ACTIVO".equals(user.get("estado"))) {
            throttle.failed(input.login(),origin);
            throw new ApiException(401,"AUTH401","Las credenciales no son válidas.");
        }
        throttle.succeeded(input.login());
        request.getSession(true);
        request.changeSessionId();
        request.getSession().setMaxInactiveInterval(AUTHENTICATED_SESSION_SECONDS);
        var context=SecurityContextHolder.createEmptyContext();
        context.setAuthentication(UsernamePasswordAuthenticationToken.authenticated(user.get("id").toString(),null,List.of()));
        SecurityContextHolder.setContext(context);
        contexts.saveContext(context,request,response);
        csrf.saveToken(null,request,response);
        return ResponseEntity.noContent().build();
    }
    @PostMapping("/sesion/logout") ResponseEntity<Void> logout(HttpServletRequest request,HttpServletResponse response) {
        var session=request.getSession(false);
        if (session != null) session.invalidate();
        SecurityContextHolder.clearContext();
        return ResponseEntity.noContent().build();
    }
    @GetMapping("/sesion/actual") Map<String,Object> current(Authentication authentication) {
        UUID id=access.user(authentication);
        var user=access.current(id);
        Map<UUID,Map<String,Object>> sites=new LinkedHashMap<>();
        access.sites(id).forEach(row -> {
            UUID site=(UUID) row.get("id");
            sites.computeIfAbsent(site,ignored -> {
                Map<String,Object> entry=new LinkedHashMap<>(row); entry.remove("rol_codigo"); entry.put("roles",new ArrayList<String>()); entry.put("capacidades",new ArrayList<String>()); return entry;
            });
            @SuppressWarnings("unchecked") var roles=(List<String>) sites.get(site).get("roles");
            roles.add(row.get("rol_codigo").toString());
            @SuppressWarnings("unchecked") var capabilities=(List<String>) sites.get(site).get("capacidades");
            if (!capabilities.contains("CONSULTAR")) capabilities.add("CONSULTAR");
            String role=row.get("rol_codigo").toString();
            if (!role.equals("AUDITOR") && !capabilities.contains("ESCRIBIR")) capabilities.add("ESCRIBIR");
        });
        return Map.of("usuario_id",id,"nombre",user.get("nombre"),"sedes",sites.values());
    }
    @GetMapping("/salud") Map<String,Object> health() { return health.status(); }
    public record Login(@NotBlank @Size(max=80) String login,@NotBlank @Size(max=72) String contrasena) { }
}
