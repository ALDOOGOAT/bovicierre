package mx.bovicierre.acceso;

import java.io.IOException;
import javax.sql.DataSource;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import mx.bovicierre.shared.ApiErrors;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class AvailabilityFilter extends OncePerRequestFilter {
    private final JdbcTemplate auth;
    public AvailabilityFilter(@Qualifier("authDataSource") DataSource ds) { auth=new JdbcTemplate(ds); }
    @Override protected boolean shouldNotFilter(HttpServletRequest request) { return !request.getRequestURI().startsWith("/api/") || request.getRequestURI().equals("/api/v1/salud"); }
    @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain) throws ServletException,IOException {
        try {
            auth.queryForObject("select 1",Integer.class);
            chain.doFilter(request,response);
        } catch (org.springframework.dao.DataAccessException ex) { ApiErrors.write(response,ApiErrors.database((Throwable) ex),ApiErrors.correlation(request)); }
    }
}
