SET ROLE bovi_owner;
CREATE TABLE infra.spring_session (
	PRIMARY_ID CHAR(36) NOT NULL,
	SESSION_ID CHAR(36) NOT NULL,
	CREATION_TIME BIGINT NOT NULL,
	LAST_ACCESS_TIME BIGINT NOT NULL,
	MAX_INACTIVE_INTERVAL INT NOT NULL,
	EXPIRY_TIME BIGINT NOT NULL,
	PRINCIPAL_NAME VARCHAR(100),
	CONSTRAINT spring_session_PK PRIMARY KEY (PRIMARY_ID)
);

CREATE UNIQUE INDEX spring_session_IX1 ON infra.spring_session (SESSION_ID);
CREATE INDEX spring_session_IX2 ON infra.spring_session (EXPIRY_TIME);
CREATE INDEX spring_session_IX3 ON infra.spring_session (PRINCIPAL_NAME);

CREATE TABLE infra.spring_session_attributes (
	SESSION_PRIMARY_ID CHAR(36) NOT NULL,
	ATTRIBUTE_NAME VARCHAR(200) NOT NULL,
	ATTRIBUTE_BYTES BYTEA NOT NULL,
	CONSTRAINT spring_session_attributes_PK PRIMARY KEY (SESSION_PRIMARY_ID, ATTRIBUTE_NAME),
	CONSTRAINT spring_session_attributes_FK FOREIGN KEY (SESSION_PRIMARY_ID) REFERENCES infra.spring_session(PRIMARY_ID) ON DELETE CASCADE
);
CREATE FUNCTION bovi.fn_json_decimal(j jsonb) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE SET search_path = pg_catalog AS $$
DECLARE k text; v jsonb; result jsonb:='{}';
BEGIN
 FOR k,v IN SELECT * FROM jsonb_each(j) LOOP
 IF jsonb_typeof(v)='number' AND (k LIKE '%kg' OR k LIKE '%pct' OR k IN ('importe','total','total_ajustado','saldo','disponible','monto','precio_unitario','base_valor','cantidad','cargos_pactados','bonificaciones_pactadas','delta_inventario','delta_costo_venta','delta_perdida','venta_neta','costo_vendido','gastos_directos','margen','costo','inventario','perdida','precio_mxn','costo_vigente')) THEN
 IF k IN ('importe','total','total_ajustado','saldo','disponible','monto','cargos_pactados','bonificaciones_pactadas','delta_inventario','delta_costo_venta','delta_perdida','venta_neta','costo_vendido','gastos_directos','margen','costo','inventario','perdida','precio_mxn','costo_vigente') THEN v:=jsonb_build_object('importe',v#>>'{}','moneda','MXN'); ELSE v:=to_jsonb(v#>>'{}'); END IF; END IF;
 result:=result||jsonb_build_object(k,v);
 END LOOP;
 IF j ? 'neto_kg' THEN result:=result||jsonb_build_object('neto',jsonb_build_object('kg',j->>'neto_kg'),'bruto',CASE WHEN j->>'bruto_kg' IS NULL THEN NULL ELSE jsonb_build_object('kg',j->>'bruto_kg') END,'tara',CASE WHEN j->>'tara_kg' IS NULL THEN NULL ELSE jsonb_build_object('kg',j->>'tara_kg') END); END IF;
 RETURN result;
END $$;
CREATE FUNCTION bovi.fn_liquidacion_json(e uuid,s uuid,lid uuid) RETURNS jsonb LANGUAGE sql STABLE SET search_path = pg_catalog AS $$
SELECT bovi.fn_json_decimal(to_jsonb(l))||jsonb_build_object('parte_id',o.parte_id,'ajustes_cargo',jsonb_build_object('importe',coalesce((SELECT sum(monto) FROM bovi.ajuste_liquidacion WHERE (empresa_id,sucursal_id,liquidacion_id,naturaleza)=(e,s,lid,'CARGO')),0)::text,'moneda','MXN'),'ajustes_abono',jsonb_build_object('importe',coalesce((SELECT sum(monto) FROM bovi.ajuste_liquidacion WHERE (empresa_id,sucursal_id,liquidacion_id,naturaleza)=(e,s,lid,'ABONO')),0)::text,'moneda','MXN'),'aplicaciones_netas',jsonb_build_object('importe',(l.total_ajustado-l.saldo)::text,'moneda','MXN'),'conceptos',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(c))||jsonb_build_object('numero',c.numero_concepto)),'[]') FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(e,s,lid))) FROM bovi.v_saldo_liquidacion l JOIN bovi.operacion o ON (o.empresa_id,o.sucursal_id,o.id)=(l.empresa_id,l.sucursal_id,l.operacion_id) WHERE (l.empresa_id,l.sucursal_id,l.id)=(e,s,lid)
$$;
CREATE FUNCTION bovi.fn_validar_conciliacion_propietario(e uuid,s uuid,a uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE fk record; localcols text; joincols text; nonnull text; missing bigint; totalmissing bigint:=0; errors jsonb:='[]'; settlements bigint;
BEGIN
 PERFORM bovi.fn_scope(e,s,a,NULL);
 FOR fk IN SELECT c.conname,c.conrelid,c.confrelid,c.conkey,c.confkey FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE c.contype='f' AND n.nspname='bovi' LOOP
 SELECT string_agg(format('child.%I=parent.%I',ca.attname,pa.attname),' AND ' ORDER BY keys.ord),string_agg(format('child.%I IS NOT NULL',ca.attname),' AND ' ORDER BY keys.ord) INTO joincols,nonnull FROM unnest(fk.conkey,fk.confkey) WITH ORDINALITY keys(l,r,ord) JOIN pg_attribute ca ON ca.attrelid=fk.conrelid AND ca.attnum=keys.l JOIN pg_attribute pa ON pa.attrelid=fk.confrelid AND pa.attnum=keys.r;
 EXECUTE format('SELECT count(*) FROM %s child WHERE %s AND NOT EXISTS(SELECT 1 FROM %s parent WHERE %s)',fk.conrelid::regclass,nonnull,fk.confrelid::regclass,joincols) INTO missing;
 totalmissing:=totalmissing+missing;
 IF missing>0 THEN errors:=errors||jsonb_build_array(jsonb_build_object('restriccion',fk.conname,'huerfanos',missing)); END IF;
 END LOOP;
 SELECT count(*) INTO settlements FROM bovi.liquidacion l WHERE l.empresa_id=e AND l.sucursal_id=s AND l.total IS DISTINCT FROM (SELECT sum(importe) FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(l.empresa_id,l.sucursal_id,l.id));
 RETURN jsonb_build_object('nodo',bovi.fn_nodo(),'corte_en',now(),'huerfanos',totalmissing,'liquidaciones_desbalanceadas',settlements,'errores',errors,'inventario',coalesce((SELECT sum(delta_inventario) FROM bovi.asiento_valoracion WHERE empresa_id=e AND sucursal_id=s),0)::text,'perdida',coalesce((SELECT sum(delta_perdida) FROM bovi.asiento_valoracion WHERE empresa_id=e AND sucursal_id=s),0)::text);
END $$;
CREATE FUNCTION bovi.consultar(e uuid,s uuid,a uuid,recurso text,params jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE tab text; filtro text:=''; sql text; rows jsonb; detail jsonb; totaln integer; size integer:=coalesce((params->>'tamano')::integer,25); page integer:=coalesce((params->>'pagina')::integer,1); idn uuid:=(params->>'id')::uuid;
BEGIN
 -- Lectura autorizada en propietario o maestros A; la conexión nunca toma empresa del navegador.
 IF NOT EXISTS(SELECT 1 FROM infra.nodo_config WHERE empresa_id=e) OR NOT EXISTS(SELECT 1 FROM bovi.membresia_usuario m JOIN bovi.usuario u ON u.empresa_id=m.empresa_id AND u.id=m.usuario_id WHERE m.empresa_id=e AND m.sucursal_id=s AND m.usuario_id=a AND m.vigente AND u.estado='ACTIVO') THEN RAISE EXCEPTION 'Permiso denegado' USING ERRCODE='42501'; END IF;
 IF size NOT BETWEEN 1 AND 100 OR page<1 THEN RAISE EXCEPTION 'Paginación inválida' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Paginación inválida','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 CASE recurso
 WHEN 'conciliacion' THEN RETURN bovi.fn_validar_conciliacion_propietario(e,s,a);
 WHEN 'comparacion_pesajes' THEN
 SELECT bovi.fn_json_decimal(to_jsonb(p)) INTO detail FROM bovi.pesaje p WHERE (empresa_id,sucursal_id,id)=(e,s,(params->>'inicial_id')::uuid) AND estado IN ('APROBADO','CORREGIDO');
 SELECT bovi.fn_json_decimal(to_jsonb(p)) INTO rows FROM bovi.pesaje p WHERE (empresa_id,sucursal_id,id)=(e,s,(params->>'final_id')::uuid) AND estado IN ('APROBADO','CORREGIDO');
 IF detail IS NULL OR rows IS NULL THEN RAISE EXCEPTION 'Pesajes no aprobados o inexistentes' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV013','regla_id','RN-014','campos','[]'::jsonb)::text; END IF;
 IF EXISTS((SELECT animal_id FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,(params->>'inicial_id')::uuid) EXCEPT SELECT animal_id FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,(params->>'final_id')::uuid)) UNION (SELECT animal_id FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,(params->>'final_id')::uuid) EXCEPT SELECT animal_id FROM bovi.pesaje_animal WHERE (empresa_id,sucursal_id,pesaje_id)=(e,s,(params->>'inicial_id')::uuid))) THEN RETURN jsonb_build_object('estado','NO_COMPARABLE','motivo','La composición de animales difiere','peso_inicial_kg',detail->>'neto_kg','peso_final_kg',rows->>'neto_kg'); END IF;
 RETURN jsonb_build_object('estado','COMPARABLE','peso_inicial_kg',detail->>'neto_kg','peso_final_kg',rows->>'neto_kg','variacion_kg',((detail->>'neto_kg')::numeric-(rows->>'neto_kg')::numeric)::text,'variacion_pct',round(100*((detail->>'neto_kg')::numeric-(rows->>'neto_kg')::numeric)/(detail->>'neto_kg')::numeric,6)::text);
 WHEN 'comando' THEN
 SELECT jsonb_build_object('estado',estado,'resultado',resultado) INTO detail FROM bovi.clave_idempotencia WHERE empresa_id=e AND sucursal_id=s AND principal_id=a AND comando=params->>'comando' AND clave=params->>'clave';
 IF detail IS NULL THEN RAISE EXCEPTION 'Comando no encontrado' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV404','regla_id','RN-032','campos','[]'::jsonb)::text; END IF; RETURN detail;
 WHEN 'contrapartes' THEN tab:='parte';
 WHEN 'predios' THEN tab:='predio';
 WHEN 'animales','animal' THEN tab:='animal'; filtro:=' AND t.sede_operadora_id=$2';
 WHEN 'usuarios' THEN
 IF NOT EXISTS(SELECT 1 FROM bovi.membresia_usuario WHERE (empresa_id,sucursal_id,usuario_id,rol_codigo)=(e,s,a,'ADMIN') AND vigente) THEN RAISE EXCEPTION 'Permiso denegado' USING ERRCODE='42501'; END IF;
 tab:='usuario'; filtro:=' AND EXISTS(SELECT 1 FROM bovi.membresia_usuario m WHERE (m.empresa_id,m.sucursal_id,m.usuario_id)=(t.empresa_id,$2,t.id) AND m.vigente)';
 WHEN 'operaciones','operacion' THEN tab:='operacion';
 WHEN 'inventario_posiciones','reportes_inventario' THEN tab:='posicion_inventario';
 WHEN 'pagos','pago' THEN tab:='v_disponible_pago';
 WHEN 'gastos' THEN tab:='gasto_operacion';
 WHEN 'reparto_gasto' THEN RETURN jsonb_build_object('gasto_id',idn,'metodo',coalesce(params->>'metodo','POR_CABEZA'),'elementos',(SELECT jsonb_agg(bovi.fn_json_decimal(to_jsonb(r))) FROM bovi.fn_reparto(e,s,idn,coalesce(params->>'metodo','POR_CABEZA'),params->'asignaciones') r));
 WHEN 'periodo_versiones' THEN RETURN jsonb_build_object('elementos',(SELECT coalesce(jsonb_agg(to_jsonb(v) ORDER BY numero_version),'[]') FROM bovi.cierre_periodo_version v WHERE (v.empresa_id,v.sucursal_id,v.periodo_id)=(e,s,idn)));
 WHEN 'liquidaciones','liquidacion','reportes_cartera' THEN tab:='v_saldo_liquidacion';
 WHEN 'periodos' THEN tab:='periodo_cierre';
 WHEN 'documentos','documento' THEN tab:='documento';
 WHEN 'reportes_margen' THEN tab:='v_margen_operacion';
 WHEN 'auditoria' THEN tab:='auditoria_evento';
 WHEN 'operacion_pesajes' THEN tab:='pesaje'; filtro:=' AND t.operacion_id=$3'; idn:=NULL;
 WHEN 'operacion_expediente' THEN
 IF NOT EXISTS(SELECT 1 FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,idn)) THEN RAISE EXCEPTION 'Operación inexistente' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV404','regla_id','RN-001','campos','[]'::jsonb)::text; END IF;
 RETURN jsonb_build_object('operacion_id',idn,'eventos',(SELECT coalesce(jsonb_agg(to_jsonb(h) ORDER BY ocurrido_en),'[]') FROM(SELECT p.id,p.ocurrido_en,p.tipo,p.tipo::text AS descripcion FROM bovi.movimiento_inventario p WHERE (p.empresa_id,p.sucursal_id,p.operacion_id)=(e,s,idn) UNION ALL SELECT w.id,w.pesado_en,'PESAJE',w.estado::text FROM bovi.pesaje w WHERE (w.empresa_id,w.sucursal_id,w.operacion_id)=(e,s,idn) UNION ALL SELECT l.id,l.confirmada_en,'CONFIRMACION',l.direccion::text FROM bovi.liquidacion l WHERE (l.empresa_id,l.sucursal_id,l.operacion_id)=(e,s,idn))h),'documentos',(SELECT coalesce(jsonb_agg(to_jsonb(d)-'clave_almacenamiento'),'[]') FROM bovi.documento d JOIN bovi.operacion_documento link ON (link.empresa_id,link.sucursal_id,link.documento_id)=(d.empresa_id,d.sucursal_id,d.id) WHERE (link.empresa_id,link.sucursal_id,link.operacion_id)=(e,s,idn)));

 WHEN 'sincronizacion' THEN
 RETURN jsonb_build_object('nodo',bovi.fn_nodo(),'estado','ASINCRONA','corte',now(),'ultima_sincronizacion',(SELECT max(latest_end_time) FROM pg_stat_subscription),'avisos','Replicación asíncrona; la antigüedad por stream no garantiza disponibilidad del propietario','pendientes',(SELECT count(*) FROM bovi.evento_outbox e1 LEFT JOIN infra.entrega_outbox d ON d.evento_id=e1.id AND d.destino='LOCAL' WHERE e1.empresa_id=e AND e1.sucursal_id=s AND e1.propietario_despacho=bovi.fn_nodo() AND d.confirmado_en IS NULL),'fallos_apply',(SELECT coalesce(sum(apply_error_count),0) FROM pg_stat_subscription_stats));
 WHEN 'simulador' THEN
 RETURN (SELECT jsonb_build_object('operacion_id',params->>'id','total',jsonb_build_object('importe',sum(total)::text,'moneda','MXN'),'lotes',jsonb_agg(bovi.fn_json_decimal(to_jsonb(q))),'conceptos',jsonb_agg(jsonb_build_object('tipo','BASE','cantidad',q.cantidad::text,'unidad',q.unidad,'precio_unitario',q.precio::text,'importe',jsonb_build_object('importe',q.base::text,'moneda','MXN')))) FROM bovi.fn_calcular_liquidacion(e,s,(params->>'id')::uuid) q);
 ELSE RAISE EXCEPTION 'Recurso desconocido' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Recurso desconocido','codigo','BV015','regla_id','RN-017','campos','[]'::jsonb)::text;
 END CASE;
 IF tab NOT IN ('parte','predio','animal','usuario') THEN filtro:=' AND t.sucursal_id=$2'||filtro; END IF;
 IF idn IS NOT NULL AND tab<>'v_margen_operacion' THEN filtro:=filtro||' AND t.id=$3'; END IF;
 IF params ? 'operacion_id' AND tab IN ('gasto_operacion','pesaje','v_saldo_liquidacion') THEN filtro:=filtro||' AND t.operacion_id='||quote_literal(params->>'operacion_id')||'::uuid'; END IF;
 sql:=format('SELECT count(*) FROM bovi.%I t WHERE t.empresa_id=$1 %s',tab,filtro);
 EXECUTE sql INTO totaln USING e,s,coalesce(idn,(params->>'id')::uuid);
 sql:=format('SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(q))%s),''[]''::jsonb) FROM (SELECT t.*%s FROM bovi.%I t WHERE t.empresa_id=$1 %s ORDER BY %s LIMIT $4 OFFSET $5) q',CASE WHEN tab='usuario' THEN '-''hash_contrasena''' ELSE '' END,CASE WHEN tab='v_margen_operacion' THEN ', t.venta_neta-t.costo_vendido-t.gastos_directos AS margen' WHEN tab='documento' THEN ',t.clave_almacenamiento AS storage_key' WHEN tab='usuario' THEN ',t.login_normalizado AS login,(t.estado=''ACTIVO'') AS activo,(SELECT jsonb_agg(rol_codigo) FROM bovi.membresia_usuario m WHERE (m.empresa_id,m.sucursal_id,m.usuario_id)=(t.empresa_id,$2,t.id) AND vigente) AS roles' WHEN tab='v_saldo_liquidacion' THEN ',(SELECT parte_id FROM bovi.operacion o WHERE (o.empresa_id,o.sucursal_id,o.id)=(t.empresa_id,t.sucursal_id,t.operacion_id)) AS parte_id' WHEN tab='operacion' THEN ',(SELECT nombre FROM bovi.parte p WHERE (p.empresa_id,p.id)=(t.empresa_id,t.parte_id)) AS contraparte' WHEN tab='posicion_inventario' THEN ', EXISTS(SELECT 1 FROM bovi.reserva_venta r WHERE (r.empresa_id,r.sucursal_id,r.posicion_id)=(t.empresa_id,t.sucursal_id,t.id) AND estado=''ACTIVA'' AND vence_en>now()) AS reservada,(SELECT coalesce(sum(importe),0) FROM bovi.asignacion_costo c WHERE (c.empresa_id,c.sucursal_id,c.posicion_id)=(t.empresa_id,t.sucursal_id,t.id)) AS costo_vigente' ELSE '' END,tab,filtro,CASE WHEN tab='v_margen_operacion' THEN 't.operacion_id' ELSE 't.id' END);
 EXECUTE sql INTO rows USING e,s,coalesce(idn,(params->>'id')::uuid),size,(page-1)*size;
 IF recurso IN ('animal','operacion','liquidacion','pago','documento') THEN
 detail:=rows->0; IF detail IS NULL THEN RAISE EXCEPTION 'Recurso inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Recurso inexistente','codigo','BV404','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 IF recurso='documento' THEN detail:=detail||jsonb_build_object('revisiones',(SELECT coalesce(jsonb_agg(to_jsonb(r)),'[]') FROM bovi.revision_documento r WHERE (r.empresa_id,r.sucursal_id,r.documento_id)=(e,s,idn))); END IF;
 IF recurso='animal' THEN detail:=detail||jsonb_build_object('identificaciones',(SELECT coalesce(jsonb_agg(to_jsonb(i)),'[]') FROM bovi.animal_identificacion i WHERE i.empresa_id=e AND i.animal_id=idn)); END IF;
 IF recurso='operacion' THEN detail:=detail||jsonb_build_object('numero_version_actual',(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)),'contratos',(SELECT jsonb_agg(to_jsonb(cv) ORDER BY numero_version) FROM bovi.contrato_version cv WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)),'lotes',(SELECT coalesce(jsonb_agg(to_jsonb(l)||coalesce((SELECT bovi.fn_json_decimal(to_jsonb(c)) FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote,c.numero_version)=(e,s,idn,l.numero_lote,(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)))),'{}'::jsonb)||jsonb_build_object('animales',(SELECT coalesce(jsonb_agg(animal_id),'[]') FROM bovi.seleccion_compra sc WHERE (sc.empresa_id,sc.sucursal_id,sc.operacion_id,sc.numero_lote)=(e,s,idn,l.numero_lote)),'posiciones',(SELECT coalesce(jsonb_agg(posicion_id),'[]') FROM bovi.seleccion_venta sv WHERE (sv.empresa_id,sv.sucursal_id,sv.operacion_id,sv.numero_lote)=(e,s,idn,l.numero_lote)),'condicion',(SELECT bovi.fn_json_decimal(to_jsonb(c)) FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote,c.numero_version)=(e,s,idn,l.numero_lote,(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)))))),'[]') FROM bovi.lote_operacion l WHERE (l.empresa_id,l.sucursal_id,l.operacion_id)=(e,s,idn)),'pesajes',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(p))),'[]') FROM bovi.pesaje p WHERE (p.empresa_id,p.sucursal_id,p.operacion_id)=(e,s,idn)),'liquidacion',(SELECT bovi.fn_json_decimal(to_jsonb(l)) FROM bovi.v_saldo_liquidacion l WHERE (l.empresa_id,l.sucursal_id,l.operacion_id)=(e,s,idn))); END IF;
 IF recurso='liquidacion' THEN detail:=bovi.fn_liquidacion_json(e,s,idn)||jsonb_build_object('conceptos',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(c))),'[]') FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(e,s,idn)),'aplicaciones',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(c))),'[]') FROM bovi.aplicacion_pago c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(e,s,idn)),'parte_id',(SELECT parte_id FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,(detail->>'operacion_id')::uuid))); END IF;
 RETURN detail;
 END IF;
 RETURN jsonb_build_object('elementos',rows,'pagina',page,'tamano',size,'total',totaln,'corte',now());
END $$;
CREATE FUNCTION bovi.despachar_outbox(p_limite integer DEFAULT 50) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE r record; cnt integer:=0;
BEGIN
 FOR r IN SELECT e.* FROM bovi.evento_outbox e LEFT JOIN infra.entrega_outbox d ON d.evento_id=e.id AND d.destino='LOCAL' WHERE e.propietario_despacho=bovi.fn_nodo() AND e.tipo_evento<>'ANIMAL_MUERTO' AND d.confirmado_en IS NULL ORDER BY e.creado_en LIMIT least(p_limite,100) FOR UPDATE OF e SKIP LOCKED LOOP
 INSERT INTO bovi.mensaje_inbox VALUES('DEMO_LOCAL',r.nodo_origen,r.id,r.empresa_id,r.sucursal_id,now(),'APLICADO') ON CONFLICT DO NOTHING;
 INSERT INTO infra.entrega_outbox(evento_id,destino,intentos,proximo_intento,confirmado_en,ultimo_error) VALUES(r.id,'LOCAL',1,NULL,now(),NULL) ON CONFLICT(evento_id,destino) DO UPDATE SET intentos=infra.entrega_outbox.intentos+1,confirmado_en=now(); cnt:=cnt+1;
 END LOOP; RETURN jsonb_build_object('procesados',cnt);
END $$;
CREATE FUNCTION bovi.consumir_muerte(e uuid,s uuid,eventid uuid,payload jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
 IF bovi.fn_nodo()<>'A' OR NOT EXISTS(SELECT 1 FROM infra.nodo_config WHERE empresa_id=e) THEN RAISE EXCEPTION 'Consumidor central sólo A' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Consumidor central sólo A','codigo','BV501','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 IF NOT EXISTS(SELECT 1 FROM bovi.evento_outbox WHERE empresa_id=e AND sucursal_id=s AND id=eventid AND tipo_evento='ANIMAL_MUERTO' AND nodo_origen='B' AND evento_outbox.payload=consumir_muerte.payload) THEN RAISE EXCEPTION 'Evento remoto todavía no converge o inválido' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Evento remoto todavía no converge o inválido','codigo','BV404','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.mensaje_inbox VALUES('IDENTIDAD_CENTRAL','B',eventid,e,s,now(),'APLICADO') ON CONFLICT DO NOTHING;
 IF FOUND THEN UPDATE bovi.animal SET situacion='MUERTO' WHERE empresa_id=e AND sede_operadora_id=s AND id=(payload->>'animal_id')::uuid; IF NOT FOUND THEN RAISE EXCEPTION 'Identidad inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Identidad inexistente','codigo','BV011','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 INSERT INTO bovi.auditoria_evento(empresa_id,sucursal_id,actor_id,comando,correlation_id,nodo_origen,entidad,entidad_id,cambio) VALUES(e,s,NULL,'consumir_muerte',eventid,'A','animal',(payload->>'animal_id')::uuid,jsonb_build_object('situacion','MUERTO','evento_origen',eventid));
 END IF;
 RETURN jsonb_build_object('event_id',eventid,'estado','APLICADO');
END $$;
CREATE FUNCTION bovi.reclamar_entregas(p_worker uuid,p_limite integer DEFAULT 50) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE r record; claimed jsonb:='[]';
BEGIN
 IF p_worker IS NULL OR p_limite NOT BETWEEN 1 AND 100 THEN RAISE EXCEPTION 'Lease inválida' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-044','campos','[]'::jsonb)::text; END IF;
 FOR r IN SELECT e.* FROM bovi.evento_outbox e LEFT JOIN infra.entrega_outbox d ON (d.evento_id,d.destino)=(e.id,'A') WHERE e.propietario_despacho=bovi.fn_nodo() AND e.tipo_evento='ANIMAL_MUERTO' AND d.confirmado_en IS NULL AND (d.lease_vence_en IS NULL OR d.lease_vence_en<=now()) AND (d.proximo_intento IS NULL OR d.proximo_intento<=now()) ORDER BY e.creado_en,e.id LIMIT p_limite FOR UPDATE OF e SKIP LOCKED LOOP
 INSERT INTO infra.entrega_outbox(evento_id,destino,intentos,lease_token,lease_vence_en) VALUES(r.id,'A',1,p_worker,now()+interval '30 seconds') ON CONFLICT(evento_id,destino) DO UPDATE SET intentos=infra.entrega_outbox.intentos+1,lease_token=p_worker,lease_vence_en=now()+interval '30 seconds',ultimo_error=NULL;
 claimed:=claimed||jsonb_build_array(jsonb_build_object('id',r.id,'empresa_id',r.empresa_id,'sucursal_id',r.sucursal_id,'payload',r.payload,'lease_token',p_worker));
 END LOOP;RETURN claimed;
END $$;
CREATE FUNCTION bovi.confirmar_entrega(eventid uuid,worker uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
 UPDATE infra.entrega_outbox SET confirmado_en=now(),lease_token=NULL,lease_vence_en=NULL WHERE evento_id=eventid AND destino='A' AND lease_token=worker AND lease_vence_en>now();
 IF NOT FOUND THEN RAISE EXCEPTION 'Lease vencida o ajena' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV402','regla_id','RN-044','campos','[]'::jsonb)::text; END IF;
END $$;
CREATE FUNCTION bovi.fallar_entrega(eventid uuid,worker uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
 UPDATE infra.entrega_outbox SET proximo_intento=now()+least(interval '5 minutes',interval '5 seconds'*intentos),ultimo_error='Destino no disponible; reintento pendiente',lease_token=NULL,lease_vence_en=NULL WHERE evento_id=eventid AND destino='A' AND lease_token=worker;
 IF NOT FOUND THEN RAISE EXCEPTION 'Lease ajena' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV402','regla_id','RN-044','campos','[]'::jsonb)::text; END IF;
END $$;
CREATE FUNCTION bovi.archivo_referenciado(p_sha256 text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM bovi.documento d JOIN infra.nodo_config c ON c.empresa_id=d.empresa_id WHERE d.sha256=p_sha256)
$$;
RESET ROLE;
GRANT USAGE ON SCHEMA bovi,infra TO bovi_command,bovi_app_a,bovi_app_b,bovi_auth,bovi_auditor,bovi_repl,bovi_worker;
GRANT USAGE ON SCHEMA public TO bovi_command;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA bovi,infra TO bovi_command;
GRANT SELECT ON ALL TABLES IN SCHEMA bovi TO bovi_app_a,bovi_app_b,bovi_auditor,bovi_repl;
REVOKE SELECT ON bovi.usuario FROM bovi_app_a,bovi_app_b,bovi_auditor,bovi_repl;
GRANT SELECT(empresa_id,id,login_normalizado,nombre,estado,nodo_origen,creado_en) ON bovi.usuario TO bovi_app_a,bovi_app_b,bovi_auditor;
GRANT SELECT ON bovi.usuario TO bovi_repl;
GRANT SELECT ON infra.nodo_config TO bovi_app_a,bovi_app_b,bovi_auth,bovi_auditor,bovi_worker;
GRANT SELECT ON bovi.usuario,bovi.membresia_usuario,bovi.sucursal TO bovi_auth;
GRANT SELECT,INSERT,UPDATE,DELETE ON infra.spring_session,infra.spring_session_attributes TO bovi_auth;
GRANT SELECT ON bovi.evento_outbox,infra.entrega_outbox TO bovi_worker;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA bovi FROM PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA bovi TO bovi_command;
GRANT EXECUTE ON FUNCTION bovi.cmd_ejecutar(uuid,uuid,uuid,text,text,uuid,text,jsonb),bovi.consultar(uuid,uuid,uuid,text,jsonb) TO bovi_app_a,bovi_app_b;
GRANT EXECUTE ON FUNCTION bovi.fn_nodo() TO bovi_app_a,bovi_app_b,bovi_auditor,bovi_worker;
GRANT EXECUTE ON FUNCTION bovi.despachar_outbox(integer),bovi.consumir_muerte(uuid,uuid,uuid,jsonb),bovi.confirmar_entrega(uuid,uuid),bovi.fallar_entrega(uuid,uuid),bovi.reclamar_entregas(uuid,integer) TO bovi_worker;
DO $$ DECLARE r record; BEGIN
 FOR r IN SELECT p.oid::regprocedure AS fn FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='bovi' AND p.prosecdef LOOP EXECUTE format('ALTER FUNCTION %s OWNER TO bovi_command',r.fn); END LOOP;
END $$;
ALTER DEFAULT PRIVILEGES FOR ROLE bovi_owner IN SCHEMA bovi REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

GRANT EXECUTE ON FUNCTION bovi.archivo_referenciado(text) TO bovi_worker;

GRANT EXECUTE ON FUNCTION bovi.fn_validar_conciliacion_propietario(uuid,uuid,uuid) TO bovi_app_a,bovi_app_b,bovi_auditor;
