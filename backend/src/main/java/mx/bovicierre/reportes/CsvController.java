package mx.bovicierre.reportes;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;
import tools.jackson.databind.JsonNode;

@RestController
public class CsvController {
    private final AccessService access;
    private final CommandService commands;
    public CsvController(AccessService access,CommandService commands) { this.access=access; this.commands=commands; }
    @GetMapping("/api/v1/sedes/{sedeId}/reportes/{tipo}/csv")
    ResponseEntity<String> export(@PathVariable UUID sedeId,@PathVariable String tipo,Authentication auth) {
        if (!List.of("cartera","margen","inventario").contains(tipo)) throw new ApiException(404,"BV404","Reporte no disponible.");
        UUID user=access.user(auth);
        List<JsonNode> rows=new ArrayList<>();
        for (int page=1; ;page++) {
            var response=JsonSupport.JSON.readTree(commands.query(user,sedeId,"reportes_"+tipo,JsonSupport.JSON.createObjectNode().put("pagina",page).put("tamano",100)));
            if (tipo.equals("margen")) { rows.add(response); break; }
            JsonNode items=tipo.equals("cartera") ? response.path("filas") : response.has("elementos") ? response.get("elementos") : response.path("items");
            items.forEach(rows::add);
            if (rows.size()>=response.path("total").asLong() || items.isEmpty()) break;
            if (rows.size()>=10000) throw new ApiException(422,"BV015","El reporte supera 10000 filas; descargue un conjunto más pequeño.");
        }
        return ResponseEntity.ok().contentType(MediaType.parseMediaType("text/csv;charset=UTF-8")).header("Content-Disposition","attachment; filename=\""+tipo+".csv\"").body(csv(rows));
    }
    public static String cell(String value) {
        String trimmed=value.stripLeading();
        if (!trimmed.isEmpty() && "=+-@".indexOf(trimmed.charAt(0))>=0 || !value.isEmpty() && "\t\r\n".indexOf(value.charAt(0))>=0) value="'"+value;
        return "\""+value.replace("\"","\"\"")+"\"";
    }
    public static String csv(List<JsonNode> rows) {
        if (rows.isEmpty()) return "";
        List<String> keys=new ArrayList<>();rows.getFirst().properties().forEach(entry -> keys.add(entry.getKey()));
        StringBuilder csv=new StringBuilder(String.join(",",keys.stream().map(CsvController::cell).toList())).append("\r\n");
        for (JsonNode row : rows) {
            List<String> cells=keys.stream().map(key -> { JsonNode value=row.path(key); return cell(value.isValueNode() ? value.asText() : JsonSupport.JSON.writeValueAsString(value)); }).toList();
            csv.append(String.join(",",cells)).append("\r\n");
        }
        return csv.toString();
    }
}
