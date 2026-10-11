package mx.bovicierre.evidencia;

import java.util.UUID;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.CommandService;
import mx.bovicierre.shared.JsonSupport;

@RestController
public class SettlementController {
    private final AccessService access;
    private final CommandService commands;
    public SettlementController(AccessService access,CommandService commands) { this.access=access; this.commands=commands; }
    @GetMapping("/api/v1/sedes/{sedeId}/liquidaciones/{id}/comprobante")
    ResponseEntity<byte[]> receipt(@PathVariable UUID sedeId,@PathVariable UUID id,Authentication auth) {
        var liquidation=JsonSupport.JSON.readTree(commands.query(access.user(auth),sedeId,"liquidacion",JsonSupport.JSON.createObjectNode().put("id",id.toString())));
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_PDF).header("Content-Disposition","attachment; filename=\"liquidacion-"+id+".pdf\"").body(SettlementPdf.render(liquidation));
    }
}
