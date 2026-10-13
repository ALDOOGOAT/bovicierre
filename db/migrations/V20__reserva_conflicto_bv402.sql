-- V20 (GOLD-ACAD-03 / RN-018): dos reservas simultáneas de la misma posición. cmd_ejecutar serializa con
-- FOR UPDATE, pero la reserva es estado derivado (la posición sigue DISPONIBLE) y el perdedor chocaba con
-- uk_reserva_venta_activo (23505 → 409 genérico). Ahora recibe el conflicto de negocio BV402; la UNIQUE queda de respaldo.
CREATE FUNCTION bovi.trg_reserva_activa_unica() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
BEGIN
 IF NEW.estado='ACTIVA' AND EXISTS(SELECT 1 FROM bovi.reserva_venta r WHERE (r.empresa_id,r.sucursal_id,r.posicion_id)=(NEW.empresa_id,NEW.sucursal_id,NEW.posicion_id) AND r.estado='ACTIVA') THEN
  RAISE EXCEPTION 'Posición ya reservada por otra venta' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Posición ya reservada por otra venta','codigo','BV402','regla_id','RN-018','campos',jsonb_build_array(jsonb_build_object('campo','posiciones','problema','reservada')))::text;
 END IF;
 RETURN NEW;
END $$;
ALTER FUNCTION bovi.trg_reserva_activa_unica() OWNER TO bovi_owner;
REVOKE ALL ON FUNCTION bovi.trg_reserva_activa_unica() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bovi.trg_reserva_activa_unica() TO bovi_command;
CREATE TRIGGER reserva_activa_unica BEFORE INSERT ON bovi.reserva_venta FOR EACH ROW EXECUTE FUNCTION bovi.trg_reserva_activa_unica();
