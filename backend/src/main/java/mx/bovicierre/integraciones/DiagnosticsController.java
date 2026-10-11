package mx.bovicierre.integraciones;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.CacheControl;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;

@RestController
@RequestMapping("/api/v1/sedes/{sedeId}/integraciones/diagnostico")
public class DiagnosticsController {
    private final AccessService access;
    private final CommandService commands;
    private final NodeHealth health;
    public DiagnosticsController(AccessService access,CommandService commands,NodeHealth health) {this.access=access;this.commands=commands;this.health=health;}
    @GetMapping
    ResponseEntity<Map<String,Object>> snapshot(@PathVariable UUID sedeId,Authentication auth) {
        UUID user=access.user(auth);
        if(!access.authorize(user,sedeId,false).roles().contains("ADMIN")) throw new ApiException(403,"AUTH403","Se requiere rol ADMIN para el diagnóstico.");
        Object sync;
        try {sync=JsonSupport.JSON.readTree(commands.query(user,sedeId,"sincronizacion",JsonSupport.JSON.createObjectNode()));}
        catch(org.springframework.dao.DataAccessException ex) {sync=Map.of("estado","NO_DISPONIBLE","codigo",ApiErrors.database((Throwable)ex).code);}
        Map<String,Object> result=new LinkedHashMap<>(commands.diagnostics());
        result.put("pools",health.pools());result.put("sincronizacion",sync);result.put("capturado_en",java.time.Instant.now().toString());
        return ResponseEntity.ok().cacheControl(CacheControl.noStore()).body(result);
    }
}
