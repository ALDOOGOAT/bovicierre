package mx.bovicierre;
import java.nio.file.Files;
import java.nio.file.Path;
import org.flywaydb.core.Flyway;
public final class Migrate {
    public static void main(String[] args) throws Exception {
        if (args.length != 3 && args.length != 4) throw new IllegalArgumentException("url, archivo de secreto, directorio de migraciones");
        var flyway=Flyway.configure().dataSource(args[0],"postgres",Files.readString(Path.of(args[1])).trim())
            .locations("filesystem:"+args[2]).defaultSchema("infra").schemas("infra")
            .cleanDisabled(true).baselineOnMigrate(false).baselineVersion("3").baselineDescription("Adopción auditada de catálogo existente; no ejecución V1-3").load();
        if (args.length == 4) {
            if (!args[3].equals("baseline3")) throw new IllegalArgumentException("Modo inválido");
            flyway.baseline();
        }
        var result=flyway.migrate();
        flyway.validate();
        System.out.println("Flyway: migraciones="+result.migrationsExecuted+"; versión="+result.targetSchemaVersion);
    }
}
