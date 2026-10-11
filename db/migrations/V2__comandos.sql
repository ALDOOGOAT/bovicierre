SET ROLE bovi_owner;
CREATE FUNCTION bovi.fn_nodo() RETURNS text LANGUAGE sql STABLE SET search_path = pg_catalog AS $$ SELECT nodo::text FROM infra.nodo_config $$;
CREATE FUNCTION bovi.fn_scope(e uuid,s uuid,a uuid,rol text DEFAULT NULL,maestro boolean DEFAULT false) RETURNS void LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM infra.nodo_config WHERE empresa_id=e) OR NOT EXISTS(SELECT 1 FROM bovi.membresia_usuario m JOIN bovi.usuario u ON u.empresa_id=m.empresa_id AND u.id=m.usuario_id WHERE m.empresa_id=e AND m.sucursal_id=s AND m.usuario_id=a AND m.vigente AND u.estado='ACTIVO' AND (rol IS NULL OR m.rol_codigo IN ('ADMIN',rol))) THEN RAISE EXCEPTION 'Permiso denegado' USING ERRCODE='42501'; END IF;
 IF maestro THEN IF bovi.fn_nodo()<>'A' THEN RAISE EXCEPTION 'Maestros sólo en A' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Maestros sólo en A','codigo','BV501','regla_id','RN-041','campos','[]'::jsonb)::text; END IF;
 ELSIF NOT EXISTS(SELECT 1 FROM bovi.sucursal WHERE empresa_id=e AND id=s AND nodo_dueno=bovi.fn_nodo()) THEN RAISE EXCEPTION 'Escritor de sede no disponible' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Escritor de sede no disponible','codigo','BV501','regla_id','RN-041','campos','[]'::jsonb)::text; END IF;
END $$;
CREATE FUNCTION bovi.trg_propietario() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE j jsonb:=to_jsonb(NEW); oldj jsonb:=to_jsonb(OLD); n text:=bovi.fn_nodo();
BEGIN
 IF TG_TABLE_NAME IN ('empresa','sucursal','rol_aplicacion','usuario','membresia_usuario','parte','predio','animal','animal_identificacion') THEN
   IF n<>'A' THEN RAISE EXCEPTION 'Maestro requiere A' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Maestro requiere A','codigo','BV501','regla_id','RN-041','campos','[]'::jsonb)::text; END IF;
 ELSIF TG_TABLE_NAME NOT IN ('auditoria_evento','evento_outbox') AND j ? 'sucursal_id' AND NOT EXISTS(SELECT 1 FROM bovi.sucursal WHERE empresa_id=(j->>'empresa_id')::uuid AND id=(j->>'sucursal_id')::uuid AND nodo_dueno=n) THEN RAISE EXCEPTION 'Sede de otro nodo' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Sede de otro nodo','codigo','BV501','regla_id','RN-041','campos','[]'::jsonb)::text; END IF;
 IF j ? 'nodo_origen' AND j->>'nodo_origen'<>n THEN RAISE EXCEPTION 'Origen de otro nodo' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Origen de otro nodo','codigo','BV501','regla_id','RN-041','campos','[]'::jsonb)::text; END IF;
 IF j ? 'empresa_id' AND NOT EXISTS(SELECT 1 FROM infra.nodo_config WHERE empresa_id=(j->>'empresa_id')::uuid) THEN RAISE EXCEPTION 'Empresa fuera del despliegue' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' AND ((TG_TABLE_NAME='animal' AND j->'sede_operadora_id' IS DISTINCT FROM oldj->'sede_operadora_id') OR (TG_TABLE_NAME='sucursal' AND j->'nodo_dueno' IS DISTINCT FROM oldj->'nodo_dueno') OR (TG_TABLE_NAME='operacion' AND j->'tipo' IS DISTINCT FROM oldj->'tipo')) THEN RAISE EXCEPTION 'Columna inmutable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Columna inmutable','codigo','BV010','regla_id','RN-004','campos','[]'::jsonb)::text; END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION bovi.trg_inmutable() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN RAISE EXCEPTION 'Hecho inmutable; requiere contramovimiento' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Hecho inmutable; requiere contramovimiento','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END $$;
CREATE FUNCTION bovi.trg_borrador() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE j jsonb:=CASE WHEN TG_OP='DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
BEGIN
 IF TG_TABLE_NAME='condicion_lote' AND EXISTS(SELECT 1 FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=((j->>'empresa_id')::uuid,(j->>'sucursal_id')::uuid,(j->>'operacion_id')::uuid,(j->>'numero_version')::smallint) AND estado='ACEPTADA') THEN RAISE EXCEPTION 'Condición aceptada inmutable' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 IF EXISTS(SELECT 1 FROM bovi.operacion WHERE empresa_id=(j->>'empresa_id')::uuid AND sucursal_id=(j->>'sucursal_id')::uuid AND id=(j->>'operacion_id')::uuid AND estado NOT IN ('BORRADOR','ACORDADA')) THEN RAISE EXCEPTION 'Composición confirmada inmutable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Composición confirmada inmutable','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
CREATE FUNCTION bovi.trg_aprobado() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
 IF TG_TABLE_NAME='contrato_version' AND OLD.estado='ACEPTADA' THEN RAISE EXCEPTION 'Contrato aceptado inmutable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Contrato aceptado inmutable','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 IF TG_TABLE_NAME='pesaje' AND OLD.estado IN ('APROBADO','CORREGIDO') AND NOT(TG_OP='UPDATE' AND OLD.estado='APROBADO' AND NEW.estado='CORREGIDO' AND (to_jsonb(OLD)-'estado')=(to_jsonb(NEW)-'estado')) THEN RAISE EXCEPTION 'Pesaje aprobado inmutable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pesaje aprobado inmutable','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
CREATE FUNCTION bovi.trg_pesaje_composicion() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE j jsonb:=CASE WHEN TG_OP='DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
BEGIN
 IF EXISTS(SELECT 1 FROM bovi.pesaje WHERE empresa_id=(j->>'empresa_id')::uuid AND sucursal_id=(j->>'sucursal_id')::uuid AND id=(j->>'pesaje_id')::uuid AND estado<>'PROPUESTA') THEN RAISE EXCEPTION 'Composición pesaje inmutable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Composición pesaje inmutable','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
DO $$ DECLARE t record; BEGIN
 FOR t IN SELECT tablename FROM pg_tables WHERE schemaname='bovi' AND tablename NOT IN ('clave_idempotencia','mensaje_inbox') LOOP
 EXECUTE format('CREATE TRIGGER guarda_propietario BEFORE INSERT OR UPDATE ON bovi.%I FOR EACH ROW EXECUTE FUNCTION bovi.trg_propietario()',t.tablename);
 END LOOP;
 FOR t IN SELECT unnest(ARRAY['liquidacion','concepto_liquidacion','ajuste_liquidacion','asignacion_costo','asiento_valoracion','aplicacion_pago','cierre_periodo_version','movimiento_inventario','documento','auditoria_evento','evento_outbox','revision_administrativa','revision_documento']) AS n LOOP
 EXECUTE format('CREATE TRIGGER hecho_inmutable BEFORE UPDATE OR DELETE ON bovi.%I FOR EACH ROW EXECUTE FUNCTION bovi.trg_inmutable()',t.n);
 END LOOP;
 FOR t IN SELECT unnest(ARRAY['lote_operacion','seleccion_compra','seleccion_venta','condicion_lote']) AS n LOOP
 EXECUTE format('CREATE TRIGGER solo_borrador BEFORE INSERT OR UPDATE OR DELETE ON bovi.%I FOR EACH ROW EXECUTE FUNCTION bovi.trg_borrador()',t.n);
 END LOOP;
END $$;
CREATE TRIGGER aprobado_inmutable BEFORE UPDATE OR DELETE ON bovi.contrato_version FOR EACH ROW EXECUTE FUNCTION bovi.trg_aprobado();
CREATE TRIGGER aprobado_inmutable BEFORE UPDATE OR DELETE ON bovi.pesaje FOR EACH ROW EXECUTE FUNCTION bovi.trg_aprobado();
CREATE TRIGGER composicion_inmutable BEFORE INSERT OR UPDATE OR DELETE ON bovi.pesaje_animal FOR EACH ROW EXECUTE FUNCTION bovi.trg_pesaje_composicion();
CREATE FUNCTION bovi.fn_periodo(e uuid,s uuid,f date,pid uuid) RETURNS uuid LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE r bovi.periodo_cierre%ROWTYPE;
BEGIN
 IF f IS NULL OR pid IS NULL THEN RAISE EXCEPTION 'Periodo y fecha de reconocimiento requeridos' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV025','regla_id','RN-039','campos',jsonb_build_array(jsonb_build_object('campo','periodo_id','problema','invalido'),jsonb_build_object('campo','fecha_reconocimiento','problema','invalido')))::text; END IF;
 SELECT * INTO r FROM bovi.periodo_cierre WHERE (empresa_id,sucursal_id,id)=(e,s,pid) FOR UPDATE;
 IF NOT FOUND OR r.estado<>'ABIERTO' OR f NOT BETWEEN r.desde AND r.hasta THEN RAISE EXCEPTION 'Periodo cerrado o fecha fuera del periodo' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV025','regla_id','RN-039','campos',jsonb_build_array(jsonb_build_object('campo','periodo_id','problema','invalido'),jsonb_build_object('campo','fecha_reconocimiento','problema','invalido')))::text; END IF;
 RETURN pid;
END $$;
CREATE FUNCTION bovi.fn_periodo_payload(e uuid,s uuid,j jsonb) RETURNS uuid LANGUAGE sql SET search_path = pg_catalog AS $$ SELECT bovi.fn_periodo(e,s,(j->>'fecha_reconocimiento')::date,(j->>'periodo_id')::uuid) $$;
CREATE FUNCTION bovi.fn_repartir(m numeric,n integer) RETURNS TABLE(numero integer,importe numeric) LANGUAGE sql IMMUTABLE SET search_path = pg_catalog AS $$
 SELECT i, round(m/n,2) + CASE WHEN i<=abs(round((m-round(m/n,2)*n)*100)) THEN sign(m-round(m/n,2)*n)*0.01 ELSE 0 END FROM generate_series(1,n) i WHERE n>0
$$;
CREATE VIEW bovi.v_saldo_liquidacion AS SELECT l.*, l.total + coalesce((SELECT sum(CASE naturaleza WHEN 'CARGO' THEN monto ELSE -monto END) FROM bovi.ajuste_liquidacion a WHERE (a.empresa_id,a.sucursal_id,a.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id)),0) AS total_ajustado, l.total + coalesce((SELECT sum(CASE naturaleza WHEN 'CARGO' THEN monto ELSE -monto END) FROM bovi.ajuste_liquidacion a WHERE (a.empresa_id,a.sucursal_id,a.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id)),0) - coalesce((SELECT sum(CASE naturaleza WHEN 'APLICACION' THEN importe ELSE -importe END) FROM bovi.aplicacion_pago a WHERE (a.empresa_id,a.sucursal_id,a.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id)),0) AS saldo FROM bovi.liquidacion l;
CREATE VIEW bovi.v_disponible_pago AS SELECT p.*,p.importe-coalesce((SELECT sum(CASE naturaleza WHEN 'APLICACION' THEN importe ELSE -importe END) FROM bovi.aplicacion_pago a WHERE (a.empresa_id,a.sucursal_id,a.pago_id)=(p.empresa_id,p.sucursal_id,p.id)),0)-coalesce((SELECT sum(r.importe) FROM bovi.pago r WHERE (r.empresa_id,r.sucursal_id,r.pago_origen_id)=(p.empresa_id,p.sucursal_id,p.id)),0) AS disponible FROM bovi.pago p;
CREATE VIEW bovi.v_margen_operacion AS SELECT o.empresa_id,o.sucursal_id,o.id AS operacion_id,l.total_ajustado AS venta_neta,coalesce((SELECT sum(delta_costo_venta) FROM bovi.asiento_valoracion a WHERE (a.empresa_id,a.sucursal_id,a.operacion_id)=(o.empresa_id,o.sucursal_id,o.id)),0) AS costo_vendido,coalesce((SELECT sum(CASE naturaleza WHEN 'COSTO' THEN importe ELSE -importe END) FROM bovi.gasto_operacion g WHERE (g.empresa_id,g.sucursal_id,g.operacion_id)=(o.empresa_id,o.sucursal_id,o.id) AND clasificacion='DIRECTO_VENTA' AND g.estado='APROBADO'),0) AS gastos_directos,'PROVISIONAL'::text AS estado_margen FROM bovi.operacion o JOIN bovi.v_saldo_liquidacion l ON (l.empresa_id,l.sucursal_id,l.operacion_id)=(o.empresa_id,o.sucursal_id,o.id) WHERE o.tipo='VENTA';
CREATE FUNCTION bovi.fn_calcular_liquidacion(e uuid,s uuid,op uuid) RETURNS TABLE(numero_lote smallint,cantidad numeric,unidad text,precio numeric,base numeric,cargos numeric,bonificaciones numeric,total numeric,pesaje_id uuid) LANGUAGE sql STABLE SET search_path = pg_catalog AS $$
 SELECT c.numero_lote, q.cantidad,c.unidad_precio::text,c.precio_unitario,round(q.cantidad*c.precio_unitario,2),c.cargos_pactados,c.bonificaciones_pactadas,round(q.cantidad*c.precio_unitario,2)+c.cargos_pactados-c.bonificaciones_pactadas,c.pesaje_base_id
 FROM bovi.condicion_lote c JOIN bovi.operacion o ON (o.empresa_id,o.sucursal_id,o.id)=(c.empresa_id,c.sucursal_id,c.operacion_id)
 LEFT JOIN bovi.pesaje p ON (p.empresa_id,p.sucursal_id,p.id)=(c.empresa_id,c.sucursal_id,c.pesaje_base_id)
 CROSS JOIN LATERAL(SELECT CASE c.unidad_precio WHEN 'KG' THEN p.neto_kg*(1-c.deduccion_pct/100) ELSE (CASE o.tipo WHEN 'COMPRA' THEN (SELECT count(*) FROM bovi.seleccion_compra x WHERE (x.empresa_id,x.sucursal_id,x.operacion_id,x.numero_lote)=(c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote)) ELSE (SELECT count(*) FROM bovi.seleccion_venta x WHERE (x.empresa_id,x.sucursal_id,x.operacion_id,x.numero_lote)=(c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote)) END) END AS cantidad) q
 WHERE c.empresa_id=e AND c.sucursal_id=s AND c.operacion_id=op AND c.numero_version=CASE WHEN o.estado='BORRADOR' THEN (SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,op)) ELSE coalesce(o.numero_version_aceptada,1) END
 ORDER BY c.numero_lote
$$;
CREATE FUNCTION bovi.fn_codigo(c text) RETURNS text LANGUAGE plpgsql IMMUTABLE SET search_path = pg_catalog AS $$
DECLARE norm text:=upper(c);
BEGIN IF norm IS NULL OR length(c) NOT BETWEEN 1 AND 40 OR norm !~ '^[A-Z0-9 -]+$' OR norm !~ '[A-Z0-9]' THEN RAISE EXCEPTION 'Código inválido; sólo letras ASCII, números, espacios y guiones' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Código inválido; sólo letras ASCII, números, espacios y guiones','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF; RETURN regexp_replace(norm,'[ -]','','g'); END $$;
CREATE FUNCTION bovi.fn_normalizar_payload(cmd text,j jsonb) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE SET search_path = pg_catalog AS $$
DECLARE outj jsonb:=j; lot jsonb; lots jsonb:='[]'; v text;
BEGIN
 IF cmd='registrar_animal' AND j ? 'identificaciones' THEN outj:=outj||jsonb_build_object('codigo',j#>>'{identificaciones,0,codigo}','sistema',j#>>'{identificaciones,0,sistema}'); END IF;
 IF cmd='corregir_pesaje' THEN outj:=outj||jsonb_build_object('corrige_a_id',coalesce(j->>'corrige_a_id',j->>'pesaje_id')); END IF;
 FOREACH v IN ARRAY ARRAY['importe','monto','cargos_pactados','bonificaciones_pactadas'] LOOP IF jsonb_typeof(j->v)='object' THEN IF j#>>ARRAY[v,'moneda'] IS DISTINCT FROM 'MXN' THEN RAISE EXCEPTION 'Sólo MXN' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Sólo MXN','codigo','BV015','regla_id','RN-034','campos','[]'::jsonb)::text; END IF; outj:=outj||jsonb_build_object(v,j#>>ARRAY[v,'importe']); END IF; END LOOP;
 FOREACH v IN ARRAY ARRAY['bruto','tara','neto'] LOOP
 IF j ? v THEN IF j#>>ARRAY[v,'kg'] IS NULL THEN RAISE EXCEPTION 'Unidad debe ser KG' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Unidad debe ser KG','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF; outj:=outj||jsonb_build_object(v||'_kg',j#>>ARRAY[v,'kg']); END IF;
 END LOOP;
 IF j ? 'lotes' THEN
 FOR lot IN SELECT value FROM jsonb_array_elements(j->'lotes') LOOP
 lot:=bovi.fn_normalizar_payload('lote',lot); lot:=lot||jsonb_build_object('animal_ids',coalesce(lot->'animal_ids',lot->'animales','[]'::jsonb),'posicion_ids',coalesce(lot->'posicion_ids',lot->'posiciones','[]'::jsonb));
 IF lot ? 'neto' THEN lot:=lot||jsonb_build_object('neto_kg',lot#>>'{neto,kg}'); END IF;
 lots:=lots||jsonb_build_array(lot);
 END LOOP; outj:=outj||jsonb_build_object('lotes',lots);
 END IF;
 RETURN outj;
END $$;
CREATE FUNCTION bovi.fn_reparto(e uuid,s uuid,gid uuid,metodo text,asignaciones jsonb DEFAULT NULL) RETURNS TABLE(posicion_id uuid,base_valor numeric,importe numeric) LANGUAGE plpgsql STABLE SET search_path = pg_catalog AS $$
DECLARE g bovi.gasto_operacion%ROWTYPE; ids uuid[]; weights numeric[]; valuesn numeric[]; sourceweight numeric; entry jsonb; amount numeric; totalweight numeric; roundedtotal numeric; residual integer; idx integer; signn integer;
BEGIN
 SELECT * INTO g FROM bovi.gasto_operacion WHERE (empresa_id,sucursal_id,id)=(e,s,gid);
 IF NOT FOUND THEN RAISE EXCEPTION 'Gasto inexistente' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 SELECT array_agg(id ORDER BY id) INTO ids FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,compra_operacion_id)=(e,s,g.operacion_id);
 IF ids IS NULL THEN RAISE EXCEPTION 'Compra sin posiciones' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 IF metodo NOT IN ('POR_CABEZA','POR_PESO_MEDIDO','IMPORTE_INDIVIDUAL') THEN RAISE EXCEPTION 'Método inválido' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos',jsonb_build_array(jsonb_build_object('campo','metodo','problema','invalido')))::text; END IF;
 IF metodo='IMPORTE_INDIVIDUAL' THEN
 IF jsonb_typeof(asignaciones) IS DISTINCT FROM 'array' OR jsonb_array_length(asignaciones)<>cardinality(ids) OR (SELECT count(DISTINCT value->>'posicion_id') FROM jsonb_array_elements(asignaciones))<>cardinality(ids) THEN RAISE EXCEPTION 'Importes individuales requieren todas las posiciones una vez' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos',jsonb_build_array(jsonb_build_object('campo','asignaciones','problema','invalido')))::text; END IF;
 END IF;
 FOREACH posicion_id IN ARRAY ids LOOP
 IF metodo='POR_CABEZA' THEN sourceweight:=1;
 ELSIF metodo='POR_PESO_MEDIDO' THEN
 SELECT pa.peso_individual_kg INTO sourceweight FROM bovi.posicion_inventario p JOIN bovi.condicion_lote c ON (c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote,c.numero_version)=(p.empresa_id,p.sucursal_id,p.compra_operacion_id,p.compra_numero_lote,(SELECT numero_version FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,operacion_id)=(p.empresa_id,p.sucursal_id,p.compra_operacion_id))) JOIN bovi.pesaje w ON (w.empresa_id,w.sucursal_id,w.id)=(c.empresa_id,c.sucursal_id,c.pesaje_base_id) JOIN bovi.pesaje_animal pa ON (pa.empresa_id,pa.sucursal_id,pa.pesaje_id,pa.animal_id)=(w.empresa_id,w.sucursal_id,w.id,p.animal_id) WHERE (p.empresa_id,p.sucursal_id,p.id)=(e,s,posicion_id) AND w.estado='APROBADO';
 IF sourceweight IS NULL OR sourceweight<=0 THEN RAISE EXCEPTION 'Faltan pesos individuales medidos; no se infieren del peso del lote' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-013','campos',jsonb_build_array(jsonb_build_object('campo','metodo','problema','invalido')))::text; END IF;
 ELSE
 SELECT value INTO entry FROM jsonb_array_elements(asignaciones) WHERE (value->>'posicion_id')::uuid=posicion_id;
 amount:=coalesce(entry#>>'{importe,importe}',entry->>'importe')::numeric;
 IF entry IS NULL OR amount<=0 OR amount<>round(amount,2) OR (entry#>>'{importe,moneda}' IS NOT NULL AND entry#>>'{importe,moneda}'<>'MXN') THEN RAISE EXCEPTION 'Importe individual inválido' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos',jsonb_build_array(jsonb_build_object('campo','asignaciones','problema','invalido')))::text; END IF;
 sourceweight:=1; valuesn:=array_append(valuesn,amount);
 END IF;
 weights:=array_append(weights,sourceweight);
 END LOOP;
 amount:=g.importe*CASE g.naturaleza WHEN 'COSTO' THEN 1 ELSE -1 END;
 IF metodo='IMPORTE_INDIVIDUAL' THEN
 IF (SELECT sum(v) FROM unnest(valuesn) v)<>g.importe THEN RAISE EXCEPTION 'Asignaciones no suman gasto' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV018','regla_id','RN-026','campos',jsonb_build_array(jsonb_build_object('campo','asignaciones','problema','invalido')))::text; END IF;
 ELSE
 SELECT sum(v) INTO totalweight FROM unnest(weights) v;
 SELECT array_agg(round(amount*v/totalweight,2) ORDER BY ord),sum(round(amount*v/totalweight,2)) INTO valuesn,roundedtotal FROM unnest(weights) WITH ORDINALITY AS vals(v,ord);
 residual:=round((amount-roundedtotal)*100); signn:=sign(residual);
 FOR idx IN 1..abs(residual) LOOP valuesn[idx]:=valuesn[idx]+signn*0.01; END LOOP;
 END IF;
 FOR idx IN 1..cardinality(ids) LOOP posicion_id:=ids[idx];base_valor:=weights[idx];importe:=valuesn[idx]*CASE WHEN metodo='IMPORTE_INDIVIDUAL' AND g.naturaleza='BONIFICACION' THEN -1 ELSE 1 END;RETURN NEXT; END LOOP;
END $$;
CREATE FUNCTION bovi.cmd_ejecutar(p_empresa uuid,p_sucursal uuid,p_actor uuid,p_clave text,p_hash text,p_correlation uuid,p_comando text,p_payload jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
#variable_conflict use_column
DECLARE e uuid:=p_empresa; s uuid:=p_sucursal; a uuid:=p_actor; j jsonb:=p_payload; n text:=bovi.fn_nodo(); result jsonb; prev bovi.clave_idempotencia%ROWTYPE; op bovi.operacion%ROWTYPE; pos bovi.posicion_inventario%ROWTYPE; pay bovi.pago%ROWTYPE; liq bovi.liquidacion%ROWTYPE; app bovi.aplicacion_pago%ROWTYPE; gasto bovi.gasto_operacion%ROWTYPE; r record; c record; lot jsonb; x jsonb; idn uuid:=uuidv7(); opid uuid:=coalesce((j->>'operacion_id')::uuid,(j->>'id')::uuid); pid uuid; lid uuid; wid uuid; aid uuid; per uuid; amount numeric; totaln numeric; cost numeric; cnt integer; k integer; idx integer:=0; seqn integer; contractn smallint; preserve boolean:=false; clas text; nature text; f date:=coalesce((j->>'fecha_economica')::date,(j->>'fecha_operacion')::date,current_date); ref uuid; ids uuid[]; state text;
BEGIN
 j:=bovi.fn_normalizar_payload(p_comando,j); opid:=coalesce((j->>'operacion_id')::uuid,(j->>'id')::uuid);
 IF p_comando='corregir_pesaje' AND (j->>'operacion_id') IS NULL THEN SELECT operacion_id INTO opid FROM bovi.pesaje WHERE (empresa_id,sucursal_id,id)=(e,s,(j->>'corrige_a_id')::uuid); END IF;
 IF p_comando='liberar_reserva' AND opid IS NULL THEN SELECT operacion_id INTO opid FROM bovi.reserva_venta WHERE (empresa_id,sucursal_id,id)=(e,s,(j->>'reserva_id')::uuid); END IF;
 PERFORM bovi.fn_scope(e,s,a,CASE WHEN p_comando IN ('registrar_pago','validar_pago','aplicar_pago','revertir_aplicacion','reembolsar_pago') THEN 'CAJA' WHEN p_comando IN ('ajustar_liquidacion','cerrar_periodo','reabrir_periodo','registrar_baja','anular_venta','registrar_revision','crear_usuario','actualizar_usuario','asignar_membresia') THEN 'ADMIN' ELSE 'OPERADOR' END,p_comando IN ('crear_contraparte','crear_predio','registrar_animal','crear_usuario','actualizar_usuario','asignar_membresia'));
 IF p_clave IS NULL OR length(p_clave) NOT BETWEEN 16 AND 80 OR p_hash !~ '^[0-9a-f]{64}$' THEN RAISE EXCEPTION 'Idempotencia inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Idempotencia inválida','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.clave_idempotencia VALUES(e,s,a,p_comando,p_clave,p_hash,'EN_CURSO',NULL,now(),'infinity'::timestamptz) ON CONFLICT DO NOTHING;
 SELECT * INTO prev FROM bovi.clave_idempotencia WHERE (empresa_id,sucursal_id,principal_id,comando,clave)=(e,s,a,p_comando,p_clave) FOR UPDATE;
 IF prev.hash_peticion<>p_hash THEN RAISE EXCEPTION 'Clave usada con payload distinto' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Clave usada con payload distinto','codigo','BV405','regla_id','RN-032','campos','[]'::jsonb)::text; END IF;
 IF prev.estado='COMPLETADA' THEN RETURN prev.resultado; END IF;
 CASE p_comando
 WHEN 'crear_usuario' THEN
 IF j->>'hash_contrasena' !~ '^\{bcrypt\}\$2[aby]\$[0-9]{2}\$[./A-Za-z0-9]{53}$' THEN RAISE EXCEPTION 'Hash de contraseña inválido' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-001','campos',jsonb_build_array(jsonb_build_object('campo','contrasena','problema','invalido')))::text; END IF;
 INSERT INTO bovi.usuario(empresa_id,id,login_normalizado,nombre,hash_contrasena,estado,nodo_origen) VALUES(e,idn,lower(btrim(j->>'login')),j->>'nombre',j->>'hash_contrasena','ACTIVO',n);
 WHEN 'actualizar_usuario' THEN
 idn:=coalesce((j->>'usuario_id')::uuid,(j->>'id')::uuid);
 UPDATE bovi.usuario SET nombre=coalesce(j->>'nombre',nombre),estado=coalesce(j->>'estado',estado) WHERE empresa_id=e AND id=idn;
 IF NOT FOUND THEN RAISE EXCEPTION 'Usuario inexistente' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV404','regla_id','RN-001','campos','[]'::jsonb)::text; END IF;
 WHEN 'asignar_membresia' THEN
 IF j ? 'sucursal_id' AND (j->>'sucursal_id')::uuid<>s THEN RAISE EXCEPTION 'Membresía fuera de la sede autorizada' USING ERRCODE='42501'; END IF;
 idn:=(j->>'usuario_id')::uuid;
 INSERT INTO bovi.membresia_usuario VALUES(e,coalesce((j->>'sucursal_id')::uuid,s),idn,j->>'rol_codigo',coalesce((j->>'vigente')::boolean,true),n) ON CONFLICT(empresa_id,sucursal_id,usuario_id,rol_codigo) DO UPDATE SET vigente=excluded.vigente;
 WHEN 'crear_contraparte' THEN
 INSERT INTO bovi.parte(empresa_id,id,tipo_persona,nombre,rfc,telefono,es_sintetico,nodo_origen) VALUES(e,idn,coalesce(j->>'tipo_persona','FISICA'),j->>'nombre',nullif(upper(j->>'rfc'),''),j->>'telefono',coalesce((j->>'es_sintetico')::boolean,true),n);
 WHEN 'crear_predio' THEN
 INSERT INTO bovi.predio(empresa_id,id,nombre,clave_upp_declarada,municipio,entidad_federativa,parte_responsable_id,nodo_origen) VALUES(e,idn,j->>'nombre',j->>'clave_upp_declarada',j->>'municipio',j->>'entidad_federativa',(j->>'parte_responsable_id')::uuid,n);
 WHEN 'registrar_animal' THEN
 INSERT INTO bovi.animal(empresa_id,id,sede_operadora_id,sexo,fecha_nacimiento_declarada,raza_declarada,situacion,nodo_origen) VALUES(e,idn,coalesce((j->>'sede_operadora_id')::uuid,s),j->>'sexo',(j->>'fecha_nacimiento_declarada')::date,j->>'raza_declarada','VIGENTE',n);
 FOR x IN SELECT value FROM jsonb_array_elements(coalesce(j->'identificaciones',jsonb_build_array(jsonb_build_object('sistema',coalesce(j->>'sistema','INTERNO'),'codigo',j->>'codigo')))) LOOP INSERT INTO bovi.animal_identificacion(empresa_id,animal_id,sistema,codigo_declarado,codigo_normalizado,estado,vigente_desde,nodo_origen) VALUES(e,idn,x->>'sistema',x->>'codigo',bovi.fn_codigo(x->>'codigo'),'VIGENTE',current_date,n); END LOOP;
 WHEN 'crear_operacion','editar_operacion' THEN
 IF p_comando='crear_operacion' THEN
 INSERT INTO bovi.folio_contador VALUES(e,s,j->>'tipo',extract(year FROM f)::smallint,1,n) ON CONFLICT(empresa_id,sucursal_id,tipo,anio) DO UPDATE SET ultimo=bovi.folio_contador.ultimo+1 RETURNING ultimo INTO seqn;
 INSERT INTO bovi.operacion(empresa_id,sucursal_id,id,tipo,folio,parte_id,predio_origen_id,predio_destino_id,estado,estado_entrega,fecha_operacion,nodo_origen,creado_por) VALUES(e,s,idn,j->>'tipo',left(j->>'tipo',1)||'-'||extract(year FROM f)::text||'-'||lpad(seqn::text,6,'0'),(j->>'parte_id')::uuid,(j->>'predio_origen_id')::uuid,(j->>'predio_destino_id')::uuid,'BORRADOR','PENDIENTE',f,n,a);
 opid:=idn;
 ELSE
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF NOT FOUND OR op.estado<>'BORRADOR' OR op.version_lock IS DISTINCT FROM (j->>'version_lock')::integer THEN RAISE EXCEPTION 'Reabra el acuerdo o actualice la versión antes de editar' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV412','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 IF EXISTS(SELECT 1 FROM bovi.reserva_venta WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) AND estado='ACTIVA') THEN RAISE EXCEPTION 'Libere reservas para editar' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV402','regla_id','RN-018','campos','[]'::jsonb)::text; END IF;
 preserve:=EXISTS(SELECT 1 FROM bovi.pesaje WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) OR EXISTS(SELECT 1 FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) AND estado='ACEPTADA');
 SELECT max(numero_version) INTO contractn FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 IF preserve THEN
 IF EXISTS(WITH incoming AS (SELECT ord::smallint numero_lote,(val#>>'{}')::uuid item FROM jsonb_array_elements(coalesce(j->'lotes','[]')) WITH ORDINALITY l(body,ord) CROSS JOIN LATERAL jsonb_array_elements(CASE op.tipo WHEN 'COMPRA' THEN body->'animal_ids' ELSE body->'posicion_ids' END) val), previous AS (SELECT numero_lote,animal_id item FROM bovi.seleccion_compra WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) UNION ALL SELECT numero_lote,posicion_id FROM bovi.seleccion_venta WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) SELECT * FROM ((TABLE incoming EXCEPT TABLE previous) UNION (TABLE previous EXCEPT TABLE incoming)) diff) THEN RAISE EXCEPTION 'La composición con historia debe conservarse' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 END IF;
 DELETE FROM bovi.condicion_lote WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn);
 IF NOT preserve THEN
 DELETE FROM bovi.seleccion_compra WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 DELETE FROM bovi.seleccion_venta WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 DELETE FROM bovi.lote_operacion WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 END IF;
 UPDATE bovi.operacion SET parte_id=coalesce((j->>'parte_id')::uuid,parte_id),fecha_operacion=f,version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 END IF;
 IF p_comando='editar_operacion' AND j ? 'requiere_recepcion' THEN UPDATE bovi.contrato_version SET requiere_recepcion=(j->>'requiere_recepcion')::boolean WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn); END IF;
 IF p_comando='crear_operacion' THEN contractn:=1; INSERT INTO bovi.contrato_version(empresa_id,sucursal_id,operacion_id,numero_version,estado,politica_redondeo,requiere_recepcion,nodo_origen) VALUES(e,s,opid,contractn,'PROPUESTA','HALF_UP_2',coalesce((j->>'requiere_recepcion')::boolean,false),n); END IF;
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 FOR lot IN SELECT value FROM jsonb_array_elements(coalesce(j->'lotes','[]')) LOOP
 idx:=idx+1;
 IF NOT preserve THEN
 INSERT INTO bovi.lote_operacion VALUES(e,s,opid,idx,lot->>'descripcion',n);
 IF op.tipo='COMPRA' THEN
 FOR x IN SELECT value FROM jsonb_array_elements(lot->'animal_ids') LOOP INSERT INTO bovi.seleccion_compra VALUES(e,s,opid,idx,(x#>>'{}')::uuid,'COMPRA',n); END LOOP;
 ELSE
 FOR x IN SELECT value FROM jsonb_array_elements(lot->'posicion_ids') LOOP INSERT INTO bovi.seleccion_venta VALUES(e,s,opid,idx,(x#>>'{}')::uuid,'VENTA',n); END LOOP;
 END IF;
 END IF;
 IF lot->>'unidad_precio'='KG' AND lot ? 'neto_kg' THEN
 wid:=uuidv7();
 INSERT INTO bovi.pesaje(empresa_id,sucursal_id,id,operacion_id,numero_lote,modo,neto_kg,ticket_folio,bascula,estado,fuente,nodo_origen) VALUES(e,s,wid,opid,idx,'NETO_REPORTADO',(lot->>'neto_kg')::numeric,lot->>'ticket_folio',lot->>'bascula','PROPUESTA','MANUAL',n);
 INSERT INTO bovi.pesaje_animal(empresa_id,sucursal_id,pesaje_id,animal_id,nodo_origen) SELECT e,s,wid,animal_id,n FROM bovi.seleccion_compra WHERE (empresa_id,sucursal_id,operacion_id,numero_lote)=(e,s,opid,idx) UNION ALL SELECT e,s,wid,p.animal_id,n FROM bovi.seleccion_venta v JOIN bovi.posicion_inventario p ON (p.empresa_id,p.sucursal_id,p.id)=(v.empresa_id,v.sucursal_id,v.posicion_id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id,v.numero_lote)=(e,s,opid,idx);
 ELSE wid:=(lot->>'pesaje_base_id')::uuid; END IF;
 INSERT INTO bovi.condicion_lote VALUES(e,s,opid,contractn,idx,lot->>'unidad_precio',(lot->>'precio_unitario')::numeric,CASE WHEN lot->>'unidad_precio'='KG' THEN 'PESAJE' ELSE 'NINGUNA' END,wid,coalesce((lot->>'deduccion_pct')::numeric,0),coalesce((lot->>'cargos_pactados')::numeric,0),coalesce((lot->>'bonificaciones_pactadas')::numeric,0),n);
 END LOOP;
 IF coalesce((j->>'acordar')::boolean,false) THEN
 UPDATE bovi.contrato_version SET estado='ACEPTADA',aceptada_por=a,aceptada_en=now() WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn);
 UPDATE bovi.operacion SET estado='ACORDADA',numero_version_aceptada=contractn WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 END IF;
 idn:=opid;
 WHEN 'acordar_operacion','reabrir_operacion' THEN
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF NOT FOUND OR op.version_lock IS DISTINCT FROM (j->>'version_lock')::integer OR op.estado<>(CASE p_comando WHEN 'acordar_operacion' THEN 'BORRADOR' ELSE 'ACORDADA' END) THEN RAISE EXCEPTION 'Estado o versión no permite acuerdo' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV412','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 SELECT max(numero_version) INTO contractn FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 IF p_comando='acordar_operacion' THEN
 IF NOT EXISTS(SELECT 1 FROM bovi.condicion_lote WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn)) THEN RAISE EXCEPTION 'Acuerdo sin condiciones' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 UPDATE bovi.contrato_version SET estado='ACEPTADA',aceptada_por=a,aceptada_en=now() WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn);
 UPDATE bovi.operacion SET estado='ACORDADA',numero_version_aceptada=contractn,version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 ELSE
 INSERT INTO bovi.contrato_version SELECT empresa_id,sucursal_id,operacion_id,contractn+1,'PROPUESTA',politica_redondeo,requiere_recepcion,documento_id,NULL,NULL,nodo_origen FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn);
 INSERT INTO bovi.condicion_lote SELECT empresa_id,sucursal_id,operacion_id,contractn+1,numero_lote,unidad_precio,precio_unitario,base_pesaje,pesaje_base_id,deduccion_pct,cargos_pactados,bonificaciones_pactadas,nodo_origen FROM bovi.condicion_lote WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn);
 UPDATE bovi.operacion SET estado='BORRADOR',version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 END IF; idn:=opid;
 WHEN 'registrar_pesaje','corregir_pesaje' THEN
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF op.estado NOT IN ('BORRADOR','ACORDADA') THEN RAISE EXCEPTION 'Operación comprometida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Operación comprometida','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 IF p_comando='corregir_pesaje' THEN UPDATE bovi.pesaje SET estado='CORREGIDO' WHERE (empresa_id,sucursal_id,id)=(e,s,(j->>'corrige_a_id')::uuid) AND estado='APROBADO'; IF NOT FOUND THEN RAISE EXCEPTION 'Pesaje no aprobado' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pesaje no aprobado','codigo','BV013','regla_id','RN-013','campos','[]'::jsonb)::text; END IF; END IF;
 INSERT INTO bovi.pesaje(empresa_id,sucursal_id,id,operacion_id,numero_lote,modo,bruto_kg,tara_kg,neto_kg,ticket_folio,bascula,pesado_en,documento_id,estado,fuente,corrige_a_id,nodo_origen) VALUES(e,s,idn,opid,(j->>'numero_lote')::smallint,j->>'modo',(j->>'bruto_kg')::numeric,(j->>'tara_kg')::numeric,CASE WHEN j->>'modo'='BRUTO_TARA' THEN (j->>'bruto_kg')::numeric-(j->>'tara_kg')::numeric ELSE (j->>'neto_kg')::numeric END,j->>'ticket_folio',j->>'bascula',coalesce((j->>'pesado_en')::timestamptz,now()),(j->>'documento_id')::uuid,'PROPUESTA',coalesce(j->>'fuente','MANUAL'),(j->>'corrige_a_id')::uuid,n);
 FOR x IN SELECT value FROM jsonb_array_elements(j->'animales') LOOP INSERT INTO bovi.pesaje_animal VALUES(e,s,idn,(x->>'animal_id')::uuid,coalesce(x->>'peso_individual_kg',x#>>'{peso_individual,kg}')::numeric,n); END LOOP;
 UPDATE bovi.condicion_lote SET pesaje_base_id=idn WHERE (empresa_id,sucursal_id,operacion_id,numero_lote)=(e,s,opid,(j->>'numero_lote')::smallint) AND numero_version=(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) AND unidad_precio='KG' AND op.estado='BORRADOR';
 WHEN 'aprobar_pesaje' THEN
 idn:=coalesce((j->>'pesaje_id')::uuid,(j->>'id')::uuid);
 IF NOT EXISTS(SELECT 1 FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,idn)) THEN RAISE EXCEPTION 'Falta composición' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Falta composición','codigo','BV013','regla_id','RN-013','campos','[]'::jsonb)::text; END IF;
 UPDATE bovi.pesaje SET estado='APROBADO',aprobado_por=a,aprobado_en=now() WHERE (empresa_id,sucursal_id,id)=(e,s,idn) AND estado='PROPUESTA'; IF NOT FOUND THEN RAISE EXCEPTION 'Pesaje no propuesto' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pesaje no propuesto','codigo','BV013','regla_id','RN-013','campos','[]'::jsonb)::text; END IF;
 WHEN 'reservar_venta','liberar_reserva' THEN
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF op.tipo IS DISTINCT FROM 'VENTA' OR op.estado NOT IN ('BORRADOR','ACORDADA') THEN RAISE EXCEPTION 'Venta inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Venta inválida','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 FOR pos IN SELECT p.* FROM bovi.posicion_inventario p JOIN bovi.seleccion_venta v ON (v.empresa_id,v.sucursal_id,v.posicion_id)=(p.empresa_id,p.sucursal_id,p.id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id)=(e,s,opid) ORDER BY p.id FOR UPDATE OF p LOOP
 UPDATE bovi.reserva_venta SET estado='EXPIRADA',cerrada_en=now() WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pos.id) AND estado='ACTIVA' AND vence_en<=now();
 IF p_comando='liberar_reserva' THEN UPDATE bovi.reserva_venta SET estado='LIBERADA',cerrada_en=now() WHERE (empresa_id,sucursal_id,operacion_id,posicion_id)=(e,s,opid,pos.id) AND estado='ACTIVA';
 ELSE
 IF pos.estado<>'DISPONIBLE' OR EXISTS(SELECT 1 FROM bovi.animal WHERE empresa_id=e AND id=pos.animal_id AND situacion<>'VIGENTE') OR EXISTS(SELECT 1 FROM bovi.movimiento_inventario WHERE empresa_id=e AND sucursal_id=s AND posicion_id=pos.id AND tipo='BAJA') THEN RAISE EXCEPTION 'Posición no disponible' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Posición no disponible','codigo','BV402','regla_id','RN-018','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.reserva_venta(empresa_id,sucursal_id,operacion_id,numero_lote,posicion_id,estado,creada_en,vence_en,nodo_origen) SELECT e,s,opid,v.numero_lote,pos.id,'ACTIVA',now(),coalesce((j->>'vence_en')::timestamptz,now()+interval '15 minutes'),n FROM bovi.seleccion_venta v WHERE (empresa_id,sucursal_id,operacion_id,posicion_id)=(e,s,opid,pos.id);
 END IF;
 END LOOP; idn:=opid;
 WHEN 'confirmar_operacion','confirmar_compra','confirmar_venta' THEN
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 per:=bovi.fn_periodo_payload(e,s,j);
 IF j ? 'periodo_id' AND per<>(j->>'periodo_id')::uuid THEN RAISE EXCEPTION 'Periodo no corresponde fecha reconocimiento' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Periodo no corresponde fecha reconocimiento','codigo','BV025','regla_id','RN-039','campos','[]'::jsonb)::text; END IF;
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF NOT FOUND OR op.estado NOT IN ('BORRADOR','ACORDADA') OR op.version_lock IS DISTINCT FROM (j->>'version_lock')::integer THEN RAISE EXCEPTION 'Operación o versión inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Operación o versión inválida','codigo','BV412','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 IF NOT EXISTS(SELECT 1 FROM bovi.lote_operacion WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) OR EXISTS(SELECT 1 FROM bovi.fn_calcular_liquidacion(e,s,opid) WHERE cantidad IS NULL OR cantidad<=0 OR total<0) OR EXISTS(SELECT 1 FROM bovi.condicion_lote c JOIN bovi.pesaje p ON (p.empresa_id,p.sucursal_id,p.id)=(c.empresa_id,c.sucursal_id,c.pesaje_base_id) WHERE (c.empresa_id,c.sucursal_id,c.operacion_id)=(e,s,opid) AND c.numero_version=(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) AND p.estado<>'APROBADO') THEN RAISE EXCEPTION 'Partidas o pesajes pendientes' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Partidas o pesajes pendientes','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 FOR r IN SELECT c.numero_lote,c.pesaje_base_id FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id)=(e,s,opid) AND c.numero_version=(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid)) AND c.unidad_precio='KG' LOOP
 IF EXISTS(WITH measured AS(SELECT animal_id FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,r.pesaje_base_id)), selected AS(SELECT animal_id FROM bovi.seleccion_compra WHERE (empresa_id,sucursal_id,operacion_id,numero_lote)=(e,s,opid,r.numero_lote) UNION ALL SELECT p.animal_id FROM bovi.seleccion_venta v JOIN bovi.posicion_inventario p ON (p.empresa_id,p.sucursal_id,p.id)=(v.empresa_id,v.sucursal_id,v.posicion_id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id,v.numero_lote)=(e,s,opid,r.numero_lote)) SELECT animal_id FROM ((TABLE measured EXCEPT TABLE selected) UNION (TABLE selected EXCEPT TABLE measured)) diff) THEN RAISE EXCEPTION 'Conjunto de pesaje no comparable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Conjunto de pesaje no comparable','codigo','BV013','regla_id','RN-013','campos','[]'::jsonb)::text; END IF;
 END LOOP;
 SELECT max(numero_version) INTO contractn FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid);
 UPDATE bovi.contrato_version SET estado='ACEPTADA',aceptada_por=a,aceptada_en=now() WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn) AND estado='PROPUESTA';
 UPDATE bovi.operacion SET numero_version_aceptada=contractn WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 SELECT sum(total) INTO totaln FROM bovi.fn_calcular_liquidacion(e,s,opid);
 IF totaln IS NULL THEN RAISE EXCEPTION 'Sin condiciones' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Sin condiciones','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.liquidacion(empresa_id,sucursal_id,id,operacion_id,numero_version,direccion,total,snapshot_contraparte_nombre,snapshot_contraparte_rfc,snapshot_condiciones,vence_el,periodo_id,confirmada_por,confirmada_en,nodo_origen) SELECT e,s,idn,opid,contractn,CASE op.tipo WHEN 'COMPRA' THEN 'POR_PAGAR' ELSE 'POR_COBRAR' END,totaln,p.nombre,p.rfc,(SELECT jsonb_agg(to_jsonb(c)-'nodo_origen') FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id)=(e,s,opid) AND c.numero_version=contractn),(j->>'vence_el')::date,per,a,now(),n FROM bovi.parte p WHERE (p.empresa_id,p.id)=(e,op.parte_id);
 lid:=idn;
 FOR r IN SELECT * FROM bovi.fn_calcular_liquidacion(e,s,opid) LOOP
 idx:=idx+1;
 INSERT INTO bovi.concepto_liquidacion VALUES(e,s,lid,idx,'BASE','Precio pactado',r.numero_lote,r.cantidad,r.unidad,r.precio,r.base,r.pesaje_id,n);
 IF r.cargos>0 THEN idx:=idx+1; INSERT INTO bovi.concepto_liquidacion VALUES(e,s,lid,idx,'CARGO','Cargo pactado',r.numero_lote,1,'MXN',NULL,r.cargos,NULL,n); END IF;
 IF r.bonificaciones>0 THEN idx:=idx+1; INSERT INTO bovi.concepto_liquidacion VALUES(e,s,lid,idx,'BONIFICACION','Bonificación pactada',r.numero_lote,1,'MXN',NULL,-r.bonificaciones,NULL,n); END IF;
 END LOOP;
 IF op.tipo='COMPRA' THEN
 FOR r IN SELECT sc.* FROM bovi.seleccion_compra sc WHERE (sc.empresa_id,sc.sucursal_id,sc.operacion_id)=(e,s,opid) ORDER BY animal_id LOOP
 PERFORM 1 FROM bovi.animal WHERE empresa_id=e AND id=r.animal_id AND situacion='VIGENTE' FOR UPDATE; IF NOT FOUND THEN RAISE EXCEPTION 'Identidad no vigente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Identidad no vigente','codigo','BV011','regla_id','RN-005','campos','[]'::jsonb)::text; END IF;
 IF EXISTS(SELECT 1 FROM bovi.posicion_inventario WHERE empresa_id=e AND animal_id=r.animal_id AND estado='BAJA') THEN RAISE EXCEPTION 'Animal con baja requiere revisión central' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Animal con baja requiere revisión central','codigo','BV011','regla_id','RN-005','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.posicion_inventario(empresa_id,sucursal_id,animal_id,numero_ciclo,compra_operacion_id,compra_numero_lote,estado,nodo_origen) SELECT e,s,r.animal_id,coalesce(max(numero_ciclo),0)+1,opid,r.numero_lote,CASE WHEN (SELECT requiere_recepcion FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(e,s,opid,contractn)) THEN 'PENDIENTE_RECEPCION' ELSE 'DISPONIBLE' END,n FROM bovi.posicion_inventario WHERE empresa_id=e AND animal_id=r.animal_id;
 END LOOP;
 FOR c IN SELECT * FROM bovi.concepto_liquidacion WHERE (empresa_id,sucursal_id,liquidacion_id)=(e,s,lid) ORDER BY numero_concepto LOOP
 SELECT count(*) INTO cnt FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,compra_operacion_id,compra_numero_lote)=(e,s,opid,c.numero_lote);
 k:=0; ref:=uuidv7();
 FOR pos IN SELECT * FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,compra_operacion_id,compra_numero_lote)=(e,s,opid,c.numero_lote) ORDER BY id LOOP
 k:=k+1; SELECT importe INTO amount FROM bovi.fn_repartir(c.importe,cnt) WHERE numero=k;
 IF amount<>0 THEN
 aid:=uuidv7(); INSERT INTO bovi.asignacion_costo(empresa_id,sucursal_id,id,posicion_id,fuente_liquidacion_id,fuente_numero_concepto,metodo,base_valor,importe,lote_reparto_id,periodo_id,nodo_origen) VALUES(e,s,aid,pos.id,lid,c.numero_concepto,'POR_CABEZA',1,amount,ref,per,n);
 END IF;
 END LOOP;
 END LOOP;
 FOR pos IN SELECT * FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,compra_operacion_id)=(e,s,opid) ORDER BY id LOOP
 SELECT sum(importe) INTO cost FROM bovi.asignacion_costo WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pos.id);
 IF cost<=0 THEN RAISE EXCEPTION 'Costo inicial no positivo' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Costo inicial no positivo','codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.asiento_valoracion(empresa_id,sucursal_id,posicion_id,periodo_id,clase,sentido,importe,operacion_id,fecha_economica,nodo_origen) VALUES(e,s,pos.id,per,'ADQUISICION','AUMENTO',cost,opid,coalesce((j->>'fecha_reconocimiento')::date,current_date),n);
 END LOOP;
 ELSE
 FOR pos IN SELECT p.* FROM bovi.posicion_inventario p JOIN bovi.seleccion_venta v ON (v.empresa_id,v.sucursal_id,v.posicion_id)=(p.empresa_id,p.sucursal_id,p.id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id)=(e,s,opid) ORDER BY p.id FOR UPDATE OF p LOOP
 IF pos.estado<>'DISPONIBLE' OR NOT EXISTS(SELECT 1 FROM bovi.reserva_venta WHERE (empresa_id,sucursal_id,operacion_id,posicion_id)=(e,s,opid,pos.id) AND estado='ACTIVA' AND vence_en>now()) OR EXISTS(SELECT 1 FROM bovi.animal WHERE empresa_id=e AND id=pos.animal_id AND situacion<>'VIGENTE') THEN RAISE EXCEPTION 'Reserva vencida o posición no disponible' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Reserva vencida o posición no disponible','codigo','BV403','regla_id','RN-019','campos','[]'::jsonb)::text; END IF;
 SELECT sum(delta_inventario) INTO cost FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pos.id);
 INSERT INTO bovi.asiento_valoracion(empresa_id,sucursal_id,posicion_id,periodo_id,clase,sentido,importe,operacion_id,fecha_economica,nodo_origen) VALUES(e,s,pos.id,per,'VENTA','AUMENTO',cost,opid,coalesce((j->>'fecha_reconocimiento')::date,current_date),n);
 UPDATE bovi.posicion_inventario SET estado='VENDIDA_PENDIENTE_ENTREGA' WHERE (empresa_id,sucursal_id,id)=(e,s,pos.id);
 UPDATE bovi.reserva_venta SET estado='CONSUMIDA',cerrada_en=now() WHERE (empresa_id,sucursal_id,operacion_id,posicion_id)=(e,s,opid,pos.id) AND estado='ACTIVA';
 END LOOP;
 END IF;
 UPDATE bovi.operacion SET estado='CONFIRMADA',numero_version_aceptada=contractn,confirmada_en=now(),version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid);
 result:=bovi.fn_liquidacion_json(e,s,lid); idn:=lid;
 WHEN 'registrar_pago' THEN
 per:=NULL;
 INSERT INTO bovi.pago(empresa_id,sucursal_id,id,parte_id,tipo,importe,metodo,referencia,recibido_el,estado,pago_origen_id,documento_id,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento,naturaleza) VALUES(e,s,idn,(j->>'parte_id')::uuid,j->>'tipo',(j->>'importe')::numeric,j->>'metodo',j->>'referencia',coalesce((j->>'recibido_el')::date,current_date),'REGISTRADO',NULL,(j->>'documento_id')::uuid,a,n,NULL,NULL,'NORMAL');
 WHEN 'validar_pago' THEN
 pid:=coalesce((j->>'pago_id')::uuid,(j->>'id')::uuid); SELECT * INTO pay FROM bovi.pago WHERE (empresa_id,sucursal_id,id)=(e,s,pid); per:=bovi.fn_periodo_payload(e,s,j);
 UPDATE bovi.pago SET estado='VALIDADO',periodo_id=per,fecha_reconocimiento=(j->>'fecha_reconocimiento')::date WHERE (empresa_id,sucursal_id,id)=(e,s,pid) AND estado='REGISTRADO'; IF NOT FOUND THEN RAISE EXCEPTION 'Pago inválido' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pago inválido','codigo','BV020','regla_id','RN-029','campos','[]'::jsonb)::text; END IF; idn:=pid;
 WHEN 'aplicar_pago' THEN
 per:=bovi.fn_periodo_payload(e,s,j); pid:=(j->>'pago_id')::uuid;
 SELECT * INTO pay FROM bovi.pago WHERE (empresa_id,sucursal_id,id)=(e,s,pid) FOR UPDATE;
 IF NOT FOUND OR pay.estado<>'VALIDADO' OR pay.naturaleza='REEMBOLSO' THEN RAISE EXCEPTION 'Pago no validado' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pago no validado','codigo','BV020','regla_id','RN-029','campos','[]'::jsonb)::text; END IF;
 FOR lot IN SELECT value FROM jsonb_array_elements(coalesce(j->'aplicaciones',jsonb_build_array(jsonb_build_object('liquidacion_id',j->>'liquidacion_id','importe',j->>'importe')))) ORDER BY value->>'liquidacion_id' LOOP
 lid:=(lot->>'liquidacion_id')::uuid; amount:=coalesce(lot#>>'{importe,importe}',lot->>'importe')::numeric;
 SELECT * INTO liq FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,lid) FOR UPDATE;
 IF NOT FOUND OR NOT EXISTS(SELECT 1 FROM bovi.operacion WHERE (empresa_id,sucursal_id,id,parte_id,moneda)=(e,s,liq.operacion_id,pay.parte_id,pay.moneda)) OR (pay.tipo='COBRO')<>(liq.direccion='POR_COBRAR') THEN RAISE EXCEPTION 'Pago y obligación incompatibles' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Pago y obligación incompatibles','codigo','BV021','regla_id','RN-030','campos','[]'::jsonb)::text; END IF;
 IF amount<=0 OR amount<>(round(amount,2)) OR amount>(SELECT disponible FROM bovi.v_disponible_pago WHERE (empresa_id,sucursal_id,id)=(e,s,pid)) OR amount>(SELECT saldo FROM bovi.v_saldo_liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,lid)) THEN RAISE EXCEPTION 'Excede saldo o disponible' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Excede saldo o disponible','codigo','BV020','regla_id','RN-029','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.aplicacion_pago(empresa_id,sucursal_id,id,pago_id,liquidacion_id,importe,naturaleza,reverso_de_id,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento) VALUES(e,s,idn,pid,lid,amount,'APLICACION',NULL,a,n,per,coalesce((j->>'fecha_reconocimiento')::date,current_date));
 idn:=uuidv7(); END LOOP; result:=jsonb_build_object('pago_id',pid,'estado','APLICADO');
 WHEN 'revertir_aplicacion' THEN
 per:=bovi.fn_periodo_payload(e,s,j);
 SELECT * INTO app FROM bovi.aplicacion_pago WHERE (empresa_id,sucursal_id,id)=(e,s,coalesce((j->>'aplicacion_id')::uuid,(j->>'id')::uuid)) AND naturaleza='APLICACION'; IF NOT FOUND THEN RAISE EXCEPTION 'Aplicación inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Aplicación inexistente','codigo','BV022','regla_id','RN-033','campos','[]'::jsonb)::text; END IF;
 PERFORM 1 FROM bovi.pago WHERE (empresa_id,sucursal_id,id)=(e,s,app.pago_id) FOR UPDATE;
 PERFORM 1 FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,app.liquidacion_id) FOR UPDATE;
 INSERT INTO bovi.aplicacion_pago(empresa_id,sucursal_id,id,pago_id,liquidacion_id,importe,naturaleza,reverso_de_id,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento) VALUES(e,s,idn,app.pago_id,app.liquidacion_id,app.importe,'REVERSO',app.id,a,n,per,coalesce((j->>'fecha_reconocimiento')::date,current_date));
 WHEN 'reembolsar_pago' THEN
 per:=bovi.fn_periodo_payload(e,s,j); pid:=(j->>'pago_id')::uuid;
 SELECT * INTO pay FROM bovi.pago WHERE (empresa_id,sucursal_id,id)=(e,s,pid) FOR UPDATE;
 amount:=(j->>'importe')::numeric;
 IF NOT FOUND OR pay.estado<>'VALIDADO' OR pay.naturaleza='REEMBOLSO' OR amount<=0 OR amount>(SELECT disponible FROM bovi.v_disponible_pago WHERE (empresa_id,sucursal_id,id)=(e,s,pid)) THEN RAISE EXCEPTION 'Reembolso excede disponible' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Reembolso excede disponible','codigo','BV020','regla_id','RN-029','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.pago(empresa_id,sucursal_id,id,parte_id,tipo,importe,metodo,referencia,recibido_el,estado,pago_origen_id,documento_id,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento,naturaleza) VALUES(e,s,idn,pay.parte_id,CASE pay.tipo WHEN 'COBRO' THEN 'PAGO' ELSE 'COBRO' END,amount,j->>'metodo',j->>'referencia',current_date,'VALIDADO',pid,(j->>'documento_id')::uuid,a,n,per,coalesce((j->>'fecha_reconocimiento')::date,current_date),'REEMBOLSO');
 WHEN 'ajustar_liquidacion' THEN
 per:=bovi.fn_periodo_payload(e,s,j); lid:=(j->>'liquidacion_id')::uuid;
 SELECT * INTO liq FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,lid);
 PERFORM 1 FROM bovi.pago WHERE empresa_id=e AND sucursal_id=s AND id IN(SELECT pago_id FROM bovi.aplicacion_pago WHERE (empresa_id,sucursal_id,liquidacion_id)=(e,s,lid)) ORDER BY id FOR UPDATE;
 SELECT * INTO liq FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,lid) FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Liquidación inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Liquidación inexistente','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 amount:=(j->>'monto')::numeric;
 IF j->>'naturaleza'='ABONO' THEN
 SELECT total_ajustado,saldo INTO r FROM bovi.v_saldo_liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,lid);
 IF amount>r.total_ajustado THEN RAISE EXCEPTION 'Bonificación excede obligación' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV020','regla_id','RN-029','campos',jsonb_build_array(jsonb_build_object('campo','monto','problema','invalido')))::text; END IF;
 IF amount>r.saldo THEN
 IF NOT coalesce((j->>'reaplicar_pagos')::boolean,false) THEN RAISE EXCEPTION 'Confirme reverso y reaplicación atómica' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV020','regla_id','RN-029','campos',jsonb_build_array(jsonb_build_object('campo','reaplicar_pagos','problema','invalido')))::text; END IF;
 totaln:=r.total_ajustado-amount;
 FOR app IN SELECT * FROM bovi.aplicacion_pago ap WHERE (ap.empresa_id,ap.sucursal_id,ap.liquidacion_id)=(e,s,lid) AND ap.naturaleza='APLICACION' AND NOT EXISTS(SELECT 1 FROM bovi.aplicacion_pago rev WHERE (rev.empresa_id,rev.sucursal_id,rev.reverso_de_id)=(e,s,ap.id)) ORDER BY ap.aplicada_en,ap.id LOOP
 INSERT INTO bovi.aplicacion_pago(empresa_id,sucursal_id,pago_id,liquidacion_id,importe,naturaleza,reverso_de_id,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento) VALUES(e,s,app.pago_id,lid,app.importe,'REVERSO',app.id,a,n,per,(j->>'fecha_reconocimiento')::date);
 cost:=least(app.importe,totaln);
 IF cost>0 THEN INSERT INTO bovi.aplicacion_pago(empresa_id,sucursal_id,pago_id,liquidacion_id,importe,naturaleza,registrado_por,nodo_origen,periodo_id,fecha_reconocimiento) VALUES(e,s,app.pago_id,lid,cost,'APLICACION',a,n,per,(j->>'fecha_reconocimiento')::date); END IF; totaln:=totaln-cost;
 END LOOP;
 END IF;
 END IF;
 INSERT INTO bovi.ajuste_liquidacion(empresa_id,sucursal_id,id,liquidacion_id,naturaleza,monto,motivo,fuente,documento_id,revierte_ajuste_id,periodo_id,registrado_por,nodo_origen,fecha_reconocimiento) VALUES(e,s,idn,lid,j->>'naturaleza',amount,j->>'motivo',coalesce(j->>'fuente','OTRO'),(j->>'documento_id')::uuid,(j->>'revierte_ajuste_id')::uuid,per,a,n,coalesce((j->>'fecha_reconocimiento')::date,current_date));
 WHEN 'registrar_gasto' THEN
 per:=bovi.fn_periodo_payload(e,s,j);
 INSERT INTO bovi.gasto_operacion(empresa_id,sucursal_id,id,operacion_id,naturaleza,clasificacion,importe,concepto,proveedor_parte_id,referencia_origen,documento_id,bonifica_gasto_id,estado,fecha_economica,snapshot_fuente_externa,nodo_origen,periodo_id,fecha_reconocimiento) VALUES(e,s,idn,opid,coalesce(j->>'naturaleza','COSTO'),j->>'clasificacion',(j->>'importe')::numeric,j->>'concepto',(j->>'proveedor_parte_id')::uuid,j->>'referencia_origen',(j->>'documento_id')::uuid,(j->>'bonifica_gasto_id')::uuid,'BORRADOR',f,j->'snapshot_fuente_externa',n,per,coalesce((j->>'fecha_reconocimiento')::date,current_date));
 WHEN 'repartir_gasto','registrar_costo_tardio' THEN
 SELECT * INTO gasto FROM bovi.gasto_operacion WHERE (empresa_id,sucursal_id,id)=(e,s,coalesce((j->>'gasto_id')::uuid,(j->>'id')::uuid));
 per:=bovi.fn_periodo_payload(e,s,j);
 SELECT * INTO gasto FROM bovi.gasto_operacion WHERE (empresa_id,sucursal_id,id)=(e,s,gasto.id) FOR UPDATE;
 IF NOT FOUND OR gasto.estado<>'BORRADOR' THEN RAISE EXCEPTION 'Gasto ya distribuido o inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Gasto ya distribuido o inexistente','codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 IF gasto.naturaleza='BONIFICACION' THEN
 SELECT * INTO r FROM bovi.gasto_operacion WHERE (empresa_id,sucursal_id,id)=(e,s,gasto.bonifica_gasto_id) FOR UPDATE;
 IF r.estado<>'APROBADO' OR r.clasificacion<>gasto.clasificacion OR r.operacion_id<>gasto.operacion_id OR gasto.importe>r.importe-coalesce((SELECT sum(importe) FROM bovi.gasto_operacion WHERE (empresa_id,sucursal_id,bonifica_gasto_id)=(e,s,r.id) AND estado='APROBADO'),0) THEN RAISE EXCEPTION 'Bonificación incompatible o excesiva' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Bonificación incompatible o excesiva','codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 END IF;
 IF gasto.clasificacion='CAPITALIZABLE' THEN
 SELECT array_agg(id ORDER BY id) INTO ids FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,compra_operacion_id)=(e,s,gasto.operacion_id);
 cnt:=cardinality(ids); IF cnt IS NULL OR cnt=0 THEN RAISE EXCEPTION 'Compra aún no confirmada' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Compra aún no confirmada','codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 k:=0; ref:=uuidv7();
 FOR pos IN SELECT * FROM bovi.posicion_inventario WHERE empresa_id=e AND sucursal_id=s AND id=ANY(ids) ORDER BY id FOR UPDATE LOOP
 SELECT * INTO c FROM bovi.fn_reparto(e,s,gasto.id,coalesce(j->>'metodo','POR_CABEZA'),j->'asignaciones') WHERE posicion_id=pos.id; amount:=c.importe;
 IF amount=0 THEN CONTINUE; END IF;
 SELECT sum(importe) INTO cost FROM bovi.asignacion_costo WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pos.id);
 IF cost+amount<0 THEN RAISE EXCEPTION 'Costo acumulado negativo' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Costo acumulado negativo','codigo','BV018','regla_id','RN-026','campos','[]'::jsonb)::text; END IF;
 aid:=uuidv7();
 INSERT INTO bovi.asignacion_costo(empresa_id,sucursal_id,id,posicion_id,fuente_gasto_id,metodo,base_valor,importe,lote_reparto_id,periodo_id,nodo_origen) VALUES(e,s,aid,pos.id,gasto.id,coalesce(j->>'metodo','POR_CABEZA'),c.base_valor,amount,ref,per,n);
 clas:=CASE WHEN pos.estado='BAJA' THEN 'COSTO_TARDIO_PERDIDA' WHEN pos.estado IN ('VENDIDA_PENDIENTE_ENTREGA','CERRADA_VENTA') THEN 'COSTO_TARDIO_VENTA' ELSE 'COSTO_TARDIO_INVENTARIO' END;
 opid:=gasto.operacion_id;
 IF clas='COSTO_TARDIO_VENTA' THEN SELECT operacion_id INTO opid FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pos.id) AND clase='VENTA' ORDER BY registrado_en DESC LIMIT 1; END IF;
 INSERT INTO bovi.asiento_valoracion(empresa_id,sucursal_id,posicion_id,periodo_id,clase,sentido,importe,asignacion_id,operacion_id,fecha_economica,nodo_origen) VALUES(e,s,pos.id,per,clas,CASE WHEN amount>0 THEN 'AUMENTO' ELSE 'DISMINUCION' END,abs(amount),aid,opid,coalesce((j->>'fecha_reconocimiento')::date,current_date),n);
 END LOOP;
 END IF;
 UPDATE bovi.gasto_operacion SET estado='APROBADO',aprobado_por=a,aprobado_en=now(),periodo_id=per,fecha_reconocimiento=coalesce((j->>'fecha_reconocimiento')::date,current_date) WHERE (empresa_id,sucursal_id,id)=(e,s,gasto.id); idn:=gasto.id;
 WHEN 'registrar_movimiento','registrar_baja' THEN
 IF j ? 'motivo_baja' THEN j:=j||jsonb_build_object('motivo',j->>'motivo_baja'); END IF;
 ids:=ARRAY(SELECT (value#>>'{}')::uuid FROM jsonb_array_elements(coalesce(j->'posiciones',jsonb_build_array(j->'posicion_id'))) ORDER BY value#>>'{}');
 IF cardinality(ids)=0 THEN RAISE EXCEPTION 'Seleccione posiciones' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV026','regla_id','RN-020','campos',jsonb_build_array(jsonb_build_object('campo','posiciones','problema','invalido')))::text; END IF;
 FOR pid IN SELECT unnest(ids) LOOP
 idn:=uuidv7();
 IF p_comando='registrar_baja' OR j->>'tipo'='BAJA' THEN PERFORM bovi.fn_scope(e,s,a,'ADMIN'); per:=bovi.fn_periodo_payload(e,s,j); END IF;
 SELECT * INTO pos FROM bovi.posicion_inventario WHERE (empresa_id,sucursal_id,id)=(e,s,pid) FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Posición inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Posición inexistente','codigo','BV026','regla_id','RN-020','campos','[]'::jsonb)::text; END IF;
 nature:=coalesce(j->>'tipo',CASE WHEN p_comando='registrar_baja' THEN 'BAJA' END); opid:=coalesce((j->>'operacion_id')::uuid,pos.compra_operacion_id);
 IF nature='RECEPCION' THEN
 IF pos.estado<>'PENDIENTE_RECEPCION' THEN RAISE EXCEPTION 'Recepción inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Recepción inválida','codigo','BV026','regla_id','RN-020','campos','[]'::jsonb)::text; END IF;
 UPDATE bovi.posicion_inventario SET estado='DISPONIBLE' WHERE (empresa_id,sucursal_id,id)=(e,s,pid);
 ELSIF nature='ENTREGA' THEN
 IF pos.estado<>'VENDIDA_PENDIENTE_ENTREGA' OR NOT EXISTS(SELECT 1 FROM bovi.seleccion_venta v JOIN bovi.operacion o ON (o.empresa_id,o.sucursal_id,o.id)=(v.empresa_id,v.sucursal_id,v.operacion_id) WHERE (v.empresa_id,v.sucursal_id,v.posicion_id,v.operacion_id)=(e,s,pid,opid) AND o.estado='CONFIRMADA') THEN RAISE EXCEPTION 'Entrega inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Entrega inválida','codigo','BV026','regla_id','RN-020','campos','[]'::jsonb)::text; END IF;
 UPDATE bovi.posicion_inventario SET estado='CERRADA_VENTA',cerrada_en=now() WHERE (empresa_id,sucursal_id,id)=(e,s,pid);
 ELSIF nature='BAJA' THEN
 IF pos.estado NOT IN ('DISPONIBLE','PENDIENTE_RECEPCION') OR j->>'motivo' NOT IN ('PERDIDA','MUERTE') OR NOT EXISTS(SELECT 1 FROM bovi.documento WHERE (empresa_id,sucursal_id,id)=(e,s,(j->>'documento_id')::uuid)) OR EXISTS(SELECT 1 FROM bovi.reserva_venta WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pid) AND estado='ACTIVA' AND vence_en>now()) THEN RAISE EXCEPTION 'Baja requiere evidencia y posición libre' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Baja requiere evidencia y posición libre','codigo','BV024','regla_id','RN-038','campos','[]'::jsonb)::text; END IF;
 SELECT sum(delta_inventario) INTO cost FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,posicion_id)=(e,s,pid);
 INSERT INTO bovi.asiento_valoracion(empresa_id,sucursal_id,posicion_id,periodo_id,clase,sentido,importe,operacion_id,fecha_economica,nodo_origen) VALUES(e,s,pid,per,'BAJA','AUMENTO',cost,opid,coalesce((j->>'fecha_reconocimiento')::date,current_date),n);
 UPDATE bovi.posicion_inventario SET estado='BAJA',motivo_baja=j->>'motivo',cerrada_en=now() WHERE (empresa_id,sucursal_id,id)=(e,s,pid);
 IF j->>'motivo'='MUERTE' THEN
 IF n='A' THEN UPDATE bovi.animal SET situacion='MUERTO' WHERE empresa_id=e AND id=pos.animal_id;
 ELSE INSERT INTO bovi.evento_outbox(empresa_id,sucursal_id,tipo_evento,version_payload,payload,nodo_origen,propietario_despacho) VALUES(e,s,'ANIMAL_MUERTO',1,jsonb_build_object('animal_id',pos.animal_id,'posicion_id',pid,'documento_id',j->>'documento_id'),n,n); END IF;
 END IF;
 ELSE RAISE EXCEPTION 'Tipo movimiento inválido' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Tipo movimiento inválido','codigo','BV026','regla_id','RN-020','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.movimiento_inventario(empresa_id,sucursal_id,id,posicion_id,operacion_id,tipo,ocurrido_en,predio_id,custodio_parte_id,documento_id,registrado_por,nodo_origen) VALUES(e,s,idn,pid,opid,nature,coalesce((j->>'ocurrido_en')::timestamptz,now()),(j->>'predio_id')::uuid,(j->>'custodio_parte_id')::uuid,(j->>'documento_id')::uuid,a,n);
 UPDATE bovi.operacion SET estado_entrega=CASE WHEN NOT EXISTS(SELECT 1 FROM bovi.seleccion_venta v JOIN bovi.posicion_inventario p ON (p.empresa_id,p.sucursal_id,p.id)=(v.empresa_id,v.sucursal_id,v.posicion_id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id)=(e,s,opid) AND p.estado<>'CERRADA_VENTA') THEN 'COMPLETA' ELSE 'PARCIAL' END WHERE (empresa_id,sucursal_id,id)=(e,s,opid) AND tipo='VENTA';
 END LOOP; result:=jsonb_build_object('id',idn,'posiciones',to_jsonb(ids));
 WHEN 'crear_periodo' THEN
 PERFORM bovi.fn_scope(e,s,a,'ADMIN');
 PERFORM pg_advisory_xact_lock(hashtextextended(e::text||s::text,0));
 IF EXISTS(SELECT 1 FROM bovi.periodo_cierre WHERE empresa_id=e AND sucursal_id=s AND estado='ABIERTO') THEN RAISE EXCEPTION 'Sólo un periodo abierto' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV025','regla_id','RN-039','campos','[]'::jsonb)::text; END IF;
 f:=coalesce((j->>'desde')::date,(j->>'fecha_inicio')::date);
 IF f IS NULL OR f<>date_trunc('month',f)::date OR coalesce((j->>'hasta')::date,(j->>'fecha_fin')::date) IS DISTINCT FROM (f+interval '1 month'-interval '1 day')::date OR EXISTS(SELECT 1 FROM bovi.periodo_cierre WHERE empresa_id=e AND sucursal_id=s HAVING max(hasta)+1<>f) THEN RAISE EXCEPTION 'Periodo debe ser mes calendario consecutivo' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV025','regla_id','RN-039','campos',jsonb_build_array(jsonb_build_object('campo','desde','problema','invalido'),jsonb_build_object('campo','hasta','problema','invalido')))::text; END IF;
 INSERT INTO bovi.periodo_cierre(empresa_id,sucursal_id,id,desde,hasta,estado,nodo_origen) VALUES(e,s,idn,f,(f+interval '1 month'-interval '1 day')::date,'ABIERTO',n);
 WHEN 'cerrar_periodo','reabrir_periodo' THEN
 pid:=coalesce((j->>'periodo_id')::uuid,(j->>'id')::uuid);
 SELECT * INTO r FROM bovi.periodo_cierre WHERE (empresa_id,sucursal_id,id)=(e,s,pid) FOR UPDATE;
 IF NOT FOUND OR (p_comando='cerrar_periodo' AND r.estado<>'ABIERTO') OR (p_comando='reabrir_periodo' AND r.estado<>'CERRADO') THEN RAISE EXCEPTION 'Estado de periodo inválido' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Estado de periodo inválido','codigo','BV025','regla_id','RN-039','campos','[]'::jsonb)::text; END IF;
 IF p_comando='reabrir_periodo' AND EXISTS(SELECT 1 FROM bovi.periodo_cierre WHERE empresa_id=e AND sucursal_id=s AND (estado='ABIERTO' OR desde>r.desde)) THEN RAISE EXCEPTION 'Reabrir primero periodos posteriores' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Reabrir primero periodos posteriores','codigo','BV025','regla_id','RN-039','campos','[]'::jsonb)::text; END IF;
 result:=jsonb_build_object('inventario',coalesce((SELECT sum(delta_inventario) FROM bovi.asiento_valoracion WHERE empresa_id=e AND sucursal_id=s AND fecha_economica<=r.hasta),0)::text,'costo_venta',coalesce((SELECT sum(delta_costo_venta) FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,periodo_id)=(e,s,pid)),0)::text,'perdida',coalesce((SELECT sum(delta_perdida) FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,periodo_id)=(e,s,pid)),0)::text,'cartera',coalesce((SELECT sum(saldo) FROM bovi.v_saldo_liquidacion WHERE empresa_id=e AND sucursal_id=s),0)::text);
 SELECT coalesce(max(numero_version),0)+1 INTO seqn FROM bovi.cierre_periodo_version WHERE (empresa_id,sucursal_id,periodo_id)=(e,s,pid);
 INSERT INTO bovi.cierre_periodo_version VALUES(e,s,pid,seqn,CASE WHEN p_comando='cerrar_periodo' THEN 'CIERRE' ELSE 'REAPERTURA' END,a,j->>'motivo',now(),encode(public.digest(result::text,'sha256'),'hex'),result,n);
 UPDATE bovi.periodo_cierre SET estado=CASE WHEN p_comando='cerrar_periodo' THEN 'CERRADO' ELSE 'ABIERTO' END,version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,pid); idn:=pid; result:=jsonb_build_object('id',pid,'numero_version',seqn,'totales',result);
 WHEN 'registrar_documento' THEN
 IF j ? 'documento_previo_id' AND NOT EXISTS(SELECT 1 FROM bovi.documento d WHERE (d.empresa_id,d.sucursal_id,d.id)=(e,s,(j->>'documento_previo_id')::uuid) AND d.version+1=(j->>'version')::integer) THEN RAISE EXCEPTION 'Versión documental inválida' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-037','campos',jsonb_build_array(jsonb_build_object('campo','version','problema','invalido')))::text; END IF;
 INSERT INTO bovi.documento(empresa_id,sucursal_id,id,tipo_documental,clave_almacenamiento,sha256,tamano_bytes,mime,version,documento_previo_id,emisor,folio,fecha_emision,vigente_hasta,origen_texto,destino_texto,finalidad,es_sintetico,nodo_origen,subido_por) VALUES(e,s,idn,j->>'tipo_documental',coalesce(j->>'clave_almacenamiento',j->>'storage_key'),j->>'sha256',(j->>'tamano_bytes')::bigint,j->>'mime',coalesce((j->>'version')::smallint,1),(j->>'documento_previo_id')::uuid,j->>'emisor',j->>'folio',(j->>'fecha_emision')::date,(j->>'vigente_hasta')::date,j->>'origen_texto',j->>'destino_texto',j->>'finalidad',coalesce((j->>'es_sintetico')::boolean,true),n,a);
 IF opid IS NOT NULL THEN INSERT INTO bovi.operacion_documento VALUES(e,s,opid,idn,'EVIDENCIA',n); END IF;
 SELECT to_jsonb(d)-'clave_almacenamiento' INTO result FROM bovi.documento d WHERE (d.empresa_id,d.sucursal_id,d.id)=(e,s,idn);
 WHEN 'registrar_revision' THEN
 INSERT INTO bovi.revision_administrativa(empresa_id,sucursal_id,id,operacion_id,identificacion_id,criterio,resultado,revision_anterior_id,responsable_id,revisado_en,nodo_origen) VALUES(e,s,idn,opid,(j->>'identificacion_id')::uuid,j->>'criterio',j->>'resultado',(j->>'revision_anterior_id')::uuid,a,now(),n);
 FOR x IN SELECT value FROM jsonb_array_elements(coalesce(j->'documentos','[]')) LOOP INSERT INTO bovi.revision_documento VALUES(e,s,idn,(x->>'documento_id')::uuid,x->>'resultado',x->>'observacion',n); END LOOP;
 WHEN 'cancelar_operacion' THEN
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF op.estado NOT IN ('BORRADOR','ACORDADA') THEN RAISE EXCEPTION 'Sólo borrador cancelable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Sólo borrador cancelable','codigo','BV016','regla_id','RN-023','campos','[]'::jsonb)::text; END IF;
 UPDATE bovi.reserva_venta SET estado='LIBERADA',cerrada_en=now() WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) AND estado='ACTIVA';
 UPDATE bovi.operacion SET estado='CANCELADA',version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid); idn:=opid;
 WHEN 'anular_venta' THEN
 per:=bovi.fn_periodo_payload(e,s,j);
 SELECT * INTO op FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,opid) FOR UPDATE;
 IF op.tipo<>'VENTA' OR op.estado<>'CONFIRMADA' OR EXISTS(SELECT 1 FROM bovi.movimiento_inventario WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) AND tipo='ENTREGA') THEN RAISE EXCEPTION 'Venta no anulable' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Venta no anulable','codigo','BV026','regla_id','RN-020','campos','[]'::jsonb)::text; END IF;
 PERFORM 1 FROM bovi.posicion_inventario p JOIN bovi.seleccion_venta v ON (v.empresa_id,v.sucursal_id,v.posicion_id)=(p.empresa_id,p.sucursal_id,p.id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id)=(e,s,opid) ORDER BY p.id FOR UPDATE OF p;
 SELECT * INTO liq FROM bovi.liquidacion WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,opid) FOR UPDATE;
 SELECT total_ajustado,saldo INTO r FROM bovi.v_saldo_liquidacion WHERE (empresa_id,sucursal_id,id)=(e,s,liq.id);
 IF r.saldo<>r.total_ajustado THEN RAISE EXCEPTION 'Revierta aplicaciones antes de anular' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Revierta aplicaciones antes de anular','codigo','BV020','regla_id','RN-029','campos','[]'::jsonb)::text; END IF;
 FOR pos IN SELECT p.* FROM bovi.posicion_inventario p JOIN bovi.seleccion_venta v ON (v.empresa_id,v.sucursal_id,v.posicion_id)=(p.empresa_id,p.sucursal_id,p.id) WHERE (v.empresa_id,v.sucursal_id,v.operacion_id)=(e,s,opid) ORDER BY p.id FOR UPDATE OF p LOOP
 SELECT sum(delta_costo_venta) INTO cost FROM bovi.asiento_valoracion WHERE (empresa_id,sucursal_id,operacion_id,posicion_id)=(e,s,opid,pos.id);
 INSERT INTO bovi.asiento_valoracion(empresa_id,sucursal_id,posicion_id,periodo_id,clase,sentido,importe,operacion_id,fecha_economica,nodo_origen) VALUES(e,s,pos.id,per,'ANULACION_VENTA','AUMENTO',cost,opid,coalesce((j->>'fecha_reconocimiento')::date,current_date),n);
 UPDATE bovi.posicion_inventario SET estado='DISPONIBLE' WHERE (empresa_id,sucursal_id,id)=(e,s,pos.id);
 END LOOP;
 IF r.total_ajustado>0 THEN INSERT INTO bovi.ajuste_liquidacion(empresa_id,sucursal_id,liquidacion_id,naturaleza,monto,motivo,fuente,periodo_id,registrado_por,nodo_origen,fecha_reconocimiento) VALUES(e,s,liq.id,'ABONO',r.total_ajustado,j->>'motivo','ANULACION',per,a,n,coalesce((j->>'fecha_reconocimiento')::date,current_date)); END IF;
 UPDATE bovi.operacion SET estado='ANULADA',version_lock=version_lock+1 WHERE (empresa_id,sucursal_id,id)=(e,s,opid); idn:=opid;
 ELSE RAISE EXCEPTION 'Comando desconocido: %',p_comando USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Comando desconocido: %','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text;
 END CASE;
 result:=coalesce(result,jsonb_build_object('id',idn));
 INSERT INTO bovi.auditoria_evento(empresa_id,sucursal_id,actor_id,comando,correlation_id,nodo_origen,entidad,entidad_id,cambio) VALUES(e,s,a,p_comando,p_correlation,n,'comando',idn,result);
 INSERT INTO bovi.evento_outbox(empresa_id,sucursal_id,tipo_evento,version_payload,payload,nodo_origen,propietario_despacho) VALUES(e,s,p_comando,1,result,n,n);
 UPDATE bovi.clave_idempotencia SET estado='COMPLETADA',resultado=result WHERE (empresa_id,sucursal_id,principal_id,comando,clave)=(e,s,a,p_comando,p_clave);
 RETURN result;
END $$;
RESET ROLE;
