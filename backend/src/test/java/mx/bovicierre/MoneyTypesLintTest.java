package mx.bovicierre;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/** RN-034 / DIV-12b: los importes viajan como cadena decimal exacta y se calculan en NUMERIC; nadie usa coma flotante. */
class MoneyTypesLintTest {
    static List<String> offenders(Path root, String glob, Pattern forbidden) throws Exception {
        var matcher = root.getFileSystem().getPathMatcher("glob:" + glob);
        try (var files = Files.walk(root)) {
            var sources = files.filter(Files::isRegularFile).filter(p -> matcher.matches(p.getFileName()))
                .filter(p -> !p.toString().contains("generated")).toList();
            assertTrue(sources.size() > 5, "Sin fuentes que revisar en " + root.toAbsolutePath());
            return sources.stream().flatMap(p -> {
                    try { return Files.readAllLines(p).stream().filter(l -> forbidden.matcher(l).find()).map(l -> p + ": " + l.strip()); }
                    catch (java.io.IOException e) { throw new java.io.UncheckedIOException(e); }
                }).toList();
        }
    }
    @Test void backendNeverUsesFloatingPoint() throws Exception {
        assertEquals(List.of(), offenders(Path.of("src/main/java"), "*.java", Pattern.compile("\\b(double|float|Double|Float)\\b")));
    }
    @Test void frontendNeverParsesMoneyAsFloat() throws Exception {
        assertEquals(List.of(), offenders(Path.of("../frontend/src"), "*.{ts,tsx}", Pattern.compile("\\b(parseFloat|toFixed)\\b|Number\\.parseFloat")));
    }
}
