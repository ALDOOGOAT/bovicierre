-- V14 (DIV-04, SF-08). No reescribe V1-V13.
-- DIV-04 / RN-023: estados terminales inmutables en la base, no sólo en cmd_ejecutar.
-- Transiciones permitidas, tomadas de cmd_ejecutar V13: operacion CONFIRMADA→ANULADA (anular_venta) y
-- estado_entrega en CONFIRMADA (entregas); version_lock puede avanzar. Todo lo demás exige reverso/ajuste.
CREATE FUNCTION bovi.trg_estado_terminal() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
DECLARE libres text[]:=ARRAY['estado','estado_entrega','version_lock']; bloqueado boolean:=false;
BEGIN
 IF TG_TABLE_NAME='operacion' AND OLD.estado IN ('CONFIRMADA','ANULADA','CANCELADA') THEN
  bloqueado:=TG_OP='DELETE' OR (to_jsonb(OLD)-libres)<>(to_jsonb(NEW)-libres)
   OR NOT ((OLD.estado=NEW.estado AND (OLD.estado='CONFIRMADA' OR OLD.estado_entrega=NEW.estado_entrega))
        OR (OLD.estado='CONFIRMADA' AND NEW.estado='ANULADA' AND OLD.estado_entrega=NEW.estado_entrega));
 ELSIF TG_TABLE_NAME='gasto_operacion' THEN bloqueado:=OLD.estado='APROBADO';
 ELSIF TG_TABLE_NAME='pago' THEN bloqueado:=OLD.estado IN ('VALIDADO','REVERTIDO');
 ELSIF TG_TABLE_NAME='posicion_inventario' THEN bloqueado:=OLD.estado IN ('CERRADA_VENTA','BAJA');
 END IF;
 IF bloqueado THEN RAISE EXCEPTION 'Hecho en estado terminal inmutable; requiere reverso o ajuste' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Hecho en estado terminal inmutable; requiere reverso o ajuste','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
ALTER FUNCTION bovi.trg_estado_terminal() OWNER TO bovi_owner;
REVOKE ALL ON FUNCTION bovi.trg_estado_terminal() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bovi.trg_estado_terminal() TO bovi_command;
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['operacion','gasto_operacion','pago','posicion_inventario'] LOOP
  EXECUTE format('CREATE TRIGGER estado_terminal_inmutable BEFORE UPDATE OR DELETE ON bovi.%I FOR EACH ROW EXECUTE FUNCTION bovi.trg_estado_terminal()',t);
 END LOOP;
END $$;

-- SF-08: pg_temp explícito y al final, para que una tabla temporal del llamador no sombree catálogos
-- no calificados; y sin TEMP para PUBLIC (ningún rol de ejecución crea tablas temporales).
DO $$ DECLARE f regprocedure; BEGIN
 FOR f IN SELECT p.oid::regprocedure FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
          WHERE n.nspname IN ('bovi','infra') AND p.proconfig @> ARRAY['search_path=pg_catalog'] LOOP
  EXECUTE format('ALTER FUNCTION %s SET search_path = pg_catalog, pg_temp',f);
 END LOOP;
 EXECUTE format('REVOKE TEMPORARY ON DATABASE %I FROM PUBLIC',current_database());
END $$;
