package mx.bovicierre.shared;

import javax.sql.DataSource;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.session.jdbc.config.annotation.SpringSessionDataSource;
import org.springframework.session.jdbc.config.annotation.SpringSessionTransactionManager;

@Configuration
public class DatabaseConfiguration {
    private DataSource pool(Environment env, String name) {
        String prefix = "bovi.database." + name + ".";
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(env.getRequiredProperty(prefix + "url"));
        config.setUsername(env.getRequiredProperty(prefix + "username"));
        config.setPassword(env.getRequiredProperty(prefix + "password"));
        config.setMaximumPoolSize(name.startsWith("worker") ? 2 : 4);
        config.setMinimumIdle(0);
        config.setConnectionTimeout(3000);
        config.setValidationTimeout(1000);
        config.setInitializationFailTimeout(-1);
        config.setPoolName("bovi-" + name);
        return new HikariDataSource(config);
    }

    @Bean("ownerA") DataSource ownerA(Environment env) { return pool(env, "a"); }
    @Bean("ownerB") DataSource ownerB(Environment env) { return pool(env, "b"); }
    @Bean("workerA") DataSource workerA(Environment env) { return pool(env,"worker-a"); }
    @Bean("workerB") DataSource workerB(Environment env) { return pool(env,"worker-b"); }
    @Bean("authDataSource") @SpringSessionDataSource
    DataSource authDataSource(Environment env) { return pool(env, "auth"); }
    @Bean @SpringSessionTransactionManager
    DataSourceTransactionManager sessionTransactionManager(@Qualifier("authDataSource") DataSource ds) {
        return new DataSourceTransactionManager(ds);
    }
}
