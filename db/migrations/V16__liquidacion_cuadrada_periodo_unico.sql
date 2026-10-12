-- V16 (DIV-05). No reescribe V1-V15.
-- (a) liquidacion.total = Σ concepto_liquidacion.importe, comprobado al confirmar la transacción (DEFERRABLE
--     INITIALLY DEFERRED: cmd_ejecutar inserta la liquidación antes que sus conceptos). Misma expresión que
--     fn_validar_conciliacion_propietario (V3), que pasa de detectar a impedir. UPDATE/DELETE ya los bloquea V2.
CREATE FUNCTION bovi.trg_liquidacion_cuadrada() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
DECLARE lid uuid:=CASE WHEN TG_TABLE_NAME='liquidacion' THEN NEW.id ELSE NEW.liquidacion_id END;
BEGIN
 IF EXISTS(SELECT 1 FROM bovi.liquidacion l WHERE (l.empresa_id,l.sucursal_id,l.id)=(NEW.empresa_id,NEW.sucursal_id,lid)
           AND l.total IS DISTINCT FROM (SELECT sum(c.importe) FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id))) THEN
  RAISE EXCEPTION 'Liquidación descuadrada respecto a sus conceptos' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Liquidación descuadrada respecto a sus conceptos','codigo','BV015','regla_id','RN-023','campos',jsonb_build_array(jsonb_build_object('campo','total','problema','descuadrado')))::text;
 END IF;
 RETURN NULL;
END $$;
ALTER FUNCTION bovi.trg_liquidacion_cuadrada() OWNER TO bovi_owner;
REVOKE ALL ON FUNCTION bovi.trg_liquidacion_cuadrada() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bovi.trg_liquidacion_cuadrada() TO bovi_command;
CREATE CONSTRAINT TRIGGER liquidacion_cuadrada AFTER INSERT ON bovi.liquidacion DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION bovi.trg_liquidacion_cuadrada();
CREATE CONSTRAINT TRIGGER liquidacion_cuadrada AFTER INSERT ON bovi.concepto_liquidacion DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION bovi.trg_liquidacion_cuadrada();

-- (b) ADR-015 / RN-039: un solo periodo ABIERTO por sede, también fuera de cmd_ejecutar (advisory lock en V13).
CREATE UNIQUE INDEX uk_periodo_un_abierto ON bovi.periodo_cierre (empresa_id, sucursal_id) WHERE estado = 'ABIERTO';
