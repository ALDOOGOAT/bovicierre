package mx.bovicierre;

import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import mx.bovicierre.shared.JsonSupport;
import static org.junit.jupiter.api.Assertions.*;

@EnabledIfEnvironmentVariable(named="BOVI_API_IT",matches="true")
class ApiPostgresTest {
    final String base=System.getenv().getOrDefault("BOVI_API_TEST_URL","http://127.0.0.1:18080/api/v1");
    final CookieManager cookies=new CookieManager(null,CookiePolicy.ACCEPT_ALL);
    final HttpClient client=HttpClient.newBuilder().cookieHandler(cookies).build();
    String token;
    String csrfHeader;
    HttpResponse<String> send(String method,String path,String body,String key) throws Exception { return send(method,path,body,key,null); }
    HttpResponse<String> send(String method,String path,String body,String key,String match) throws Exception {
        var builder=HttpRequest.newBuilder(URI.create(base+path)).header("Content-Type","application/json");
        if (token!=null) builder.header(csrfHeader,token);
        if (match!=null) builder.header("If-Match",match);
        if (key!=null) builder.header("Idempotency-Key",key);
        return client.send(builder.method(method,body==null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body)).build(),HttpResponse.BodyHandlers.ofString());
    }
    void csrf() throws Exception {
        var response=send("GET","/sesion/csrf",null,null);
        assertEquals(200,response.statusCode(),response.body());
        assertTrue(response.headers().firstValue("cache-control").orElse("").contains("no-store"));
        var json=JsonSupport.JSON.readTree(response.body());
        token=json.get("token").asText(); csrfHeader=json.get("headerName").asText();
    }
    void login() throws Exception {
        csrf();
        String password=Files.readString(Path.of(System.getenv("BOVI_TEST_PASSWORD_FILE"))).trim();
        var body=JsonSupport.JSON.createObjectNode().put("login","demo.admin").put("contrasena",password);
        var response=send("POST","/sesion/login",JsonSupport.JSON.writeValueAsString(body),null);
        assertEquals(204,response.statusCode(),response.body());
        assertTrue(cookies.getCookieStore().getCookies().stream().anyMatch(cookie -> cookie.getName().equals("BOVI_SESSION") && cookie.isHttpOnly()));
        csrf();
    }
    @Test void sessionRequiresCsrfAndCurrentAuthorization() throws Exception {
        var anonymous=client.send(HttpRequest.newBuilder(URI.create(base+"/sesion/actual")).GET().build(),HttpResponse.BodyHandlers.ofByteArray());
        assertEquals(401,anonymous.statusCode());
        String error=java.nio.charset.StandardCharsets.UTF_8.newDecoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(anonymous.body())).toString();
        assertEquals("Se requiere una sesión activa.",JsonSupport.JSON.readTree(error).path("mensaje").asText());
        assertTrue(anonymous.headers().firstValue("content-type").orElse("").toLowerCase(java.util.Locale.ROOT).contains("charset=utf-8"));
        assertEquals(403,send("POST","/sesion/login","{}",null).statusCode());
        login();
        assertEquals(200,send("GET","/sesion/actual",null,null).statusCode());
        assertEquals(403,send("GET","/sedes/cccccccc-cccc-4ccc-8ccc-cccccccccccc/operaciones",null,null).statusCode());
        assertEquals(204,send("POST","/sesion/logout","{}",null).statusCode());
        assertEquals(401,send("GET","/sesion/actual",null,null).statusCode());
    }
    @Test void retryReturnsOriginalAndChangedPayloadConflicts() throws Exception {
        login();
        String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/contrapartes";
        String key=UUID.randomUUID().toString();
        String body="{\"tipo_persona\":\"FISICA\",\"nombre\":\"DEMO API "+key+"\"}";
        var first=send("POST",site,body,key);
        assertEquals(201,first.statusCode(),first.body());
        var retry=send("POST",site,body,key);
        assertEquals(first.body(),retry.body());
        assertEquals(409,send("POST",site,body.replace("DEMO API","DEMO changed"),key).statusCode());
        assertEquals(400,send("POST",site,body,"short").statusCode());
        String seat=site.substring(0,site.lastIndexOf('/'));
        String party=JsonSupport.JSON.readTree(first.body()).path("id").asText();
        String draft=post(seat+"/operaciones",JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",java.time.LocalDate.now().toString()),201).path("id").asText();
        String original="\""+get(seat+"/operaciones/"+draft).path("version_lock").asLong()+"\"";
        var edited=send("PATCH",seat+"/operaciones/"+draft,"{\"fecha_operacion\":\""+java.time.LocalDate.now().plusDays(1)+"\"}",UUID.randomUUID().toString(),original);
        assertEquals(200,edited.statusCode(),edited.body());
        assertEquals(412,send("POST",seat+"/operaciones/"+draft+"/cancelar","{\"motivo\":\"DEMO stale\"}",UUID.randomUUID().toString(),original).statusCode());
        String current="\""+get(seat+"/operaciones/"+draft).path("version_lock").asLong()+"\"",cancelKey=UUID.randomUUID().toString();
        var cancelled=send("POST",seat+"/operaciones/"+draft+"/cancelar","{\"motivo\":\"DEMO cancelación\"}",cancelKey,current);
        assertEquals(200,cancelled.statusCode(),cancelled.body());
        assertEquals(cancelled.body(),send("POST",seat+"/operaciones/"+draft+"/cancelar","{\"motivo\":\"DEMO cancelación\"}",cancelKey,current).body());
        send("POST","/sesion/logout","{}",null);
    }
    tools.jackson.databind.JsonNode get(String path) throws Exception {
        var response=send("GET",path,null,null); assertEquals(200,response.statusCode(),response.body()); return JsonSupport.JSON.readTree(response.body());
    }
    tools.jackson.databind.JsonNode post(String path,tools.jackson.databind.JsonNode body,int status) throws Exception {
        var response=send("POST",path,JsonSupport.JSON.writeValueAsString(body),UUID.randomUUID().toString()); assertEquals(status,response.statusCode(),response.body()); return JsonSupport.JSON.readTree(response.body());
    }
    @Test void canonicalPurchaseSalePaymentAndReceiptThroughApi() throws Exception {
        login();
        String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
        String date=java.time.LocalDate.now().toString();
        var periods=get(site+"/periodos");
        var rows=periods.has("elementos") ? periods.get("elementos") : periods.get("items");
        String period="";
        for (var row : rows) if (row.path("estado").asText().equals("ABIERTO")) period=row.path("id").asText();
        if (period.isEmpty()) {
            var create=JsonSupport.JSON.createObjectNode().put("desde",java.time.LocalDate.now().withDayOfMonth(1).toString()).put("hasta",java.time.LocalDate.now().withDayOfMonth(java.time.LocalDate.now().lengthOfMonth()).toString());
            period=post(site+"/periodos",create,201).path("id").asText();
        }
        var recognition=JsonSupport.JSON.createObjectNode().put("periodo_id",period).put("fecha_reconocimiento",date);
        String party=post(site+"/contrapartes",JsonSupport.JSON.createObjectNode().put("nombre","DEMO API recorrido "+UUID.randomUUID()),201).path("id").asText();
        var animalBody=JsonSupport.JSON.createObjectNode().put("sexo","M");
        animalBody.putArray("identificaciones").addObject().put("sistema","INTERNO").put("codigo","DEMO"+UUID.randomUUID().toString().replace("-",""));
        String animal=post(site+"/animales",animalBody,201).path("id").asText();
        var buyBody=JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",date);
        String buy=post(site+"/operaciones",buyBody,201).path("id").asText();
        var edit=JsonSupport.JSON.createObjectNode();
        var lot=edit.putArray("lotes").addObject().put("numero_lote",1).put("unidad_precio","CABEZA").put("precio_unitario","1000.0000");lot.putArray("animales").add(animal);
        String version="\""+get(site+"/operaciones/"+buy).path("version_lock").asLong()+"\"";
        assertEquals(428,send("PATCH",site+"/operaciones/"+buy,JsonSupport.JSON.writeValueAsString(edit),UUID.randomUUID().toString()).statusCode());
        var changed=send("PATCH",site+"/operaciones/"+buy,JsonSupport.JSON.writeValueAsString(edit),UUID.randomUUID().toString(),version); assertEquals(200,changed.statusCode(),changed.body());
        var preview=get(site+"/operaciones/"+buy+"/simulador"); assertEquals("1000.00",preview.path("total").path("importe").asText());
        var operation=get(site+"/operaciones/"+buy); assertEquals("BORRADOR",operation.path("estado").asText());
        version="\""+operation.path("version_lock").asLong()+"\"";
        var agreed=send("POST",site+"/operaciones/"+buy+"/acordar","{}",UUID.randomUUID().toString(),version); assertEquals(200,agreed.statusCode(),agreed.body());
        var accepted=get(site+"/operaciones/"+buy); assertEquals("ACORDADA",accepted.path("estado").asText());
        version="\""+accepted.path("version_lock").asLong()+"\"";
        var reopened=send("POST",site+"/operaciones/"+buy+"/reabrir","{}",UUID.randomUUID().toString(),version); assertEquals(200,reopened.statusCode(),reopened.body());
        var reopenedOperation=get(site+"/operaciones/"+buy); assertEquals(2,reopenedOperation.path("numero_version_actual").asInt());
        assertEquals(accepted.path("contratos").get(0),reopenedOperation.path("contratos").get(0));
        version="\""+reopenedOperation.path("version_lock").asLong()+"\"";
        agreed=send("POST",site+"/operaciones/"+buy+"/acordar","{}",UUID.randomUUID().toString(),version); assertEquals(200,agreed.statusCode(),agreed.body());
        version="\""+get(site+"/operaciones/"+buy).path("version_lock").asLong()+"\"";
        String key=UUID.randomUUID().toString();
        var confirmed=send("POST",site+"/operaciones/"+buy+"/confirmar",JsonSupport.JSON.writeValueAsString(recognition),key,version); assertEquals(200,confirmed.statusCode(),confirmed.body());
        var settlement=JsonSupport.JSON.readTree(confirmed.body());assertEquals("1000.00",settlement.path("total").path("importe").asText());
        assertEquals(confirmed.body(),send("POST",site+"/operaciones/"+buy+"/confirmar",JsonSupport.JSON.writeValueAsString(recognition),key,version).body());
        assertEquals("COMPLETADA",get(site+"/comandos/confirmar_operacion/"+key).path("estado").asText());
        var inventory=get(site+"/inventario/posiciones?tamano=100");
        var vendible=get(site+"/inventario/posiciones?tamano=100&disponibles_para_venta=true");
        for(var row:vendible.path("elementos")) {assertEquals("DISPONIBLE",row.path("estado").asText());assertFalse(row.path("reservada").asBoolean());}
        assertEquals(200,send("GET",site+"/inventario/posiciones?disponibles_para_venta=false",null,null).statusCode());
        assertEquals(400,send("GET",site+"/inventario/posiciones?disponibles_para_venta=yes",null,null).statusCode());
        rows=inventory.has("elementos") ? inventory.get("elementos") : inventory.get("items");
        String position="";for (var row : rows) if (row.path("animal_id").asText().equals(animal)) position=row.path("id").asText();assertFalse(position.isEmpty());
        var sellBody=JsonSupport.JSON.createObjectNode().put("tipo","VENTA").put("parte_id",party).put("fecha_operacion",date);
        lot=sellBody.putArray("lotes").addObject().put("numero_lote",1).put("unidad_precio","CABEZA").put("precio_unitario","1600.0000");lot.putArray("posiciones").add(position);
        String sell=post(site+"/operaciones",sellBody,201).path("id").asText();
        post(site+"/operaciones/"+sell+"/reservas",JsonSupport.JSON.createObjectNode().put("vence_en",java.time.Instant.now().plusSeconds(900).toString()),201);
        version="\""+get(site+"/operaciones/"+sell).path("version_lock").asLong()+"\"";
        agreed=send("POST",site+"/operaciones/"+sell+"/acordar","{}",UUID.randomUUID().toString(),version); assertEquals(200,agreed.statusCode(),agreed.body());
        version="\""+get(site+"/operaciones/"+sell).path("version_lock").asLong()+"\"";
        confirmed=send("POST",site+"/operaciones/"+sell+"/confirmar",JsonSupport.JSON.writeValueAsString(recognition),UUID.randomUUID().toString(),version);assertEquals(200,confirmed.statusCode(),confirmed.body());
        String liq=JsonSupport.JSON.readTree(confirmed.body()).path("id").asText();
        var pay=recognition.deepCopy().put("parte_id",party).put("tipo","COBRO").put("metodo","EFECTIVO").put("recibido_el",date);pay.putObject("importe").put("importe","1200.00").put("moneda","MXN");
        String payment=post(site+"/pagos",pay,201).path("id").asText();post(site+"/pagos/"+payment+"/validar",recognition,200);
        var apply=recognition.deepCopy();var application=apply.putArray("aplicaciones").addObject().put("liquidacion_id",liq);application.putObject("importe").put("importe","1200.00").put("moneda","MXN");
        post(site+"/pagos/"+payment+"/aplicaciones",apply,201);assertEquals("400.00",get(site+"/liquidaciones/"+liq).path("saldo").path("importe").asText());
        var receipt=send("GET",site+"/liquidaciones/"+liq+"/comprobante",null,null);assertEquals(200,receipt.statusCode());assertTrue(receipt.body().startsWith("%PDF-1.4"));
        var cartera=get(site+"/reportes/cartera?direccion=POR_COBRAR&tamano=100&vencida=false");
        assertTrue(cartera.path("filas").isArray());assertFalse(cartera.path("corte_en").asText().isBlank());
        for(var row:cartera.path("filas")) assertTrue(row.path("saldo").path("importe").isTextual());
        assertEquals(400,send("GET",site+"/reportes/cartera?vencida=yes",null,null).statusCode());
        assertEquals(400,send("GET",site+"/reportes/cartera?periodo_id=invalid",null,null).statusCode());
        assertEquals(400,send("GET",site+"/reportes/cartera?periodo_id="+period,null,null).statusCode());
        assertEquals(400,send("GET",site+"/reportes/margen?operacion_id=1-1-1-1-1",null,null).statusCode());
        assertEquals(400,send("GET",site+"/reportes/margen?periodo_id=invalid",null,null).statusCode());
        var margen=get(site+"/reportes/margen");
        for(String field:java.util.List.of("venta_neta","costo_vendido","gastos_directos","margen","perdidas")) {
            assertTrue(margen.path(field).path("importe").isTextual(),field);assertEquals("MXN",margen.path(field).path("moneda").asText());
        }
        assertFalse(margen.path("corte_en").asText().isBlank());
        var carteraCsv=send("GET",site+"/reportes/cartera/csv",null,null);assertEquals(200,carteraCsv.statusCode(),carteraCsv.body());
        assertTrue(carteraCsv.body().split("\r\n")[0].contains("\"liquidacion_id\""));
        String ownRow=java.util.Arrays.stream(carteraCsv.body().split("\r\n")).filter(line -> line.contains("\""+liq+"\"")).findFirst().orElseThrow();
        assertTrue(ownRow.contains("\"\"importe\"\":\"\"400.00\"\""),ownRow);
        var margenCsv=send("GET",site+"/reportes/margen/csv",null,null);assertEquals(200,margenCsv.statusCode(),margenCsv.body());
        var exported=margenCsv.body().split("\r\n");assertEquals(2,exported.length);assertTrue(exported[0].contains("\"venta_neta\""));assertTrue(exported[0].contains("\"margen\""));
        assertTrue(exported[1].contains("\"\"importe\"\":\"\""+margen.path("venta_neta").path("importe").asText()+"\"\""),exported[1]);
        var inventoryCsv=send("GET",site+"/reportes/inventario/csv",null,null);assertEquals(200,inventoryCsv.statusCode());
        assertTrue(inventoryCsv.body().split("\r\n")[0].contains("\"animal_id\""));assertTrue(inventoryCsv.body().contains("\""+position+"\""));
        recognition.put("motivo","DEMO anulación con versión obsoleta");
        assertEquals(412,send("POST",site+"/operaciones/"+sell+"/anular",recognition.toString(),UUID.randomUUID().toString(),"\"0\"").statusCode());
        assertEquals("400.00",get(site+"/liquidaciones/"+liq).path("saldo").path("importe").asText());
        send("POST","/sesion/logout","{}",null);
    }

    @Test void adminCreatesMembershipAndCurrentAuthorizationRejectsBlockedUser() throws Exception {
        login();
        String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
        String name="demo.api."+UUID.randomUUID().toString().substring(0,8);
        String password=UUID.randomUUID().toString();
        var body=JsonSupport.JSON.createObjectNode().put("login",name).put("nombre","DEMO API usuario").put("contrasena",password);
        String key=UUID.randomUUID().toString(), json=JsonSupport.JSON.writeValueAsString(body);
        var first=send("POST",site+"/usuarios",json,key);assertEquals(201,first.statusCode(),first.body());
        assertFalse(first.body().contains("hash_contrasena"));assertFalse(first.body().contains(password));
        assertEquals(first.body(),send("POST",site+"/usuarios",json,key).body());
        var diagnosis=get(site+"/integraciones/diagnostico");
        assertTrue(diagnosis.path("proceso").path("contadores_se_reinician").asBoolean());
        assertTrue(diagnosis.path("comandos").path("completados").asLong()>0);
        assertEquals(1000,diagnosis.path("consultas").path("umbral_lenta_ms").asInt());
        assertEquals(4,diagnosis.path("pools").path("A").path("maximo").asInt());
        assertTrue(diagnosis.path("pools").path("A").path("activos").asInt()>=0);
        assertFalse(diagnosis.toString().contains("jdbc:"));assertFalse(diagnosis.toString().contains(password));
        assertFalse(diagnosis.toString().contains("contrasena"));assertTrue(diagnosis.has("sincronizacion"));
        String user=JsonSupport.JSON.readTree(first.body()).path("id").asText();
        post(site+"/usuarios/"+user+"/membresias",JsonSupport.JSON.createObjectNode().put("rol_codigo","AUDITOR").put("vigente",true),200);
        ApiPostgresTest auditor=new ApiPostgresTest();auditor.csrf();
        var loginBody=JsonSupport.JSON.createObjectNode().put("login",name).put("contrasena",password);
        assertEquals(204,auditor.send("POST","/sesion/login",JsonSupport.JSON.writeValueAsString(loginBody),null).statusCode());auditor.csrf();
        assertEquals(200,auditor.send("GET",site+"/operaciones",null,null).statusCode());
        assertEquals(403,auditor.send("GET",site+"/integraciones/diagnostico",null,null).statusCode());
        assertEquals(403,auditor.send("POST",site+"/contrapartes","{\"nombre\":\"DEMO forbidden\"}",UUID.randomUUID().toString()).statusCode());
        var blocked=send("PATCH",site+"/usuarios/"+user,"{\"estado\":\"BLOQUEADO\"}",UUID.randomUUID().toString());assertEquals(200,blocked.statusCode(),blocked.body());
        assertEquals(401,auditor.send("GET","/sesion/actual",null,null).statusCode());
        send("POST","/sesion/logout","{}",null);
    }

    HttpResponse<String> upload(String site,byte[] content,String previous,String operation,String key) throws Exception {
        String boundary="BOVI"+UUID.randomUUID().toString().replace("-","");
        var bytes=new java.io.ByteArrayOutputStream();
        bytes.writeBytes(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"tipo_documental\"\r\n\r\nDEMO_TICKET\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        if (previous!=null) bytes.writeBytes(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"documento_previo_id\"\r\n\r\n"+previous+"\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        if (operation!=null) bytes.writeBytes(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"operacion_id\"\r\n\r\n"+operation+"\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        bytes.writeBytes(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"archivo\"; filename=\"DEMO.pdf\"\r\nContent-Type: application/pdf\r\n\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        bytes.writeBytes(content);bytes.writeBytes(("\r\n--"+boundary+"--\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        var request=HttpRequest.newBuilder(URI.create(base+site+"/documentos")).header("Content-Type","multipart/form-data; boundary="+boundary).header(csrfHeader,token).header("Idempotency-Key",key).POST(HttpRequest.BodyPublishers.ofByteArray(bytes.toByteArray())).build();
        return client.send(request,HttpResponse.BodyHandlers.ofString());
    }
    @Test void privateFilesRetryVersionsAndReviewKeepOriginal() throws Exception {
        login();String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
        String party=post(site+"/contrapartes",JsonSupport.JSON.createObjectNode().put("nombre","DEMO files "+UUID.randomUUID()),201).path("id").asText();
        String operation=post(site+"/operaciones",JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",java.time.LocalDate.now().toString()),201).path("id").asText();
        byte[] pdf=mx.bovicierre.evidencia.SettlementPdf.render(JsonSupport.object("{\"id\":\"DEMO ORIGINAL\",\"conceptos\":[]}"));
        String key=UUID.randomUUID().toString();var first=upload(site,pdf,null,operation,key);assertEquals(201,first.statusCode(),first.body());
        var doc=JsonSupport.JSON.readTree(first.body());String id=doc.path("id").asText();assertEquals(1,doc.path("version").asInt());assertEquals("application/pdf",doc.path("mime").asText());
        assertEquals(first.body(),upload(site,pdf,null,operation,key).body());
        var review=JsonSupport.JSON.createObjectNode().put("criterio","DEMO revisión de versión exacta").put("resultado","SIN_OBSERVACIONES");review.putArray("documentos").addObject().put("documento_id",id).put("resultado","SIN_OBSERVACIONES");
        post(site+"/operaciones/"+operation+"/revisiones",review,200);
        byte[] revised=mx.bovicierre.evidencia.SettlementPdf.render(JsonSupport.object("{\"id\":\"DEMO NUEVO\",\"conceptos\":[]}"));
        var second=upload(site,revised,id,operation,UUID.randomUUID().toString());assertEquals(201,second.statusCode(),second.body());assertEquals(2,JsonSupport.JSON.readTree(second.body()).path("version").asInt());
        var request=HttpRequest.newBuilder(URI.create(base+site+"/documentos/"+id+"/contenido")).GET().build();var download=client.send(request,HttpResponse.BodyHandlers.ofByteArray());assertEquals(200,download.statusCode());assertArrayEquals(pdf,download.body());
        assertEquals(422,upload(site,"<html>fake</html>".getBytes(),null,operation,UUID.randomUUID().toString()).statusCode());
        var anonymous=new ApiPostgresTest();assertEquals(401,anonymous.send("GET",site+"/documentos/"+id+"/contenido",null,null).statusCode());
        send("POST","/sesion/logout","{}",null);
    }

    @Test void providerCaptureAcceptanceAndExpenseSnapshotRemainCanonical() throws Exception {
        login();
        String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
        var tariffs=get(site+"/integraciones/proveedor/tarifas?tamano=10");
        assertFalse(tariffs.path("elementos").isEmpty());
        var quote=tariffs.path("elementos").get(0); assertTrue(quote.path("hash_sha256").asText().matches("[a-f0-9]{64}"));
        var body=JsonSupport.JSON.createObjectNode().put("snapshot_id",quote.path("snapshot_id").asText());
        String key=UUID.randomUUID().toString();
        var accepted=send("POST",site+"/integraciones/proveedor/tarifas/aceptaciones",body.toString(),key);
        assertEquals(201,accepted.statusCode(),accepted.body());
        assertEquals(accepted.body(),send("POST",site+"/integraciones/proveedor/tarifas/aceptaciones",body.toString(),key).body());
        String party=post(site+"/contrapartes",JsonSupport.JSON.createObjectNode().put("nombre","TEST tarifa "+UUID.randomUUID()),201).path("id").asText();
        String op=post(site+"/operaciones",JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",java.time.LocalDate.now().toString()),201).path("id").asText();
        String period="";
        for(var row:get(site+"/periodos").path("elementos")) if(row.path("estado").asText().equals("ABIERTO")) period=row.path("id").asText();
        assertFalse(period.isEmpty());
        var expense=JsonSupport.JSON.createObjectNode().put("operacion_id",op).put("naturaleza","COSTO").put("clasificacion","OTRO").put("concepto","TEST transporte aceptado").put("fecha_economica",java.time.LocalDate.now().toString()).put("fecha_reconocimiento",java.time.LocalDate.now().toString()).put("periodo_id",period).put("snapshot_id",quote.path("snapshot_id").asText());
        expense.set("importe",quote.path("precio"));
        key=UUID.randomUUID().toString();
        var created=send("POST",site+"/gastos",expense.toString(),key); assertEquals(201,created.statusCode(),created.body());
        var result=JsonSupport.JSON.readTree(created.body()); assertTrue(result.has("gasto_id")); assertEquals(quote.path("precio"),result.path("importe"));
        assertEquals(site+"/gastos/"+result.path("gasto_id").asText(),created.headers().firstValue("location").orElse("").substring("/api/v1".length()));
        assertEquals(created.body(),send("POST",site+"/gastos",expense.toString(),key).body());
        var stored=get(site+"/gastos/"+result.path("gasto_id").asText());
        assertEquals(quote.path("snapshot_id").asText(),stored.path("snapshot_fuente_externa").path("snapshot_id").asText());
        var unaccepted=get(site+"/integraciones/proveedor/tarifas?tamano=1").path("elementos").get(0);
        expense.put("snapshot_id",unaccepted.path("snapshot_id").asText());
        assertEquals(422,send("POST",site+"/gastos",expense.toString(),UUID.randomUUID().toString()).statusCode());
        String siteB="/sedes/bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";
        var quoteB=get(siteB+"/integraciones/proveedor/tarifas?tamano=1").path("elementos").get(0);
        var acceptanceB=JsonSupport.JSON.createObjectNode().put("snapshot_id",quoteB.path("snapshot_id").asText());
        post(siteB+"/integraciones/proveedor/tarifas/aceptaciones",acceptanceB,201);
        assertEquals(404,send("POST",site+"/integraciones/proveedor/tarifas/aceptaciones",acceptanceB.toString(),UUID.randomUUID().toString()).statusCode());
        String opB=post(siteB+"/operaciones",JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",java.time.LocalDate.now().toString()),201).path("id").asText();
        String periodB="",recognitionB="";
        java.time.LocalDate lastEnd=null;
        for(var row:get(siteB+"/periodos?tamano=100").path("elementos")) {
            var end=java.time.LocalDate.parse(row.path("hasta").asText());
            if(lastEnd==null || end.isAfter(lastEnd)) lastEnd=end;
            if(row.path("estado").asText().equals("ABIERTO")) {periodB=row.path("id").asText();recognitionB=row.path("desde").asText();}
        }
        if(periodB.isEmpty()) {
            var start=lastEnd==null ? java.time.LocalDate.now().withDayOfMonth(1) : lastEnd.plusDays(1);
            var createdPeriod=post(siteB+"/periodos",JsonSupport.JSON.createObjectNode().put("desde",start.toString()).put("hasta",start.withDayOfMonth(start.lengthOfMonth()).toString()),201);
            periodB=createdPeriod.path("id").asText();recognitionB=start.toString();
        }
        assertFalse(periodB.isEmpty());
        expense.put("operacion_id",opB).put("periodo_id",periodB).put("snapshot_id",quoteB.path("snapshot_id").asText());
        expense.put("fecha_reconocimiento",recognitionB);
        expense.set("importe",quoteB.path("precio"));
        var expenseB=post(siteB+"/gastos",expense,201);
        assertEquals(quoteB.path("snapshot_id").asText(),get(siteB+"/gastos/"+expenseB.path("gasto_id").asText()).path("snapshot_fuente_externa").path("snapshot_id").asText());
        send("POST","/sesion/logout","{}",null);
    }

    @Test void identificationBoundaryRejectsLengthUnicodeAndUnknownSystemWithoutSqlLeak() throws Exception {
        login();
        String route="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/animales";
        for(String invalid:java.util.List.of("X".repeat(41),"Ñ123","--- ")) {
            var body=JsonSupport.JSON.createObjectNode().put("sexo","M"); body.putArray("identificaciones").addObject().put("sistema","INTERNO").put("codigo",invalid);
            var response=send("POST",route,body.toString(),UUID.randomUUID().toString());
            assertEquals(400,response.statusCode(),response.body()); assertFalse(response.body().contains("SQL"));
        }
        var body=JsonSupport.JSON.createObjectNode().put("sexo","M"); body.putArray("identificaciones").addObject().put("sistema","NO_PERMITIDO").put("codigo","DEMO123");
        assertEquals(400,send("POST",route,body.toString(),UUID.randomUUID().toString()).statusCode());
        var numeric=JsonSupport.JSON.createObjectNode().put("sexo","M"); numeric.putArray("identificaciones").addObject().put("sistema","INTERNO").put("codigo",12345);
        assertEquals(400,send("POST",route,numeric.toString(),UUID.randomUUID().toString()).statusCode());
        var valid=JsonSupport.JSON.createObjectNode().put("sexo","M"); valid.putArray("identificaciones").addObject().put("sistema","INTERNO").put("codigo","DEMO"+UUID.randomUUID().toString().replace("-","")+"1234");
        assertEquals(201,send("POST",route,valid.toString(),UUID.randomUUID().toString()).statusCode());
        send("POST","/sesion/logout","{}",null);
    }

    @Test void weightCorrectionKeepsOriginalCompositionAndRequiresReason() throws Exception {
        login();String site="/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
        String party=post(site+"/contrapartes",JsonSupport.JSON.createObjectNode().put("nombre","DEMO corrección "+UUID.randomUUID()),201).path("id").asText();
        var animals=new java.util.ArrayList<String>();
        for(int i=0;i<3;i++) {
            var animal=JsonSupport.JSON.createObjectNode().put("sexo","M");animal.putArray("identificaciones").addObject().put("sistema","INTERNO").put("codigo","DEMO"+UUID.randomUUID().toString().replace("-",""));
            animals.add(post(site+"/animales",animal,201).path("id").asText());
        }
        var draft=JsonSupport.JSON.createObjectNode().put("tipo","COMPRA").put("parte_id",party).put("fecha_operacion",java.time.LocalDate.now().toString());
        var lot=draft.putArray("lotes").addObject().put("numero_lote",1).put("unidad_precio","KG").put("precio_unitario","10.0000");lot.putArray("animales").add(animals.get(0)).add(animals.get(1));
        String operation=post(site+"/operaciones",draft,201).path("id").asText();
        var ticket=JsonSupport.JSON.createObjectNode().put("numero_lote",1).put("modo","NETO_REPORTADO").put("pesado_en",java.time.Instant.now().toString());ticket.putObject("neto").put("kg","300.000");
        var composition=ticket.putArray("animales");composition.addObject().put("animal_id",animals.get(0)).putObject("peso_individual").put("kg","100.000");composition.addObject().put("animal_id",animals.get(1));
        String original=post(site+"/operaciones/"+operation+"/pesajes",ticket,201).path("id").asText();post(site+"/pesajes/"+original+"/aprobar",JsonSupport.JSON.createObjectNode(),200);
        var history=get(site+"/operaciones/"+operation+"/pesajes").path("elementos");assertEquals(1,history.size());assertEquals(2,history.get(0).path("animales").size());
        var originalComposition=history.get(0).path("animales").deepCopy();
        for(var entry:originalComposition) {
            if(entry.path("animal_id").asText().equals(animals.get(0))) assertEquals("100.000",entry.path("peso_individual").path("kg").asText());
            else assertTrue(entry.path("peso_individual").isMissingNode() || entry.path("peso_individual").isNull());
        }
        String route=site+"/pesajes/"+original+"/correcciones";
        assertEquals(400,send("POST",route,ticket.toString(),UUID.randomUUID().toString()).statusCode());
        var correction=ticket.deepCopy().put("motivo","DEMO error de captura, conservar ticket original");correction.putObject("neto").put("kg","301.000");
        ((tools.jackson.databind.node.ObjectNode)correction.path("animales").get(0)).putObject("peso_individual").put("kg","101.000");
        var wrong=correction.deepCopy().put("corrige_a_id",UUID.randomUUID().toString());assertEquals(400,send("POST",route,wrong.toString(),UUID.randomUUID().toString()).statusCode());
        var subset=correction.deepCopy();subset.putArray("animales").add(correction.path("animales").get(0).deepCopy());
        assertEquals(422,send("POST",route,subset.toString(),UUID.randomUUID().toString()).statusCode());
        var superset=correction.deepCopy();((tools.jackson.databind.node.ArrayNode)superset.path("animales")).addObject().put("animal_id",animals.get(2));
        assertEquals(422,send("POST",route,superset.toString(),UUID.randomUUID().toString()).statusCode());
        var untouched=get(site+"/operaciones/"+operation+"/pesajes").path("elementos");
        assertEquals(1,untouched.size());assertEquals("APROBADO",untouched.get(0).path("estado").asText());assertEquals(originalComposition,untouched.get(0).path("animales"));
        String key=UUID.randomUUID().toString();var response=send("POST",route,correction.toString(),key);assertEquals(201,response.statusCode(),response.body());String revised=JsonSupport.JSON.readTree(response.body()).path("id").asText();
        assertEquals(response.body(),send("POST",route,correction.toString(),key).body());assertEquals(409,send("POST",route,correction.deepCopy().put("motivo","DEMO otro motivo").toString(),key).statusCode());
        history=get(site+"/operaciones/"+operation+"/pesajes").path("elementos");assertEquals(2,history.size());
        for(var entry:history) {
            if(entry.path("id").asText().equals(original)) {assertEquals("CORREGIDO",entry.path("estado").asText());assertEquals(originalComposition,entry.path("animales"));}
            if(entry.path("id").asText().equals(revised)) {assertEquals(original,entry.path("corrige_a_id").asText());assertEquals(correction.path("motivo").asText(),entry.path("motivo_correccion").asText());assertEquals(2,entry.path("animales").size());}
        }
        send("POST","/sesion/logout","{}",null);
    }

}
