package mx.bovicierre.shared;

import java.sql.SQLException;
import java.util.Map;
import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import tools.jackson.databind.JsonNode;

@RestControllerAdvice
public class ApiErrors {
    public static UUID correlation(HttpServletRequest request) {
        Object value = request.getAttribute("correlation_id");
        if (value instanceof UUID id) return id;
        UUID id = UUID.randomUUID();
        request.setAttribute("correlation_id", id);
        return id;
    }
    public static Map<String, Object> body(ApiException ex, UUID id) {
        var body=new java.util.LinkedHashMap<String,Object>();
        body.put("codigo",ex.code); body.put("mensaje",ex.getMessage()); body.put("correlation_id",id); body.put("campos",ex.fields);
        if (ex.rule!=null) body.put("regla_id",ex.rule);
        return body;
    }
    public static void write(HttpServletResponse response, ApiException ex, UUID id) throws java.io.IOException {
        response.setStatus(ex.status);
        response.setCharacterEncoding(java.nio.charset.StandardCharsets.UTF_8.name());
        response.setContentType("application/problem+json;charset=UTF-8");
        response.setHeader("X-Correlation-ID", id.toString());
        response.getWriter().write(JsonSupport.JSON.writeValueAsString(body(ex, id)));
    }
    @ExceptionHandler(ApiException.class)
    ResponseEntity<?> api(ApiException ex, HttpServletRequest request) {
        return ResponseEntity.status(ex.status).contentType(org.springframework.http.MediaType.APPLICATION_PROBLEM_JSON).body(body(ex, correlation(request)));
    }
    public static ApiException database(Throwable ex) {
        Throwable cause = ex;
        while (cause != null && !(cause instanceof SQLException)) cause = cause.getCause();
        if (!(cause instanceof SQLException sql)) return ex instanceof org.springframework.jdbc.CannotGetJdbcConnectionException ? new ApiException(503,"BV501","El nodo requerido no está disponible.") : internal();
        String state = sql.getSQLState();
        if ("P0001".equals(state) && sql instanceof org.postgresql.util.PSQLException pg && pg.getServerErrorMessage() != null) {
            try {
                JsonNode error = JsonSupport.JSON.readTree(pg.getServerErrorMessage().getDetail());
                String code=error.path("codigo").asText(), rule=error.path("regla_id").asText();
                if (!code.matches("BV[045][0-9]{2}") || !rule.matches("RN-[0-9]{3}")) return internal();
                JsonNode fields=error.path("campos");
                if (!fields.isArray() || fields.size()>50) return internal();
                var publicFields=new java.util.ArrayList<Map<String,String>>();
                for (JsonNode field : fields) {
                    String name=field.path("campo").asText(), problem=field.path("problema").asText();
                    if (name.isBlank() || name.length()>160 || problem.isBlank() || problem.length()>160 || name.chars().anyMatch(Character::isISOControl) || problem.chars().anyMatch(Character::isISOControl)) return internal();
                    publicFields.add(Map.of("campo",name,"problema",problem));
                }
                int status=code.equals("BV412") ? 412 : code.equals("BV428") ? 428 : code.equals("BV404") ? 404 : code.startsWith("BV5") ? 503 : code.startsWith("BV4") ? 409 : 422;
                String message=switch(code) {
                    case "BV405" -> "La clave de idempotencia ya se utilizó con otro contenido.";
                    case "BV412" -> "La versión cambió; recargue el recurso.";
                    case "BV404" -> "El recurso no existe o no está disponible en esta sede.";
                    case "BV402" -> "La posición ya está comprometida o no está disponible.";
                    case "BV403" -> "La reserva venció; revise la disponibilidad.";
                    case "BV020" -> "La aplicación excede el saldo o el importe disponible.";
                    case "BV025" -> "El periodo está cerrado o no admite la fecha solicitada.";
                    default -> status==503 ? "El nodo requerido no está disponible." : "La solicitud no cumple las reglas del dominio.";
                };
                ApiException result=new ApiException(status,code,message); result.rule=rule; result.fields=publicFields; return result;
            } catch (Exception ignored) { return internal(); }
        }
        String constraint=sql instanceof org.postgresql.util.PSQLException pg && pg.getServerErrorMessage()!=null ? pg.getServerErrorMessage().getConstraint() : null;
        if ("23505".equals(state) && constraint!=null && constraint.startsWith("uk_")) return new ApiException(409,"BV401","El registro ya existe o entra en conflicto.");
        if ("23001".equals(state) && constraint!=null && constraint.startsWith("fk_")) return new ApiException(409,"BV401","El registro tiene referencias que impiden modificarlo.");
        if ("23503".equals(state) && constraint!=null && constraint.startsWith("fk_")) return new ApiException(422,"BV015","Las referencias no corresponden a esta empresa o sede.");
        if ("23514".equals(state) && constraint!=null && constraint.matches("[a-z_][a-z0-9_]*_check[0-9]*")) return new ApiException(422,"BV015","Los datos no cumplen las reglas del dominio.");
        if (java.util.Set.of("23502","22P02","22001","22003","22007").contains(state)) return new ApiException(422,"BV015","Los datos no cumplen las reglas del dominio.");
        if ("42501".equals(state)) return new ApiException(403,"AUTH403","No tiene permiso para esta acción.");
        if ("40001".equals(state) || "40P01".equals(state)) return new ApiException(409,"BV409","Conflicto concurrente; reintente con la misma clave.");
        if (sql instanceof java.sql.SQLTransientConnectionException || sql instanceof java.sql.SQLNonTransientConnectionException || state!=null && state.startsWith("08")) return new ApiException(503,"BV501","El nodo requerido no está disponible.");
        return internal();
    }
    private static ApiException internal() { return new ApiException(500,"BV500","No fue posible procesar la solicitud."); }
    @ExceptionHandler(org.springframework.web.multipart.MaxUploadSizeExceededException.class)
    ResponseEntity<?> oversized(RuntimeException ex,HttpServletRequest request) { return api(new ApiException(413,"BV023","El archivo supera el límite de 20 MiB."),request); }
    @ExceptionHandler({DataAccessException.class,org.springframework.transaction.TransactionException.class})
    ResponseEntity<?> database(RuntimeException ex, HttpServletRequest request) { return api(database((Throwable) ex), request); }
    @ExceptionHandler({org.springframework.web.bind.MissingRequestHeaderException.class, org.springframework.web.method.annotation.MethodArgumentTypeMismatchException.class, org.springframework.http.converter.HttpMessageNotReadableException.class, org.springframework.web.bind.MethodArgumentNotValidException.class})
    ResponseEntity<?> invalid(Exception ex, HttpServletRequest request) { return api(new ApiException(400,"BV400","La solicitud no es válida."),request); }
}
