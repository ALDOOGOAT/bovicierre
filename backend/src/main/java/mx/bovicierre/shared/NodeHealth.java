package mx.bovicierre.shared;

import java.util.LinkedHashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class NodeHealth {
    private final Map<String,JdbcTemplate> nodes;
    private final Map<String,DataSource> pools;
    public NodeHealth(@Qualifier("ownerA") DataSource a,@Qualifier("ownerB") DataSource b,@Qualifier("authDataSource") DataSource auth,@Qualifier("workerA") DataSource workerA,@Qualifier("workerB") DataSource workerB) {
        nodes=Map.of("A",new JdbcTemplate(a),"B",new JdbcTemplate(b),"AUTORIZACION_A",new JdbcTemplate(auth));
        pools=Map.of("A",a,"B",b,"AUTORIZACION_A",auth,"WORKER_A",workerA,"WORKER_B",workerB);
    }
    public Map<String,Object> status() {
        Map<String,String> statuses=new LinkedHashMap<>();
        nodes.forEach((node,jdbc) -> {
            try { jdbc.queryForObject("select 1",Integer.class); statuses.put(node,"DISPONIBLE"); }
            catch (org.springframework.dao.DataAccessException ex) { statuses.put(node,"NO_DISPONIBLE"); }
        });
        return Map.of("estado","ACTIVO","nodos",statuses);
    }
    public Map<String,Object> pools() {
        Map<String,Object> result=new LinkedHashMap<>();
        pools.forEach((node,source) -> {
            if(source instanceof com.zaxxer.hikari.HikariDataSource pool && pool.getHikariPoolMXBean()!=null) {
                var bean=pool.getHikariPoolMXBean();
                result.put(node,Map.of("activos",bean.getActiveConnections(),"inactivos",bean.getIdleConnections(),"esperando",bean.getThreadsAwaitingConnection(),"maximo",pool.getMaximumPoolSize()));
            } else result.put(node,Map.of("estado","NO_DISPONIBLE"));
        });
        return result;
    }
}
