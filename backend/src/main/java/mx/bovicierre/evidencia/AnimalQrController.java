package mx.bovicierre.evidencia;

import java.util.UUID;
import com.google.zxing.BarcodeFormat;
import com.google.zxing.qrcode.QRCodeWriter;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.CommandService;
import mx.bovicierre.shared.JsonSupport;

@RestController
public class AnimalQrController {
    private final AccessService access;
    private final CommandService commands;
    public AnimalQrController(AccessService access,CommandService commands) { this.access=access; this.commands=commands; }
    @GetMapping(value="/api/v1/sedes/{sedeId}/animales/{id}/qr",produces="image/svg+xml")
    ResponseEntity<String> qr(@PathVariable UUID sedeId,@PathVariable UUID id,Authentication auth) throws com.google.zxing.WriterException {
        commands.query(access.user(auth),sedeId,"animal",JsonSupport.JSON.createObjectNode().put("id",id.toString()));
        String url="/?sede="+sedeId+"#animales/"+id;
        return ResponseEntity.ok().contentType(MediaType.parseMediaType("image/svg+xml")).cacheControl(org.springframework.http.CacheControl.noStore()).body(svg(url));
    }
    public static String svg(String url) throws com.google.zxing.WriterException {
        var matrix=new QRCodeWriter().encode(url,BarcodeFormat.QR_CODE,0,0);
        StringBuilder path=new StringBuilder();
        for (int y=0;y<matrix.getHeight();y++) for (int x=0;x<matrix.getWidth();x++) if (matrix.get(x,y)) path.append('M').append(x).append(' ').append(y).append("h1v1h-1z");
        return "<svg xmlns=\"http://www.w3.org/2000/svg\" role=\"img\" aria-label=\"QR interno de la ficha animal\" viewBox=\"0 0 "+matrix.getWidth()+" "+matrix.getHeight()+"\"><rect width=\"100%\" height=\"100%\" fill=\"white\"/><path fill=\"black\" d=\""+path+"\"/></svg>";
    }
}
