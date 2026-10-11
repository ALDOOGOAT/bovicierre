package mx.bovicierre.operaciones;

import java.util.UUID;
import mx.bovicierre.acceso.AccessService;
import mx.bovicierre.shared.*;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.security.core.Authentication;
import tools.jackson.databind.node.ObjectNode;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class PesajeCorrectionTest {
    final AccessService access=mock(AccessService.class);
    final CommandService commands=mock(CommandService.class);
    final CoreController controller=new CoreController(access,commands);
    final Authentication auth=mock(Authentication.class);
    final UUID user=UUID.randomUUID(),site=UUID.randomUUID(),original=UUID.randomUUID();
    final MockHttpServletRequest request=new MockHttpServletRequest("POST","/api/v1/sedes/"+site+"/pesajes/"+original+"/correcciones");

    @Test void correctionPreservesExactOriginalReasonAndMeasuredComposition() {
        when(access.user(auth)).thenReturn(user);
        when(commands.command(eq(user),eq(site),eq("corregir_pesaje"),any(),anyString(),any())).thenReturn("{\"id\":\""+UUID.randomUUID()+"\"}");
        ObjectNode body=JsonSupport.object("{\"numero_lote\":1,\"modo\":\"NETO_REPORTADO\",\"neto\":{\"kg\":\"101.000\"},\"pesado_en\":\"2026-10-11T12:00:00Z\",\"animales\":[{\"animal_id\":\""+UUID.randomUUID()+"\"}],\"motivo\":\"Error de captura del ticket original\"}");
        var response=controller.action(site,original,body.toString(),UUID.randomUUID().toString(),null,auth,request);
        assertEquals(201,response.getStatusCode().value());
        var captured=org.mockito.ArgumentCaptor.forClass(ObjectNode.class);
        verify(commands).command(eq(user),eq(site),eq("corregir_pesaje"),captured.capture(),anyString(),any());
        assertEquals(original.toString(),captured.getValue().path("corrige_a_id").asText());
        assertEquals(body.path("motivo"),captured.getValue().path("motivo"));
        assertEquals(body.path("animales"),captured.getValue().path("animales"));
        assertFalse(captured.getValue().path("animales").get(0).has("peso_individual"));
    }

    @Test void invalidReasonOrContradictoryOriginalNeverReachesSql() {
        for (String body:java.util.List.of("{}","{\"motivo\":null}","{\"motivo\":123}","{\"motivo\":\"   \"}","{\"motivo\":\""+"x".repeat(201)+"\"}","{\"motivo\":\"Corrección\",\"corrige_a_id\":\""+UUID.randomUUID()+"\"}","{\"motivo\":\"Corrección\",\"corrige_a_id\":123}")) {
            assertEquals(400,assertThrows(ApiException.class,() -> controller.action(site,original,body,UUID.randomUUID().toString(),null,auth,request)).status);
        }
        verifyNoInteractions(commands);
    }
}
