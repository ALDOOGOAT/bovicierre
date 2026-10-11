package mx.bovicierre.shared;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import mx.bovicierre.acceso.AccessService;
import tools.jackson.databind.node.ObjectNode;

@Service
public class CommandService {
    private static final org.slf4j.Logger LOG=org.slf4j.LoggerFactory.getLogger(CommandService.class);
    private final AccessService access;
    private final Map<String,JdbcTemplate> jdbc;
    private final Map<String,TransactionTemplate> transactions;
    private final java.time.Instant processStarted=java.time.Instant.now();
    private final java.util.concurrent.atomic.LongAdder successes=new java.util.concurrent.atomic.LongAdder(),commandErrors=new java.util.concurrent.atomic.LongAdder(),commandNanos=new java.util.concurrent.atomic.LongAdder(),queries=new java.util.concurrent.atomic.LongAdder(),queryErrors=new java.util.concurrent.atomic.LongAdder(),slowQueries=new java.util.concurrent.atomic.LongAdder(),queryNanos=new java.util.concurrent.atomic.LongAdder();
    private static final java.util.Set<String> MASTER=java.util.Set.of("crear_contraparte","registrar_animal","crear_predio","crear_usuario","actualizar_usuario","asignar_membresia");
    public CommandService(AccessService access,@Qualifier("ownerA") DataSource a,@Qualifier("ownerB") DataSource b) {
        this.access=access;
        jdbc=Map.of("A",new JdbcTemplate(a),"B",new JdbcTemplate(b));
        transactions=Map.of("A",new TransactionTemplate(new DataSourceTransactionManager(a)),"B",new TransactionTemplate(new DataSourceTransactionManager(b)));
    }
    public String command(UUID user,UUID site,String command,ObjectNode payload,String key,UUID correlation) {
        return command(user,site,command,payload,key,correlation,JsonSupport.hash(command,payload));
    }
    public String command(UUID user,UUID site,String command,ObjectNode payload,String key,UUID correlation,String hash) {
        long started=System.nanoTime();
        String owner="NO_RESUELTO",outcome="FALLO",errorCode=null;
        try {
            var scope=access.authorize(user,site,true);
            owner=MASTER.contains(command) ? "A" : scope.owner();
            java.util.Set<String> required=command.contains("periodo") || command.equals("anular_venta") || command.equals("registrar_baja") || java.util.Set.of("crear_usuario","actualizar_usuario","asignar_membresia","registrar_revision","ajustar_liquidacion").contains(command) ? java.util.Set.of("ADMIN") :
                java.util.Set.of("registrar_pago","aplicar_pago","revertir_aplicacion","reembolsar_pago","validar_pago").contains(command) ? java.util.Set.of("ADMIN","CAJA") : java.util.Set.of("ADMIN","OPERADOR");
            if (scope.roles().stream().noneMatch(required::contains)) throw new ApiException(403,"AUTH403","No tiene permiso para esta acción.");
            if (key == null || key.isBlank() || key.length() < 16 || key.length() > 80) throw new ApiException(400,"BV400","Se requiere una Idempotency-Key de entre 16 y 80 caracteres.");
            JsonSupport.decimals(payload);
            if(command.equals("registrar_animal")) JsonSupport.animalIdentifications(payload);
            String node=MASTER.contains(command) ? "A" : scope.owner();
            if (!transactions.containsKey(node)) throw new ApiException(503,"BV501","El propietario de la sede no está configurado.");
            for (int attempt=0; ; attempt++) {
                try {
                    String response=transactions.get(node).execute(status -> jdbc.get(node).queryForObject("select bovi.cmd_ejecutar(?,?,?,?,?,?,?,?::jsonb)::text",String.class,
                        scope.company(),scope.site(),user,key,hash,correlation,command,JsonSupport.JSON.writeValueAsString(payload)));
                    outcome="COMPLETADA";
                    return response;
                } catch (org.springframework.dao.DataAccessException ex) {
                    Throwable cause=ex.getMostSpecificCause();
                    if (attempt < 2 && cause instanceof java.sql.SQLException sql && List.of("40001","40P01").contains(sql.getSQLState())) {
                        try { Thread.sleep(java.util.concurrent.ThreadLocalRandom.current().nextLong(20,81)*(attempt+1)); }
                        catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); throw new ApiException(503,"BV501","La solicitud fue interrumpida."); }
                        continue;
                    }
                    throw ex;
                }
            }
        } catch(ApiException ex) {
            errorCode=ex.code;outcome=ex.status<500 ? "RECHAZADA" : "FALLO";throw ex;
        } catch(RuntimeException ex) {
            var mapped=ApiErrors.database((Throwable)ex);
            errorCode=mapped.code;outcome=mapped.status<500 ? "RECHAZADA" : "FALLO";throw ex;
        } finally {
            long elapsed=System.nanoTime()-started;
            commandNanos.add(elapsed);
            if(outcome.equals("COMPLETADA")) successes.increment(); else commandErrors.increment();
            var event=JsonSupport.JSON.createObjectNode().put("evento","COMANDO_TERMINADO").put("comando",command).put("correlation_id",correlation==null ? null : correlation.toString()).put("nodo_dueno",owner).put("duracion_ms",java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(elapsed)).put("resultado",outcome);
            if(errorCode!=null) event.put("codigo",errorCode);
            LOG.info("{}",JsonSupport.JSON.writeValueAsString(event));
        }
    }
    public String query(UUID user,UUID site,String resource,ObjectNode params) {
        var scope=access.authorize(user,site,false);
        if (resource.equals("usuarios") && !scope.roles().contains("ADMIN")) throw new ApiException(403,"AUTH403","Se requiere rol ADMIN.");
        String node=resource.equals("comando") && MASTER.contains(params.path("comando").asText()) ? "A" : java.util.Set.of("contrapartes","animales","animal","predios","usuarios").contains(resource) ? "A" : scope.owner();
        if (!jdbc.containsKey(node)) throw new ApiException(503,"BV501","El propietario de la sede no está configurado.");
        return timedQuery(node,resource,() -> jdbc.get(node).queryForObject("select bovi.consultar(?,?,?,?,?::jsonb)::text",String.class,scope.company(),site,user,resource,JsonSupport.JSON.writeValueAsString(params)));
    }
    public String providerTariffs(UUID user,UUID site,ObjectNode params) {
        var scope=access.authorize(user,site,false);
        // Cada llamada autocommit termina antes de la siguiente; nunca mantiene locks financieros durante FDW.
        String quotes=timedQuery("A","leer_tarifas_proveedor",() -> jdbc.get("A").queryForObject("select bovi.leer_tarifas_proveedor(?,?,?,?::jsonb)::text",String.class,scope.company(),site,user,JsonSupport.JSON.writeValueAsString(params)));
        return timedQuery(scope.owner(),"capturar_tarifas_proveedor",() -> jdbc.get(scope.owner()).queryForObject("select bovi.capturar_tarifas_proveedor(?,?,?,?::jsonb)::text",String.class,scope.company(),site,user,quotes));
    }
    private String timedQuery(String node,String resource,java.util.function.Supplier<String> query) {
        long started=System.nanoTime();String outcome="COMPLETADA",errorCode=null;
        try { return query.get(); }
        catch(RuntimeException ex) {queryErrors.increment();outcome="FALLO";errorCode=ApiErrors.database((Throwable)ex).code;throw ex;}
        finally {
            long elapsed=System.nanoTime()-started;queries.increment();queryNanos.add(elapsed);
            if(elapsed>=java.util.concurrent.TimeUnit.SECONDS.toNanos(1)) {
                slowQueries.increment();
                var event=JsonSupport.JSON.createObjectNode().put("evento","CONSULTA_LENTA").put("recurso",resource).put("nodo_dueno",node).put("duracion_ms",java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(elapsed)).put("resultado",outcome);
                if(errorCode!=null) event.put("codigo",errorCode);
                LOG.info("{}",JsonSupport.JSON.writeValueAsString(event));
            }
        }
    }
    public Map<String,Object> diagnostics() {
        return Map.of("proceso",Map.of("iniciado_en",processStarted.toString(),"contadores_se_reinician",true),"comandos",Map.of("completados",successes.sum(),"errores",commandErrors.sum(),"duracion_total_ms",java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(commandNanos.sum())),"consultas",Map.of("total",queries.sum(),"errores",queryErrors.sum(),"lentas",slowQueries.sum(),"umbral_lenta_ms",1000,"duracion_total_ms",java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(queryNanos.sum())));
    }
}
