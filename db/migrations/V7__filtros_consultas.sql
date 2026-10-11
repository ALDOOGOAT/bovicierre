-- Búsqueda q literal parametrizada y filtros whitelist; mismo filtro para count y página.
CREATE OR REPLACE FUNCTION bovi.consultar(e uuid,s uuid,a uuid,recurso text,params jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE tab text; filtro text:=''; sql text; rows jsonb; detail jsonb; totaln integer; size integer:=coalesce((params->>'tamano')::integer,25); page integer:=coalesce((params->>'pagina')::integer,1); idn uuid:=(params->>'id')::uuid; searchq text:=nullif(btrim(params->>'q'),''); pattern text; statefilter text:=nullif(params->>'estado',''); typefilter text:=nullif(params->>'tipo','');
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
 WHEN 'gastos','gasto' THEN tab:='gasto_operacion';
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
 IF searchq IS NOT NULL THEN
 IF length(searchq)>200 THEN RAISE EXCEPTION 'Búsqueda demasiado larga' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-001','campos',jsonb_build_array(jsonb_build_object('campo','q','problema','invalido')))::text; END IF;
 pattern:='%'||replace(replace(replace(searchq,chr(92),chr(92)||chr(92)),'%',chr(92)||'%'),'_',chr(92)||'_')||'%';
 filtro:=filtro||' AND ('||CASE tab
 WHEN 'parte' THEN 't.id::text ILIKE $6 OR t.nombre ILIKE $6 OR t.rfc ILIKE $6'
 WHEN 'predio' THEN 't.id::text ILIKE $6 OR t.nombre ILIKE $6'
 WHEN 'usuario' THEN 't.id::text ILIKE $6 OR t.nombre ILIKE $6 OR t.login_normalizado ILIKE $6'
 WHEN 'operacion' THEN 't.id::text ILIKE $6 OR t.folio ILIKE $6 OR EXISTS(SELECT 1 FROM bovi.parte p WHERE (p.empresa_id,p.id)=(t.empresa_id,t.parte_id) AND p.nombre ILIKE $6)'
 WHEN 'animal' THEN 't.id::text ILIKE $6 OR EXISTS(SELECT 1 FROM bovi.animal_identificacion i WHERE (i.empresa_id,i.animal_id)=(t.empresa_id,t.id) AND (i.codigo_declarado ILIKE $6 OR i.codigo_normalizado ILIKE $6))'
 WHEN 'posicion_inventario' THEN 't.id::text ILIKE $6 OR t.animal_id::text ILIKE $6 OR EXISTS(SELECT 1 FROM bovi.animal_identificacion i WHERE (i.empresa_id,i.animal_id)=(t.empresa_id,t.animal_id) AND (i.codigo_declarado ILIKE $6 OR i.codigo_normalizado ILIKE $6))'
 WHEN 'v_disponible_pago' THEN 't.id::text ILIKE $6 OR t.referencia ILIKE $6 OR EXISTS(SELECT 1 FROM bovi.parte p WHERE (p.empresa_id,p.id)=(t.empresa_id,t.parte_id) AND p.nombre ILIKE $6)'
 WHEN 'v_saldo_liquidacion' THEN 't.id::text ILIKE $6 OR t.operacion_id::text ILIKE $6 OR t.snapshot_contraparte_nombre ILIKE $6'
 WHEN 'v_margen_operacion' THEN 't.operacion_id::text ILIKE $6 OR EXISTS(SELECT 1 FROM bovi.operacion o JOIN bovi.parte p ON (p.empresa_id,p.id)=(o.empresa_id,o.parte_id) WHERE (o.empresa_id,o.sucursal_id,o.id)=(t.empresa_id,t.sucursal_id,t.operacion_id) AND (o.folio ILIKE $6 OR p.nombre ILIKE $6))'
 WHEN 'gasto_operacion' THEN 't.id::text ILIKE $6 OR t.concepto ILIKE $6 OR t.referencia_origen ILIKE $6'
 WHEN 'documento' THEN 't.id::text ILIKE $6 OR t.folio ILIKE $6 OR t.emisor ILIKE $6 OR t.tipo_documental ILIKE $6'
 WHEN 'periodo_cierre' THEN 't.id::text ILIKE $6 OR t.desde::text ILIKE $6 OR t.hasta::text ILIKE $6'
 ELSE 't.id::text ILIKE $6' END||')';
 END IF;
 IF statefilter IS NOT NULL THEN
 IF tab NOT IN ('operacion','posicion_inventario','v_disponible_pago') OR statefilter NOT IN ('BORRADOR','ACORDADA','CONFIRMADA','CANCELADA','ANULADA','PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA','CERRADA_VENTA','BAJA','REGISTRADO','VALIDADO') THEN RAISE EXCEPTION 'Filtro estado no admitido' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-001','campos',jsonb_build_array(jsonb_build_object('campo','estado','problema','invalido')))::text; END IF;
 filtro:=filtro||' AND t.estado=$7';
 END IF;
 IF typefilter IS NOT NULL THEN
 IF (tab='operacion' AND typefilter IN ('COMPRA','VENTA')) OR (tab='v_disponible_pago' AND typefilter IN ('COBRO','PAGO')) THEN filtro:=filtro||' AND t.tipo=$8';
 ELSE RAISE EXCEPTION 'Filtro tipo no admitido' USING ERRCODE='P0001',DETAIL=jsonb_build_object('codigo','BV015','regla_id','RN-001','campos',jsonb_build_array(jsonb_build_object('campo','tipo','problema','invalido')))::text; END IF;
 END IF;
 IF tab NOT IN ('parte','predio','animal','usuario') THEN filtro:=' AND t.sucursal_id=$2'||filtro; END IF;
 IF idn IS NOT NULL AND tab<>'v_margen_operacion' THEN filtro:=filtro||' AND t.id=$3'; END IF;
 IF params ? 'operacion_id' AND tab IN ('gasto_operacion','pesaje','v_saldo_liquidacion') THEN filtro:=filtro||' AND t.operacion_id='||quote_literal((params->>'operacion_id')::uuid)||'::uuid'; END IF;
 sql:=format('SELECT count(*) FROM bovi.%I t WHERE t.empresa_id=$1 %s',tab,filtro);
 EXECUTE sql INTO totaln USING e,s,coalesce(idn,(params->>'id')::uuid),size,(page-1)*size,pattern,statefilter,typefilter;
 sql:=format('SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(q))%s),''[]''::jsonb) FROM (SELECT t.*%s FROM bovi.%I t WHERE t.empresa_id=$1 %s ORDER BY %s LIMIT $4 OFFSET $5) q',CASE WHEN tab='usuario' THEN '-''hash_contrasena''' ELSE '' END,CASE WHEN tab='v_margen_operacion' THEN ', t.venta_neta-t.costo_vendido-t.gastos_directos AS margen' WHEN tab='documento' THEN ',t.clave_almacenamiento AS storage_key' WHEN tab='usuario' THEN ',t.login_normalizado AS login,(t.estado=''ACTIVO'') AS activo,(SELECT jsonb_agg(rol_codigo) FROM bovi.membresia_usuario m WHERE (m.empresa_id,m.sucursal_id,m.usuario_id)=(t.empresa_id,$2,t.id) AND vigente) AS roles' WHEN tab='v_saldo_liquidacion' THEN ',(SELECT parte_id FROM bovi.operacion o WHERE (o.empresa_id,o.sucursal_id,o.id)=(t.empresa_id,t.sucursal_id,t.operacion_id)) AS parte_id' WHEN tab='operacion' THEN ',(SELECT nombre FROM bovi.parte p WHERE (p.empresa_id,p.id)=(t.empresa_id,t.parte_id)) AS contraparte' WHEN tab='posicion_inventario' THEN ', EXISTS(SELECT 1 FROM bovi.reserva_venta r WHERE (r.empresa_id,r.sucursal_id,r.posicion_id)=(t.empresa_id,t.sucursal_id,t.id) AND estado=''ACTIVA'' AND vence_en>now()) AS reservada,(SELECT coalesce(sum(importe),0) FROM bovi.asignacion_costo c WHERE (c.empresa_id,c.sucursal_id,c.posicion_id)=(t.empresa_id,t.sucursal_id,t.id)) AS costo_vigente' ELSE '' END,tab,filtro,CASE WHEN tab='v_margen_operacion' THEN 't.operacion_id' ELSE 't.id' END);
 EXECUTE sql INTO rows USING e,s,coalesce(idn,(params->>'id')::uuid),size,(page-1)*size,pattern,statefilter,typefilter;
 IF recurso IN ('animal','operacion','liquidacion','pago','documento','gasto') THEN
 detail:=rows->0; IF detail IS NULL THEN RAISE EXCEPTION 'Recurso inexistente' USING ERRCODE='P0001', DETAIL=jsonb_build_object('mensaje','Recurso inexistente','codigo','BV404','regla_id','RN-017','campos','[]'::jsonb)::text; END IF;
 IF recurso='documento' THEN detail:=detail||jsonb_build_object('revisiones',(SELECT coalesce(jsonb_agg(to_jsonb(r)),'[]') FROM bovi.revision_documento r WHERE (r.empresa_id,r.sucursal_id,r.documento_id)=(e,s,idn))); END IF;
 IF recurso='animal' THEN detail:=detail||jsonb_build_object('identificaciones',(SELECT coalesce(jsonb_agg(to_jsonb(i)),'[]') FROM bovi.animal_identificacion i WHERE i.empresa_id=e AND i.animal_id=idn)); END IF;
 IF recurso='operacion' THEN detail:=detail||jsonb_build_object('numero_version_actual',(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)),'contratos',(SELECT jsonb_agg(to_jsonb(cv) ORDER BY numero_version) FROM bovi.contrato_version cv WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)),'lotes',(SELECT coalesce(jsonb_agg(to_jsonb(l)||coalesce((SELECT bovi.fn_json_decimal(to_jsonb(c)) FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote,c.numero_version)=(e,s,idn,l.numero_lote,(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)))),'{}'::jsonb)||jsonb_build_object('animales',(SELECT coalesce(jsonb_agg(animal_id),'[]') FROM bovi.seleccion_compra sc WHERE (sc.empresa_id,sc.sucursal_id,sc.operacion_id,sc.numero_lote)=(e,s,idn,l.numero_lote)),'posiciones',(SELECT coalesce(jsonb_agg(posicion_id),'[]') FROM bovi.seleccion_venta sv WHERE (sv.empresa_id,sv.sucursal_id,sv.operacion_id,sv.numero_lote)=(e,s,idn,l.numero_lote)),'condicion',(SELECT bovi.fn_json_decimal(to_jsonb(c)) FROM bovi.condicion_lote c WHERE (c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_lote,c.numero_version)=(e,s,idn,l.numero_lote,(SELECT max(numero_version) FROM bovi.contrato_version WHERE (empresa_id,sucursal_id,operacion_id)=(e,s,idn)))))),'[]') FROM bovi.lote_operacion l WHERE (l.empresa_id,l.sucursal_id,l.operacion_id)=(e,s,idn)),'pesajes',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(p))),'[]') FROM bovi.pesaje p WHERE (p.empresa_id,p.sucursal_id,p.operacion_id)=(e,s,idn)),'liquidacion',(SELECT bovi.fn_json_decimal(to_jsonb(l)) FROM bovi.v_saldo_liquidacion l WHERE (l.empresa_id,l.sucursal_id,l.operacion_id)=(e,s,idn))); END IF;
 IF recurso='liquidacion' THEN detail:=bovi.fn_liquidacion_json(e,s,idn)||jsonb_build_object('conceptos',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(c))),'[]') FROM bovi.concepto_liquidacion c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(e,s,idn)),'aplicaciones',(SELECT coalesce(jsonb_agg(bovi.fn_json_decimal(to_jsonb(c))),'[]') FROM bovi.aplicacion_pago c WHERE (c.empresa_id,c.sucursal_id,c.liquidacion_id)=(e,s,idn)),'parte_id',(SELECT parte_id FROM bovi.operacion WHERE (empresa_id,sucursal_id,id)=(e,s,(detail->>'operacion_id')::uuid))); END IF;
 RETURN detail;
 END IF;
 RETURN jsonb_build_object('elementos',rows,'pagina',page,'tamano',size,'total',totaln,'corte',now());
END $$;
