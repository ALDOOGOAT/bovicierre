package mx.bovicierre.operaciones;

import java.util.Map;
import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;
import tools.jackson.databind.node.ObjectNode;

@RestController
@RequestMapping("/api/v1/sedes/{sedeId}")
public class CoreController {
    private final AccessService access;
    private final CommandService commands;
    public CoreController(AccessService access,CommandService commands) { this.access=access; this.commands=commands; }
    private String relative(HttpServletRequest request) {
        String uri=request.getRequestURI();
        return uri.substring(uri.indexOf('/',uri.indexOf("/sedes/")+7)+1);
    }
    private ResponseEntity<String> result(String json,int status) {
        var response=ResponseEntity.status(status).contentType(MediaType.APPLICATION_JSON);
        var node=JsonSupport.JSON.readTree(json);
        if (node.has("version_lock")) response.eTag("\""+node.get("version_lock").asLong()+"\"");
        return response.body(json);
    }
    private ResponseEntity<String> write(UUID site,String command,String body,String key,String match,String idKey,UUID id,boolean version,int status,Authentication authentication,HttpServletRequest request) {
        ObjectNode payload=JsonSupport.object(body == null || body.isBlank() ? "{}" : body);
        if (payload.has("empresa_id") || payload.has("sucursal_id") || payload.has("actor_id") || payload.has("nodo_dueno") || payload.has("sede_operadora_id") || payload.has("nodo_origen") || payload.has("version_lock"))
            throw new ApiException(400,"BV400","El ámbito y la versión se determinan en el servidor.");
        if (id != null) payload.put(idKey,id.toString());
        if (command.equals("corregir_pesaje")) {
            var original=payload.get("corrige_a_id");
            if (original!=null) {
                try {
                    if (!original.isTextual() || !id.equals(UUID.fromString(original.asText()))) throw new IllegalArgumentException();
                } catch (IllegalArgumentException ex) {
                    throw new ApiException(400,"BV400","corrige_a_id debe identificar el pesaje de la ruta.");
                }
            }
            var reason=payload.get("motivo");
            if (reason==null || !reason.isTextual() || reason.asText().isBlank() || reason.asText().length()>200)
                throw new ApiException(400,"BV400","La corrección requiere un motivo de entre 1 y 200 caracteres.");
            payload.put("corrige_a_id",id.toString());
        }
        if (version) payload.put("version_lock",JsonSupport.version(match));
        String json=commands.command(access.user(authentication),site,command,payload,key,ApiErrors.correlation(request));
        var response=result(json,status);
        if(command.equals("registrar_gasto")) {
            var node=JsonSupport.JSON.readTree(json);
            String gasto=node.path("gasto_id").asText(node.path("id").asText());
            return ResponseEntity.status(status).headers(response.getHeaders()).header("Location","/api/v1/sedes/"+site+"/gastos/"+gasto).body(json);
        }
        return response;
    }
    @GetMapping("/pesajes/comparacion")
    ResponseEntity<String> compare(@PathVariable UUID sedeId,@RequestParam UUID inicial_id,@RequestParam UUID final_id,Authentication auth) {
        return result(commands.query(access.user(auth),sedeId,"comparacion_pesajes",JsonSupport.JSON.createObjectNode().put("inicial_id",inicial_id.toString()).put("final_id",final_id.toString())),200);
    }
    @GetMapping("/comandos/{comando}/{clave}")
    ResponseEntity<String> commandResult(@PathVariable UUID sedeId,@PathVariable String comando,@PathVariable String clave,Authentication auth) {
        if (!comando.matches("[a-z_]{3,60}") || clave.length()<16 || clave.length()>80) throw new ApiException(400,"BV400","La referencia del comando no es válida.");
        return result(commands.query(access.user(auth),sedeId,"comando",JsonSupport.JSON.createObjectNode().put("comando",comando).put("clave",clave)),200);
    }
    @GetMapping({"/contrapartes","/predios","/animales","/operaciones","/inventario/posiciones","/pagos","/gastos","/liquidaciones","/periodos","/documentos","/reportes/cartera","/reportes/margen","/reportes/inventario","/auditoria","/sincronizacion","/usuarios"})
    ResponseEntity<String> list(@PathVariable UUID sedeId,@RequestParam Map<String,String> query,Authentication auth,HttpServletRequest request) {
        String resource=relative(request).replace('/','_');
        if(resource.equals("reportes_cartera") && query.containsKey("periodo_id"))
            throw new ApiException(400,"BV400","La cartera actual no admite filtro de periodo; consulte la versión del cierre.");
        ObjectNode params=JsonSupport.JSON.createObjectNode();
        query.forEach((name,value) -> {
            validateIdFilter(name,value);
            if(name.equals("disponibles_para_venta") || name.equals("vencida")) {
                if(!value.equals("true") && !value.equals("false")) throw new ApiException(400,"BV400",name+" requiere true o false.");
                params.put(name,Boolean.parseBoolean(value));
            } else params.put(name,value);
        });
        int page=integer(query.getOrDefault("pagina","1")),size=integer(query.getOrDefault("tamano","25"));
        if (page < 1 || size < 1 || size > 100) throw new ApiException(400,"BV400","La paginación no es válida.");
        params.put("pagina",page); params.put("tamano",size);
        return result(commands.query(access.user(auth),sedeId,resource,params),200);
    }
    private int integer(String value) { try { return Integer.parseInt(value); } catch (NumberFormatException ex) { throw new ApiException(400,"BV400","La paginación no es válida."); } }
    private void validateIdFilter(String name,String value) {
        if (!name.equals("periodo_id") && !name.equals("operacion_id")) return;
        try {
            if (!UUID.fromString(value).toString().equalsIgnoreCase(value)) throw new IllegalArgumentException();
        } catch (IllegalArgumentException ex) {
            throw new ApiException(400,"BV400",name+" requiere un UUID válido.");
        }
    }
    @GetMapping({"/animales/{id}","/operaciones/{id}","/liquidaciones/{id}","/pagos/{id}","/gastos/{id}","/gastos/{id}/reparto","/operaciones/{id}/pesajes","/operaciones/{id}/expediente","/operaciones/{id}/simulador","/periodos/{id}/versiones"})
    ResponseEntity<String> one(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestParam Map<String,String> query,Authentication auth,HttpServletRequest request) {
        String relative=relative(request);
        String resource=relative.endsWith("/versiones") ? "periodo_versiones" : relative.endsWith("/pesajes") ? "operacion_pesajes" : relative.endsWith("/expediente") ? "operacion_expediente" : relative.endsWith("/simulador") ? "simulador" : relative.startsWith("animales/") ? "animal" : relative.startsWith("operaciones/") ? "operacion" : relative.startsWith("liquidaciones/") ? "liquidacion" : relative.startsWith("pagos/") ? "pago" : relative.endsWith("/reparto") ? "reparto_gasto" : "gasto";
        var params=JsonSupport.JSON.createObjectNode(); query.forEach((name,value) -> {validateIdFilter(name,value);params.put(name,value);}); params.put("id",id.toString());
        return result(commands.query(access.user(auth),sedeId,resource,params),200);
    }
    @PostMapping({"/contrapartes","/predios","/animales","/operaciones","/pagos","/gastos","/periodos","/inventario/movimientos"})
    ResponseEntity<String> create(@PathVariable UUID sedeId,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,Authentication auth,HttpServletRequest request) {
        String suffix=request.getRequestURI().substring(request.getRequestURI().lastIndexOf('/')+1);
        String command=Map.of("contrapartes","crear_contraparte","predios","crear_predio","animales","registrar_animal","operaciones","crear_operacion","pagos","registrar_pago","gastos","registrar_gasto","periodos","crear_periodo","movimientos","registrar_movimiento").get(suffix);
        return write(sedeId,command,body,key,null,null,null,false,201,auth,request);
    }
    @PatchMapping("/operaciones/{id}")
    ResponseEntity<String> edit(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestBody String body,@RequestHeader("Idempotency-Key") String key,@RequestHeader(value="If-Match",required=false) String match,Authentication auth,HttpServletRequest request) {
        return write(sedeId,"editar_operacion",body,key,match,"operacion_id",id,true,200,auth,request);
    }
    @PostMapping({"/operaciones/{id}/acordar","/operaciones/{id}/reabrir","/operaciones/{id}/confirmar","/operaciones/{id}/cancelar","/operaciones/{id}/anular","/operaciones/{id}/revisiones","/operaciones/{id}/pesajes","/operaciones/{id}/reservas","/pesajes/{id}/aprobar","/pesajes/{id}/correcciones","/reservas/{id}/liberar","/liquidaciones/{id}/ajustes","/gastos/{id}/reparto","/pagos/{id}/validar","/pagos/{id}/aplicaciones","/pagos/{id}/reembolsos","/aplicaciones/{id}/reverso","/periodos/{id}/cierre","/periodos/{id}/cerrar","/periodos/{id}/reabrir"})
    ResponseEntity<String> action(@PathVariable UUID sedeId,@PathVariable UUID id,@RequestBody(required=false) String body,@RequestHeader("Idempotency-Key") String key,@RequestHeader(value="If-Match",required=false) String match,Authentication auth,HttpServletRequest request) {
        String suffix=request.getRequestURI().substring(request.getRequestURI().lastIndexOf('/')+1);
        String command=switch(suffix) {
            case "acordar" -> "acordar_operacion"; case "revisiones" -> "registrar_revision"; case "confirmar" -> "confirmar_operacion"; case "cancelar" -> "cancelar_operacion"; case "anular" -> "anular_venta";
            case "pesajes" -> "registrar_pesaje"; case "reservas" -> "reservar_venta";
            case "aprobar" -> "aprobar_pesaje"; case "correcciones" -> "corregir_pesaje"; case "liberar" -> "liberar_reserva";
            case "ajustes" -> "ajustar_liquidacion"; case "reparto" -> "repartir_gasto"; case "validar" -> "validar_pago";
            case "aplicaciones" -> "aplicar_pago"; case "reembolsos" -> "reembolsar_pago"; case "reverso" -> "revertir_aplicacion";
            case "cierre", "cerrar" -> "cerrar_periodo"; case "reabrir" -> request.getRequestURI().contains("/operaciones/") ? "reabrir_operacion" : "reabrir_periodo"; default -> throw new IllegalStateException();
        };
        String relative=relative(request);
        String idKey=relative.substring(0,relative.indexOf('/'));
        idKey=switch(idKey) { case "operaciones" -> "operacion_id"; case "pesajes" -> "pesaje_id"; case "reservas" -> "reserva_id"; case "liquidaciones" -> "liquidacion_id"; case "gastos" -> "gasto_id"; case "pagos" -> "pago_id"; case "aplicaciones" -> "aplicacion_id"; default -> "periodo_id"; };
        int status=java.util.Set.of("pesajes","correcciones","reservas","ajustes","reparto","aplicaciones","reembolsos","reverso","cierre","cerrar").contains(suffix) ? 201 : 200;
        return write(sedeId,command,body,key,match,idKey,id,java.util.Set.of("confirmar","cancelar","anular","acordar").contains(suffix) || command.equals("reabrir_operacion"),status,auth,request);
    }
}
