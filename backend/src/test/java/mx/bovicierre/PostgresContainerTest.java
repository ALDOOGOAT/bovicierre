package mx.bovicierre;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.testcontainers.postgresql.PostgreSQLContainer;
import com.github.dockerjava.api.model.Ports;
import com.github.dockerjava.api.model.ExposedPort;
import mx.bovicierre.shared.JsonSupport;
import static org.junit.jupiter.api.Assertions.*;

@EnabledIfEnvironmentVariable(named="BOVI_TC_IT",matches="true")
class PostgresContainerTest {
    @Test void freshPostgresMigrationsRestrictRuntimeAndKeepCanonicalReplay() throws Exception {
        String password=UUID.randomUUID().toString();
        try(var pg=new PostgreSQLContainer("postgres:18.6").withDatabaseName("bovicierre").withUsername("postgres").withPassword(password)) {
            pg.withCreateContainerCmdModifier(cmd -> cmd.getHostConfig().withPortBindings(new com.github.dockerjava.api.model.PortBinding(Ports.Binding.bindIpAndPort("127.0.0.1",0),new ExposedPort(5432))));
            pg.start();
            Path database=Path.of("../db").toAbsolutePath().normalize();
            if(!Files.exists(database)) database=Path.of("db").toAbsolutePath().normalize();
            UUID company=UUID.randomUUID(),site=UUID.randomUUID(),actor=UUID.randomUUID();
            try(var admin=DriverManager.getConnection(pg.getJdbcUrl(),"postgres",password);var sql=admin.createStatement()) {
                sql.execute(Files.readString(database.resolve("bootstrap/01_roles.sql")));
                try(var migrations=Files.list(database.resolve("migrations"))) {
                    for(var migration:migrations.filter(path -> path.getFileName().toString().matches("V[0-9]+__.*\\.sql")).sorted(java.util.Comparator.comparingInt(path -> Integer.parseInt(path.getFileName().toString().substring(1,path.getFileName().toString().indexOf("__"))))).toList()) sql.execute(Files.readString(migration));
                }
                sql.execute("INSERT INTO infra.nodo_config VALUES('A','"+company+"','TEST fresh PostgreSQL');");
                sql.execute("INSERT INTO bovi.empresa VALUES('"+company+"','TEST empresa',NULL,'ACTIVA','A',now()); INSERT INTO bovi.sucursal VALUES('"+company+"','"+site+"','TEST-A','TEST Sede','A','America/Mexico_City','A'); INSERT INTO bovi.rol_aplicacion VALUES('ADMIN','Administración');");
                String hash="{bcrypt}"+new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder().encode(UUID.randomUUID().toString());
                sql.execute("INSERT INTO bovi.usuario VALUES('"+company+"','"+actor+"','test.actor','TEST actor','"+hash+"','ACTIVO','A',now()); INSERT INTO bovi.membresia_usuario VALUES('"+company+"','"+site+"','"+actor+"','ADMIN',true,'A');");
                // Random ephemeral authentication; no functional password is committed.
                sql.execute("ALTER ROLE bovi_app_a PASSWORD '"+password+"'");
                assertEquals("23514",assertThrows(SQLException.class,() -> sql.execute("UPDATE bovi.sucursal SET codigo='lowercase'")).getSQLState());
            }
            try(var runtime=DriverManager.getConnection(pg.getJdbcUrl(),"bovi_app_a",password);var sql=runtime.createStatement()) {
                assertEquals("42501",assertThrows(SQLException.class,() -> sql.execute("CREATE TABLE bovi.forbidden(id int)")).getSQLState());
                assertEquals("42501",assertThrows(SQLException.class,() -> sql.execute("DELETE FROM bovi.parte")).getSQLState());
                assertEquals("42501",assertThrows(SQLException.class,() -> sql.execute("SELECT hash_contrasena FROM bovi.usuario")).getSQLState());
                var body=JsonSupport.JSON.createObjectNode().put("nombre","TEST fresh canonical");
                String key=UUID.randomUUID().toString(),hash=JsonSupport.hash("crear_contraparte",body);
                String first=command(runtime,company,site,actor,key,hash,body.toString());
                assertEquals(first,command(runtime,company,site,actor,key,hash,body.toString()));
                var error=assertThrows(SQLException.class,() -> command(runtime,company,site,actor,key,"changed-intent",body.toString()));
                assertEquals("P0001",error.getSQLState());
                assertEquals("P0001",assertThrows(SQLException.class,() -> command(runtime,company,site,actor,UUID.randomUUID().toString(),"missing-name","{}")).getSQLState());
                try(var count=sql.executeQuery("SELECT count(*) FROM bovi.parte")) { assertTrue(count.next()); assertEquals(1,count.getInt(1)); }
                try(var version=sql.executeQuery("SHOW server_version_num")) { assertTrue(version.next()); assertTrue(version.getInt(1)>=180000); }
            }
        }
    }
    private String command(Connection connection,UUID company,UUID site,UUID actor,String key,String hash,String body) throws SQLException {
        try(var statement=connection.prepareStatement("SELECT bovi.cmd_ejecutar(?,?,?,?,?,?,?,?::jsonb)::text")) {
            statement.setObject(1,company); statement.setObject(2,site); statement.setObject(3,actor); statement.setString(4,key); statement.setString(5,hash); statement.setObject(6,UUID.randomUUID()); statement.setString(7,"crear_contraparte"); statement.setString(8,body);
            try(var rows=statement.executeQuery()) { assertTrue(rows.next()); return rows.getString(1); }
        }
    }
}
