package mx.bovicierre.shared;

public class ApiException extends RuntimeException {
    public final int status;
    public final String code;
    public String rule;
    public java.util.List<java.util.Map<String,String>> fields=java.util.List.of();
    public ApiException(int status, String code, String message) {
        super(message);
        this.status = status;
        this.code = code;
    }
}
