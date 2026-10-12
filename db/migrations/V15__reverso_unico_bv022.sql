-- V15 (DIV-08 / RN-033): un segundo reverso de la misma aplicación responde BV022 ("original no revertido")
-- en lugar de chocar con uk_aplicacion_pago_reverso_de_id (409 BV401). cmd_ejecutar bloquea el pago FOR UPDATE
-- antes de insertar, así que el segundo intento ve el reverso ya confirmado; la UNIQUE queda como respaldo.
CREATE FUNCTION bovi.trg_reverso_unico() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM bovi.aplicacion_pago WHERE (empresa_id,sucursal_id,reverso_de_id)=(NEW.empresa_id,NEW.sucursal_id,NEW.reverso_de_id)) THEN
  RAISE EXCEPTION 'La aplicación ya fue revertida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','La aplicación ya fue revertida','codigo','BV022','regla_id','RN-033','campos',jsonb_build_array(jsonb_build_object('campo','aplicacion_id','problema','ya_revertida')))::text;
 END IF;
 RETURN NEW;
END $$;
ALTER FUNCTION bovi.trg_reverso_unico() OWNER TO bovi_owner;
REVOKE ALL ON FUNCTION bovi.trg_reverso_unico() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bovi.trg_reverso_unico() TO bovi_command;
CREATE TRIGGER reverso_unico BEFORE INSERT ON bovi.aplicacion_pago FOR EACH ROW WHEN (NEW.reverso_de_id IS NOT NULL) EXECUTE FUNCTION bovi.trg_reverso_unico();
