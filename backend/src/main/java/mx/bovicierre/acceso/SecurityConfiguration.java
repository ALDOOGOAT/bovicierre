package mx.bovicierre.acceso;

import java.io.IOException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AnonymousAuthenticationFilter;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.csrf.HttpSessionCsrfTokenRepository;
import org.springframework.security.web.csrf.CsrfTokenRequestAttributeHandler;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.filter.OncePerRequestFilter;
import mx.bovicierre.shared.ApiErrors;
import mx.bovicierre.shared.ApiException;

@Configuration
public class SecurityConfiguration {
    @Bean org.springframework.security.core.userdetails.UserDetailsService noGeneratedUsers() { return name -> { throw new org.springframework.security.core.userdetails.UsernameNotFoundException("Credenciales no disponibles."); }; }
    @Bean BCryptPasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(12); }
    @Bean HttpSessionSecurityContextRepository securityContextRepository() { return new HttpSessionSecurityContextRepository(); }
    @Bean HttpSessionCsrfTokenRepository csrfRepository() { var repository=new HttpSessionCsrfTokenRepository(); repository.setHeaderName("X-XSRF-TOKEN"); return repository; }
    @Bean SecurityFilterChain security(HttpSecurity http, AccessService access, HttpSessionSecurityContextRepository context, HttpSessionCsrfTokenRepository csrf) {
        http.authorizeHttpRequests(r -> r.requestMatchers("/api/v1/sesion/csrf", "/api/v1/sesion/login", "/api/v1/salud").permitAll().anyRequest().authenticated())
            .csrf(c -> c.csrfTokenRepository(csrf).csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()))
            .securityContext(c -> c.securityContextRepository(context))
            .requestCache(c -> c.disable())
            .formLogin(c -> c.disable()).httpBasic(c -> c.disable()).logout(c -> c.disable())
            .exceptionHandling(c -> c.authenticationEntryPoint((req,res,ex) -> ApiErrors.write(res,new ApiException(401,"AUTH401","Se requiere una sesión activa."),ApiErrors.correlation(req)))
                .accessDeniedHandler((req,res,ex) -> ApiErrors.write(res,new ApiException(403,"AUTH403","No tiene permiso o el token CSRF no es válido."),ApiErrors.correlation(req))))
            .addFilterAfter(new OncePerRequestFilter() {
                @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain) throws ServletException,IOException {
                    var authentication=org.springframework.security.core.context.SecurityContextHolder.getContext().getAuthentication();
                    try {
                        if (authentication != null && !(authentication instanceof org.springframework.security.authentication.AnonymousAuthenticationToken)) access.current(access.user(authentication));
                        response.setHeader("X-Correlation-ID",ApiErrors.correlation(request).toString());
                        chain.doFilter(request,response);
                    } catch (ApiException ex) { ApiErrors.write(response,ex,ApiErrors.correlation(request)); }
                    catch (org.springframework.dao.DataAccessException ex) { ApiErrors.write(response,ApiErrors.database((Throwable) ex),ApiErrors.correlation(request)); }
                }
            },AnonymousAuthenticationFilter.class);
        return http.build();
    }
}
