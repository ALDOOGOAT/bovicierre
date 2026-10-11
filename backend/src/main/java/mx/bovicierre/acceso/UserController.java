package mx.bovicierre.acceso;

import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.shared.*;

@RestController
@RequestMapping("/api/v1/sedes/{sedeId}/usuarios")
public class UserController {
    private final AccessService access;
    private final CommandService commands;
    private final BCryptPasswordEncoder encoder;
    public UserController(AccessService access,CommandService commands,BCryptPasswordEncoder encoder) { this.access=access; this.commands=commands; this.encoder=encoder; }
    private ResponseEntity<String> write(UUID site,String command,String body,String key,UUID target,Authentication auth,HttpServletRequest request,int status) {
        UUID user=access.user(auth);
        var scope=access.authorize(user,site,true);
        if (!scope.roles().contains("ADMIN")) throw new ApiException(403,"AUTH403","Se requiere rol ADMIN.");
        var payload=JsonSupport.object(body);
        if (!command.equals("crear_usuario") && payload.has("contrasena")) throw new ApiException(400,"BV400","La contraseña sólo se admite al crear usuario.");
        if (payload.has("hash_contrasena") || payload.has("empresa_id") || payload.has("sucursal_id") || payload.has("actor_id")) throw new ApiException(400,"BV400","El ámbito y las credenciales se determinan en el servidor.");
        if (target!=null) payload.put("usuario_id",target.toString());
        String fingerprint=JsonSupport.hash(command,payload);
        if (payload.has("contrasena")) {
            var password=payload.remove("contrasena");
            if (!password.isTextual() || password.asText().isBlank() || password.asText().getBytes(java.nio.charset.StandardCharsets.UTF_8).length>72) throw new ApiException(400,"BV400","La contraseña debe contener entre 1 y 72 bytes UTF-8.");
            payload.put("hash_contrasena","{bcrypt}"+encoder.encode(password.asText()));
        } else if (command.equals("crear_usuario")) throw new ApiException(400,"BV400","Se requiere contraseña.");
        return ResponseEntity.status(status).contentType(MediaType.APPLICATION_JSON).body(commands.command(user,site,command,payload,key,ApiErrors.correlation(request),fingerprint));
    }
    @PostMapping
    ResponseEntity<String> create(@PathVariable UUID sedeId,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) { return write(sedeId,"crear_usuario",body,key,null,auth,request,201); }
    @PatchMapping("/{id}")
    ResponseEntity<String> update(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) { return write(sedeId,"actualizar_usuario",body,key,id,auth,request,200); }
    @PostMapping("/{id}/membresias")
    ResponseEntity<String> membership(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) { return write(sedeId,"asignar_membresia",body,key,id,auth,request,200); }
}
