package mx.bovicierre.evidencia;

import java.io.ByteArrayOutputStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import tools.jackson.databind.JsonNode;

public final class SettlementPdf {
    private static final Charset ENCODING=Charset.forName("windows-1252");
    private SettlementPdf() { }
    // shortcut: fuente WinAnsi para comprobantes en español; incrustar Unicode si se admiten otros alfabetos.
    public static byte[] render(JsonNode liquidation) {
        List<String> lines=new ArrayList<>(List.of("BoviCierre - comprobante interno no fiscal","Liquidación: "+liquidation.path("id").asText(),"Operación: "+liquidation.path("operacion_id").asText(),"Contraparte: "+liquidation.path("snapshot_contraparte_nombre").asText(),"Dirección: "+liquidation.path("direccion").asText(),"Total: "+money(liquidation.path("total")),"Ajustes cargo: "+money(liquidation.path("ajustes_cargo")),"Ajustes abono: "+money(liquidation.path("ajustes_abono")),"Aplicaciones netas: "+money(liquidation.path("aplicaciones_netas")),"Saldo: "+money(liquidation.path("saldo")),"Vencimiento: "+liquidation.path("vence_el").asText(),"","Conceptos:"));
        for (JsonNode concept : liquidation.path("conceptos")) {
            lines.add(concept.path("numero").asText()+". "+concept.path("tipo").asText()+" "+concept.path("cantidad").asText()+" "+concept.path("unidad").asText()+" x "+concept.path("precio_unitario").asText()+" = "+money(concept.path("importe")));
        }
        lines.add(""); lines.add("Documento derivado de hechos confirmados; no genera una operación económica.");
        List<byte[]> objects=new ArrayList<>();
        objects.add(bytes("<< /Type /Catalog /Pages 2 0 R >>"));
        int pages=(lines.size()+39)/40;
        StringBuilder kids=new StringBuilder();
        for (int page=0;page<pages;page++) kids.append(4+page*2).append(" 0 R ");
        objects.add(bytes("<< /Type /Pages /Count "+pages+" /Kids ["+kids+"] >>"));
        objects.add(bytes("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"));
        for (int page=0;page<pages;page++) {
            int contentId=5+page*2;
            objects.add(bytes("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents "+contentId+" 0 R >>"));
            StringBuilder content=new StringBuilder("BT /F1 10 Tf 14 TL 40 752 Td\n");
            for (String line : lines.subList(page*40,Math.min(lines.size(),(page+1)*40))) content.append('(').append(line.replace("\\","\\\\").replace("(","\\(").replace(")","\\)").replaceAll("[\\r\\n\\p{Cntrl}]"," ")).append(") Tj T*\n");
            byte[] stream=bytes(content+"ET\n");
            ByteArrayOutputStream object=new ByteArrayOutputStream();
            object.writeBytes(bytes("<< /Length "+stream.length+" >>\nstream\n"));object.writeBytes(stream);object.writeBytes(bytes("endstream"));objects.add(object.toByteArray());
        }
        ByteArrayOutputStream pdf=new ByteArrayOutputStream();pdf.writeBytes(bytes("%PDF-1.4\n"));
        List<Integer> offsets=new ArrayList<>();
        for (int index=0;index<objects.size();index++) {
            offsets.add(pdf.size());pdf.writeBytes(bytes((index+1)+" 0 obj\n"));pdf.writeBytes(objects.get(index));pdf.writeBytes(bytes("\nendobj\n"));
        }
        int xref=pdf.size();pdf.writeBytes(bytes("xref\n0 "+(objects.size()+1)+"\n0000000000 65535 f \n"));
        for (int offset : offsets) pdf.writeBytes(bytes(String.format(java.util.Locale.ROOT,"%010d 00000 n \n",offset)));
        pdf.writeBytes(bytes("trailer\n<< /Size "+(objects.size()+1)+" /Root 1 0 R >>\nstartxref\n"+xref+"\n%%EOF\n"));
        return pdf.toByteArray();
    }
    private static String money(JsonNode value) { return value.isObject() ? value.path("importe").asText()+" "+value.path("moneda").asText() : value.asText(); }
    private static byte[] bytes(String text) { return text.getBytes(ENCODING); }
}
