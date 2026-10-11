package mx.bovicierre.evidencia;

import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;

@RestController
@RequestMapping("/api/v1/sedes/{sedeId}/documentos")
public class DocumentController {
    private final mx.bovicierre.evidencia.application.DocumentStorage files;
    private final AccessService access;
    private final CommandService commands;
    public DocumentController(mx.bovicierre.evidencia.application.DocumentStorage files,AccessService access,CommandService commands) { this.files=files; this.access=access; this.commands=commands; }
    @PostMapping(consumes=MediaType.MULTIPART_FORM_DATA_VALUE)
    ResponseEntity<String> upload(@PathVariable UUID sedeId,@RequestPart("archivo") MultipartFile file,@RequestParam String tipo_documental,@RequestParam(required=false) UUID operacion_id,@RequestParam(required=false) UUID documento_previo_id,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) {
        UUID user=access.user(auth);
        var scope=access.authorize(user,sedeId,true);
        if (tipo_documental.isBlank() || tipo_documental.length()>60) throw new ApiException(400,"BV400","El tipo documental no es válido.");
        try(var upload=files.stage(file)) {
        var stored=upload.stored();
        var payload=JsonSupport.JSON.createObjectNode().put("tipo_documental",tipo_documental).put("sha256",stored.sha256()).put("tamano_bytes",stored.size()).put("mime",stored.mime()).put("storage_key",JsonSupport.hash("almacenamiento",JsonSupport.JSON.createObjectNode().put("empresa",scope.company().toString()).put("sede",sedeId.toString()).put("usuario",user.toString()).put("clave",key).put("sha256",stored.sha256()))).put("nombre_original",stored.name());
        if (operacion_id != null) payload.put("operacion_id",operacion_id.toString());
        if (documento_previo_id!=null) {
            var previous=JsonSupport.JSON.readTree(commands.query(user,sedeId,"documento",JsonSupport.JSON.createObjectNode().put("id",documento_previo_id.toString())));
            payload.put("documento_previo_id",documento_previo_id.toString()).put("version",previous.path("version").asInt()+1);
        }
        return ResponseEntity.status(201).contentType(MediaType.APPLICATION_JSON).body(commands.command(user,sedeId,"registrar_documento",payload,key,ApiErrors.correlation(request),JsonSupport.hash("registrar_documento",payload.deepCopy().put("nombre_original",file.getOriginalFilename()))));
        }
    }
    @GetMapping("/{id}")
    ResponseEntity<String> metadata(@PathVariable UUID sedeId,@PathVariable UUID id,Authentication auth) {
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(commands.query(access.user(auth),sedeId,"documento",JsonSupport.JSON.createObjectNode().put("id",id.toString())));
    }
    @GetMapping("/{id}/contenido")
    ResponseEntity<FileSystemResource> download(@PathVariable UUID sedeId,@PathVariable UUID id,Authentication auth) {
        String json=commands.query(access.user(auth),sedeId,"documento",JsonSupport.JSON.createObjectNode().put("id",id.toString()));
        var metadata=JsonSupport.JSON.readTree(json);
        var file=files.path(metadata.path("sha256").asText());
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_OCTET_STREAM).header("Content-Disposition","attachment; filename=\"documento-"+id+"\"").header("X-Content-Type-Options","nosniff").body(new FileSystemResource(file));
    }
    @PostMapping("/{id}/revisiones")
    ResponseEntity<String> review(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) {
        var payload=JsonSupport.object(body);
        if (!payload.has("documentos")) payload.putArray("documentos").addObject().put("documento_id",id.toString()).put("resultado",payload.path("resultado").asText());
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(commands.command(access.user(auth),sedeId,"registrar_revision",payload,key,ApiErrors.correlation(request)));
    }
}
