package mx.bovicierre;

import mx.bovicierre.shared.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ContractTest {
    @Test void canonicalIdempotencyIncludesIntentAndVersion() {
        var a=JsonSupport.object("{\"precio_unitario\":\"48.0000\",\"version_lock\":1,\"lotes\":[{\"numero_lote\":1,\"animales\":[\"a\",\"b\"]}]}");
        var b=JsonSupport.object("{\"lotes\":[{\"animales\":[\"a\",\"b\"],\"numero_lote\":1}],\"version_lock\":1,\"precio_unitario\":\"48.0000\"}");
        assertEquals(JsonSupport.hash("confirmar_operacion",a),JsonSupport.hash("confirmar_operacion",b));
        b.put("version_lock",2);
        assertNotEquals(JsonSupport.hash("confirmar_operacion",a),JsonSupport.hash("confirmar_operacion",b));
        assertNotEquals(JsonSupport.hash("confirmar_operacion",a),JsonSupport.hash("cancelar_operacion",a));
    }
    @Test void exactDecimalsRejectNumbersNaNAndScientificNotation() {
        assertDoesNotThrow(() -> JsonSupport.decimals(JsonSupport.object("{\"monto\":{\"importe\":\"100.00\",\"moneda\":\"MXN\"},\"cargos_pactados\":{\"importe\":\"10.00\",\"moneda\":\"MXN\"}}")));
        JsonSupport.decimals(JsonSupport.object("{\"importe\":{\"importe\":\"1000.00\",\"moneda\":\"MXN\"},\"precio_unitario\":\"48.0000\"}"));
        for (String value : java.util.List.of("48.1","\"NaN\"","\"1e3\"","\"Infinity\"")) {
            assertThrows(ApiException.class,() -> JsonSupport.decimals(JsonSupport.object("{\"precio_unitario\":"+value+"}")));
        }
    }
    @Test void optimisticVersionIsRequiredAndStrong() {
        assertEquals(1,JsonSupport.version("\"1\""));
        assertEquals(0,JsonSupport.version("\"0\""));
        assertEquals(428,assertThrows(ApiException.class,() -> JsonSupport.version(null)).status);
        for (String etag : java.util.List.of("1","W/\"1\"","\"-1\"","*")) assertThrows(ApiException.class,() -> JsonSupport.version(etag));
    }
    static org.postgresql.util.PSQLException pg(String code,String constraint,String detail) {
        String message="SERROR\0C"+code+"\0Msecret SQL private_key\0";
        if (constraint!=null) message+="n"+constraint+"\0";
        if (detail!=null) message+="D"+detail+"\0";
        return new org.postgresql.util.PSQLException(new org.postgresql.util.ServerErrorMessage(message+"\0"));
    }
    @Test void structuredDatabaseDetailIsValidated() {
        ApiException rule=ApiErrors.database(pg("P0001",null,"{\"codigo\":\"BV405\",\"regla_id\":\"RN-032\",\"campos\":[]}"));
        assertEquals(409,rule.status); assertEquals("RN-032",rule.rule);
        assertEquals(500,ApiErrors.database(pg("P0001",null,"{\"codigo\":\"BV405\",\"regla_id\":\"secret SQL\",\"campos\":[]}")).status);
        assertEquals(500,ApiErrors.database(pg("P0001",null,"malformed JSON")).status);
        assertEquals(500,ApiErrors.database(new java.sql.SQLException("SQL syntax secret","42601")).status);
        // CHECK con nombre explícito (condicion_lote_base_tipo) también es 422, nunca 500.
        assertEquals(422,ApiErrors.database(pg("23514","condicion_lote_base_tipo",null)).status);
        // DAST: byte nulo / codificación inválida → 400, nunca 500.
        assertEquals(400,ApiErrors.database(new java.sql.SQLException("unsupported Unicode escape","22P05")).status);
        assertEquals(400,ApiErrors.database(new java.sql.SQLException("invalid byte sequence","22021")).status);
    }
    @Test void nativeDatabaseMessagesNeverLeakSql() {
        ApiException conflict=ApiErrors.database(pg("23505","uk_animal_identificacion_codigo",null));
        assertEquals(409,conflict.status);
        assertFalse(conflict.getMessage().contains("private_key"));
        // DIV-01: UNIQUE inline de V1 con nombre autogenerado por PostgreSQL también es conflicto 409, no 500.
        assertEquals(409,ApiErrors.database(pg("23505","usuario_empresa_id_login_normalizado_key",null)).status);
        assertEquals(409,ApiErrors.database(pg("23505","animal_identificacion_empresa_id_sistema_codigo_normalizado_key",null)).status);
        assertEquals(500,ApiErrors.database(pg("23505","otro_indice",null)).status);
        assertEquals(422,ApiErrors.database(pg("23503","fk_operacion_2",null)).status);
        assertEquals(422,ApiErrors.database(pg("23514","sucursal_check2",null)).status);
        assertEquals(422,ApiErrors.database(new java.sql.SQLException("private SQL", "22001")).status);
        assertEquals(409,ApiErrors.database(pg("23001","fk_operacion_2",null)).status);
        assertEquals(500,ApiErrors.database(pg("23001","unexpected_configuration",null)).status);
        assertEquals(503,ApiErrors.database(new java.sql.SQLException("hostname password", "08006")).status);
    }
}
