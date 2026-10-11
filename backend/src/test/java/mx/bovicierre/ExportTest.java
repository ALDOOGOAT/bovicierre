package mx.bovicierre;

import org.junit.jupiter.api.Test;
import mx.bovicierre.evidencia.AnimalQrController;
import mx.bovicierre.reportes.CsvController;
import static org.junit.jupiter.api.Assertions.*;

class ExportTest {
    @Test void csvPreventsFormulasAndEscapesQuotes() {
        assertEquals("\"' =HYPERLINK(\"\"http://example.test\"\")\"",CsvController.cell(" =HYPERLINK(\"http://example.test\")"));
        assertEquals("\"DEMO\"",CsvController.cell("DEMO"));
        assertEquals("\"'@SUM(1)\"",CsvController.cell("@SUM(1)"));
    }
    @Test void qrEncodesInternalRouteWithoutAnExternalGenerator() throws Exception {
        String svg=AnimalQrController.svg("/?sede=aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa#animales/11111111-1111-4111-8111-111111111111");
        assertTrue(svg.startsWith("<svg"));assertTrue(svg.contains("<path"));assertFalse(svg.contains("<script"));
    }
}
