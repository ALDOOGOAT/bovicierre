package mx.bovicierre.evidencia;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.DriverManager;
import mx.bovicierre.shared.JsonSupport;

/** Local administration command. Never starts the web server or scheduled workers. */
public final class CleanupMain {
    private CleanupMain() { }
    public static void main(String[] args) throws Exception {
        if(args.length>1 || (args.length==1 && !args[0].equals("--execute"))) throw new IllegalArgumentException("Uso: cleanup-documents.sh [--execute]");
        var env=System.getenv();
        String secrets=env.getOrDefault("BOVI_SECRETS_DIR",env.getOrDefault("BOVI_SECRET_DIR",System.getProperty("user.home")+"/.local/share/bovicierre-academic/secrets"));
        String password=Files.readString(Path.of(secrets,"worker_password")).strip();
        String directory=env.getOrDefault("BOVI_DOCUMENTS_DIR",System.getProperty("user.home")+"/.local/share/bovicierre-academic/private-documents");
        // Establish both dependencies before scanning; any failed reference check aborts deletion.
        try(var a=DriverManager.getConnection(env.getOrDefault("BOVI_DB_A_URL","jdbc:postgresql://127.0.0.1:19999/bovicierre"),"bovi_worker",password);
            var b=DriverManager.getConnection(env.getOrDefault("BOVI_DB_B_URL","jdbc:postgresql://127.0.0.1:19998/bovicierre"),"bovi_worker",password);
            var qa=a.prepareStatement("select bovi.archivo_referenciado(?)");
            var qb=b.prepareStatement("select bovi.archivo_referenciado(?)")) {
            qa.setQueryTimeout(5); qb.setQueryTimeout(5);
            var result=new PrivateDocuments(directory).cleanup(args.length==1,hash -> {
                try {
                    qa.setString(1,hash); qb.setString(1,hash);
                    boolean inA,inB;
                    try(var rows=qa.executeQuery()) { if(!rows.next()) throw new IllegalStateException("Referencia A no disponible."); inA=rows.getBoolean(1); }
                    try(var rows=qb.executeQuery()) { if(!rows.next()) throw new IllegalStateException("Referencia B no disponible."); inB=rows.getBoolean(1); }
                    return inA||inB;
                } catch(java.sql.SQLException ex) { throw new IllegalStateException("No se pudo comprobar ambos nodos; limpieza interrumpida."); }
            });
            System.out.println(JsonSupport.JSON.writeValueAsString(result));
        } catch(java.sql.SQLException ex) { throw new IllegalStateException("No están disponibles ambos nodos; no se inicia la limpieza."); }
    }
}
