package mx.bovicierre.shared;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.TreeMap;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

public final class JsonSupport {
    public static final JsonMapper JSON = JsonMapper.builder().build();
    private JsonSupport() { }
    public static ObjectNode object(String body) {
        try {
            JsonNode node = JSON.readTree(body);
            if (node == null || !node.isObject()) throw new IllegalArgumentException();
            return (ObjectNode) node;
        } catch (Exception ex) {
            throw new ApiException(400, "BV400", "El cuerpo debe ser un objeto JSON válido.");
        }
    }
    private static JsonNode sorted(JsonNode value) {
        if (value.isObject()) {
            ObjectNode result = JSON.createObjectNode();
            TreeMap<String, JsonNode> fields = new TreeMap<>();
            value.properties().forEach(entry -> fields.put(entry.getKey(), entry.getValue()));
            fields.forEach((key, child) -> result.set(key, sorted(child)));
            return result;
        }
        if (value.isArray()) {
            var result = JSON.createArrayNode();
            value.forEach(child -> result.add(sorted(child)));
            return result;
        }
        return value;
    }
    public static String hash(String command, JsonNode body) {
        try {
            byte[] content = (command + "\n" + JSON.writeValueAsString(sorted(body))).getBytes(StandardCharsets.UTF_8);
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(content));
        } catch (Exception ex) { throw new IllegalStateException(ex); }
    }
    public static long version(String etag) {
        if (etag == null) throw new ApiException(428, "BV428", "Se requiere If-Match.");
        if (!etag.matches("\"(?:0|[1-9][0-9]{0,17})\"")) throw new ApiException(400, "BV400", "If-Match debe contener la versión entre comillas.");
        return Long.parseLong(etag.substring(1, etag.length() - 1));
    }
    public static void animalIdentifications(ObjectNode payload) {
        JsonNode identifications=payload.get("identificaciones");
        if(identifications==null) identifications=JSON.createArrayNode().add(payload.deepCopy().put("sistema",payload.path("sistema").asText("INTERNO")));
        if(!identifications.isArray() || identifications.isEmpty()) throw new ApiException(400,"BV400","Se requiere al menos una identificación del animal.");
        for(JsonNode identification:identifications) {
            String system=identification.path("sistema").asText(),code=identification.path("codigo").asText();
            if(!identification.isObject() || !identification.path("codigo").isTextual() || !identification.path("sistema").isTextual() || !java.util.Set.of("SINIIGA","SINIDA","INTERNO","OTRO").contains(system) || !code.matches("[A-Za-z0-9 -]{1,40}") || !code.matches(".*[A-Za-z0-9].*")) throw new ApiException(400,"BV400","La identificación requiere sistema permitido y código de 1 a 40 caracteres ASCII: letras, números, espacios o guiones.");
        }
    }
    public static void decimals(JsonNode node) {
        if (node.isObject()) node.properties().forEach(entry -> {
            String key = entry.getKey();
            JsonNode value = entry.getValue();
            if (java.util.Set.of("total","saldo","disponible","margen","costo_vigente").contains(key)) throw new ApiException(400,"BV400","Los totales se calculan en el servidor.");
            if (java.util.Set.of("cantidad", "valor", "importe", "monto", "cargos_pactados", "bonificaciones_pactadas", "precio_unitario", "bruto_kg", "tara_kg", "neto_kg", "peso_kg", "peso_individual_kg", "kg", "deduccion_pct", "base_valor").contains(key)) {
                if (java.util.Set.of("importe","monto","cargos_pactados","bonificaciones_pactadas").contains(key) && value.isObject()) {
                    if (!value.has("importe") || !"MXN".equals(value.path("moneda").asText())) throw new ApiException(400,"BV400","El importe requiere moneda MXN y cadena decimal.");
                } else if (!value.isTextual() || !value.asText().matches(switch(key) {
                    case "importe", "monto", "cargos_pactados", "bonificaciones_pactadas" -> "-?[0-9]{1,16}\\.[0-9]{2}";
                    case "precio_unitario" -> "[0-9]{1,10}\\.[0-9]{4}";
                    case "kg", "valor", "bruto_kg", "tara_kg", "neto_kg", "peso_kg", "peso_individual_kg" -> "[0-9]{1,11}\\.[0-9]{3}";
                    default -> "-?[0-9]{1,16}(\\.[0-9]{1,6})?";
                }))
                    throw new ApiException(400, "BV400", "Los valores decimales deben enviarse como cadenas exactas.");
            }
            decimals(value);
        });
        else if (node.isArray()) node.forEach(JsonSupport::decimals);
    }
}
