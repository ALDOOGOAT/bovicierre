-- Canonicaliza Dinero escala2; conserva precisión fuente y paginación explícita.
CREATE OR REPLACE FUNCTION bovi.consultar_tarifas_proveedor(e uuid,s uuid,a uuid,params jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE r record; sid uuid; snap jsonb; result jsonb:='[]'; countn integer:=0; totaln integer; page integer:=coalesce((params->>'pagina')::integer,1); size integer:=coalesce((params->>'tamano')::integer,25);
BEGIN
 PERFORM bovi.fn_scope(e,s,a,'OPERADOR');
 IF page<1 OR size NOT BETWEEN 1 AND 100 THEN RAISE EXCEPTION 'Paginación inválida' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-035','campos','[]'::jsonb)::text; END IF;
 SELECT count(*) INTO totaln FROM ext_proveedor.tarifa_transporte WHERE (params->>'ruta' IS NULL OR ruta=params->>'ruta');
 -- Conexión remota antes de cualquier transacción financiera; ninguna fila económica se bloquea.
 FOR r IN SELECT * FROM ext_proveedor.tarifa_transporte WHERE (params->>'ruta' IS NULL OR ruta=params->>'ruta') ORDER BY ruta LIMIT size OFFSET (page-1)*size LOOP
 snap:=jsonb_build_object('fuente','DEMO_PROVEEDOR_SIMULADO','ruta',r.ruta,'origen',r.origen,'destino',r.destino,'precio',jsonb_build_object('importe',round(r.precio_mxn,2)::numeric(14,2)::text,'moneda','MXN'),'precio_unitario_fuente',r.precio_mxn::text,'politica_redondeo','HALF_UP_2','unidad',r.unidad,'vigente_desde',r.vigente_desde,'version',r.version,'capturado_en',now());
 sid:=uuidv7();
 INSERT INTO infra.tarifa_snapshot(id,empresa_id,sucursal_id,actor_id,ruta,precio,hash_sha256,snapshot) VALUES(sid,e,s,a,r.ruta,r.precio_mxn,encode(public.digest(snap::text,'sha256'),'hex'),snap);
 result:=result||jsonb_build_array(snap||jsonb_build_object('snapshot_id',sid,'hash_sha256',encode(public.digest(snap::text,'sha256'),'hex')));countn:=countn+1;
 END LOOP;
 RETURN jsonb_build_object('elementos',result,'pagina',page,'tamano',size,'total',totaln,'corte',now());
END $$;
