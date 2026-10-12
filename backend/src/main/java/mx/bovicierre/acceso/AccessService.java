package mx.bovicierre.acceso;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import mx.bovicierre.shared.ApiException;

@Service
public class AccessService {
    private final JdbcTemplate auth;
    public AccessService(@Qualifier("authDataSource") DataSource source) { auth = new JdbcTemplate(source); }
    public Map<String, Object> login(String login) {
        var rows = auth.queryForList("select id, empresa_id, nombre, hash_contrasena, estado from bovi.usuario where empresa_id=(select empresa_id from infra.nodo_config) and login_normalizado = ?", login.trim().toLowerCase(java.util.Locale.ROOT));
        return rows.size() == 1 ? rows.getFirst() : null;
    }
    public UUID user(Authentication authentication) {
        if (authentication == null || !authentication.isAuthenticated() || authentication instanceof org.springframework.security.authentication.AnonymousAuthenticationToken)
            throw new ApiException(401,"AUTH401","Se requiere una sesión activa.");
        return UUID.fromString(authentication.getName());
    }
    public Map<String, Object> current(UUID user) {
        var rows = auth.queryForList("select id, nombre from bovi.usuario where empresa_id=(select empresa_id from infra.nodo_config) and id = ? and estado = 'ACTIVO'",user);
        if (rows.size() != 1) throw new ApiException(401,"AUTH401","La sesión ya no está autorizada.");
        return rows.getFirst();
    }
    public List<Map<String,Object>> sites(UUID user) {
        return auth.queryForList("select s.id,s.empresa_id,s.codigo,s.nombre,s.nodo_dueno, m.rol_codigo from bovi.membresia_usuario m join bovi.sucursal s on s.empresa_id=m.empresa_id and s.id=m.sucursal_id where m.empresa_id=(select empresa_id from infra.nodo_config) and m.usuario_id=? and m.vigente=true order by s.codigo,m.rol_codigo",user);
    }
    /** Usuario con alguna membresía (vigente o no) en la sede: un ADMIN sólo administra usuarios de su sede. */
    public boolean member(UUID user, UUID site) {
        Integer n = auth.queryForObject("select count(*) from bovi.membresia_usuario where empresa_id=(select empresa_id from infra.nodo_config) and usuario_id=? and sucursal_id=?", Integer.class, user, site);
        return n != null && n > 0;
    }
    public Scope authorize(UUID user, UUID site, boolean mutation) {
        current(user);
        List<Map<String,Object>> rows = sites(user).stream().filter(row -> site.equals(row.get("id"))).toList();
        if (rows.isEmpty()) throw new ApiException(403,"AUTH403","No tiene permiso para esta sede.");
        List<String> roles = rows.stream().map(row -> row.get("rol_codigo").toString()).distinct().toList();
        if (mutation && roles.stream().noneMatch(role -> List.of("ADMIN","OPERADOR","CAJA").contains(role)))
            throw new ApiException(403,"AUTH403","No tiene permiso para esta acción.");
        Map<String,Object> first=rows.getFirst();
        return new Scope((UUID) first.get("empresa_id"),site,first.get("nodo_dueno").toString(),roles);
    }
    public record Scope(UUID company, UUID site, String owner, List<String> roles) { }
}
