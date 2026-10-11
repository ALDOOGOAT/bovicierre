package mx.bovicierre.integraciones;

import java.util.Map;
import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;

@RestController
@RequestMapping("/api/v1/sedes/{sedeId}/integraciones/proveedor/tarifas")
public class ProviderController {
    private final AccessService access;
    private final CommandService commands;
    public ProviderController(AccessService access,CommandService commands) { this.access=access; this.commands=commands; }
    @GetMapping
    ResponseEntity<String> tariffs(@PathVariable UUID sedeId,@RequestParam Map<String,String> query,Authentication auth) {
        int page,size;
        try { page=Integer.parseInt(query.getOrDefault("pagina","1")); size=Integer.parseInt(query.getOrDefault("tamano","25")); }
        catch(NumberFormatException ex) { throw new ApiException(400,"BV400","La paginación no es válida."); }
        if(page<1 || size<1 || size>100 || query.getOrDefault("ruta","").length()>160) throw new ApiException(400,"BV400","La consulta de tarifas no es válida.");
        var params=JsonSupport.JSON.createObjectNode().put("pagina",page).put("tamano",size);
        if(query.containsKey("ruta")) params.put("ruta",query.get("ruta"));
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).cacheControl(org.springframework.http.CacheControl.noStore()).body(commands.providerTariffs(access.user(auth),sedeId,params));
    }
    @PostMapping("/aceptaciones")
    ResponseEntity<String> accept(@PathVariable UUID sedeId,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) {
        var payload=JsonSupport.object(body);
        if(payload.size()!=1 || !payload.path("snapshot_id").isTextual()) throw new ApiException(400,"BV400","Se requiere únicamente snapshot_id de la consulta previa.");
        try { UUID.fromString(payload.path("snapshot_id").asText()); }
        catch(IllegalArgumentException ex) { throw new ApiException(400,"BV400","El snapshot no es válido."); }
        return ResponseEntity.status(201).contentType(MediaType.APPLICATION_JSON).body(commands.command(access.user(auth),sedeId,"aceptar_tarifa",payload,key,ApiErrors.correlation(request)));
    }
}
