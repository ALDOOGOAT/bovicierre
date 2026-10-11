package mx.bovicierre;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
public class BoviCierreApplication {
    public static void main(String[] args) {
        var application=new SpringApplication(BoviCierreApplication.class);
        String directory=System.getenv().getOrDefault("BOVI_RUNTIME_DIR",System.getProperty("user.home")+"/.local/share/bovicierre-academic/run");
        application.addListeners(new org.springframework.boot.context.ApplicationPidFileWriter(directory+"/api.pid"));
        application.run(args);
    }
}
