package mx.bovicierre.evidencia.application;

import java.nio.file.Path;
import org.springframework.web.multipart.MultipartFile;

/** Port for the private content lifecycle; metadata remains a canonical SQL command. */
public interface DocumentStorage {
    record Stored(String sha256,long size,String mime,String name) { }
    interface Upload extends AutoCloseable {
        Stored stored();
        @Override void close();
    }
    Upload stage(MultipartFile file);
    Path path(String sha256);
}
