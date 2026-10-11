package mx.bovicierre.integraciones;

import java.util.Map;
import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionTemplate;
import mx.bovicierre.shared.JsonSupport;

@Component
public class OutboxWorker {
    private final Map<String,JdbcTemplate> jdbc;
    private final Map<String,TransactionTemplate> transactions;
    private final boolean enabled;
    private final UUID worker=UUID.randomUUID();
    private final java.util.Set<String> unavailable=new java.util.HashSet<>();
    private static final org.slf4j.Logger LOG=org.slf4j.LoggerFactory.getLogger(OutboxWorker.class);
    public OutboxWorker(@Qualifier("workerA") DataSource a,@Qualifier("workerB") DataSource b,@Value("${bovi.outbox-enabled}") boolean enabled) {
        this.enabled=enabled;
        jdbc=Map.of("A",new JdbcTemplate(a),"B",new JdbcTemplate(b));
        transactions=Map.of("A",new TransactionTemplate(new DataSourceTransactionManager(a)),"B",new TransactionTemplate(new DataSourceTransactionManager(b)));
    }
    @Scheduled(initialDelay=10000,fixedDelay=5000)
    public void dispatch() {
        if (!enabled) return;
        for (String node : java.util.List.of("A","B")) {
            try {
                transactions.get(node).execute(status -> jdbc.get(node).queryForObject("select bovi.despachar_outbox(50)::text",String.class));
                if (unavailable.remove(node)) LOG.info("Outbox: propietario {} disponible",node);
            } catch (org.springframework.dao.DataAccessException | org.springframework.transaction.TransactionException ex) {
                if (unavailable.add(node)) LOG.warn("Outbox: propietario {} no disponible; se conserva el trabajo pendiente",node);
            }
        }
        try {
            String claimed=transactions.get("B").execute(status -> jdbc.get("B").queryForObject("select bovi.reclamar_entregas(?,20)::text",String.class,worker));
            for (var event : JsonSupport.JSON.readTree(claimed)) {
                UUID id=UUID.fromString(event.path("id").asText());
                try {
                    transactions.get("A").execute(status -> jdbc.get("A").queryForObject("select bovi.consumir_muerte(?,?,?,?::jsonb)::text",String.class,UUID.fromString(event.path("empresa_id").asText()),UUID.fromString(event.path("sucursal_id").asText()),id,JsonSupport.JSON.writeValueAsString(event.path("payload"))));
                    transactions.get("B").execute(status -> jdbc.get("B").queryForObject("select bovi.confirmar_entrega(?,?)::text",String.class,id,worker));
                    unavailable.remove("IDENTIDAD");
                } catch (org.springframework.dao.DataAccessException | org.springframework.transaction.TransactionException ex) {
                    transactions.get("B").execute(status -> jdbc.get("B").queryForObject("select bovi.fallar_entrega(?,?)::text",String.class,id,worker));
                    if (unavailable.add("IDENTIDAD")) LOG.warn("Outbox: identidad central pendiente; el próximo ciclo reintenta sin duplicar el consumo");
                }
            }
        } catch (org.springframework.dao.DataAccessException | org.springframework.transaction.TransactionException ex) {
            if (unavailable.add("IDENTIDAD")) LOG.warn("Outbox: la entrega conserva su lease hasta vencer; se reintentará desde el propietario");
        }
    }
}
