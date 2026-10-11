package mx.bovicierre;

import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import mx.bovicierre.evidencia.SettlementPdf;
import mx.bovicierre.shared.JsonSupport;
import static org.junit.jupiter.api.Assertions.*;

class SettlementPdfTest {
    @Test void pdfCrossReferenceUsesActualByteOffsets() {
        var liquidation=JsonSupport.object("{\"id\":\"DEMO\",\"total\":{\"importe\":\"240000.00\",\"moneda\":\"MXN\"},\"conceptos\":[]}");
        byte[] bytes=SettlementPdf.render(liquidation);
        String pdf=new String(bytes,StandardCharsets.ISO_8859_1);
        assertTrue(pdf.startsWith("%PDF-1.4")); assertTrue(pdf.endsWith("%%EOF\n")); assertTrue(pdf.contains("240000.00 MXN"));
        int xref=Integer.parseInt(pdf.substring(pdf.indexOf("startxref\n")+10,pdf.lastIndexOf("\n%%EOF")));
        assertEquals("xref",pdf.substring(xref,xref+4));
        String[] table=pdf.substring(xref).split("\n");
        for (int index=3;index<8;index++) {
            int offset=Integer.parseInt(table[index].substring(0,10));
            assertTrue(pdf.substring(offset).startsWith((index-2)+" 0 obj"));
        }
    }
}
