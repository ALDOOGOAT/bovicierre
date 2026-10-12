-- V17: corrige V16. PL/pgSQL resuelve NEW.id aunque la rama del CASE no se ejecute, y concepto_liquidacion no
-- tiene columna id, así que cualquier concepto nuevo fallaba al confirmar. Se lee la columna vía jsonb.
CREATE OR REPLACE FUNCTION bovi.trg_liquidacion_cuadrada() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
DECLARE lid uuid:=(to_jsonb(NEW)->>CASE WHEN TG_TABLE_NAME='liquidacion' THEN 'id' ELSE 'liquidacion_id' END)::uuid;
BEGIN
 IF EXISTS(SELECT 1 FROM bovi.liquidacion l WHERE (l.empresa_id,l.sucursal_id,l.id)=(NEW.empresa_id,NEW.sucursal_id,lid)
           AND l.total IS DISTINCT FROM (SELECT sum(c.importe) FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id))) THEN
  RAISE EXCEPTION 'Liquidación descuadrada respecto a sus conceptos' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Liquidación descuadrada respecto a sus conceptos','codigo','BV015','regla_id','RN-023','campos',jsonb_build_array(jsonb_build_object('campo','total','problema','descuadrado')))::text;
 END IF;
 RETURN NULL;
END $$;
