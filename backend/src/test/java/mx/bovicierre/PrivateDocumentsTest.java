package mx.bovicierre;

import java.nio.file.Files;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockMultipartFile;
import mx.bovicierre.evidencia.PrivateDocuments;
import mx.bovicierre.shared.ApiException;
import static org.junit.jupiter.api.Assertions.*;

class PrivateDocumentsTest {
    @TempDir java.nio.file.Path directory;
    @Test void privateAddressIsContentHashAndTamperingIsDetected() throws Exception {
        var files=new PrivateDocuments(directory.toString());
        var stored=files.store(new MockMultipartFile("archivo","../../ticket.pdf","text/html","%PDF-1.7\nDEMO".getBytes()));
        assertEquals("application/pdf",stored.mime());
        assertEquals(directory.resolve(stored.sha256()),files.path(stored.sha256()));
        assertFalse(stored.name().contains("/"));
        Files.writeString(directory.resolve(stored.sha256()),"changed");
        assertEquals(409,assertThrows(ApiException.class,() -> files.path(stored.sha256())).status);
    }
    @Test void htmlAndTraversalAreRejected() {
        assertThrows(ApiException.class,() -> PrivateDocuments.type("<script>alert(1)</script>".getBytes()));
        assertThrows(ApiException.class,() -> new PrivateDocuments(directory.toString()).path("../../etc/passwd"));
    }
    @Test void exactTwentyMiBBoundaryIsAcceptedAndLargerFileRejected() {
        byte[] content=new byte[20*1024*1024];
        System.arraycopy("%PDF-".getBytes(),0,content,0,5);
        var files=new PrivateDocuments(directory.toString());
        assertEquals(content.length,files.store(new MockMultipartFile("archivo","limite.pdf","application/pdf",content)).size());
        var larger=java.util.Arrays.copyOf(content,content.length+1);
        assertEquals(422,assertThrows(ApiException.class,() -> files.store(new MockMultipartFile("archivo","excedido.pdf","application/pdf",larger))).status);
    }
    @Test void cleanupOnlyDeletesOldUnreferencedUnlockedContent() throws Exception {
        var files=new PrivateDocuments(directory.toString());
        var upload=files.stage(new MockMultipartFile("archivo","documento.pdf","application/pdf","%PDF-1.7\nretained".getBytes()));
        var hash=upload.stored().sha256();
        var path=directory.resolve(hash);
        Files.setLastModifiedTime(path,java.nio.file.attribute.FileTime.from(java.time.Instant.now().minusSeconds(90000)));
        var executor=java.util.concurrent.Executors.newSingleThreadExecutor();
        try {
            var locked=executor.submit(() -> files.cleanup(true,value -> { fail("No se consulta DB para una carga bloqueada"); return false; })).get();
            assertEquals(java.util.List.of(hash),locked.omitidos());
            assertTrue(Files.exists(path));
        } finally { upload.close(); executor.close(); }
        assertEquals(java.util.List.of(hash),files.cleanup(true,value -> true).omitidos());
        var diagnostic=files.cleanup(false,value -> false);
        assertEquals(java.util.List.of(hash),diagnostic.candidatos());
        assertTrue(Files.exists(path));
        assertEquals(java.util.List.of(hash),files.cleanup(true,value -> false).eliminados());
        assertFalse(Files.exists(path));
    }
    @Test void failedReferenceCheckAndRecentFilesCannotBeDeleted() throws Exception {
        var files=new PrivateDocuments(directory.toString());
        var stored=files.store(new MockMultipartFile("archivo","documento.pdf","application/pdf","%PDF-1.7\nrecent".getBytes()));
        assertTrue(files.cleanup(true,value -> false).candidatos().isEmpty());
        var path=directory.resolve(stored.sha256());
        Files.setLastModifiedTime(path,java.nio.file.attribute.FileTime.from(java.time.Instant.now().minusSeconds(90000)));
        assertThrows(IllegalStateException.class,() -> files.cleanup(true,value -> { throw new IllegalStateException("nodo no disponible"); }));
        assertTrue(Files.exists(path));
    }

}
