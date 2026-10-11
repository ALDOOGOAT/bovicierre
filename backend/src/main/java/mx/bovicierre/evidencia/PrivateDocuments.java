package mx.bovicierre.evidencia;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.file.StandardOpenOption;
import java.nio.file.LinkOption;
import java.time.Instant;
import java.time.Duration;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Predicate;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import mx.bovicierre.shared.ApiException;

@Service
public class PrivateDocuments implements mx.bovicierre.evidencia.application.DocumentStorage {
    private final Path root;
    private static final ConcurrentHashMap<String,ReentrantLock> LOCKS=new ConcurrentHashMap<>();
    public PrivateDocuments(@Value("${bovi.documents}") String root) { this.root=Path.of(root).toAbsolutePath().normalize(); }
    public Stored store(MultipartFile file) { try (var upload=stage(file)) { return upload.stored(); } }
    public final class Upload implements mx.bovicierre.evidencia.application.DocumentStorage.Upload {
        private final Stored stored;
        private final HeldLock lock;
        private Upload(Stored stored,HeldLock lock) { this.stored=stored; this.lock=lock; }
        public Stored stored() { return stored; }
        @Override public void close() { lock.close(); }
    }
    private record HeldLock(ReentrantLock local,FileChannel channel,FileLock file) implements AutoCloseable {
        public void close() {
            try { try { file.release(); } finally { channel.close(); } }
            catch(IOException ex) { org.slf4j.LoggerFactory.getLogger(PrivateDocuments.class).warn("No se pudo liberar el bloqueo de almacenamiento."); }
            finally { local.unlock(); }
        }
    }
    private void directories() throws IOException {
        Files.createDirectories(root);
        Files.setPosixFilePermissions(root,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
        Files.createDirectories(root.resolve(".locks"));
        Files.setPosixFilePermissions(root.resolve(".locks"),java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    }
    private HeldLock lock(String hash,boolean wait) throws IOException {
        var local=LOCKS.computeIfAbsent(root+"/"+hash,key -> new ReentrantLock());
        if (wait) local.lock(); else if (!local.tryLock()) return null;
        FileChannel channel=null;
        try {
            channel=FileChannel.open(root.resolve(".locks").resolve(hash+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);
            Files.setPosixFilePermissions(root.resolve(".locks").resolve(hash+".lock"),java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
            FileLock file=wait ? channel.lock() : channel.tryLock();
            if(file==null) { channel.close(); local.unlock(); return null; }
            return new HeldLock(local,channel,file);
        } catch(IOException|RuntimeException ex) { if(channel!=null) channel.close(); local.unlock(); throw ex; }
    }
    public Upload stage(MultipartFile file) {
        if (file.isEmpty() || file.getSize() > 20L*1024*1024) throw new ApiException(422,"BV023","El archivo debe contener entre 1 byte y 20 MiB.");
        try {
            byte[] bytes=file.getBytes();
            String mime=type(bytes);
            String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
            directories();
            var held=lock(hash,true);
            Path temporary=null;
            try {
                temporary=root.resolve(hash+"-"+java.util.UUID.randomUUID()+".part");
                Files.createFile(temporary);
                Files.write(temporary,bytes);
                Files.setPosixFilePermissions(temporary,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
                Files.move(temporary,root.resolve(hash),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
                String name=file.getOriginalFilename() == null ? "documento" : file.getOriginalFilename().replaceAll("[^\\p{L}\\p{N}._ -]","_");
                if (name.length()>160) name=name.substring(0,160);
                return new Upload(new Stored(hash,bytes.length,mime,name),held);
            } catch(IOException|RuntimeException ex) { held.close(); throw ex; }
            finally { if(temporary!=null) Files.deleteIfExists(temporary); }
        } catch (IOException ex) { throw new ApiException(503,"BV503","El almacenamiento privado no está disponible."); }
        catch (java.security.NoSuchAlgorithmException ex) { throw new IllegalStateException(ex); }
    }
    public record Cleanup(String modo,List<String> candidatos,List<String> eliminados,List<String> omitidos) { }
    /** Both node checks must succeed. Locks span upload publication through metadata commit. */
    public Cleanup cleanup(boolean execute,Predicate<String> referenced) {
        var candidates=new ArrayList<String>(); var removed=new ArrayList<String>(); var skipped=new ArrayList<String>();
        try {
            directories();
            try(var paths=Files.list(root)) {
                for(var path:paths.toList()) {
                    String name=path.getFileName().toString();
                    if(!name.matches("[0-9a-f]{64}(?:-[A-Za-z0-9-]+\\.part)?") || !Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)) continue;
                    if(!Files.getLastModifiedTime(path,LinkOption.NOFOLLOW_LINKS).toInstant().isBefore(Instant.now().minus(Duration.ofHours(24)))) continue;
                    String hash=name.substring(0,64);
                    try(var held=lock(hash,false)) {
                        if(held==null) { skipped.add(name); continue; }
                        if(!Files.exists(path,LinkOption.NOFOLLOW_LINKS) || !Files.getLastModifiedTime(path,LinkOption.NOFOLLOW_LINKS).toInstant().isBefore(Instant.now().minus(Duration.ofHours(24))) || referenced.test(hash)) { skipped.add(name); continue; }
                        candidates.add(name);
                        if(execute) { Files.delete(path); removed.add(name); }
                    }
                }
            }
            return new Cleanup(execute?"EJECUTAR":"DIAGNOSTICO",List.copyOf(candidates),List.copyOf(removed),List.copyOf(skipped));
        } catch(IOException ex) { throw new ApiException(503,"BV503","No se pudo revisar el almacenamiento privado."); }
    }
    public static String type(byte[] bytes) {
        if (bytes.length>=5 && bytes[0]=='%' && bytes[1]=='P' && bytes[2]=='D' && bytes[3]=='F' && bytes[4]=='-') return "application/pdf";
        if (bytes.length>=8 && Arrays.equals(Arrays.copyOf(bytes,8),new byte[]{(byte)137,80,78,71,13,10,26,10})) return "image/png";
        if (bytes.length>=3 && bytes[0]==(byte)255 && bytes[1]==(byte)216 && bytes[2]==(byte)255) return "image/jpeg";
        throw new ApiException(422,"BV023","Sólo se admiten archivos PDF, PNG y JPEG identificados por su contenido.");
    }
    public Path path(String sha256) {
        if (sha256 == null || !sha256.matches("[0-9a-f]{64}")) throw new ApiException(404,"BV404","Documento no disponible.");
        Path file=root.resolve(sha256);
        if (!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)) throw new ApiException(404,"BV404","Documento no disponible.");
        try {
            byte[] bytes=Files.readAllBytes(file);
            if (!sha256.equals(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)))) throw new ApiException(409,"BV023","La integridad del documento no coincide.");
        } catch (IOException ex) { throw new ApiException(503,"BV503","El almacenamiento privado no está disponible."); }
        catch (java.security.NoSuchAlgorithmException ex) { throw new IllegalStateException(ex); }
        return file;
    }
}
