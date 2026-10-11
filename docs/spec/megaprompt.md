# BoviCierre — Megaprompt maestro para Claude Code

## Especificación de negocio, datos, arquitectura y ejecución

**Versión:** 1.0.  
**Contexto:** proyecto universitario de Tópicos Avanzados de Bases de Datos con intención de convertirse en un SaaS B2B.  
**Equipo:** Aldo Fabio Contreras Marroquín, backend y bases de datos; Jared, frontend.  
**Inicio de planificación:** 11 de octubre de 2026. **Entrega académica objetivo:** 31 de octubre de 2026. Zona del equipo: America/Mexico_City.  
**Naturaleza de este documento:** instrucciones ejecutables y decisiones propuestas. No representa software ya implementado, investigación de campo realizada ni validación comercial obtenida.

**Cómo usarlo:** adjunta este archivo a Claude Code o colócalo en el repositorio y pídele que lo lea completo. La primera entrega exigida es el paquete de negocio, MER Chen, modelo relacional, arquitectura y contexto; después continúa la implementación por tareas. Los comandos que aparecen son instrucciones para el entorno de ejecución de Claude, no evidencia de que ya se ejecutaron.

## Guía de lectura

- Secciones 0–4: encargo, rúbrica, negocio, monetización y contexto pecuario.
- Secciones 5–8: reglas, teoría, MER Chen y esquema relacional candidato.
- Secciones 9–11: stack, arquitectura, administración, transacciones, M–M y FDW.
- Secciones 12–13: casos difíciles, API, frontend, despliegue y recuperación.
- Secciones 14–15: README, contexto Markdown, trazabilidad y /graphify.
- Secciones 16–17: metodología, calendario y tareas de Aldo y Jared con casillas.
- Secciones 18–20: pruebas, entrega al profesor, primeras acciones y bibliografía.

---

# 0. Tu encargo y cómo debes trabajar

Actúa como arquitecto de software, analista del dominio ganadero y desarrollador senior de BoviCierre. Debes comprender, documentar y construir el proyecto de forma incremental. Trabaja dentro del repositorio real que te dé el usuario y conserva el trabajo existente.

Tu primera prioridad es dejar correctamente fundamentados el negocio, las reglas, el modelo conceptual entidad–relación, el modelo relacional, la arquitectura y el plan de ejecución. No empieces por una interfaz ficticia ni por generar tablas sin haber revisado su significado. El primer incremento debe producir archivos y diagramas reales, verificables y editables.

Lee este documento completo. Si una sección entra en conflicto con otra, identifica el conflicto, resuélvelo con una decisión documentada y propaga la corrección a los artefactos afectados. No escojas silenciosamente la opción más fácil.

## 0.1 Protocolo inicial

1. Inspecciona el directorio de trabajo, el estado de Git, README, CLAUDE.md, AGENTS.md, skills, configuración, dependencias y archivos existentes. Respeta las instrucciones aplicables y los permisos del entorno.
2. Identifica si estás en un proyecto nuevo o en uno iniciado. No sobrescribas trabajo, hooks o instrucciones existentes.
3. Crea un inventario breve de herramientas y versiones disponibles: Java, Maven, Node, gestor de paquetes frontend, Docker/Compose, PostgreSQL, Graphviz/draw.io y Graphify.
4. Clasifica cada requisito como comprobado en la imagen, instrucción expresa, decisión propuesta o pendiente de validación.
5. Crea la documentación de contexto y una matriz de trazabilidad antes de implementar reglas monetarias.
6. Produce el MER Chen y sus vistas, el modelo relacional y el diccionario. Revisa identidad, cardinalidades, participación y correspondencia.
7. Prepara arquitectura, ADR, contrato OpenAPI y tareas paralelas para Aldo y Jared.
8. Genera el grafo con la implementación real de /graphify; verifica los resultados. Si existe un bloqueo de herramienta, registra su causa y continúa las tareas independientes.
9. Entrega una lista de archivos creados, decisiones tomadas, validaciones efectivamente realizadas y siguientes tareas. Una propuesta o un archivo vacío no cuentan como implementación.

Continúa las fases siguientes en el orden del backlog, con evidencia de finalización. No pidas confirmación para correcciones rutinarias dentro de este alcance. Si falta acceso externo, una interpretación obligatoria del profesor o una decisión comercial que no puedes inferir, deja únicamente esa dependencia pendiente y avanza en lo demás.

No inventes entrevistas, clientes, integraciones, resultados de pruebas, certificaciones, firmas ni estadísticas. No atribuyas a Aldo o Jared commits o trabajo que todavía no realizaron. La asignación de tareas indica responsabilidad futura.

## 0.2 Estándar de redacción y presentación

Escribe documentación técnica en español claro, con nombres estables, ejemplos propios y fuentes verificables. Usa explicaciones concretas, tablas útiles y diagramas legibles. Evita publicidad, superlativos, relleno, emojis decorativos y afirmaciones como “listo para producción” sin evidencia.

La apariencia profesional de los diagramas debe provenir de una notación correcta, composición cuidada y revisión de las exportaciones. No afirmes que fueron hechos manualmente ni alteres su procedencia. Conserva bibliografía y evidencia auténticas conforme a las reglas de la materia.

# 1. Requisitos académicos obligatorios

La imagen proporcionada por el usuario contiene:

| ID | Requisito visible | Evidencia que debes producir |
|---|---|---|
| AC-01 | MER | Modelo conceptual con entidades, atributos, relaciones y restricciones de participación |
| AC-02 | Modelo relacional | Relaciones, claves, referencias y transformación verificable desde el MER |
| AC-03 | Administración de BDD: usuarios, constraints y reglas | Scripts de roles/usuarios, privilegios, restricciones y pruebas positivas/negativas |
| AC-04 | PL y triggers | Funciones/procedimientos PL/pgSQL y triggers con una finalidad de negocio o auditoría |
| AC-05 | Transacciones | Operaciones atómicas, rollback, concurrencia e idempotencia demostrados |
| AC-06 | Replicación M–M | Dos nodos escritores con una política explícita de propiedad y replicación bidireccional |
| AC-07 | FDW | Consulta real a otra instancia de base de datos y documentación de permisos |
| AC-08 | Programa en Java | Backend Java ejecutable con reglas de dominio, SOLID y patrones justificados |
| AC-09 | PostgreSQL y Pgpool-II en el dibujo | Servicios, configuración, conexión de la aplicación y demostración operativa |

También integrarás POO, programación avanzada, diseño y administración de bases de datos. No afirmes que cubriste “todo el temario” si no se dispone del programa completo. Crea una matriz de cobertura y agrega cualquier criterio que el profesor confirme después.

“DER”, “ER” y “MER” pueden referirse al mismo modelo conceptual según la clase; no inventes tres diseños inconexos. Entrega expresamente: MER conceptual Chen, diagrama lógico relacional y esquema físico PostgreSQL.

La interpretación inicial de M–M es que ambos nodos aceptan escrituras sobre recursos diferentes, definidos por sede propietaria. Si el profesor exige dos escritores sobre una misma fila, debes registrar ese requisito como cambio arquitectónico; origin = none no es un resolvedor de conflictos.

# 2. Contexto y límites del negocio

## 2.1 Qué es BoviCierre

BoviCierre es un SaaS B2B para comercializadores recurrentes de ganado bovino en pie y centros de compra/acopio. Ayuda a reconstruir cada negocio: qué animales participaron, qué peso se utilizó, qué condiciones se pactaron, qué gastos se asignaron, cómo se calculó la liquidación y qué queda por cobrar o pagar.

El usuario del SaaS compra y vende ganado por cuenta propia en el MVP. Aldo y Jared venden el software y su servicio de implantación. El importe de las operaciones ganaderas pertenece al negocio del cliente y no constituye ingreso de BoviCierre.

Propuesta de valor a validar: “Explicar cada liquidación y conciliar inventario, saldos y margen con la evidencia que respalda el trato”.

## 2.2 Cliente inicial propuesto

Comercializador o acopiador con una o dos sedes, operaciones recurrentes, precios por kilogramo o por cabeza, pagos parciales, tickets de báscula y un responsable administrativo. El comprador del software es el dueño o administrador con facultad para contratar.

Es una hipótesis de segmento, no un mercado validado. El número de cabezas de ganado de una región no equivale al número de clientes dispuestos a pagar por software.

## 2.3 Alcance del MVP de octubre

Incluye:

- Empresas usuarias, sedes, usuarios y permisos.
- Contrapartes que pueden actuar como compradores o vendedores.
- Establecimientos, identificación animal, lotes y ciclos de inventario.
- Acuerdos comerciales y versiones de condiciones.
- Compras y ventas en moneda MXN por kilogramo o por cabeza.
- Pesajes de lote o individuales claramente diferenciados.
- Reserva de animales para venta y prevención de doble venta.
- Recepciones, entregas y movimientos físicos básicos.
- Gastos, asignación de costos, liquidaciones y ajustes.
- Registro de pagos manuales, aplicaciones y saldos.
- Expediente documental y revisión administrativa.
- Reporte de margen comercial, cartera e inventario.
- Auditoría, respaldo/restauración, replicación y FDW.
- Simulador explicable de margen y QR interno.
- OCR supervisado como mejora priorizable después del núcleo.

Quedan para una fase posterior: exportación, subastas, sacrificio y cortes, producción de leche, reproducción, nutrición, diagnósticos, prescripciones veterinarias, crédito, custodia de dinero, timbrado CFDI, CFDI de traslado/Carta Porte, básculas conectadas en tiempo real, cambio de sede escritora del mismo animal, transacciones entre sedes y edición concurrente libre de una misma entidad en ambos nodos.

No reduzcas la ambición funcional eliminando los requisitos del profesor. Ajusta primero extras como OCR o visualizaciones avanzadas si la ruta crítica se retrasa.

## 2.4 Competencia y diferenciación

EngordaMax anuncia compras, pesajes, merma, costos y utilidad. Agryxo/Agroapp anuncia compras/ventas, inventario, cartera, margen y controles contra doble venta. Son referencias competitivas, no fuentes de código ni pruebas de demanda para nuestro producto. [F01–F02]

La especialización propuesta es una mesa de cierre comercial que reúna evidencia original, condiciones versionadas, costos y saldos, con facilidad de uso para una operación regional. Valida esta hipótesis con un comprador; no publiques que el producto es el primero, el único o que elimina todo fraude.

# 3. Modelo de negocio y validación comercial

## 3.1 Business Model Canvas propuesto

Usa los nueve bloques del Canvas como hipótesis versionadas. La referencia metodológica es Strategyzer. [F03]

| Bloque | Hipótesis inicial de BoviCierre | Qué falta validar |
|---|---|---|
| Segmentos | Comercializadores y acopiadores recurrentes de bovinos en pie | Frecuencia, complejidad y capacidad de contratación |
| Propuesta de valor | Liquidación explicable, saldos conciliados y margen por operación | Cuál de esos problemas tiene prioridad real |
| Canales | Demostración directa, referencias y contactos del sector | Costo y tasa de conversión de cada canal |
| Relación | Implantación acompañada, capacitación y soporte definido | Horas de soporte por cliente |
| Ingresos | Configuración inicial más suscripción | Disposición a pagar y permanencia |
| Recursos | Software, reglas validadas, infraestructura y equipo | Capacidad operativa de dos personas |
| Actividades | Desarrollo, operación, respaldos, soporte y ventas | Costo real y esfuerzo recurrente |
| Socios | Cliente piloto, asesor contable/pecuario y proveedores cuando exista acuerdo | Acuerdos y acceso efectivo |
| Costos | Trabajo, alojamiento, almacenamiento, respaldos, soporte, ventas y administración | Presupuesto y costos medidos |

No conviertas “socios posibles” en alianzas firmadas.

## 3.2 Oferta comercial que se probará

- Suscripción como rango de investigación: MXN 2,000–4,000 al mes por sede.
- Precio de referencia para los ejemplos: MXN 2,000 por sede/mes.
- Configuración y migración inicial: cotización separada por horas, complejidad y calidad de datos.
- Integraciones especiales: alcance y presupuesto aparte.
- No cobrar comisión sobre el ganado en el MVP.
- No custodiar dinero de las partes: el sistema registra y concilia pagos.
- Documentar qué incluye la suscripción: sedes, usuarios, almacenamiento, exportación, horarios y límites de soporte. No ofrecer servicio ilimitado sin dimensionarlo.
- Definir cancelación, entrega/exportación de datos, retención y responsabilidades en la propuesta comercial antes de un piloto real.

Estos importes son hipótesis del proyecto, no precios de mercado comprobados ni ingresos asegurados.

## 3.3 Economía del SaaS

Documenta las fórmulas, su periodo y lo que cada costo incluye:

~~~text
MRR = suma de las mensualidades recurrentes activas
Ingreso de implementación = cobros únicos por configuración
Contribución por cliente = mensualidad − costo variable mensual de atenderlo
Equilibrio operativo = techo(costos fijos mensuales / contribución por cliente)
CAC = gasto atribuible a adquirir clientes / clientes nuevos adquiridos
~~~ 

Si la contribución es cero o negativa, la fórmula de equilibrio no produce un número válido de clientes rentable. No mezcles MRR con cobros únicos, impuestos trasladados o volumen de compraventa de ganado.

Ejemplo exclusivamente ilustrativo para empresas de una sede cada una: mensualidad 2,000; costo variable por cliente 550; costos fijos mensuales 6,000. Contribución 1,450; equilibrio operativo a 5 clientes. Con 5 clientes: 10,000 − 2,750 − 6,000 = 1,250 antes de conceptos no incluidos. Declara si esos costos incluyen trabajo, adquisición, impuestos y amortización del desarrollo. No llames utilidad neta a ese resultado incompleto. Define el rango de capacidad dentro del que esos costos son válidos: al crecer pueden aumentar servidores y soporte.

Crea un presupuesto editable que incluya el valor del tiempo de Aldo y Jared, aunque inicialmente no se paguen un sueldo. Actualiza los costos con cotizaciones reales antes de vender.

## 3.4 Plan de validación

Prepara un guion para cinco entrevistas del mismo segmento, sin afirmar que ya se realizaron:

1. ¿Cómo se acuerda hoy el peso y el precio?
2. ¿Qué documento muestra una compra completa?
3. ¿Quién registra, modifica y autoriza?
4. ¿Cómo controlan anticipos y pagos parciales?
5. ¿Qué pasa si un ticket cambia o hay diferencia de peso?
6. ¿Cómo dividen o mezclan lotes para vender?
7. ¿Cómo detectan un animal comprometido en otro trato?
8. ¿Cuánto tarda preparar y conciliar una liquidación?
9. ¿Qué dato les falta para conocer el margen?
10. ¿Quién decide una compra de software y con qué presupuesto?

Solicita muestras anonimizadas solamente con autorización de su dueño. Reconstruye un caso, prueba el prototipo y registra observaciones. Criterios propuestos: tres entrevistados reconocen un problema frecuente; uno permite validar un flujo completo; al menos un decisor acepta discutir un piloto con precio. Son metas de aprendizaje, no resultados.

Métricas del piloto: tiempo mediano de cierre, liquidaciones conciliadas sin diferencia inexplicada, consumos de soporte, porcentaje de operaciones con evidencia y saldos vencidos correctamente identificados. No atribuyas una mejora causal al software sin una comparación adecuada.

## 3.5 Contribución social

La hipótesis de impacto es mejorar la transparencia de pagos a productores, conservar evidencia comercial y facilitar trazabilidad administrativa. Mide esos resultados. El software no sustituye la autoridad sanitaria, la acreditación de propiedad ni la revisión profesional correspondiente.

# 4. Sustento del dominio y contexto normativo

## 4.1 Glosario mínimo

Define, con ejemplo y diferencias: empresa cliente del SaaS; sede; nodo escritor; contraparte; establecimiento; UPP; PSG; animal; identificación oficial; lote; membresía de lote; posición/ciclo de inventario; custodia; operación de compra/venta; acuerdo; versión; pesaje; bruto/tara/neto; variación física; ajuste contractual; liquidación comercial; obligación; pago; aplicación; reverso; costo de adquisición; costo de venta; gasto directo; margen provisional y margen cerrado.

La NOM-001-SAG/GAN-2015 usa SINIDA; SINIIGA aparece en la operación del sistema de identificación. Conserva el contexto de ambas denominaciones. La norma y su estado vigente deben verificarse en fuentes oficiales. [F04–F05]

Un establecimiento registrado, el propietario comercial y la sede que escribe en PostgreSQL no representan lo mismo.

## 4.2 Requisitos reales y alcance del software

La identificación oficial y los registros de ingreso/salida son relevantes para la comercialización y el acopio. Registra el identificador como texto, con evidencia y procedencia; un formato válido no demuestra autenticidad. El QR interno no sustituye un arete ni documento oficial. [F04]

La movilización depende de origen, destino, finalidad y disposiciones vigentes. El acuerdo federal consultado de diciembre de 2025 incluye medidas diferenciadas relacionadas con el gusano barrenador. No transformes una lista documental en una autorización automática. [F06–F07]

Para el MVP, el expediente almacena emisor, folio, tipo, fechas, animales/cargamento, origen, destino, finalidad, archivo y responsable de revisión. El estado debe decir “revisión administrativa registrada”, “pendiente” o equivalente preciso; nunca “autorizado por SENASICA” por haber subido un PDF.

No se ha verificado una API pública de SINACAM disponible para este proyecto. Enlaza su consulta oficial; la integración por FDW será con un proveedor/transportista simulado e identificado como tal.

La legislación pecuaria estatal debe revisarse en su versión oficial junto con cambios posteriores. No hardcodees horarios, vigencias, rutas o requisitos sanitarios como verdades permanentes. [F08]

La liquidación interna no es un CFDI. Para facturar el servicio o integrar timbrado posteriormente, se requiere un proceso fiscal válido y revisar las herramientas/proveedores del SAT. No deduzcas el tratamiento tributario de una operación ganadera sólo por su descripción. [F09]

Para clientes reales se deberán definir aviso de privacidad, finalidades, acceso, exportación, retención y responsabilidades. El marco de datos personales vigente debe verificarse; no copies referencias institucionales obsoletas. No incluyas datos reales en demos, repositorios, logs o grafos. [F10]

## 4.3 Merma, evidencia y teoría del cálculo

La variación de peso puede depender de transporte, tiempo, manejo y otras condiciones. La fuente técnica de Oklahoma State University explica esa variabilidad; no ofrece fundamento para imponer un descuento comercial universal. [F11]

Separarás:

- Peso observado y evidencia original.
- Comparación entre dos mediciones compatibles.
- Base de peso aceptada en un contrato.
- Deducción comercial expresamente pactada.
- Reparto contable de un total entre animales.

Una estimación financiera no se presenta como una medición de báscula.

# 5. Reglas de negocio obligatorias

Crea docs/domain/business-rules.md. Cada regla debe incluir ID, razón, actor, precondiciones, transición, datos afectados, errores, implementación prevista, prueba y fuente o decisión que la origina.

Las siguientes son reglas propuestas del producto; valida detalles con el piloto sin relajar integridad o auditoría.

| ID | Regla |
|---|---|
| RN-001 | Aislamiento por empresa: un usuario sólo accede a empresas y sedes autorizadas. Las referencias cruzadas entre empresas se rechazan también en BD. |
| RN-002 | Cada animal conserva una identidad estable. Identificaciones oficiales y UUID interno son campos distintos. |
| RN-003 | La identidad maestra y sus identificadores se registran en A; la unicidad por empresa se verifica allí. UUID por sí solo no impide duplicar un arete. |
| RN-004 | La sede escritora asignada al animal es inmutable en el MVP. Propietario, custodio, ubicación y nodo responsable son conceptos diferentes. |
| RN-005 | Animal y posición de inventario son distintos. Se permite recompra tras cerrar el ciclo previo; no doble venta del ciclo vigente. |
| RN-006 | Sólo puede existir una posición activa por animal dentro de la empresa. Toda posición deriva de una adquisición registrada, no de un cambio manual de saldo. |
| RN-007 | Un lote agrupa animales/posiciones con historia. Una compra puede alimentar varias ventas y una venta puede usar posiciones de varias compras. |
| RN-008 | La selección de un animal/posición es única entre los lotes de una misma operación. La composición confirmada es histórica y no se sobrescribe; puede participar en lotes de operaciones sucesivas. |
| RN-009 | Toda operación tiene empresa, sede, tipo, contraparte, moneda, versión y estado. No admite animales de otra sede escritora. |
| RN-010 | Compra y venta por cuenta propia son los únicos modos del MVP. Un mismo tercero puede ser comprador y vendedor en momentos diferentes. |
| RN-011 | Las condiciones de precio, pesaje, ajustes y redondeo se versionan. Cambiar una versión nueva no recalcula operaciones confirmadas. |
| RN-012 | Pesos se almacenan en kg con precisión declarada. Si existe bruto y tara, tara no puede exceder bruto y neto = bruto − tara. |
| RN-013 | Un pesaje de lote conserva la lista exacta de animales incluidos. No se inventan pesos individuales dividiendo el total. |
| RN-014 | Sólo se comparan pesajes compatibles del mismo conjunto; diferencias de composición se presentan como no comparables. |
| RN-015 | Variación de peso y deducción contractual son independientes. No descontar dos veces la misma merma de forma implícita. |
| RN-016 | OCR/CSV generan propuestas de captura. Un responsable confirma valores y evidencia antes de usarlos en una liquidación. |
| RN-017 | Un borrador puede estar incompleto. Confirmar exige sus precondiciones: partidas, contraparte, condiciones válidas, pesos cuando procedan y autorización. |
| RN-018 | La reserva para venta se realiza atómicamente en el nodo propietario, bloqueando las posiciones en orden estable. Sólo una reserva activa por posición. |
| RN-019 | Las reservas tienen vencimiento explícito. Confirmar después de vencer requiere una nueva validación de disponibilidad. |
| RN-020 | Venta comercial, entrega física y cobro son ejes separados. Ninguno debe inferirse automáticamente de otro. |
| RN-021 | ConfirmarCompra crea posiciones, valoración inicial, liquidación principal confirmada y obligación correspondiente en una sola transacción local. La liquidación no dispara una segunda obligación. |
| RN-022 | ConfirmarVenta compromete las posiciones del ciclo, consume reservas y registra costo de venta, liquidación principal confirmada y obligación en una sola transacción local. La entrega posterior registra el hecho físico y no duplica venta ni costo. |
| RN-023 | Una liquidación confirmada es inmutable. Ajustes, devoluciones y reversos conservan referencia, motivo, actor y fecha. |
| RN-024 | Una tarifa nueva, un tercero renombrado o un documento posterior no altera el snapshot histórico de una liquidación. |
| RN-025 | Cada gasto tiene una clasificación: costo de adquisición asignable, gasto directo de venta u otro. No se suma dos veces. |
| RN-026 | Las asignaciones de un gasto suman exactamente el total; el método y la distribución del residuo de redondeo son deterministas. |
| RN-027 | Un costo tardío modifica el margen mediante un ajuste trazable; no edita silenciosamente una liquidación ni un periodo cerrado. |
| RN-028 | El pago existe separado de su aplicación. Un pago puede cubrir varias obligaciones y una obligación admitir varios pagos. |
| RN-029 | Las aplicaciones no exceden el pago disponible ni el saldo de la obligación, salvo un modelo explícito de crédito que no forma parte del MVP. |
| RN-030 | Pago y aplicación pertenecen a la misma empresa, sede, contraparte, moneda y dirección compatible. El pago multisedes queda fuera del MVP. |
| RN-031 | El importe no aplicado permanece como anticipo/saldo a favor. No se lo fuerza dentro de una obligación ni se lo cuenta como venta adicional. |
| RN-032 | Un reintento con la misma clave y payload devuelve el resultado previo. Reutilizar la clave con contenido distinto produce conflicto. |
| RN-033 | Reversar un pago o aplicación conserva el original y crea el contramovimiento; se verifica su efecto sobre todas las aplicaciones relacionadas. |
| RN-034 | Las operaciones monetarias usan NUMERIC y BigDecimal; nunca float/double para importes, tarifas o reparto de centavos. |
| RN-035 | El margen se obtiene de ventas reconocidas, costos de posiciones vendidas y gastos directos. Cobros y anticipos afectan caja/cartera, no margen. |
| RN-036 | Si faltan costos o revisiones, el margen se etiqueta provisional. No llamarlo utilidad neta. |
| RN-037 | Las evidencias tienen versión, hash, tamaño, tipo y control de acceso. Un hash detecta cambios; no demuestra autenticidad jurídica ni autoría. |
| RN-038 | Cancelaciones, pérdidas, muerte, devolución y venta son motivos distintos con evidencia y autorización. No eliminar animales para cuadrar stock. |
| RN-039 | Un periodo cerrado impide ediciones retroactivas ordinarias. Reapertura o ajuste requiere permiso y deja bitácora. |
| RN-040 | Una réplica retrasada no puede autorizar una operación crítica. La decisión se toma en el escritor propietario. |
| RN-041 | Si el nodo propietario está indisponible, la escritura queda sin confirmar. La aplicación no cambia de propietario automáticamente. |
| RN-042 | Un dato del proveedor por FDW no se vuelve histórico por sí mismo: guarda la cotización/condición aceptada dentro del expediente local. |
| RN-043 | Confirmar una operación y su auditoría es atómico. Un evento de integración se escribe en outbox dentro de esa misma transacción. |
| RN-044 | La entrega externa de eventos admite reintentos. Outbox no garantiza por sí solo “exactamente una vez” en sistemas externos. |
| RN-045 | Datos de demostración se identifican como sintéticos y no usan documentos oficiales aparentando autenticidad. |

## 5.1 Fórmulas y precisión

Propuesta inicial: kg con NUMERIC(14,3); tarifas por kg/cabeza con NUMERIC(14,4); importes con NUMERIC(18,2); tasas decimales con NUMERIC(9,6). Verifica límites con el dominio y registra cambios. Moneda MVP: MXN. Cantidad de animales: entero positivo.

~~~text
Peso neto = peso bruto − tara
Variación de kg = peso inicial − peso final
Variación porcentual = 100 × (peso inicial − peso final) / peso inicial
Base por kg = kg liquidables × precio por kg
Base por cabeza = número de animales × precio por cabeza
Total comercial = base + cargos pactados − bonificaciones pactadas
Saldo obligación = total emitido + ajustes de cargo − ajustes de abono − aplicaciones netas válidas
Saldo disponible de pago = importe confirmado − aplicaciones netas válidas − reembolsos/reintegros confirmados vinculados
Margen comercial = venta neta reconocida − costo de posiciones vendidas − gastos directos de venta
~~~

El peso inicial debe ser positivo para calcular el porcentaje. Conserva una variación negativa como incremento o discrepancia. No la conviertas silenciosamente en cero.

El contrato elige el pesaje base y detalla las deducciones. No combines un peso de llegada que ya refleja una variación física con una segunda deducción supuesta por “merma habitual”.

Usa redondeo HALF_UP a dos decimales para importes del MVP y documenta dónde se aplica. Si PostgreSQL y Java participan en cálculos, prueba su equivalencia en los límites. El backend obtiene los totales de la lógica canónica; no confía en totales enviados por el navegador.

Para reparto por cabezas o pesos documentados, conserva el valor exacto de cálculo, redondea las asignaciones y distribuye centavos residuales con un orden estable por ID. El método de reparto no crea mediciones individuales.

## 5.2 Casos numéricos de aceptación

**GOLD-01, operación completa ficticia:** compra de un conjunto a 5,000 kg × 48 = 240,000. Gastos de adquisición 12,000. Costo del inventario vendido 252,000. Venta del mismo conjunto a 4,900 kg × 60 = 294,000. Gastos directos de venta 8,000. Margen comercial 34,000. Anticipo recibido 50,000. Saldo por cobrar 244,000. Variación física 100 kg y 2%. El 2% no se convierte en descuento automático.

**GOLD-02, venta parcial ficticia por cabeza:** compra 10 animales a 1,000 cada uno; gasto de adquisición 1,000 repartido por cabeza. Costo por posición 1,100. Venta de 4 a 1,600 cada uno; gasto directo de esa venta 200. Venta 6,400; costo vendido 4,400; margen 1,800; inventario restante 6,600. No cargar los 11,000 completos contra esa venta parcial.

**GOLD-03, centavos:** asignar 1.00 entre tres posiciones por partes iguales da 0.34, 0.33 y 0.33 según orden estable. La suma debe ser exactamente 1.00.

**GOLD-04, pagos, dos escenarios independientes:** A) obligación 1,000, pago 600, dos aplicaciones a esa obligación por 400 y 200: saldo de obligación 400 y pago disponible 0. Repetir una aplicación no vuelve a descontar. Intentar aplicar otros 0.01 falla. B) otra obligación 1,000, pago 1,200 y aplicación 1,000: saldo de obligación 0, pago disponible 200. El remanente no genera ingreso de venta adicional.

**GOLD-05, recompra:** un animal vendido y entregado puede generar una nueva posición de inventario cuando se recompra. Debe ser imposible tener dos posiciones activas del mismo animal.

Crea fixtures y pruebas a partir de estos resultados; no copies pruebas que sólo repitan internamente la implementación.

## 5.3 Estados y transiciones

Documenta por separado:

- Operación: BORRADOR → ACORDADA → CONFIRMADA; CANCELADA sólo según precondiciones.
- Reserva: ACTIVA → CONSUMIDA, LIBERADA o EXPIRADA.
- Posición: DISPONIBLE, RESERVADA, VENDIDA_PENDIENTE_ENTREGA, CERRADA u otra transición justificada.
- Liquidación: BORRADOR → CONFIRMADA; los ajustes/reversos son nuevos registros.
- Entrega: PENDIENTE → PARCIAL → COMPLETA, con las posiciones correspondientes.
- Pago: REGISTRADO/VALIDADO y REVERTIDO según evidencia; su aplicación es una relación separada.
- Periodo: ABIERTO → CERRADO; reapertura documentada.

No uses un único campo estado para representar simultáneamente venta, pago, entrega y revisión documental. Define exactamente qué transición reconoce venta/costo para el reporte gerencial del MVP y declárala como política operativa, no como dictamen contable universal.

# 6. Sustento teórico y decisiones que debes poder defender

Crea docs/research/theoretical-foundation.md. Relaciona cada concepto con una decisión de BoviCierre, una fuente primaria y una evidencia del proyecto. No escribas un capítulo genérico desconectado de la aplicación.

| Fundamento | Aplicación concreta | Evidencia exigida |
|---|---|---|
| Modelo entidad–relación de Chen | Distinguir objetos del negocio, relaciones, atributos e identidad antes de tablas | MER conceptual, leyenda y explicación de cardinalidades [F12–F14] |
| Modelo relacional de Codd | Expresar datos mediante relaciones, claves y restricciones | Modelo relacional y transformación desde el MER [F13] |
| Dependencias funcionales y normalización | Evitar repetir contrapartes, condiciones actuales y datos incompatibles en cada operación | Claves candidatas, dependencias, descomposición y comprobación de 3FN; evaluar BCNF [F15] |
| Integridad y transacciones | Una confirmación produce todos sus efectos o ninguno | Constraints, comandos PL/pgSQL, rollback y dos conexiones concurrentes [F20–F21] |
| Replicación y propiedad de escritura | Mantener copias sin permitir dos decisiones simultáneas sobre el mismo recurso | ADR, mapa de dueños y prueba de partición/reconvergencia [F22–F26] |
| Trazabilidad comercial | Reconstruir animal, lote, pesajes, condiciones y liquidación | Expediente navegable y referencias tipadas; no equivale a certificación oficial |
| Costeo identificado para gestión | Vincular costo al ciclo de inventario de cada animal; separar existencias de lo vendido | Asignaciones y casos GOLD; política gerencial explícita |
| Separación de devengo gerencial y flujo monetario | Diferenciar obligación, anticipo, aplicación y entrega | Reportes que concilian margen, cartera y movimientos de dinero |
| Canvas y validación de hipótesis | Verificar comprador, problema, precio y costo de servir | Canvas versionado, guion, registro de evidencia y economía unitaria [F03] |
| Kanban e incrementos verticales | Coordinar a dos personas, limitar trabajo abierto y entregar flujos completos | Tablero, políticas y evidencia por hito [F16] |
| ADR y trazabilidad de decisiones | Conservar por qué se eligió una solución y qué compromisos implica | ADR con estado, contexto, decisión, alternativas y consecuencias [F17] |

La consistencia ACID de una transacción local no significa consistencia inmediata de las dos réplicas. Explica esa diferencia con el caso de doble venta.

Normalizar no significa eliminar los snapshots históricos. Un nombre, una condición o una fórmula “tal como se aceptó” es un hecho temporal diferente del valor actual del catálogo. Justifica su conservación y evita que se actualice por cascada al renombrar el catálogo.

El costo identificado y la fecha de reconocimiento aquí descritos son políticas de información gerencial del producto. No presentes este sistema como contabilidad financiera/fiscal completa ni afirmes cumplimiento de una norma contable que no has analizado para el tipo de empresa y operación.

## 6.1 Un único evento económico por operación

ACORDADA conserva las condiciones aceptadas y, en ventas, puede reservar posiciones. No produce por sí sola un segundo registro de ingresos o deuda.

CONFIRMADA es el evento de reconocimiento gerencial del MVP, cuando ya están determinados los animales, la base liquidable, la versión aceptada y los costos requeridos. El comando ConfirmarCompra o ConfirmarVenta crea y confirma la liquidación principal y los efectos de inventario/valoración en la misma transacción. Una operación tiene como máximo una liquidación principal; las correcciones posteriores son ajustes enlazados.

La entrega y el cobro se registran por separado. Confirmar un pago o completar una entrega no vuelve a generar ingreso, costo u obligación. Si el cliente necesita reconocer económicamente en otro momento, plantea una política versionada y una migración del modelo antes de cambiar los reportes.

Las cuentas por cobrar/pagar ordinarias y sus vencimientos sí forman parte del MVP. “Crédito fuera de alcance” significa que BoviCierre no origina préstamos, financia ganado ni implementa evaluación crediticia; no elimina los saldos comerciales pendientes.

# 7. Primer entregable: MER conceptual profesional

Tu primera entrega sustantiva, después del inventario del repositorio y el contexto inicial, debe ser el paquete de diseño de datos. El negocio y las reglas preceden al diagrama; el diagrama y el modelo relacional preceden a las migraciones de negocio.

## 7.1 Notación obligatoria

Usa Chen/EER de forma consistente. La leyenda debe explicar:

| Símbolo | Significado y uso |
|---|---|
| Rectángulo simple | Entidad fuerte, con identidad conceptual propia |
| Rectángulo doble | Entidad débil, identificada mediante propietario y clave parcial |
| Rombo | Relación nombrada con verbo: administra, contiene, origina, registra, comprende, aplica |
| Rombo doble | Relación identificante de una entidad débil |
| Óvalo | Atributo simple |
| Atributo subrayado | Clave conceptual/candidata elegida, con la convención explicada |
| Subrayado discontinuo | Clave parcial de una entidad débil |
| Óvalo doble | Atributo multivaluado, sólo si el concepto lo necesita |
| Óvalo discontinuo | Atributo derivado; acompáñalo de fórmula o referencia |
| Óvalos descompuestos | Atributo compuesto cuando aporte significado |
| Línea doble | Participación total en la relación |
| Línea simple | Participación parcial |
| (mínimo,máximo) | Participación de una instancia de la entidad junto a la que se coloca la etiqueta |
| ISA/EER | Especialización sólo si existe una razón real; indicar total/parcial y disjunta/solapada |

Define que “(0,N) junto a Animal” significa que un animal participa en cero o muchas instancias de esa relación. No mezcles esta interpretación con la posición de extremos de otra notación sin explicarla.

No uses flechas de flujo para representar toda relación. No conviertas cajas de tablas con columnas PK/FK en un MER Chen cambiándoles el título. El diagrama de tablas se entrega aparte.

Una FK NOT NULL no convierte automáticamente una entidad en débil. Distingue dependencia de existencia, dependencia de identificación y participación total. “Subordinación” debe explicarse en esos términos, no como una palabra decorativa.

Entidades débiles justificadas:

- LoteOperacion: se identifica por Operacion y numero_lote.
- ContratoVersion: se identifica por Operacion y numero_version.
- ConceptoLiquidacion: se identifica por Liquidacion y numero_concepto.
- CondicionLote: su identidad incluye versión contractual y lote de la misma operación; representa correctamente ambas dependencias en la vista detallada.

Si eliges un UUID físico adicional para una débil, conserva la clave comercial compuesta como UNIQUE y explica el mapeo. El UUID técnico no elimina la dependencia conceptual.

Parte puede actuar como comprador y vendedor. No diseñes una especialización disjunta Cliente/Proveedor que impida ese hecho. Para Compra/Venta, un atributo tipo inmutable es suficiente en el MVP; una especialización EER sólo se agrega si se documenta y se refleja en reglas y tablas coherentes.

## 7.2 Láminas y calidad visual

Produce:

1. Vista general conceptual por dominios, sin saturarla de atributos técnicos.
2. Identidad, contrapartes y sedes.
3. Operaciones, lotes, condiciones y pesajes.
4. Inventario, selección de venta, reserva y movimientos.
5. Liquidaciones, costos, pagos y aplicaciones.
6. Evidencia, revisiones, periodos y auditoría.
7. Diagrama lógico relacional por módulos con referencias entre láminas.

Fuentes editables preferidas: archivos .drawio con objetos y conectores reales. Exporta SVG y PDF vectoriales. Puedes usar Graphviz DOT para generar una alternativa editable reproducible, con shapes apropiados, si draw.io no está disponible; explica el formato entregado. No insertes una imagen plana en un .drawio y la presentes como elementos editables. [F43]

La lámina general puede ser A2/A1 si lo requiere el contenido; las vistas detalladas deben funcionar en A3 horizontal o en un tamaño equivalente legible. Comprueba texto, acentos, cortes, superposiciones, cardinalidades y continuidad de conectores en cada exportación.

Usa una composición sobria: fondo claro, líneas uniformes, tipografía legible, jerarquía de títulos, identificadores estables, leyenda, fecha y versión. Los colores pueden ayudar a distinguir dominios, pero la interpretación debe sobrevivir a impresión en blanco y negro. No agregues elementos decorativos que compitan con las relaciones.

No prometas que un diagrama “no parece hecho con IA”. Entrega un diagrama que pueda defenderse profesionalmente por su semántica, edición y revisión.

## 7.3 Matriz de relaciones mínima

Completa esta base en docs/database/relationship-matrix.md. Los rangos se leen como “para una instancia del primer concepto, cuántas del segundo”. Registra aparte mínimos del otro extremo, participación y condición por estado.

| ID | Relación expresada como verbo | Cardinalidad y condición | Identificación |
|---|---|---|---|
| REL-01 | Empresa administra Sucursal | Empresa 0..N sucursales; cada sucursal 1 empresa | No identificante para una sucursal con clave propia |
| REL-02 | Sucursal tramita Operacion | Sucursal 0..N operaciones; cada operación 1 sede | Dueño de escritura inmutable |
| REL-03 | Parte interviene en Operacion | Parte 0..N operaciones; cada operación 1 contraparte | Roles comprador/vendedor según tipo |
| REL-04 | Animal posee Identificacion | Animal 0..N registros de identificación; cada registro 1 animal | Unicidad del código normalizado en el maestro |
| REL-05 | Operacion contiene LoteOperacion | Borrador 0..N; confirmada 1..N; cada lote 1 operación | Identificante, débil con numero_lote |
| REL-06 | Operacion conserva ContratoVersion | Borrador 0..N versiones; confirmada referencia 1 aceptada | Identificante, numero_version |
| REL-07 | ContratoVersion establece CondicionLote | Versión 0..N condiciones; aceptada cubre los lotes vigentes | Clave de versión más lote |
| REL-08 | Lote de compra selecciona Animal | N:M histórica mediante SeleccionCompra | Un animal una vez por operación de compra |
| REL-09 | SeleccionCompra origina PosicionInventario | Selección 0..1 posición; tras confirmación 1 | Posición con identidad de ciclo propia |
| REL-10 | Animal participa en PosicionInventario | Animal 0..N posiciones históricas; posición 1 animal | Máximo 1 activa es regla temporal adicional |
| REL-11 | Lote de venta selecciona PosicionInventario | N:M histórica mediante SeleccionVenta | Sólo un compromiso comercial vigente por posición |
| REL-12 | SeleccionVenta mantiene ReservaVenta | Selección 0..N reservas históricas; cada reserva 1 selección | Máximo 1 activa por posición |
| REL-13 | PosicionInventario registra MovimientoInventario | Posición 0..N movimientos; cada movimiento 1 posición | Fuerte con evento propio; historia inmutable |
| REL-14 | LoteOperacion recibe Pesaje | Lote 0..N pesajes; pesaje 1 lote | Pesaje con identidad propia |
| REL-15 | Pesaje comprende Animal | N:M mediante PesajeAnimal | Conjunto aprobado inmutable; peso individual opcional real |
| REL-16 | Operacion origina Liquidacion | Borrador 0..1 principal; confirmada 1 principal | Liquidación fuerte; UK de operación principal |
| REL-17 | Liquidacion desglosa ConceptoLiquidacion | Borrador 0..N; confirmada 1..N conceptos | Identificante, numero_concepto |
| REL-18 | Operacion incurre en GastoOperacion | Operación 0..N gastos; gasto 1 operación | Fuente de costo trazable |
| REL-19 | Fuente de costo se distribuye en PosicionInventario | Fuente 1..N asignaciones al aprobar; posición 0..N fuentes | XOR de origen tipado; no FK polimórfica libre |
| REL-20 | Pago se aplica a Liquidacion | N:M mediante AplicacionPago con importe y fecha | Aplicación con identidad propia y reverso enlazado |
| REL-21 | Liquidacion recibe AjusteLiquidacion | Liquidación 0..N ajustes; ajuste 1 liquidación | Registro independiente, no sobrescritura |
| REL-22 | Operacion incorpora Documento | N:M mediante OperacionDocumento | Archivo privado; otras referencias específicas tipadas |
| REL-23 | RevisionAdministrativa examina Documento | N:M mediante RevisionDocumento | Alcance/criterio y resultado registrados |
| REL-24 | PeriodoCierre conserva CierrePeriodoVersion | Periodo 0..N actas/versiones | Versiones inmutables; cierres y reaperturas trazados |
| REL-25 | PosicionInventario acumula AsientoValoracion | Posición 0..N eventos de valoración | Cada evento referencia fuente y periodo de registro |

Explica relaciones recursivas de corrección/reverso en documento, pago, aplicación, pesaje o asiento, si se emplean. Distingue “corrige”, “revierte” y “reembolsa”: no son sinónimos.

La matriz es punto de partida. Contrástala con casos normales, borradores, errores, devolución y recompra; corrige cualquier cardinalidad que no puedas defender con un ejemplo.

# 8. Modelo relacional, diccionario y normalización

## 8.1 Convenciones

Adopta nombres canónicos en español para el dominio y snake_case para tablas/columnas. En este documento “sede” corresponde a sucursal; “contraparte/tercero” a parte; “establecimiento” a predio; “acuerdo” a contrato_version. Documenta los sinónimos y usa un nombre estable en el código.

E significa empresa_id y S significa sucursal_id en las tablas siguientes; no uses esas abreviaturas como nombres de columnas finales.

- Maestros: PK(E,id), salvo empresa cuya PK es id y catálogos globales de código.
- Cabeceras de negocio locales: PK(E,S,id).
- FKs locales incluyen E y S; las referencias a maestros incluyen E.
- No permitas que un UUID existente de otra empresa satisfaga una FK por sí solo.
- Animal mantiene UNIQUE(E,sede_operadora_id,id); la posición referencia (E,S,animal_id) contra esa clave.
- UUID es identidad técnica; la identidad oficial se controla mediante animal_identificacion en A.
- Usa timestamptz para instantes, date para fechas civiles y la zona del equipo para presentar.
- Cantidades, monedas, estados, fuentes y unidades son tipados. JSONB sólo para datos realmente variables, metadata de integración o snapshots documentados.
- Define DELETE/UPDATE RESTRICT para hechos comprometidos. CASCADE sólo en dependencias editables de borrador cuando sea seguro y esté justificado.
- Todo importe puede explicar su origen. No crees un saldo editable paralelo al saldo derivado.
- Comprueba valores especiales de NUMERIC además de rangos: no aceptar NaN/infinito como peso o importe.
- version_lock sirve para detectar edición concurrente de borradores; no reemplaza los bloqueos de disponibilidad monetaria o inventario.

## 8.2 Catálogo de tablas candidato

Esta base incluye soporte técnico y controles de cierre. No fuerces un número de tablas para “hacerlo grande”. Si la simplificas o amplías, demuestra que conserva las reglas y actualiza todos los diagramas.

| ID | Relación propuesta | Claves/referencias y responsabilidad |
|---|---|---|
| ENT-01 | empresa | PK(id). Perfil de la empresa cliente; maestro A. No necesita una FK circular hacia parte para el MVP. |
| ENT-02 | sucursal | PK(E,id); UK(E,codigo). FK empresa; maestro A. |
| ENT-03 | parte | PK(E,id). Persona/organización contraparte con datos mínimos; puede comprar y vender; maestro A. |
| ENT-04 | predio | PK(E,id); FK(E,parte_responsable_id) cuando proceda. Origen/destino/custodia declarados; maestro A. |
| ENT-05 | usuario | PK(E,id); UK(E,login_normalizado). Hash de contraseña y estado; maestro A. |
| ENT-06 | rol_aplicacion | PK(codigo). Catálogo controlado ADMIN/OPERADOR/CAJA/AUDITOR; no confundir con roles PostgreSQL. |
| ENT-07 | membresia_usuario | PK(E,S,usuario_id,rol_codigo); FKs completas. Autorización por sede; maestro A. |
| ENT-08 | animal | PK(E,id); UK(E,sede_operadora_id,id). Identidad estable, sede operadora y datos declarados; maestro A. |
| ENT-09 | operacion | PK(E,S,id); FKs contraparte/predios; tipo COMPRA/VENTA inmutable; moneda, folio, versión y estados explícitos; escritor local. |
| ENT-10 | lote_operacion | PK(E,S,operacion_id,numero_lote). Dependencia identificante de operación; grupo comercial. |
| ENT-11 | seleccion_compra | PK(E,S,operacion_id,numero_lote,animal_id); UK(E,S,operacion_id,animal_id). FK lote/animal; operación sólo COMPRA. |
| ENT-12 | seleccion_venta | PK(E,S,operacion_id,numero_lote,posicion_id); UK(E,S,operacion_id,posicion_id). FK lote/posición; operación sólo VENTA. |
| ENT-13 | posicion_inventario | PK(E,S,id); FK animal/selección de compra; UK(E,S,animal_id,numero_ciclo); UK(E,S,compra_operacion_id,compra_numero_lote,animal_id) para que una selección origine una sola posición; UNIQUE parcial(E,animal_id) para ciclo activo. |
| ENT-14 | movimiento_inventario | PK(E,S,id); FK posición, operación y predio/parte cuando procedan. Hechos físicos, titular declarado y disposición; inmutable. |
| ENT-15 | reserva_venta | PK(E,S,id); FK selección de venta/posición. Vence en instante explícito; UNIQUE parcial por posición con estado ACTIVA. |
| ENT-16 | contrato_version | PK(E,S,operacion_id,numero_version); FK documento. Versión aceptada inmutable. |
| ENT-17 | condicion_lote | PK(E,S,operacion_id,numero_version,numero_lote); FKs a versión y lote. Precio, unidad, base de pesaje y descuentos. |
| ENT-18 | pesaje | PK(E,S,id); FK lote, documento y corrección original. Modo BRUTO_TARA o NETO_REPORTADO, evidencia y aprobación. |
| ENT-19 | pesaje_animal | PK(E,S,pesaje_id,animal_id); FKs pesaje/animal. Composición congelada; peso individual nullable si no fue medido. |
| ENT-20 | gasto_operacion | PK(E,S,id); FK operación, proveedor/documento y fuente corregida cuando proceda. Naturaleza COSTO/BONIFICACION, importe absoluto positivo, signo derivado y clasificación capitalizable/directa; original inmutable al aprobar. |
| ENT-21 | asignacion_costo | PK(E,S,id); FK posición y exactamente una fuente tipada: concepto_liquidacion, gasto_operacion o ajuste_liquidacion de compra. Método, base congelada, importe firmado y lote de reparto. |
| ENT-22 | liquidacion | PK(E,S,id); UK(E,S,operacion_id) para principal; FK operación/versión. Importe y datos aceptados congelados. |
| ENT-23 | concepto_liquidacion | PK(E,S,liquidacion_id,numero_concepto); FK identificante liquidación y referencias a lote/condición/pesaje aplicables. |
| ENT-24 | ajuste_liquidacion | PK(E,S,id); FK liquidación/documento/original si revierte. Naturaleza CARGO/ABONO, monto positivo y motivo. |
| ENT-25 | pago | PK(E,S,id); FK parte/documento/pago de origen para devolución de dinero. Tipo, importe positivo, confirmación y evidencia. |
| ENT-26 | aplicacion_pago | PK(E,S,id); FKs pago/liquidación; FK reverso_de_id cuando corresponda. Importe, naturaleza y control de reversión. |
| ENT-27 | documento | PK(E,S,id). Clave privada, hash, tamaño, MIME, versión, documento_previo_id y propietario_escritura derivado del contexto; nunca sobrescribir bytes aceptados. Evidencia maestra en A, de operación en su dueño. |
| ENT-28 | operacion_documento | PK(E,S,operacion_id,documento_id); FKs explícitas. Evidencia general de operación. |
| ENT-29 | auditoria_evento | PK(E,S,id); actor, comando, correlación, nodo_origen y cambio pertinente. Sólo se genera en origen; se replica como dato. |
| ENT-30 | evento_outbox | PK(E,S,id). Hecho inmutable con versión del payload, nodo_origen y propietario_despacho; misma transacción que negocio. S no determina el escritor de maestros. |
| ENT-31 | mensaje_inbox | PK(consumidor,fuente_id,event_id), con E/S en el scope cuando aplique. Deduplicación verificable. |
| ENT-32 | clave_idempotencia | PK(E,S,principal_id,comando,clave). Hash de petición, estado/resultado; persistida con el comando local. |
| ENT-33 | infra.nodo_config | Configuración local, mapeo de rol técnico a propietario y empresa; no replicar ni permitir modificación por app. |
| ENT-34 | infra.entrega_outbox | PK(evento_id,destino). Intentos, próximo intento y confirmación; local, no replicada. |
| ENT-35 | infra.importacion_fuente | Fuente, corte, hash, conteos/errores y actor. Bitácora de importación, scope de deduplicación explícito. |
| ENT-36 | animal_identificacion | PK(E,id); FK animal; UK(E,sistema,codigo_normalizado). Vigencia/estado/evidencia del código; maestro A. |
| ENT-37 | periodo_cierre | PK(E,S,id); intervalo civil, estado y version_lock. Periodos no solapados dentro de la sede. |
| ENT-38 | cierre_periodo_version | PK(E,S,periodo_id,numero_version). Acta de cierre/reapertura, actor, motivo y corte/hash de conciliación. |
| ENT-39 | asiento_valoracion | PK(E,S,id); FK posición, periodo y fuente tipada/asignación. Evento de costo, salida o ajuste con signo/naturaleza documentados. |
| ENT-40 | revision_administrativa | PK(E,S,id); exactamente una FK tipada a operacion o animal_identificacion; revisión anterior si corrige, responsable y nodo_origen. Revisión de identidad en A, de operación en su dueño; criterio y resultado administrativos. |
| ENT-41 | revision_documento | PK(E,S,revision_id,documento_id). FK revisión/documento; resultado y observación de cada evidencia examinada. |

Tablas de soporte como Flyway, sesiones o catálogos cerrados pueden existir además, pero no inflan artificialmente el MER del negocio. Diagrámales en una vista técnica separada.

No modeles todos los vínculos críticos como entity_type + entity_id sin FK. En documentos genéricos conserva asociaciones explícitas; en costos define columnas fuente mutuamente excluyentes o un supertipo real con referencias verificables. Si escoges el supertipo, documenta su integridad y actualiza este catálogo.

## 8.3 Detalles que no debes omitir

**Identificación animal.** animal_identificacion, no un campo repetido en cada compra, es el registro de códigos. Conserva anteriores/inactivos y su procedencia. Un código declarado sólo se asocia a una identidad canónica de esa empresa. Normalizar texto no significa certificar autenticidad. Las colisiones, pérdida de arete y captura errónea requieren revisión central; no implementes una fusión automática ni reasignación silenciosa de códigos en el MVP. Los animales con situación de identidad sin resolver pueden quedar en borrador y no habilitar nuevos compromisos incompatibles.

**Recompra y disposición.** Un ciclo cerrado por venta/entrega puede dar lugar a recompra. Un animal registrado como muerto no se habilita para venderlo porque su ciclo esté cerrado. Las correcciones de una mortalidad mal capturada necesitan procedimiento autorizado, evidencia y reverso; no un cambio libre de estado.

**Compra y recepción.** Confirmar compra crea la posición. Si la recepción física todavía es requisito pendiente de la política aceptada, la posición se identifica como pendiente y no se ofrece como disponible para venta. Se permiten cotizaciones preliminares claramente separadas.

**Ticket neto.** Si el comprobante sólo informa neto, usa NETO_REPORTADO y no inventes bruto/tara. Si hay bruto y tara, valida la igualdad con la precisión declarada. La composición de pesaje_animal se contrasta con el lote y se congela al aprobar.

**Fuentes de costo.** El monto capitalizable de una compra y sus gastos se distribuyen una sola vez. No capitalices el mismo flete en concepto_liquidacion y gasto_operacion como si fueran hechos distintos. Conserva referencia de origen para detectar duplicados. No se contempla un módulo completo de cuentas por pagar a transportistas y otros gastos: si se incorpora, diseña su obligación y pago explícitos.

**Valoración.** asignacion_costo explica el reparto de una fuente. asiento_valoracion registra su efecto temporal en inventario o costo reconocido. No sumes ambos como si fueran dos costos. La vista de valoración usa una fuente canónica definida; la asignación es su soporte.

**Costos tardíos.** No alteres importes congelados. Reparte sobre las posiciones originales con su base histórica aprobada y clasifica el destino económico: si la posición permanece capitalizada, ajusta inventario; si tiene venta reconocida vigente, ajusta el costo de esa venta; si se dio de baja por pérdida/muerte, ajusta la pérdida vinculada y mantiene inventario cero. Una posición anulada no recibe costos nuevos sin resolver la anulación. Una posición VENDIDA_PENDIENTE_ENTREGA ya tiene inventario gerencial cero. Conserva fecha económica y fecha/periodo de registro. Las bonificaciones producen el efecto contrario bajo límites; no permitir costo acumulado negativo sin otra clase económica definida. Ningún costo tardío reabre existencias por sí solo.

**Periodo cerrado.** Los reportes publicados del cierre conservan su corte. Un ajuste posterior se registra en un periodo abierto con referencia al origen; una reapertura requiere permiso y una nueva versión de cierre. No recalcules silenciosamente un cierre ya emitido con datos posteriores.

**Aplicaciones/reembolsos.** Un reverso de aplicación libera importe previamente aplicado; un reembolso es salida/entrada real de dinero y consume la disponibilidad del pago de origen. Bloquea pago y obligación antes de comprobar sumatorias. Para el MVP usa reverso completo de una aplicación como evento único, seguido de nueva aplicación si hace falta corregir parcialmente; así evitas reversos parciales acumulados ambiguos.

**Documentos y revisiones.** Cada archivo reemplazado obtiene otro registro/versionado; una revisión conserva qué versión exacta vio. Emisor, folio, finalidad, origen, destino y vigencia se registran cuando el tipo documental lo requiere. Una revisión administrativa con observaciones no se rotula como permiso sanitario. No hagas que una sustitución de PDF invalide o apruebe silenciosamente una revisión anterior.

## 8.4 Entregables del modelo lógico y físico

Antes del DDL definitivo entrega, para CADA tabla:

- Propósito y relación con las RN.
- Notación relacional con PK, claves candidatas, UK y FK completas.
- Atributos, tipo/dominio, longitud, precisión, nulabilidad, default y unidades.
- Restricciones de fila, entre filas y temporales.
- Política de actualización/borrado y retención histórica.
- Índices propuestos y consulta/caso que cada uno favorece.
- Propietario de escritura, participación en publicación/replicación y sensibilidad de datos.
- Ejemplo válido y ejemplo que debe rechazarse.
- Transformación de entidad, relación o atributo conceptual al esquema lógico.

Documenta dependencias funcionales y claves candidatas para todo el esquema. Desarrolla por lo menos tres ejemplos completos de transformación y normalización: operación/contraparte, versión/condición por lote y liquidación/aplicaciones. Explica 1FN, 2FN y 3FN con datos del proyecto; evalúa BCNF y las consecuencias para preservación de dependencias y unión sin pérdida. No declares “todo en 3FN” sólo porque cada tabla tiene un UUID. [F15]

Genera después SQL PostgreSQL real mediante migraciones versionadas. No uses ddl-auto=create/update como fuente del diseño. No llames “modelo relacional completo” a una imagen sin claves o a una lista de nombres.

# 9. Stack y arquitectura de software

## 9.1 Stack base y extensiones compatibles

| Capa | Decisión propuesta | Justificación y límite |
|---|---|---|
| Backend | Java 21 LTS + Spring Boot 4.x, Spring Web, Validation y Security | Conserva Java del requisito, tipado y ecosistema de servidor; fijar patch compatible tras revisar BOM/documentación [F18] |
| Construcción | Maven Wrapper | Compilación reproducible sin depender de una instalación Maven arbitraria |
| Acceso a datos | Spring JDBC/JdbcTemplate y SQL explícito | Hace visibles consultas, PL/pgSQL y transacciones para la materia; mapeos separados del dominio [F19] |
| Migraciones | Flyway versionado | DDL rastreable; bootstrap de replicación separado de migraciones transaccionales |
| Persistencia | PostgreSQL 18, PL/pgSQL y extensiones justificadas | Esquema relacional y funciones concretas; misma versión mayor en A/B |
| Conexión | Pgpool-II estable compatible, una instancia raw por dueño; Hikari acotado | Cumple requisito de Pgpool sin atribuirle resolución de conflictos [F28] |
| Interfaz | React + TypeScript + Vite, router y cliente HTTP tipado | Aplicación operativa rápida, componentes y validación de tipos; versiones exactas verificadas [F45–F46] |
| Estado remoto | TanStack Query o alternativa equivalente documentada | Caché, invalidación y reintentos explícitos; no reintentar automáticamente comandos monetarios sin idempotencia |
| Formularios | React Hook Form y Zod, si el equipo confirma compatibilidad | Validación de captura y mensajes; servidor sigue siendo autoridad |
| Diseño UI | CSS con tokens o Tailwind; componentes accesibles documentados | Elegir una estrategia y mantener consistencia; no mezclar bibliotecas visuales redundantes |
| Pruebas | JUnit + Testcontainers PostgreSQL; pruebas frontend y Playwright para flujos críticos | BD real para concurrencia y SQL específico; no sustituirla con H2 [F47] |
| Infraestructura | Docker Compose + Caddy + Linux VPS | Entorno reproducible y HTTPS; documentar límite de un solo host [F30–F32] |
| Evidencia | Almacenamiento privado mediante interfaz DocumentStorage | Adaptador local para desarrollo y destino privado con respaldo para piloto; contenido fuera de tablas de negocio |
| Integración académica | postgres_fdw a un tercer PostgreSQL | Proveedor/báscula/transportista simulado, sólo lectura [F27] |
| Innovación útil | Simulador de margen, QR interno, OCR supervisado opcional y expediente explicable | Cada añadido debe resolver una tarea medible |
| Contexto del desarrollo | Graphify-Labs/graphify, paquete graphifyy, más Markdown/ADR | Grafo de documentación/código, no dependencia de ejecución del SaaS [F36–F40] |

La documentación consultada de Spring Boot mostraba 4.1.1 y compatibilidad con Java 21. Verifica el estado al iniciar y fija una versión estable mediante BOM y lockfiles. El objetivo es una combinación soportada y reproducible, no usar por obligación el número más reciente.

Registra en docs/architecture/versions.md: componente, versión exacta, fuente oficial consultada, compatibilidad, licencia relevante y forma de actualización. Haz lo mismo con Node, gestor de paquetes y librerías frontend. No copies dependencias sin comprobar que sus versiones funcionan juntas.

No agregues Kafka, Kubernetes, múltiples microservicios, Neo4j o un servicio Python al runtime sin un requisito que lo justifique. OCR, si se implementa, entra por un puerto/adaptador y entrega propuestas revisables. No coloques un modelo generativo en la ruta que decide el importe de un pago.

## 9.2 Monolito modular

Un backend Java desplegable, organizado por módulos de dominio:

1. Acceso y organización.
2. Contrapartes y establecimientos.
3. Identidad animal maestra.
4. Inventario, lotes y disponibilidad.
5. Operaciones y contratos.
6. Pesajes y evidencia.
7. Liquidaciones, costos y periodos.
8. Pagos y cartera.
9. Reportes e integraciones.
10. Auditoría y administración operativa.

Dentro de cada módulo separa domain, application y adapters cuando exista esa responsabilidad. Evita una carpeta services con toda la lógica de negocio mezclada.

- domain: conceptos, value objects, estados e invariantes independientes de HTTP.
- application: casos de uso, autorización del comando, selección de propietario y coordinación transaccional.
- adapters/in: controladores HTTP, importación y tareas internas.
- adapters/out: JDBC, archivos, OCR/FDW y publicación de eventos.
- shared: sólo tipos pequeños realmente compartidos; no un depósito de utilidades del negocio.

Cada módulo expone puertos/casos de uso definidos. No accede libremente a los repositorios privados de otro. Un monolito modular puede usar una transacción local compartida para una confirmación coordinada; eso no requiere convertirlo en microservicios.

## 9.3 POO, SOLID y patrones que debes demostrar

| Principio/patrón | Uso concreto | Evidencia |
|---|---|---|
| Encapsulación | PosicionInventario y Liquidacion restringen transiciones válidas | Métodos de dominio, no setters públicos indiscriminados |
| Value Object | Money, PesoKg, IdentificadorAnimal, Periodo | Validación de unidad/escala y operaciones explícitas |
| SRP | Cálculo, persistencia, autorización y generación de archivo con responsabilidades separadas | Clases y módulos con propósito defendible |
| OCP | Estrategias de base por kg/cabeza y asignación de costos | Agregar una estrategia sin reescribir el controlador |
| LSP | Adaptadores cumplen resultados/errores del mismo puerto | Pruebas de contrato cuando haya implementaciones sustituibles |
| ISP | Puertos pequeños para consulta, comandos y archivos | No interfaces gigantes de repositorio genérico |
| DIP | Casos de uso dependen de puertos | JDBC/almacenamiento inyectados, no construidos dentro del caso |
| Repository/Query Object | Persistencia SQL parametrizada por agregado/consulta | Mapeos y consultas explícitas |
| Strategy | Selección de criterio de reparto/base aceptada | Estrategias nombradas y pruebas de sus decisiones |
| State, si aporta claridad | Transiciones de operación/reserva/periodo | Tabla de estados y rechazo de transición inválida |
| Adapter | Archivo local/privado, OCR y fuente externa | Formato externo separado del dominio |
| Transactional Outbox | Evento consistente con el cambio de negocio | Inserción en misma transacción, despacho y deduplicación |

No crees clases o herencias artificiales sólo para decir que usaste un patrón. Evita implementar el cálculo monetario tres veces de forma distinta: Java coordina y selecciona estrategias; el cálculo que confirma importes proviene de las funciones canónicas SQL y sus snapshots. La previsualización usa esa misma lógica sin mutar. Los value objects Java validan y manejan resultados; si una fórmula se replica por necesidad técnica, comparte vectores GOLD y demuestra equivalencia.

Documenta en docs/academic/oop-solid-patterns.md qué principio se observa, en qué archivo y cómo se verifica. No atribuyas SOLID al sistema por usar Spring.

## 9.4 Topología

Crea diagramas de contexto, contenedores y despliegue, más secuencias de ConfirmarVenta y AplicarPago. El esquema orientativo siguiente es de infraestructura; NO reemplaza el MER Chen.

~~~mermaid
flowchart TB
    U["Navegador"] --> C["Caddy · HTTPS"]
    C --> F["Frontend React"]
    C --> API["API Java · monolito modular"]
    API --> PA["Pgpool A · raw"]
    API --> PB["Pgpool B · raw"]
    PA --> A["PostgreSQL A · dueño A y maestros"]
    PB --> B["PostgreSQL B · dueño B"]
    A <-->|"Replicación lógica asíncrona"| B
    A -. "FDW de lectura" .-> X["PostgreSQL externo simulado"]
    API --> D["Documentos privados"]
~~~

Cada instancia PostgreSQL es un cluster separado, con volumen y parámetros propios. La conexión de replicación es PostgreSQL a PostgreSQL; no pasa por el balanceo de Pgpool.

Los catálogos maestros se escriben en A. Las operaciones locales y sus hijos se escriben únicamente en su propietario. El frontend solicita una sede autorizada; el backend deriva y verifica el dueño. Nunca acepta un host/connection-string enviado por el usuario.

La matriz de propiedad se aplica por tipo de agregado, no sólo por sucursal_id. Un alta de animal o membresía destinada a B sigue siendo una escritura maestra en A. Sus revisiones, evidencia, auditoría y outbox conservan nodo_origen/propietario de escritura o despacho explícito, aunque S represente B. Los comandos derivan esos campos y las guardas los verifican; el cliente no los elige. La evidencia de identidad se carga/revisa por el flujo maestro en A y la de una operación por el dueño de la operación. Documenta esa excepción en las publicaciones, permisos y trabajadores. No hagas que B despache un evento maestro recibido por replicación por el solo valor de S.

Antes de iniciar una transacción, OwnerDatabaseRouter determina A o B. BranchTransactionRunner usa el TransactionTemplate y JdbcTemplate del mismo DataSource durante todo el caso. No cambies una variable de enrutamiento después de que Spring adquirió la conexión. No combines dos gestores de transacción fingiendo atomicidad distribuida.

El alta de una nueva identidad para B se procesa en A, se espera su visibilidad en B y luego se confirma la operación de B. Es un flujo explícito con estado pendiente y reintento; no una transacción entre ambos nodos.

## 9.5 ADR obligatorios

Crea al menos:

- ADR-001: monolito modular frente a microservicios.
- ADR-002: SQL explícito, cálculo canónico y migraciones.
- ADR-003: animal permanente y posición por ciclo.
- ADR-004: reconocimiento gerencial y costo por posición.
- ADR-005: maestro de identidad y propiedad de escritura inmutable.
- ADR-006: replicación bidireccional, bootstrap y recuperación.
- ADR-007: Pgpool raw y presupuesto de conexiones.
- ADR-008: autenticación, permisos y aislamiento del piloto.
- ADR-009: documentos privados, evidencia y revisión.
- ADR-010: despliegue, respaldos y límites de disponibilidad.
- ADR-011: Graphify y mantenimiento del contexto.
- ADR-012: alcance aplazado y condiciones para comercializar.

Cada ADR identifica alternativas razonables, decisión propuesta/aceptada, consecuencias y requisito atendido. No inventes un acta de aprobación del equipo.

# 10. Administración de BD, PL/pgSQL y transacciones

## 10.1 Distribución de controles

| Control | Lugar principal |
|---|---|
| Valores obligatorios, rangos y combinaciones de columnas | NOT NULL, tipos y CHECK de una fila |
| Identidad, no duplicación y referencias del mismo scope | PK, UNIQUE y FK compuestas |
| Una posición/reserva activa | Índice UNIQUE parcial con estado explícito |
| Sumatorias de aplicaciones, asignaciones y ajustes | Comando PL/pgSQL + bloqueos de filas cabecera |
| Inmutabilidad y propiedad de escritura | Privilegios y triggers específicos |
| Autorización de usuario, petición y caso de uso | Spring Security + application |
| Cálculo confirmado y snapshot | Funciones SQL canónicas y transacción local |
| Guía de captura y mensajes | Frontend; no única barrera de integridad |
| Auditoría de hechos | Inserción/triggers en el escritor, sin duplicación en apply |
| Límites de periodos y concurrencia de cierre | Bloqueo del periodo común a todas las contabilizaciones |

Un CHECK no debe consultar otras filas para garantizar un saldo o sumatoria. Las restricciones declarativas y los comandos bloqueados resuelven funciones distintas. Tampoco uses un índice con now() para decidir reservas vigentes. La expiración cambia el estado mediante un comando y se revalida al confirmar. [F20–F21]

## 10.2 Comandos que debes diseñar e implementar

Define firmas, entradas, permisos, resultado, RN, locks, SQLSTATE y pruebas para:

1. RegistrarIdentidadAnimal, ejecutado en maestro A.
2. ReservarPosiciones y Liberar/ExpirarReserva.
3. ConfirmarCompra.
4. ConfirmarVenta.
5. AprobarPesaje y RegistrarCorreccionPesaje.
6. DistribuirCosto y RegistrarCostoTardio.
7. Registrar/ConfirmarPago.
8. AplicarPago.
9. RevertirAplicacion y RegistrarReembolso/Reintegro.
10. AjustarLiquidacion.
11. RegistrarRecepcion/Entrega.
12. RegistrarBajaInventario.
13. CerrarPeriodo y ReabrirPeriodo.
14. ValidarConciliacionDelPropietario.

No requieren un stored procedure por cada botón. Usa funciones/procedimientos con límites claros, sin HTTP, correo, OCR ni llamadas externas dentro de triggers. Incluye triggers para inmutabilidad, protección de columnas propietarias y auditoría donde sean apropiados.

Si Spring controla la transacción, las funciones llamadas no ejecutan COMMIT interno. El bootstrap que crea slots/suscripciones se ejecuta por separado.

## 10.3 Concurrencia e idempotencia

ConfirmarVenta debe:

1. Resolver usuario, empresa, sede y propietario.
2. Abrir una transacción local.
3. Reclamar la clave idempotente del comando y validar el hash.
4. Bloquear periodo, operación y posiciones en un orden global documentado.
5. Comprobar versión de borrador, condiciones, pesajes aprobados, costo, disponibilidad y reserva.
6. Congelar la liquidación, registrar el costo reconocido, comprometer las posiciones, consumir reservas y crear auditoría/outbox.
7. Guardar el resultado reproducible y confirmar.
8. Si falla cualquier paso, revertir todos los efectos.

AplicarPago bloquea pago y liquidaciones en orden estable; verifica moneda, contraparte, sede y disponibilidad. Dos solicitudes concurrentes no pueden gastar el mismo saldo.

El cierre de periodo y cada comando que imputa hechos bloquean la misma fila de periodo. El costo tardío y el reconocimiento de venta bloquean la misma posición. Así se resuelven las carreras entre ambos hechos.

Usa READ COMMITTED con bloqueos explícitos para estos flujos, o justifica SERIALIZABLE y reintentos. Para SQLSTATE 40001/40P01 aplica reintento acotado del comando completo, conservando la misma clave. No reintentes errores de dominio o permisos.

Persistir idempotencia en memoria o en un caché local no basta. La clave se limita por E/S/principal/comando y su resultado se escribe atómicamente con el efecto. Mismo identificador con contenido distinto devuelve 409. Documenta retención y no eliminar claves mientras un reintento válido pueda duplicar dinero.

Los cambios de borrador usan version_lock/If-Match o equivalente. La interfaz informa el conflicto y ofrece recargar; no sobrescribe otra edición por conveniencia.

## 10.4 Roles y privilegios

Diferencia usuarios del producto de usuarios PostgreSQL.

| Rol técnico | Propósito |
|---|---|
| bovi_owner, NOLOGIN | Dueño de objetos |
| bovi_migrator | Aprovisionamiento y migraciones controladas; no usado por la app |
| bovi_app_a / bovi_app_b | Ejecución limitada al propietario configurado |
| bovi_command, NOLOGIN | Dueño de funciones privilegiadas estrictas, si son necesarias |
| bovi_auditor | Lecturas permitidas, sin mutaciones |
| bovi_repl | Replicación, separado de app y restringido por red |
| bovi_fdw_read | SELECT sobre objetos autorizados del tercero |
| bovi_monitor / bovi_backup | Permisos de observación/respaldo documentados |

La app no usa superusuario, BYPASSRLS ni propiedad de tablas. Restringe DML financiero directo y concede EXECUTE en comandos autorizados. Si usas SECURITY DEFINER, fija search_path seguro, califica objetos y revoca EXECUTE de PUBLIC cuando corresponda. No permitas a la app cambiar session_replication_role, funciones, esquemas o configuración del nodo.

Para el piloto comercial inicial: una empresa por despliegue, una o dos sedes. El modelo conserva empresa_id y referencias completas para crecimiento. No vendas aislamiento multiempresa compartido hasta implementar y verificar sus políticas negativas.

Si aplicas RLS, describe la identidad real de las conexiones, los roles de propietario y del apply. Un GUC app.empresa_id modificable no es por sí solo una frontera frente a un atacante con esa conexión. El actor HTTP se valida en el servidor; el scope de la conexión se limita mediante configuración que la app no puede editar. [F26]

Entrega scripts de creación, grants/revokes, rotación de credenciales y pruebas de permisos. Nunca incluyas contraseñas reales en README, migraciones, demos o grafo.

## 10.5 Consultas, índices y mantenimiento

Diseña consultas de inventario disponible, ficha por identificador, cartera vencida, detalle de liquidación y margen. Propón índices por filtros y joins reales, considerando E/S/estado/fecha y selectividad.

Usa EXPLAIN (ANALYZE, BUFFERS) en datos sintéticos de volumen declarado y evita ejecutar análisis mutante sobre datos reales sin evaluar su efecto. Registra plan, filas, tiempo y entorno. No agregues índices a todas las columnas: afectan escritura y almacenamiento.

Documenta autovacuum/ANALYZE, estadísticas, conexiones, crecimiento de tablas/auditoría, espacio de discos, WAL retenido y consultas lentas. Los umbrales iniciales son objetivos operativos que deberán calibrarse.

# 11. Replicación M–M y FDW: demostración rigurosa

## 11.1 Política de propiedad

La solución es replicación lógica bidireccional A ↔ B con escritor exclusivo por agregado. Ambos nodos aceptan operaciones de su sede. Los maestros se originan sólo en A. No se pretende que A y B editen simultáneamente una misma fila.

Usa origin = none en las suscripciones compatibles para evitar reenvío de cambios ya originados por replicación. Esa opción no resuelve conflictos de negocio ni garantiza unicidad entre escritores independientes. [F22]

Publica una matriz tabla → propietario → dirección → política de UPDATE/DELETE. Usa listas explícitas de tablas publicadas. Incluye padres e hijos que deban convivir, así como el evento de auditoría originado con el hecho.

No cambies la sede de un animal con UPDATE para “moverlo” entre propietarios. Esa evolución necesita transferencia controlada, fencing y otro ADR.

## 11.2 Bootstrap reproducible desde bases nuevas

1. Levantar clusters A/B y fuente FDW con volúmenes independientes.
2. Aplicar DDL, extensiones, funciones, roles y configuración en ambos nodos.
3. Mantener tablas publicadas vacías antes del alta de suscripciones.
4. Crear roles/conexiones de replicación y publicaciones explícitas; en esta receta no precrear slots manualmente.
5. Crear cada suscripción con slot_name explícito, origin = none y copy_data = false; dejar que CREATE SUBSCRIPTION cree una sola vez su slot antes de insertar datos de negocio. Si otra receta precrea slots, deberá usar create_slot = false expresamente.
6. Ejecutar CREATE SUBSCRIPTION fuera de la transacción de migración cuando crea su slot.
7. Verificar procesos/estado de tablas listas.
8. Sembrar maestros únicamente en A.
9. Esperar una barrera verificable de visibilidad en B.
10. Sembrar operaciones A en A y B en B, nunca duplicar la misma semilla.
11. Comprobar conteos por dueño, PK, huérfanos y conciliaciones.
12. Abrir escrituras de la aplicación.

copy_data = false no copia datos previos. Sólo es válido para este arranque vacío o un snapshot común validado. Para datos existentes diseña un procedimiento de corte/snapshot/slots específico; no repitas la receta de cero sobre un piloto.

La aplicación no crea ni elimina suscripciones con credenciales operativas. Mantén scripts de bootstrap separados, documentados e idempotentes donde corresponda.

## 11.3 Restricciones que deben aparecer en README

- DDL, roles y secuencias no se sincronizan automáticamente por esta replicación; aplica migraciones coordinadas. Foreign tables, vistas y large objects tampoco se replican como tablas ordinarias. [F23]
- El apply lógico usa session_replication_role = replica. Por defecto no ejecuta triggers habituales; las FK, implementadas mediante triggers, tampoco se verifican allí como en el escritor. Valida en origen y concilia al converger. [F24–F25]
- UNIQUE, CHECK y NOT NULL pueden detener la aplicación por conflicto. No declares “todos los constraints se verifican de nuevo” ni “no hay conflictos”. Investiga cada error.
- No actives ENABLE ALWAYS en todo el esquema: puede duplicar auditoría/outbox o rechazar la escritura remota.
- Excluye configuración de nodo, sesiones, historial de Flyway y estado local de despacho. Si replicas evento_outbox, sólo el propietario despacha sus eventos; infra.entrega_outbox permanece local.
- Los padres maestros deben ser visibles en B antes de crear dependencias B. No existe orden global automático entre streams diferentes.
- Folios internos por empresa/sede/tipo/periodo pueden tener huecos; no son folios fiscales. UUID no crea unicidad comercial de un arete.
- Pgpool raw conecta con su backend fijo; no sincroniza las bases ni determina el propietario.
- Dimensiona Hikari + num_init_children/max_pool y combinaciones usuario/BD, más slots y administración, contra max_connections. No pegues defaults que agoten el servidor.

## 11.4 Caídas y pruebas de recuperación de enlace

Si se interrumpe sólo la replicación, cada sede opera sobre recursos propios ya registrados, con sesión y permisos vigentes. Los reportes consolidados muestran antigüedad. Si cae el dueño, no se confirma su comando en el otro nodo. Si A no está disponible, nuevas identidades y otros maestros quedan pendientes; no prometas disponibilidad del login/administración central.

Observa pg_stat_subscription, estadísticas de errores, slots, retención de WAL y procesos de apply. Mide convergencia con eventos/barreas controladas. No interpretes cualquier diferencia entre relojes como retraso exacto.

Probar: partición, escritura permitida A/B, reconexión, ausencia de bucles, auditoría sin duplicados, conciliación y bloqueo de nuevas identidades cuando su maestro falta. Documenta cómo detectar un slot invalidado o un conflicto detenido. Limitar WAL evita crecimiento ilimitado, pero puede exigir resincronización.

Si el requisito del profesor exige dos nodos modificando la misma fila libremente, informa con precisión que se necesita otro diseño de resolución de conflictos. Conserva esta implementación con su alcance descrito mientras se aclara ese requisito.

## 11.5 FDW

Levanta un tercer PostgreSQL separado que represente un proveedor simulado: tarifas de transporte por ruta y tickets de báscula de ejemplo. Su nombre y datos deben identificar la simulación.

- Crea extensión postgres_fdw, foreign server y user mapping por aprovisionamiento.
- Expón vistas/tablas autorizadas mediante IMPORT FOREIGN SCHEMA limitado.
- La credencial remota sólo tiene SELECT; la app tampoco dispone de DML sobre foreign tables.
- Prueba que INSERT/UPDATE/DELETE fallen.
- Consulta la fuente fuera de una transacción que mantenga locks financieros.
- Al aceptar una tarifa/ticket, guarda snapshot local con fuente, referencia, fecha, moneda/unidad y versión/hash.
- Define timeout, ausencia de fuente y mensaje de reintento; no emitir media liquidación.
- No anuncies conexión oficial a SINIIGA, SENASICA o una empresa real.
- postgres_fdw no ofrece preparación remota para un commit en dos fases; no lo uses como garantía de atomicidad monetaria entre servidores. [F27]

La demostración FDW debe consultar otra instancia real. Leer un CSV y llamarlo FDW no cumple AC-07.

# 12. Casos límite, API y experiencia de usuario

## 12.1 Casos adicionales que fijan el comportamiento

**GOLD-06, costo tardío y bonificación de un gasto de transporte:** partiendo de GOLD-02, llega un flete adicional de 500 repartido sobre las diez posiciones originales, 50 por cada una. Cuatro vendidas reciben 200 de ajuste de costo; seis en inventario reciben 300. Costo vendido actualizado: 4,600; inventario: 6,900; margen actualizado de la venta: 1,600. Una bonificación de 200 del transportista sobre ese mismo gasto reduce 80 de costo vendido y 120 de inventario; margen actualizado: 1,680. Conserva la fuente gasto y su corrección. No cambia el precio/deuda del ganado con vendedor ni comprador; el módulo de cuentas por pagar a transportistas no está incluido en este MVP.

Si el periodo de la venta ya se cerró, su reporte histórico conserva la versión emitida. El nuevo periodo muestra los ajustes y la ficha de operación puede mostrar margen acumulado actualizado, identificado como tal.

**GOLD-07, obligación pagada que disminuye:** liquidación 1,000, pago 1,000 aplicado completamente, bonificación comercial 100. Un comando guiado, atómico y autorizado revierte la aplicación original completa, aplica 900 y registra el ajuste de abono 100. Resultado: obligación 900, aplicaciones netas 900, saldo pendiente 0 y pago disponible 100. Un reembolso posterior de 100 deja disponible 0. No borrar historia ni restar dos veces el pago original.

**GOLD-08, pérdida de una posición:** una posición sin venta reconocida cuesta 1,100 y se da de baja por una pérdida autorizada. El evento reduce inventario en 1,100 y registra pérdida por 1,100; no crea venta ni cuenta por cobrar. Si después llega un costo de 50 de esa posición, el inventario sigue en 0 y la pérdida acumulada queda en 1,150. El reporte presenta pérdidas separadas del margen de ventas.

**GOLD-09, compra nueva del mismo animal:** la posición del ciclo anterior cerrada por venta/entrega conserva su costo histórico. Una recompra documentada genera otra posición con su propio costo. No reutilizar la valoración anterior.

**GOLD-10, cierre concurrente:** una conexión intenta registrar un costo mientras otra cierra el periodo. Ambas bloquean la misma fila de periodo. El costo queda incluido antes del corte o es rechazado/enviado a un periodo abierto según el comando; nunca aparece retroactivamente dentro de un cierre ya publicado.

Usa estos efectos como política de valoración:

| Hecho | Δ inventario gerencial | Δ costo de venta | Δ pérdida |
|---|---:|---:|---:|
| Adquisición a costo C | +C | 0 | 0 |
| Venta reconocida de esa posición | −C | +C | 0 |
| Costo tardío δ de posición aún capitalizada | +δ | 0 | 0 |
| Costo tardío δ con venta reconocida | 0 | +δ | 0 |
| Baja por pérdida de posición aún en inventario | −C | 0 | +C |
| Costo tardío δ de posición dada de baja por pérdida/muerte | 0 | 0 | +δ |

Los signos se derivan de la clase económica, no de un número libre que el usuario pueda introducir para cuadrar saldos. El costo base y las asignaciones sirven como evidencia de los asientos; no se suman de nuevo al calcular el inventario actual.

Antes de una venta parcial, aprueba la asignación del precio original del lote: importe individual si está documentado; en su defecto, reparto gerencial por cabezas o pesos individuales realmente medidos. Las asignaciones suman exactamente el costo del lote. La recompra recibe nuevas asignaciones.

Para octubre, el piloto empieza con compras nuevas registradas de principio a fin. La migración de inventario previo requiere un módulo de apertura con origen, costo y aprobación; no inventes compras, fechas, facturas o pagos para llenar huecos. Cotízala sólo con alcance separado cuando ese flujo exista.

Una devolución después de entregar ganado no es una recompra. El flujo completo de devoluciones físicas posteriores queda aplazado para el piloto inicial y se bloquea explícitamente; deberá enlazar venta, animales, costo recuperado y ajuste económico antes de habilitarse. La corrección/anulación soportada antes de la entrega debe comprobar dependencias, pagos y periodos, y producir contramovimientos. No expongas un botón genérico “restaurar inventario” sin reglas.

La anulación total de venta antes de entregar ninguna posición revierte reconocimiento y obligación y reclasifica a inventario el costo neto vigente del ciclo, incluidos los costos tardíos vinculados. Ejemplo: costo de venta original 1,100 más ajuste 100; la anulación restituye 1,200 a inventario y deja costo neto de esa venta anulada en 0, mediante hechos nuevos del periodo abierto. No crea otra posición de compra ni altera el cierre histórico. Libera aplicaciones incompatibles con la deuda anulada según el procedimiento de reverso/reaplicación; un reembolso sigue siendo un movimiento separado.

Cada ajuste identifica su fuente: un cambio del precio de compra del ganado ajusta, en una misma transacción, la liquidación del vendedor y la valoración de las posiciones afectadas; un cambio de gasto de tercero ajusta ese gasto y su valoración; un cambio del precio de venta ajusta venta neta y deuda del comprador, sin cambiar automáticamente el costo de adquisición. No usar una bonificación sin indicar a quién y a qué obligación/fuente corresponde.

## 12.2 Contrato de API antes de integrar pantallas

Crea OpenAPI versionado en docs/api/openapi.yaml con ejemplos sintéticos de éxito/error. Jared trabaja con ese contrato y mocks; Aldo implementa sus operaciones. Todo cambio incompatible se acuerda mediante PR y actualiza tipos, mocks y pruebas.

Familias iniciales:

| Recurso/caso | Contrato esperado |
|---|---|
| Sesión y permisos | Login/logout, usuario actual, sedes y capacidades autorizadas |
| Catálogos | Contrapartes, predios, usuarios y membresías según rol |
| Identidad | Registrar/consultar animal e identificaciones; estado pendiente de maestro/convergencia |
| Operaciones | Crear/editar borrador, lotes, selecciones, versión y condiciones |
| Pesajes | Adjuntar, proponer, aprobar y corregir sin borrar versiones |
| Confirmación | POST /api/v1/operaciones/{id}/confirmar con idempotencia y versión esperada |
| Reservas | Crear, liberar y consultar expiración; conflicto de disponibilidad explícito |
| Inventario | Posiciones disponibles/históricas, ficha y movimientos de recepción/entrega/baja |
| Liquidaciones | Consulta del snapshot, desglose, ajustes y exportación de comprobante interno |
| Costos | Registrar fuente, previsualizar reparto, aprobar y añadir ajuste tardío |
| Pagos | Registrar/confirmar pago, aplicar, revertir aplicación y registrar devolución de dinero |
| Reportes | Cartera, inventario, margen de operación, periodos y conciliación |
| Evidencia | Subir archivo, obtener acceso autorizado y registrar revisión de versión concreta |
| Integraciones | Consultar proveedor FDW, importar propuesta y conservar aceptación local |

No todos los recursos necesitan CRUD de borrado. Los hechos confirmados exponen comandos de corrección, no DELETE indiscriminado.

Define:

- Money y pesos como cadenas decimales en JSON cuando sea necesario preservar exactitud; moneda/unidad explícitas.
- IDs como UUID, fechas ISO y zona de presentación; no enviar fechas ambiguas.
- Paginación y límites para listas; orden estable y filtros documentados.
- 401 sin sesión, 403 sin permiso, 404 para recurso no accesible según política uniforme, 409 por conflicto/idempotencia, 422 por regla de dominio y 503 por dueño no disponible.
- Error con codigo, mensaje comprensible, campos, regla_id y correlation_id, sin SQL ni secretos.
- Idempotency-Key para confirmaciones, aplicaciones, reversos y otros comandos con efecto.
- Versionado optimista para borradores.
- Reintentos del cliente limitados y explícitos.
- Exportaciones con fuente/fecha de corte y significado del reporte.

El servidor calcula totales y deriva el scope de la sesión; sólo acepta empresa/sede solicitada tras comprobar autorización. El navegador no elige roles, nodos ni credenciales.

## 12.3 Autenticación y documentos

Para el piloto con una API, utiliza Spring Security con sesión de servidor y cookie HttpOnly/Secure/SameSite, protección CSRF para comandos y mismo origen frontend/API. No guardes contraseñas o tokens de larga duración en localStorage. El hash de contraseña usa el mecanismo mantenido por el framework; verifica su configuración oficial.

Documenta expiración, revocación, revalidación de permisos y comportamiento cuando A no esté disponible. Las sesiones/configuración técnica no se replican como datos comerciales. Una caída/reinicio que fuerce reautenticación debe comunicarse; la disponibilidad de escritura en B depende también de tener una sesión válida. No prometas que toda la aplicación sigue disponible sólo porque B está encendido.

Los archivos se guardan fuera del directorio público. Valida tamaño, extensión/MIME real y formatos admitidos; usa nombres internos aleatorios, autorización al descargar y URLs temporales si el almacenamiento lo permite. El navegador no aporta una ruta arbitraria del servidor. Un QR interno debe requerir la autorización correspondiente y no revelar datos personales o saldos a cualquiera que lo escanee.

## 12.4 Pantallas y diseño de Jared

Diseña una aplicación B2B sobria, rápida y clara. La información principal es operativa: pendientes, diferencias, saldos y evidencia. No rellenes el dashboard con gráficas ficticias.

Pantallas:

1. Acceso y selección de sede autorizada.
2. Bandeja de operaciones con pendientes de pesaje, liquidación, entrega y pago.
3. Directorio de contrapartes/predios.
4. Identidad y ficha del animal con ciclos históricos.
5. Inventario y selección para venta.
6. Captura de compra/venta por pasos: contraparte, lotes/animales, condiciones, pesajes y revisión.
7. Comparación de tickets y explicación de variación, indicando incompatibilidad de conjuntos.
8. Detalle de liquidación: fórmula, costo, gastos, ajustes, pagos y documentos.
9. Cobros/pagos y aplicación a obligaciones compatibles.
10. Expediente y línea temporal verificable de hechos.
11. Cartera con vencimientos y filtros.
12. Reporte de margen e inventario, distinguiendo provisional, actualizado y corte cerrado.
13. Administración de usuarios/permisos.
14. Vista operativa de incidencias de sincronización con mensajes útiles, sin exponer configuración técnica.
15. Simulador de margen antes de aceptar un trato.

Para cada pantalla especifica campos, permisos, componentes, estados vacío/cargando/error, conflicto, datos atrasados y recuperación. Incluye navegación por teclado, etiquetas, foco, contraste y mensajes que no dependan sólo del color.

Diseña primero para escritorio administrativo y asegura captura esencial usable en móvil. Los importes se alinean y muestran MXN; los pesos indican kg; no mezcles separador decimal de captura con formato monetario. Muestra subtotales explicables.

La PWA/offline es un extra: si se implementa, sólo permite borradores locales claramente marcados. Una confirmación financiera o reserva requiere conexión con el dueño. No anunciar “venta completada” mientras sólo exista en IndexedDB.

No muestres Pgpool, FDW, SQL o nombres de contenedores en el flujo normal del cliente. Los detalles técnicos pertenecen a documentación y vistas administrativas cuando ayuden a resolver un incidente.

# 13. Despliegue desde desarrollo hasta piloto

## 13.1 Entornos

- dev: PostgreSQL único para iterar reglas y pantallas con rapidez.
- academic: A/B, dos Pgpool raw, PostgreSQL externo FDW, backend, frontend y documentos privados.
- staging: misma topología académica en servidor, datos sintéticos y configuración separada.
- pilot: sólo tras verificar reglas, permisos, respaldos, acceso y operación acordada con cliente.

Un test exitoso en dev no prueba M–M. Las pruebas de réplica y recuperación se ejecutan en academic/staging.

Entrega .env.example con nombres y valores ficticios, nunca credenciales reales. Compose debe declarar servicios, redes internas, healthchecks, dependencias de readiness, límites y volúmenes persistentes. “El contenedor está iniciado” no prueba que la suscripción o migración esté lista.

La imagen oficial PostgreSQL 18 usa por defecto PGDATA=/var/lib/postgresql/18/docker y su montaje de volumen en /var/lib/postgresql. Verifica la imagen/digest fijado y prueba persistencia tras recrear el contenedor; no copies ciegamente el montaje de versiones anteriores. [F29]

## 13.2 Infraestructura inicial

Propuesta de dimensionamiento para medir: VPS Linux de 4 vCPU y 8 GB RAM, disco suficiente para BD, WAL temporal y documentos; copias fuera del host. Es una hipótesis de capacidad, no garantía de rendimiento.

Como referencia consultada, un Droplet Basic de DigitalOcean con 4 vCPU/8 GiB se anunciaba en USD 48/mes. Verifica precio/región al contratar y añade respaldos, objetos, impuestos, dominio, transferencia y soporte. No conviertas a MXN sin tipo de cambio documentado. No contrates recursos de pago sin autorización del dueño de la cuenta. [F33]

Caddy sirve la interfaz y enruta /api al backend bajo HTTPS. Configura DNS y conectividad requeridos para certificados; expone 80/443 y acceso administrativo controlado. PostgreSQL, Pgpool y FDW permanecen en red privada. [F32]

Dos PostgreSQL en un VPS demuestran replicación y siguen compartiendo el fallo del host. No anunciar alta disponibilidad entre zonas ni cero pérdida de datos. Para evolucionar a múltiples hosts, conserva aislamiento de red, almacenamiento y un procedimiento probado de recuperación por propietario.

## 13.3 Pipeline y publicación

Documenta y crea una automatización de CI compatible con el repositorio:

1. Verificar formato/lint y compilación backend/frontend.
2. Ejecutar pruebas de dominio y SQL con PostgreSQL real.
3. Validar OpenAPI y migraciones en base limpia.
4. Construir imágenes con versiones identificables.
5. Publicar imágenes en el registro autorizado.
6. Desplegar staging con configuración/secrets externos.
7. Ejecutar migración una vez por nodo mediante tarea controlada.
8. Verificar salud, endpoints y flujos de compra/venta/pago.
9. Registrar versión, responsable y evidencia de despliegue.

Las migraciones A/B se coordinan. No permitas que varias instancias del backend arranquen y migren cada base por su cuenta. Prefiere cambios compatibles de expansión y contracción; detalla qué despliegue de código admite cada esquema.

No incluyas secretos en Dockerfile/imagen. Compose secrets los presenta como archivos a servicios autorizados; no afirmes que eso cifra automáticamente los archivos fuente en el host. [F31]

Un rollback de aplicación sólo es válido si la versión anterior es compatible con el esquema actual. No ejecutes una migración destructiva “down” para simular reversibilidad. El runbook indica si corresponde corrección hacia adelante o restauración con corte y reconciliación.

Si faltan credenciales del servidor, prepara y verifica todo lo local, deja el despliegue externo identificado como pendiente y no inventes una URL pública.

## 13.4 Respaldo y recuperación

Respaldar incluye BD de ambos propietarios, roles/configuración necesarios y archivos/documentos. La réplica no es un respaldo.

Para la demo:

1. Cerrar temporalmente nuevas escrituras y detener workers que produzcan efectos.
2. Esperar fin de transacciones y convergencia.
3. Registrar un corte con conteos por dueño y conciliaciones.
4. Obtener respaldos y manifiesto de objetos/hash; conservar configuración de roles.
5. Restaurar en una red aislada y medir el tiempo.
6. Validar documentos, usuarios, relaciones y cifras GOLD/conciliación.
7. Reconstruir replicación con procedimiento controlado antes de reabrir.

No reactives suscripciones/slots antiguos a ciegas al restaurar. pg_dump permite excluir publicaciones/suscripciones de un respaldo que se reconstruirá por aprovisionamiento; comprueba el contenido del archivo y la estrategia elegida. [F34]

Para un piloto que prometa RPO ≤15 minutos y RTO ≤2 horas, implementa antes backups base y archivo WAL de cada nodo fuera del host, respaldos de documentos y un ensayo medido de recuperación coherente. Son objetivos propuestos, no resultados obtenidos. Un dump diario por sí solo no sustenta un RPO de 15 minutos. [F35]

Una pareja de dumps tomados en instantes arbitrarios no prueba un snapshot global consistente. Define cortes o reconciliación de los datos autoritativos de cada sede, fencing de escrituras y reenganche seguro de replicación. La pérdida del nodo A no autoriza a convertir B en dueño de todo con un cambio de host.

## 13.5 Objetivos no funcionales a medir

| ID | Objetivo inicial | Cómo se verificará |
|---|---|---|
| RNF-01 | Ninguna doble venta ni sobreaplicación en escenarios concurrentes definidos | Dos o más conexiones reales y aserciones de estado final |
| RNF-02 | Aislamiento de empresa/sede y permisos | Casos negativos HTTP y SQL |
| RNF-03 | Importes reproducibles al centavo | GOLD-01..10 y casos límite de redondeo |
| RNF-04 | p95 de consulta habitual <500 ms y confirmación local <1 s, sin archivos/OCR | Objetivo sobre entorno/dataset/carga declarados; publicar medición real |
| RNF-05 | Prueba inicial con 20 sesiones concurrentes, 10 mil posiciones y 100 mil hechos sintéticos | Semilla reproducible, recursos y resultado; ajustar capacidad tras medir |
| RNF-06 | Reportes consolidados indican corte/antigüedad | Partición de réplica y revisión de UI |
| RNF-07 | Restauración reproducible y medida | Ensayo aislado y conciliación, no sólo archivo de backup |
| RNF-08 | Interfaz usable con teclado y móvil en captura principal | Recorrido accesible y tamaños definidos |
| RNF-09 | Compilación/despliegue reproducible | Checkout limpio, lockfiles, comandos y ausencia de pasos ocultos |
| RNF-10 | Diagnóstico sin exponer secretos | Logs con correlation_id, métricas y revisión de errores |

No conviertas estos objetivos en benchmarks ya alcanzados. Si alguno falla, publica el resultado y el ajuste propuesto.

# 14. Documentación permanente y contexto para Claude

## 14.1 Estructura del repositorio

Crea un monorepo con contenido real:

~~~text
README.md
CLAUDE.md
backend/
frontend/
db/migrations/
db/bootstrap/
db/seed/
infra/compose/
infra/caddy/
tools/
tests/integration/
docs/academic/
docs/business/
docs/domain/
docs/research/
docs/database/
docs/architecture/adr/
docs/api/
docs/ui/
docs/project/
docs/runbooks/
docs/testing/
docs/knowledge/
docs/diagrams/sources/
docs/diagrams/exports/
docs/traceability.md
docs/status.md
~~~

No generes docenas de archivos vacíos para aparentar avance. Cada documento debe contener decisiones, ejemplos y enlaces útiles, o indicar expresamente qué conocimiento falta y cómo se obtendrá.

## 14.2 Archivos de contexto obligatorios

| Archivo | Contenido mínimo |
|---|---|
| README.md | Problema, comprador, modelo de negocio, alcance, stack/versiones, arquitectura, ejecución, despliegue, diagramas, roles, calendario y tareas Aldo/Jared con casillas |
| CLAUDE.md | Reglas persistentes breves, comandos reales, decisiones no negociables, mapa de lectura y cómo actualizar docs/grafo |
| docs/business/business-model.md | Canvas, propuesta, oferta, costos, precio como hipótesis, venta piloto y límites |
| docs/business/validation-plan.md | Guion, muestras autorizadas, criterios de aprendizaje y resultados reales cuando existan |
| docs/business/unit-economics.md | Fórmulas, supuestos, capacidad, escenarios y costo del tiempo |
| docs/domain/glossary.md | Términos, unidades, sinónimos y diferencias de conceptos |
| docs/domain/business-rules.md | RN-001..045 con precondiciones, errores, pruebas y decisiones |
| docs/domain/use-cases.md | Actores, flujos normales/alternativos, invariantes y datos |
| docs/domain/states-and-calculations.md | Máquinas de estado, reconocimiento y GOLD-01..10 |
| docs/research/sources.md | Bibliografía con fecha, afirmación respaldada, aplicabilidad y limitación |
| docs/research/evidence-register.md | Distinguir hecho comprobado, hipótesis, propuesta y pendiente |
| docs/research/theoretical-foundation.md | Teoría conectada a decisiones y evidencias concretas |
| docs/academic/requirements-matrix.md | AC-01..09 y otros requisitos del temario efectivamente confirmado |
| docs/academic/oop-solid-patterns.md | POO, SOLID y patrones con referencias al código real |
| docs/database/conceptual-model.md | Entidades, identidad, atributos, participación y débiles/fuertes |
| docs/database/relationship-matrix.md | Verbos, mínimos/máximos, condiciones por estado y ejemplos |
| docs/database/relational-model.md | Relaciones, claves, restricciones y transformación del MER |
| docs/database/data-dictionary.md | Definición de cada columna, dominio, scope, fuente y sensibilidad |
| docs/database/normalization.md | Dependencias, claves, 1FN/2FN/3FN y BCNF evaluada |
| docs/database/administration.md | Roles, constraints, PL, triggers, consultas y mantenimiento |
| docs/database/replication-and-fdw.md | Propiedad, publicaciones, bootstrap, límites, FDW y pruebas |
| docs/architecture/overview.md | Módulos, capas, topología, secuencias y decisiones |
| docs/architecture/deployment.md | Entornos, infraestructura, recursos, redes y versiones |
| docs/api/openapi.yaml | Contrato implementable y ejemplos; no sólo títulos |
| docs/ui/flows-and-screens.md | Pantallas, campos, permisos, estados, errores y componentes |
| docs/project/roadmap.md | Metodología, hitos, capacidad, dependencias y fechas |
| docs/project/backlog.md | Fuente detallada de tareas, aceptación, estado y evidencia |
| docs/project/definition-of-done.md | Criterios para considerar terminado cada tipo de tarea |
| docs/runbooks/ | bootstrap, deploy, rollback, backup-restore, replication-recovery e incident |
| docs/testing/test-plan.md | Pruebas académicas, dominio, concurrencia, seguridad y recuperación |
| docs/testing/demo-script.md | Demostración cronometrada y datos sintéticos |
| docs/testing/evidence.md | Comandos, resultados, entorno, fecha y evidencias reales |
| docs/knowledge/graphify-workflow.md | Instalación, alcance, generación, actualización y exclusiones |
| docs/knowledge/graph-status.md | Último grafo real, versión, revisión, cobertura y limitaciones |
| docs/traceability.md | Requisito → regla → entidad/tabla → comando/API → pantalla → prueba → tarea |
| docs/status.md | Qué existe, pendientes, bloqueos concretos y siguiente tarea ejecutable |

El README debe ser detallado para personas. CLAUDE.md debe ser breve y específico, con objetivo menor de 200 líneas, y remitir al contexto que corresponda a la tarea. Importar todos los documentos de golpe no ahorra contexto. Respeta y fusiona cuidadosamente cualquier CLAUDE.md/AGENTS.md existente. [F41–F42]

Tras cada tarea actualiza estado, documentación afectada, evidencia y siguiente acción. No copies todos los documentos como resúmenes divergentes: cada regla tiene una fuente canónica, y README enlaza el detalle.

## 14.3 Trazabilidad mínima

Usa AC, RN, RF, RNF, UC, ENT, REL, ADR, TASK-A, TASK-J y TEST con identificadores estables. Los números definidos en este prompt se conservan; agrega nuevos sin reutilizar IDs retirados.

Ejemplo de cadena explícita:

~~~text
AC-05 / RN-018 / RN-022
→ UC ConfirmarVenta
→ ENT-12, ENT-13, ENT-15, ENT-22
→ función transaccional e índices de disponibilidad
→ POST /operaciones/{id}/confirmar
→ pantalla de confirmación
→ TEST de doble venta concurrente
→ tarea de Aldo + tarea de Jared
→ ejecución y resultado comprobados
~~~

Una arista del grafo no reemplaza esta evidencia. Si aún falta código, el estado debe decir diseñado/pendiente, no implementado.

# 15. /graphify: generar y mantener el grafo real del proyecto

Esta tarea es obligatoria porque el equipo quiere que Claude conserve contexto navegable de lo que se decide e implementa.

## 15.1 Identificar la implementación

La referencia investigada es Graphify-Labs/graphify. El paquete se llama graphifyy, con doble y; el ejecutable es graphify y el slash command se invoca dentro de Claude, no como una orden Bash. No es un comando universal incorporado en todas las instalaciones de Claude. [F36–F37]

Inspecciona la skill instalada, su origen, versión, ayuda y configuración. Si hay otro producto homónimo, no asumas que sus flags coinciden.

~~~bash
command -v graphify
~~~

Sólo si existe:

~~~bash
graphify --help
~~~

Obtén la versión por la opción que anuncie la ayuda o por metadatos de instalación. Si falta, revisa documentación oficial y prepara instalación aislada de una versión revisada de graphifyy con uv/pipx. La documentación consultada muestra:

~~~bash
uv tool install graphifyy
graphify claude install --project
~~~

Antes de instalar, fija la versión validada y revisa qué archivos/hook modifica la versión disponible. Conserva instrucciones existentes. No cambies Python del sistema ni instales un paquete parecido por adivinar el nombre.

La instalación local dentro del alcance permitido puede continuar; un servicio de pago, publicación o acceso externo no autorizado se deja pendiente. Si una herramienta/red/permiso impide Graphify, registra el bloqueo preciso, no inventes una ejecución y continúa el diseño, la documentación y el código independientes. Un mapa manual provisional se etiqueta como tal.

## 15.2 Preparar el corpus y ejecutar

Primero deben existir el contexto, las reglas, el MER, el modelo relacional, ADR, OpenAPI y backlog. Después indexa la raíz para conectar docs/, backend/, frontend/, db/ e infra/ a medida que se creen.

Configura .graphifyignore según la sintaxis oficial. Excluye:

- Credenciales, .env privados, tokens, certificados/claves privadas.
- Respaldos, dumps, datos reales y documentos de clientes.
- node_modules, target, dist, cachés, binarios y dependencias descargadas.
- Salidas graphify-out para no reindexar recursivamente el grafo.
- Cualquier archivo sintético que accidentalmente contenga información sensible.

El análisis estructural de código puede ser local; el procesamiento semántico de documentos/medios puede utilizar el modelo o backend configurado. No prometas que todo el corpus funciona offline o queda local automáticamente. Mantén datos privados fuera del corpus de desarrollo. [F36, F39]

Con la skill real disponible y sintaxis compatible, invoca en Claude:

~~~text
/graphify .
~~~

Comprueba las rutas reales. Para la implementación investigada se esperan:

~~~text
graphify-out/graph.html
graphify-out/GRAPH_REPORT.md
graphify-out/graph.json
~~~

Parsea el JSON, revisa nodos/reglas y abre el resultado visual cuando el entorno permita. Registra errores auténticos. No edites un reporte para aparentar que Graphify lo extrajo.

## 15.3 Actualizar durante todo el trabajo

Después de cambios en reglas, modelos, ADR, contratos o documentación:

~~~text
/graphify . --update
~~~

Para cambios exclusivamente estructurales de código, la documentación también ofrece:

~~~bash
graphify update .
~~~

No son equivalentes para el contenido documental: una actualización de código o un hook no sustituye la actualización semántica de los .md. Las consultas leen el grafo guardado; un resultado no demuestra que el grafo esté al día. Los hooks pueden ejecutarse en segundo plano. [F38]

Aldo y Jared mantienen salidas por checkout/worktree para evitar escribir el mismo grafo simultáneamente. Define una política de publicación/versionado de grafo apto para compartir; no actives Graphify Cloud ni un servidor público para este proyecto sin un requerimiento. [F40]

Actualiza al completar el paquete de diseño y al cerrar hitos del 18, 24, 28 y 31 de octubre. Registra en graph-status.md: fecha, versión, commit o cambios locales examinados, alcance, comando, archivos producidos, errores, conteos reales y limitaciones.

## 15.4 Verificación de utilidad

Mediante la interfaz documentada de la versión instalada, comprueba preguntas como:

- ¿Qué RN y qué comando evitan la doble venta?
- ¿Qué entidad, FK, función y prueba sostienen la aplicación de un pago?
- ¿Qué pantalla consume el contrato de liquidación?
- ¿Qué ADR explica el maestro A y la propiedad de escritura?
- ¿Dónde se documenta el costo tardío de animales vendidos?
- ¿Qué requisito del profesor demuestra cada script de replicación y FDW?

Si la implementación todavía no existe, la respuesta debe señalar diseño y tareas pendientes. Las aristas inferidas se revisan contra archivos fuente. Graphify facilita navegación; el repositorio, su documentación y las pruebas conservan la evidencia explícita.

# 16. Metodología y calendario para dos personas

## 16.1 Forma de trabajo

Usa desarrollo incremental orientado a casos completos y un flujo Kanban. No lo llames Scrum si no habrá roles, eventos y compromisos correspondientes.

Columnas: Backlog → Listo → En curso → Revisión → Hecho. Un bloqueo se marca y explica; no se oculta sacándolo del límite de trabajo.

Política inicial propuesta:

- Una tarea de implementación activa por persona.
- Una tarea en revisión compartida como máximo.
- Cada tarea entra a Listo con RN/AC, dependencia y aceptación claras.
- Integrar diariamente incrementos pequeños cuando sean coherentes.
- Reunión de coordinación de 15 minutos para contrato, bloqueos y siguiente integración.
- PR revisado por el otro integrante; autoría y revisión reales.
- main debe seguir compilando; no acumular todo el proyecto en dos ramas que se unirán el último día.
- Un cambio de modelo se refleja en migración, contrato y pantalla correspondiente.
- Medir tareas terminadas, bloqueos y tiempo de ciclo; ajustar WIP si los datos lo justifican.

Estos límites son una política del equipo, no una cifra obligatoria de la guía Kanban. [F16]

La planificación cubre 21 días calendario, 11–31 de octubre de 2026. Registra disponibilidad real. Como escenario inicial de capacidad, 4–6 horas efectivas diarias por integrante equivalen a 168–252 horas-persona si trabajan los 21 días; no es una promesa de productividad. Ajusta el calendario si no se cumple esa disponibilidad, preservando la ruta académica y el núcleo económico.

## 16.2 Calendario

| Fechas | Aldo: backend/BD | Jared: frontend | Criterio del hito |
|---|---|---|---|
| 11–13 oct | Investigación, reglas, MER Chen, relacional, claves/diccionario, ADR, OpenAPI y primer grafo | Contexto de usuarios, flujo, wireframes y revisión de términos | Paquete de diseño consistente, editable y trazable antes del código de negocio |
| 13–14 oct | Inicio de migraciones/roles, experimento M–M/FDW mínimo y estructura de auth | Proyecto frontend, sistema visual, navegación, mocks y preparación de sesión | Contrato compartido y experimento de topología verificados; auth/DDL de dominio se completan conforme a tareas |
| 15–18 oct | Maestros, inventario, compra, pesajes, evidencia y costo inicial | Catálogos, ficha, captura de compra/pesajes y revisión | Compra → posición → liquidación integrada; actualización de grafo |
| 19–22 oct | Reserva, venta, valoración, gastos, pagos/aplicaciones, ajustes y periodos | Venta, simulación, liquidación, pagos y mensajes de conflicto | Flujos económicos GOLD y concurrencia esencial demostrados |
| 23–25 oct | Reportes, auditoría, outbox, conciliación y pruebas de réplica/FDW | Cartera, margen, expediente, QR y estados de sincronización | Recorrido completo; revisión de hitos 24; extras sólo si núcleo estable |
| 26–28 oct | Staging, pipeline, backups/restauración, rendimiento y permisos | Responsive, accesibilidad, E2E, manual/capturas | Versión candidata desplegable y recuperación ensayada |
| 29–31 oct | Correcciones, evidencia SQL, manuales, ensayo de exposición y release | Correcciones visuales/flujo, capturas y demostración | Entrega académica reproducible; grafo/documentación final y propuesta de piloto |

La prueba mínima de M–M y FDW ocurre temprano para reducir el riesgo técnico. Las pruebas integrales se repiten cuando el modelo real ya está implementado.

Al entrar al 29 de octubre, congela extras. Si se retrasa la ruta crítica, elimina OCR, offline y adornos antes de quitar integridad, MER, roles, transacciones, replicación o FDW.

## 16.3 Definition of Done

Una tarea termina cuando:

1. Cumple su aceptación y la regla de negocio indicada.
2. Existe el artefacto real y se revisó.
3. Se ejecutó la prueba pertinente, cuando corresponde, con resultado guardado.
4. El contrato/documentación afectado coincide con la implementación.
5. Se revisó el cambio y se registró su evidencia.
6. Se actualizó trazabilidad y el grafo cuando cambió contexto relevante.
7. No presenta un mock como implementación de una integración exigida ni un despliegue pendiente como publicado. FDW real contra la fuente sintética prevista puede darse por terminado con sus pruebas y su condición de simulación claramente documentadas.

Para diagramas: fuente editable, exportación revisada y cardinalidades defendibles. Para BD: migración reproducible y prueba positiva/negativa. Para API: contrato, autorización y persistencia real. Para frontend: integración y estados de error. Para recuperación: restauración ejecutada y conciliada.

# 17. Backlog que debes colocar en README con casillas

Copia estas tablas al README y amplía el detalle en docs/project/backlog.md. Todas empiezan pendientes. La columna [ ] es una casilla textual editable; usa [x] sólo con evidencia. Añade debajo listas GFM por responsable con la sintaxis real "- [ ] TASK-..." para plataformas que ofrecen casillas interactivas. No prometas que un [ ] dentro de una tabla será un control interactivo. [F44]

Conserva los IDs y añade columna/enlace a evidencia al ejecutar. Las fechas son ventanas objetivo de octubre de 2026. Si una tarea se divide, usa subtareas con IDs nuevos, sin cambiar el significado de la original.

## 17.1 Aldo — backend, bases de datos e infraestructura

| Estado | ID | Tarea/entregable | Depende de | Ventana | Criterio de aceptación |
|---|---|---|---|---|---|
| [ ] | TASK-A-001 | Inventario del repo/herramientas y matriz AC | Inicio | 11 | Requisitos de imagen separados de supuestos; archivos existentes respetados |
| [ ] | TASK-A-002 | Negocio, glosario, reglas y GOLD | A-001 | 11–12 | RN completas, reconocimiento único, costos/pagos distinguibles |
| [ ] | TASK-A-003 | MER Chen y matriz de relaciones | A-002 | 11–12 | Fuertes/débiles, rombos, óvalos, verbos, mínimos/máximos y exportaciones revisadas |
| [ ] | TASK-A-004 | Modelo relacional, diccionario y normalización | A-003 | 12–13 | Todas las relaciones con claves, FKs, tipos, restricciones y justificación |
| [ ] | TASK-A-005 | Arquitectura, ADR y plan de despliegue | A-002/A-004 | 12–13 | Dueños, transacciones, límites M–M y recuperación explícitos |
| [ ] | TASK-A-006 | Contexto Markdown, README y grafo inicial | A-003/A-005/A-007 | 12–13 | Archivos sustantivos y grafo real verificado; si Graphify está bloqueado, sólo el avance documental se registra y la subtarea de grafo sigue pendiente |
| [ ] | TASK-A-007 | OpenAPI, errores y ejemplos para Jared | A-004/A-005 | 13 | Contrato validado con decimales exactos, scope e idempotencia |
| [ ] | TASK-A-008 | Backend modular y build reproducible | A-005/A-007 | 13–14 | Maven Wrapper, configuración por entorno y arranque verificable |
| [ ] | TASK-A-009 | DDL/Flyway, claves, índices y seed sintético | A-004 | 13–15 | Base limpia construida; restricciones fallan ante datos inválidos |
| [ ] | TASK-A-010 | Roles PostgreSQL, grants y guardas de dueño | A-009 | 13–15 | App sin privilegios administrativos; DML indebido rechazado |
| [ ] | TASK-A-011 | Compose A/B + Pgpool y experimento M–M mínimo | A-005 y esquema mínimo aislado | 13–14 | Dos clusters escriben dueños distintos y convergen; prueba inicial no sustituye dominio definitivo |
| [ ] | TASK-A-012 | Tercero simulado y FDW sólo lectura | A-011 | 14 | Consulta real externa; escrituras rechazadas; procedencia visible |
| [ ] | TASK-A-013 | Autenticación y permisos por sede | A-008/A-010 | 14–15 | Sesión/CSRF; pruebas 401/403 y autorización de recursos |
| [ ] | TASK-A-014 | Maestros, animal e identificaciones centrales | A-009/A-013 | 15 | Colisión de identificador resuelta en A; B espera visibilidad |
| [ ] | TASK-A-015 | Operaciones, lotes y versiones contractuales | A-014 | 15–16 | Borradores, selecciones únicas y condiciones versionadas |
| [ ] | TASK-A-016 | Documentos, revisión y pesajes | A-015 | 16–17 | Archivos privados; neto/grupo reales; revisión de versión exacta |
| [ ] | TASK-A-017 | ConfirmarCompra y asignar costo inicial | A-015/A-016 | 17–18 | Posiciones, obligación y costo inicial atómicos; componentes de compra de GOLD-01/02 y GOLD-03 completo |
| [ ] | TASK-A-018 | Movimientos, recepción, entrega y baja | A-017 | 18–20 | Ejes físicos separados; baja conserva historia y costo |
| [ ] | TASK-A-019 | Reservas, expiración y ConfirmarVenta | A-017/A-018 | 19–20 | Una venta ganadora en carrera; costo parcial correcto |
| [ ] | TASK-A-020 | Pagos, anticipos y aplicaciones | A-017/A-019 | 20–21 | Sumatorias bajo lock, mismo scope, idempotencia y GOLD-04 |
| [ ] | TASK-A-021 | Ajustes, reversos y reembolsos | A-020 | 21–22 | GOLD-07; ninguna sobreaplicación o borrado de originales |
| [ ] | TASK-A-022 | Costo tardío, valoración y periodos | A-019/A-021 | 21–23 | GOLD-06/08/10; cierre conserva versiones y concilia |
| [ ] | TASK-A-023 | Auditoría, outbox/inbox y reintentos | A-017..A-022 | 22–24 | Hecho y evento atómicos; consumidor no duplica al reintentar |
| [ ] | TASK-A-024 | Consultas de cartera, margen e inventario | A-020/A-022 | 23–24 | Totales reconciliados, corte visible y EXPLAIN documentado |
| [ ] | TASK-A-025 | Integrar aceptación de fuente FDW y QR | A-012/A-016 | 23–25 | Snapshot local de tarifa/ticket; QR con acceso autorizado |
| [ ] | TASK-A-026 | Pruebas M–M completas, fallas y conciliación | A-009/A-011/A-023 | 24–25 | Partición/reconexión del esquema definitivo, sin loops ni auditoría duplicada, sin redirigir dueño |
| [ ] | TASK-A-027 | Pruebas acumulativas de dominio/SQL/API y concurrencia | Incremental por módulo; cierre tras A-026 | 18–27 | Escenarios TEST, GOLD integrales y PostgreSQL real; no posponer pruebas hasta el final |
| [ ] | TASK-A-028 | Pipeline, staging, TLS y configuración | A-008/A-011 | 26–27 | Checkout limpio desplegable y smoke test; secretos externos |
| [ ] | TASK-A-029 | Respaldo, restauración y runbooks | A-026/A-028 | 26–28 | Restauración aislada cronometrada con cifras y archivos conciliados |
| [ ] | TASK-A-030 | Rendimiento, conexiones y observabilidad | A-024/A-028 | 27–28 | Carga/dataset declarados; límites y resultados auténticos |
| [ ] | TASK-A-031 | OCR supervisado si se aprueba el núcleo | A-016/A-027 | 25–28 opcional | Propuesta revisable, sin confirmar importes automáticamente |
| [ ] | TASK-A-032 | Dossier académico, manual SQL y exposición | A-027..A-030 | 29–31 | Cada AC enlaza artefacto y demo ejecutada |
| [ ] | TASK-A-033 | Fuentes, README y Graphify final consolidado | A-032/J-022 | 29–31 | Trazabilidad de ambos, casillas con evidencia, grafo sobre revisión integrada y release verificable |

La infraestructura de auditoría/idempotencia/periodo necesaria para los primeros comandos se implementa junto con ellos. A-022/A-023 consolidan pantallas, reglas y pruebas completas; no autorizan a posponer integridad básica hasta el final.

El experimento temprano A-011/A-012 usa un esquema mínimo aislado. A-026 prueba nuevamente el esquema definitivo de A-009 con propiedad, convergencia y conciliación. A-027 acumula evidencia desde cada módulo; J-019 puede empezar cuando el recorrido correspondiente tenga backend real y continúa junto a esa consolidación.

## 17.2 Jared — frontend e integración de experiencia

| Estado | ID | Tarea/entregable | Depende de | Ventana | Criterio de aceptación |
|---|---|---|---|---|---|
| [ ] | TASK-J-001 | Entender negocio, actores y términos | A-002 | 11–12 | Flujos y preguntas documentados; distingue operación/pago/entrega |
| [ ] | TASK-J-002 | Wireframes y arquitectura de información | J-001/A-003 | 11–12 | Recorrido compra→venta→liquidación→pago y excepciones |
| [ ] | TASK-J-003 | Tokens y componentes visuales accesibles | J-002 | 12–14 | Tablas, formularios, feedback y jerarquía consistentes |
| [ ] | TASK-J-004 | React/TS/Vite, router y build | A-007/J-003 | 13–14 | Proyecto reproducible y separación por funciones |
| [ ] | TASK-J-005 | Cliente tipado, mocks y errores del contrato | A-007/J-004 | 13–14 | Mocks identificados; formato decimal y 401/403/409/422/503 |
| [ ] | TASK-J-006 | Sesión, navegación y sede autorizada | A-013/J-005 | 14–15 | Cookie/CSRF integrados; permiso denegado sin revelar datos |
| [ ] | TASK-J-007 | Contrapartes y predios | A-014/J-006 | 15–16 | Captura/búsqueda/paginación con validación |
| [ ] | TASK-J-008 | Ficha animal, ciclos e inventario | A-014/A-017 | 16–18 | Identidad permanente, posiciones históricas y disponibilidad claras |
| [ ] | TASK-J-009 | Captura de compra y condiciones por lote | A-015/J-007 | 16–18 | Borrador por pasos; precio por kg/cabeza y versión |
| [ ] | TASK-J-010 | Pesajes, archivos y revisión | A-016/J-009 | 17–18 | Conjunto, unidad, evidencia, incompatibilidad y corrección visibles |
| [ ] | TASK-J-011 | Selección de venta y reservas | A-019/J-008 | 19–20 | Expiración/conflicto real y recarga sin doble confirmación |
| [ ] | TASK-J-012 | Simulador y detalle explicable de liquidación | A-019/J-010 | 19–21 | Fórmula, costos, ajustes, saldo y estado de entrega separados |
| [ ] | TASK-J-013 | Cobros/pagos y aplicación guiada | A-020/J-012 | 20–22 | Anticipo, disponible y saldos correctos; reintento seguro |
| [ ] | TASK-J-014 | Ajustes, devoluciones de dinero y periodos | A-021/A-022 | 21–23 | Motivo, autorización y versiones; muestra GOLD-07 sin ambigüedad |
| [ ] | TASK-J-015 | Recepciones, entregas y expediente temporal | A-018/A-023 | 22–24 | Eventos verificables, documentos privados y estados físicos claros |
| [ ] | TASK-J-016 | Cartera, margen y QR interno | A-024/A-025 | 23–25 | Datos reales de API, corte/provisionalidad y navegación autorizada |
| [ ] | TASK-J-017 | Estados de fuente caída/sincronización/conflicto | A-026/J-016 | 24–26 | Mensajes accionables; nunca confirma una escritura fallida |
| [ ] | TASK-J-018 | Responsive, teclado y accesibilidad | J-006..J-017 | 25–28 | Flujo principal usable en móvil y teclado, sin cortes de información |
| [ ] | TASK-J-019 | Pruebas E2E integradas con Aldo | Recorrido con API real/J-017; coordina A-027 | 26–28 | Compra/venta/pago, errores y permisos con backend real |
| [ ] | TASK-J-020 | UI de OCR sólo si el extra está implementado | A-031/J-010 | 25–28 opcional | Datos propuestos y revisión humana obligatoria |
| [ ] | TASK-J-021 | Manual, capturas auténticas y demo | J-018/J-019 | 29–31 | Recorrido reproducible, sin pantallas ficticias presentadas como integración |
| [ ] | TASK-J-022 | README, contexto frontend y actualización de grafo | J-021 | 29–31 | Pantallas→API→reglas enlazadas y evidencia lista; A-033 consolida después el grafo final |

Aldo es responsable de persistencia, API, infraestructura y reglas canónicas; Jared, de interacción y presentación. Ambos revisan contrato y flujos. Las tareas pueden apoyarse mutuamente, pero el responsable sigue siendo explícito. No hagas que Jared replique la lógica financiera en JavaScript para compensar una API incompleta.

Ejemplo de listas reales a expandir con todos los IDs en README:

- [ ] TASK-A-001 — Inventario y requisitos.
- [ ] TASK-A-003 — MER Chen revisado y exportado.
- [ ] TASK-A-004 — Modelo relacional y normalización.
- [ ] TASK-A-029 — Restauración ejecutada y conciliada.
- [ ] TASK-J-012 — Liquidación integrada y explicable.
- [ ] TASK-J-019 — E2E con backend real.

Las tablas detalladas y listas deben mantener el mismo estado. Una casilla se marca sólo al enlazar evidencia verificable.

# 18. Plan de pruebas y entrega al profesor

## 18.1 Pruebas de aceptación

| ID | Escenario | Resultado exigido |
|---|---|---|
| TEST-01 | GOLD-01 operación completa | Margen 34,000; saldo 244,000; diferencia física sin descuento implícito |
| TEST-02 | GOLD-02 venta parcial | Costo 4,400; margen 1,800; inventario 6,600 |
| TEST-03 | GOLD-03 redondeo | 0.34 + 0.33 + 0.33 = 1.00 reproducible |
| TEST-04 | GOLD-04 pago/anticipo | Saldos correctos y ningún doble efecto por reintento |
| TEST-05 | GOLD-05/09 recompra | Nuevo ciclo válido y jamás dos posiciones activas |
| TEST-06 | GOLD-06 costos tardíos/bonificación | Costo repartido a vendidas/no vendidas; no se cambia deuda del comprador |
| TEST-07 | GOLD-07 bonificación después del pago | Reverso/reaplicación y disponible 100; reembolso separado |
| TEST-08 | GOLD-08 baja | Inventario disminuye y pérdida separada, sin venta falsa |
| TEST-09 | GOLD-10 cierre concurrente | Corte coherente y ajustes posteriores en periodo abierto |
| TEST-10 | Dos ventas concurrentes de la misma posición | Una confirma; otra conflicto; ninguna liquidación parcial |
| TEST-11 | Dos aplicaciones compiten por pago/obligación | Nunca se sobreaplica; locks y rollback demostrados |
| TEST-12 | Misma clave con payload distinto | 409 y ningún nuevo efecto |
| TEST-13 | Identificador animal duplicado desde flujos A/B | Un alta canónica en A; revisión de conflicto |
| TEST-14 | Referencia FK de otra empresa/sede | Rechazo en BD aunque el UUID exista |
| TEST-15 | Usuario sin permiso altera sede/ID en API | Acceso rechazado y ninguna filtración/mutación |
| TEST-16 | Rol app/auditor intenta DML protegido o desactivar trigger | Permiso denegado |
| TEST-17 | Editar liquidación, contrato/pesaje aprobado | Rechazo; corrección mediante nuevo registro |
| TEST-18 | Ticket grupal sin pesos individuales | No se fabrican mediciones; conjunto congelado |
| TEST-19 | Pesajes con diferente composición | Se declara no comparable; no merma automática |
| TEST-20 | Reserva vence durante confirmación | Disponibilidad revalidada; no venta con reserva vencida |
| TEST-21 | Partición de replicación y escrituras de dueños distintos | Convergencia sin bucles/duplicación al reconectar |
| TEST-22 | Caída de A/maestro | No se cambia de dueño; B actúa sólo sobre recursos/sesiones permitidos |
| TEST-23 | Restricciones/huérfanos después de sincronizar | Conciliación explícita, sin asumir FK verificadas en apply |
| TEST-24 | Outbox enviado y caída antes del acuse local | Reintento deduplicado por consumidor |
| TEST-25 | FDW real, DML y fuente no disponible | SELECT correcto, escrituras rechazadas y error controlado |
| TEST-26 | Restauración aislada de BD y documentos | Datos, hashes y totales conciliados; tiempo real registrado |
| TEST-27 | Recreación de contenedor PG18 | Persistencia de datos demostrada |
| TEST-28 | Consultas y carga RNF | Resultados medidos con entorno y dataset, índices justificados |
| TEST-29 | Flujo UI completo y errores | Pantallas integradas, sin mocks ocultos ni confirmaciones ficticias |
| TEST-30 | MER ↔ relacional ↔ DDL ↔ reglas | Identidad, cardinalidades y constraints consistentes |
| TEST-31 | Grafo y trazabilidad | Reglas consultables y enlaces a implementación/pruebas reales |
| TEST-32 | Reconocimiento repetido por entrega/pago/PDF | No aparece una segunda venta, deuda o costo |
| TEST-33 | Animal con baja por muerte | No habilita recompra por el mero estado de ciclo cerrado |
| TEST-34 | Nuevo documento tras una revisión | La aprobación anterior conserva su versión; cambios relevantes exigen nueva revisión |
| TEST-35 | Anulación antes de entrega con costo tardío ya registrado | Restituye costo neto vigente del ciclo; ejemplo 1,200 a inventario y costo neto de venta anulada 0 |

No sustituyas las pruebas de PostgreSQL por H2. Testcontainers valida SQL real; replicación requiere dos clusters. No escribas pruebas que sólo afirmen la existencia de una clase o repitan el cálculo con el mismo método que quieren probar.

## 18.2 Paquete académico

Entrega un índice que permita al profesor revisar:

1. Planteamiento del problema, objetivo general/específicos y alcance.
2. Justificación del negocio, beneficiarios, oferta comercial y límites.
3. Marco teórico y fuentes con fecha.
4. Actores, casos de uso, RN/RF/RNF y matriz de cobertura.
5. MER Chen editable, exportaciones y explicación de notación.
6. Modelo relacional, mapeo, claves, diccionario y normalización.
7. SQL de tablas, constraints, índices, usuarios/roles y permisos.
8. PL/pgSQL y triggers con propósito y prueba.
9. Transacciones/concurrencia/idempotencia con evidencia.
10. M–M, Pgpool y FDW con diagrama, scripts, límites y demo.
11. Java/POO/SOLID/patrones con referencias al código.
12. Frontend integrado, contrato y estados de error.
13. Arquitectura, despliegue y configuración reproducible.
14. Backup/restauración medida y manual de operación.
15. README con tareas por persona, metodología y fechas.
16. Grafo de contexto actualizado y trazabilidad.
17. Manual de usuario, datos sintéticos y video/capturas si la clase los pide.
18. Resultados reales, limitaciones y siguientes pasos comerciales.

No afirmes que el profesor exige un formato de tesis, número de páginas o una norma de citación que no se haya proporcionado. Si no hay formato, usa un estilo consistente y bibliografía verificable.

## 18.3 Demostración sugerida de 12–15 minutos

- 2 min: problema, comprador, propuesta y alcance.
- 3 min: MER/relacional, entidad débil, cardinalidad y constraint destacado.
- 4 min: compra → pesaje → venta → liquidación → anticipo/saldo.
- 3 min: doble venta rechazada, permisos y replicación/FDW.
- 2 min: recuperación, arquitectura y documentación/grafo.
- 1 min: modelo comercial, resultados obtenidos y límite del piloto.

Ajusta al tiempo real de la exposición. Prepara datos sintéticos y comandos de recuperación de la demo. Una captura debe corresponder a una ejecución real; conserva la alternativa de mostrar evidencia guardada si el aula no tiene red.

# 19. Primeras acciones concretas y orden de respuesta de Claude

Empieza con este orden, sin saltar al frontend final:

1. Leer repo/instrucciones y este megaprompt; publicar inventario y plan breve.
2. Crear contexto de negocio, glosario, requisitos, RN y evidencia/fuentes.
3. Resolver contradicciones conceptuales y casos GOLD; registrar decisiones.
4. Generar MER Chen con vistas, matriz de relaciones y fuentes editables.
5. Derivar modelo relacional, claves, diccionario y normalización.
6. Revisar que selección, posición, costo, pago, periodo y propietario sean coherentes.
7. Crear arquitectura, ADR, despliegue y OpenAPI inicial.
8. Crear README, CLAUDE.md, backlog Aldo/Jared y calendario con casillas.
9. Instalar/usar Graphify real dentro de permisos, generar y verificar grafo.
10. Entregar los artefactos del primer incremento y el resultado de su revisión.
11. Continuar con migraciones/bootstrap y flujos verticales en el orden del backlog.

Tu primer informe debe incluir enlaces a archivos reales, diferencias entre decisiones propuestas y confirmadas, una muestra de relaciones explicadas y la siguiente tarea lista para ejecutar. No presentes solamente un plan prometiendo que luego crearás los .md.

Antes de una implementación financiera, verifica que MER/relacional/contrato y pruebas de ejemplo sean compatibles. La revisión ordinaria puede realizarse autónomamente; solicita información humana únicamente para una dependencia real que no puedas inferir y avanza en el resto.

Antes de comercializar, separa los hitos:

- Entrega académica funcional: requisitos y evidencia reproducibles.
- Piloto controlado: cliente, alcance, datos autorizados, respaldo/recuperación y soporte definido.
- Venta recurrente: problema/precio validados, contratación y facturación del servicio, operación medida y costos conocidos.

La entrega de octubre no demuestra por sí sola que exista product–market fit ni que todo el flujo pecuario/regulatorio esté resuelto.

# 20. Fuentes, investigación pendiente y uso responsable de evidencia

## 20.1 Bibliografía inicial consultada

Fecha de corte de esta investigación: 11 de octubre de 2026 UTC. Revisa la vigencia al implementar. Las decisiones de producto y cifras hipotéticas se identifican como propuestas; ninguna fuente externa valida automáticamente la demanda, los ingresos o la corrección de nuestra implementación.

| ID | Fuente | Qué respalda / limitación | Enlace |
|---|---|---|---|
| F01 | EngordaMax | Oferta comercial del competidor: compras, pesajes, costos y utilidad. Las afirmaciones comerciales son del proveedor. | [Fuente](https://engordamax.mx/) |
| F02 | Agryxo / Agroapp | Oferta comercial del competidor: compraventa, inventario, cartera y margen. No demuestra demanda validada para BoviCierre. | [Fuente](https://www.agryxo.com/) |
| F03 | Strategyzer — Business Model Canvas | Marco de nueve bloques para formular hipótesis del modelo de negocio. | [Fuente](https://www.strategyzer.com/library/the-business-model-canvas) |
| F04 | DOF / SIDOF — NOM-001-SAG/GAN-2015 | Texto de identificación animal; consultar alcance y disposiciones pertinentes. | [Fuente](https://sidof.segob.gob.mx/notas/docFuente/5394324) |
| F05 | Secretaría de Economía — catálogo de la NOM-001 | Estado de la norma y referencias oficiales; revalidar cambios. | [Fuente](https://platiica.economia.gob.mx/normalizacion/nom-001-sag-gan-2015/) |
| F06 | DOF / SIDOF — acuerdo DINESA, 2 diciembre 2025 | Ejemplo oficial de medidas sanitarias/movilización diferenciadas; no sustituye comprobar disposiciones posteriores. | [Fuente](https://sidof.segob.gob.mx/notas/docFuente/5774853) |
| F07 | SENASICA — SINACAM | Consulta oficial de requisitos de movilización; no se ha verificado API pública para integrarla al MVP. | [Fuente](https://sistemasssl.senasica.gob.mx/SINACAMWeb/pages/consulta/requisitos/inicio.xhtml) |
| F08 | Poder Judicial de Chiapas — Ley de Fomento y Sanidad Pecuaria | PDF oficial consultado indica última reforma 19 abril 2023; revisar reformas posteriores y requisitos del caso. | [Fuente](https://www.poderjudicialchiapas.gob.mx/storage/legislacion/584C1A2A-3BB9-4D04-9073-40767B7624EF.pdf) |
| F09 | SAT — proveedores autorizados de certificación de CFDI | Referencia para un proceso fiscal válido; no convierte un PDF interno en CFDI. | [Fuente](https://www.sat.gob.mx/portal/public/tramites/lista-de-proveedores-autorizados-de-certificacion-de-cfdi) |
| F10 | Cámara de Diputados — LFPDPPP | Texto vigente consultado sobre tratamiento de datos personales en posesión de particulares. | [Fuente](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) |
| F11 | Oklahoma State University Extension — Managing Shrink and Weighing Conditions in Beef Cattle | Factores que afectan cambios de peso; no determina descuentos comerciales universales. | [Fuente](https://extension.okstate.edu/fact-sheets/managing-shrink-and-weighing-conditions-in-beef-cattle) |
| F12 | Peter P. Chen (1976), registro institucional MIT | Fundamento del modelo entidad–relación. DOI: 10.1145/320434.320440. | [Fuente](https://dspace.mit.edu/entities/publication/5f4dcb94-111c-4368-8374-cec8842dee1d) |
| F13 | E. F. Codd (1970), IBM Research | Fundamento del modelo relacional. DOI: 10.1145/362384.362685. | [Fuente](https://research.ibm.com/publications/a-relational-model-of-data-for-large-shared-data-banks) |
| F14 | Technical University of Munich — material de modelado ER | Referencia académica de entidades, relaciones, participación y modelado. | [Fuente](https://db.in.tum.de/~grust/teaching/ss08/DBfA/db1-03.pdf) |
| F15 | Rensselaer Polytechnic Institute — BCNF, 3NF y ER | Claves, descomposiciones, unión sin pérdida y preservación de dependencias. | [Fuente](https://www.cs.rpi.edu/~sibel/csci4380/fall2026/lecture_notes/lecture7.html) |
| F16 | The Kanban Guide, versión de mayo 2025 | Flujo, políticas y control del trabajo en curso; WIP concreto del equipo es propuesta local. | [Fuente](https://kanbanguides.org/the-kanban-guide) |
| F17 | Michael Nygard — Documenting Architecture Decisions | Estructura y propósito de ADR. | [Fuente](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) |
| F18 | Spring Boot — System Requirements | Compatibilidad Java/build y versión estable; fijar patch al implementar. | [Fuente](https://docs.spring.io/spring-boot/system-requirements.html) |
| F19 | Spring Framework — JDBC Core | JdbcTemplate, recursos, consultas y acceso SQL explícito. | [Fuente](https://docs.spring.io/spring-framework/reference/data-access/jdbc/core.html) |
| F20 | PostgreSQL 18 — Constraints | Restricciones declarativas y límites de CHECK entre filas. | [Fuente](https://www.postgresql.org/docs/18/ddl-constraints.html) |
| F21 | PostgreSQL 18 — Explicit Locking | Bloqueos de filas, concurrencia y deadlocks. | [Fuente](https://www.postgresql.org/docs/18/explicit-locking.html) |
| F22 | PostgreSQL 18 — CREATE SUBSCRIPTION | Opciones origin/copy_data y condiciones de creación de suscripciones. | [Fuente](https://www.postgresql.org/docs/18/sql-createsubscription.html) |
| F23 | PostgreSQL 18 — Logical Replication Restrictions | Objetos/DDL/secuencias que no se replican automáticamente. | [Fuente](https://www.postgresql.org/docs/18/logical-replication-restrictions.html) |
| F24 | PostgreSQL 18 — Logical Replication Architecture | Proceso apply y comportamiento de triggers. | [Fuente](https://www.postgresql.org/docs/18/logical-replication-architecture.html) |
| F25 | PostgreSQL 18 — Client Connection Defaults | session_replication_role y efecto sobre triggers/FK. | [Fuente](https://www.postgresql.org/docs/18/runtime-config-client.html) |
| F26 | PostgreSQL 18 — Logical Replication Security / Row Security | Identidades de apply, privilegios y límites de RLS; revisar también ddl-rowsecurity.html. | [Fuente](https://www.postgresql.org/docs/18/logical-replication-security.html) |
| F27 | PostgreSQL 18 — postgres_fdw | Tablas externas, transacciones y límites de preparación remota. | [Fuente](https://www.postgresql.org/docs/18/postgres-fdw.html) |
| F28 | Pgpool-II — Clustering mode | Modo raw y funciones que no ofrece. | [Fuente](https://www.pgpool.net/docs/latest/en/html/runtime-config-running-mode.html) |
| F29 | Docker Official Image — PostgreSQL | Inicialización, PGDATA y cambio de montaje en PostgreSQL 18. | [Fuente](https://hub.docker.com/_/postgres) |
| F30 | Docker — Compose in production | Configuración de despliegue con Compose en un servidor. | [Fuente](https://docs.docker.com/compose/how-tos/production/) |
| F31 | Docker — Compose secrets | Entrega de secretos a servicios y mecanismo de archivos. | [Fuente](https://docs.docker.com/compose/how-tos/use-secrets/) |
| F32 | Caddy — Automatic HTTPS | Automatización TLS y condiciones de funcionamiento. | [Fuente](https://caddyserver.com/docs/automatic-https) |
| F33 | DigitalOcean — Droplet pricing | Referencia USD 48/mes del plan Basic 4 vCPU/8 GiB consultado; precio no garantizado futuro. | [Fuente](https://www.digitalocean.com/pricing/droplets) |
| F34 | PostgreSQL 18 — pg_dump | Respaldos lógicos y opciones de exclusión para reconstrucción controlada. | [Fuente](https://www.postgresql.org/docs/18/app-pgdump.html) |
| F35 | PostgreSQL 18 — Continuous Archiving and PITR | Backups base, WAL y recuperación a un punto en el tiempo. | [Fuente](https://www.postgresql.org/docs/18/continuous-archiving.html) |
| F36 | Graphify-Labs — repositorio oficial graphify | Paquete graphifyy, instalación, comandos y formatos; verificar versión real. | [Fuente](https://github.com/Graphify-Labs/graphify) |
| F37 | Graphify — CLI reference | Interfaz y comandos del ejecutable. | [Fuente](https://docs.graphify.com/reference/overview) |
| F38 | Graphify — Incremental updates | Diferencia entre actualizar estructura de código y documentos mediante el asistente. | [Fuente](https://docs.graphify.com/guides/incremental-updates) |
| F39 | Graphify — Configuration | Configuración de alcance, exclusión y backend. | [Fuente](https://docs.graphify.com/reference/configuration) |
| F40 | Graphify — Team workflows | Colaboración y estado de grafos compartidos. | [Fuente](https://docs.graphify.com/guides/team-workflows) |
| F41 | Claude Code — Memory | CLAUDE.md, contexto persistente y organización de instrucciones. | [Fuente](https://code.claude.com/docs/en/memory) |
| F42 | Claude Code — Skills | Skills, slash commands y extensión de Claude Code. | [Fuente](https://code.claude.com/docs/en/skills) |
| F43 | Graphviz — Node shapes | Shapes para diagramas reproducibles; la semántica Chen la define el modelador. | [Fuente](https://graphviz.org/doc/info/shapes.html) |
| F44 | GitHub — Tasklists | Sintaxis GFM de casillas y comportamiento de listas. | [Fuente](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists) |
| F45 | React — Quick Start | Documentación oficial del frontend propuesto. | [Fuente](https://react.dev/learn) |
| F46 | Vite — Getting Started | Inicialización y compatibilidad de herramientas/Node. | [Fuente](https://vite.dev/guide/) |
| F47 | Testcontainers for Java — PostgreSQL module | Pruebas con una instancia PostgreSQL real. | [Fuente](https://java.testcontainers.org/modules/databases/postgres/) |
| F48 | OpenStax / Rice University — Financial Accounting, 10.1 | Base conceptual para rastrear costo identificado y separar inventario de costo vendido; no dicta tratamiento fiscal del ganado. | [Fuente](https://openstax.org/books/principles-financial-accounting/pages/10-1-describe-and-demonstrate-the-basic-inventory-valuation-methods-and-their-cost-flow-assumptions) |
| F49 | OpenStax / Rice University — Managerial Accounting, 3.1 | Contribución, costos variables y rango relevante de costos fijos para economía del SaaS. | [Fuente](https://openstax.org/books/principles-managerial-accounting/pages/3-1-explain-contribution-margin-and-calculate-contribution-margin-per-unit-contribution-margin-ratio-and-total-contribution-margin) |

Las referencias OpenStax [F48–F49] apoyan conceptos de costo y contribución. BoviCierre propone una política gerencial propia por posición y una métrica denominada margen comercial. No asumas aplicación de US GAAP, IFRS/IAS 2/IAS 41 ni reglas tributarias mexicanas a partir de esos ejemplos.

En sources.md, agrega autor/institución, título, URL, publicación/versión, consulta, afirmación respaldada, alcance y notas. Diferencia el sitio comercial del proveedor de una norma, artículo académico o documentación del motor. Si un enlace deja de estar disponible, busca su ubicación oficial y registra la sustitución.

## 20.2 Qué debes buscar/verificar primero

| Tema | Fuente/búsqueda inicial | Decisión que puede cambiar |
|---|---|---|
| Rúbrica exacta | Imagen, temario y aclaraciones proporcionadas por el profesor | Interpretación de MER, M–M y evidencias obligatorias |
| Identificación | NOM-001, catálogo oficial y modificaciones DOF | Campos, terminología, evidencias y revisión |
| Movilización del piloto | SINACAM, SENASICA, DOF y norma estatal para origen/destino/finalidad | Expediente administrativo, nunca aprobación automática |
| Tratamiento de datos | Texto vigente de LFPDPPP y condiciones del cliente | Acceso, aviso, retención, exportación y responsabilidades |
| Facturación del servicio | SAT, situación fiscal y proveedor autorizado cuando corresponda | Cobro real de BoviCierre y facturación, fuera del cálculo del ganado |
| Competencia | Oferta/demo pública de EngordaMax, Agryxo y alternativas encontradas | Diferenciación, segmento y alcance de oferta |
| Demanda | Entrevistas y observación autorizada de un cierre real | Qué módulo genera disposición a pagar |
| Stack | Documentación oficial Spring, PostgreSQL, Pgpool, React, Vite y dependencias elegidas | Versiones compatibles, configuración y límites |
| Replicación | CREATE SUBSCRIPTION, seguridad, conflictos y restricciones del PostgreSQL fijado | Bootstrap, dueño, monitoreo y recuperación |
| Graphify | Repositorio y documentación de la versión instalada | Sintaxis, corpus, actualización semántica y exclusiones |
| Infraestructura | Cotización real de servidor, almacenamiento, respaldo y dominio | Costos, capacidad y precio mínimo del SaaS |

No pidas que el usuario repita datos que ya estén en sus archivos. Si no hay cliente ni rúbrica adicional, continúa con las hipótesis de este documento y déjalas visibles. No conviertas una ausencia de datos en una entrevista imaginaria.

## 20.3 Registro de riesgos y decisiones abiertas

Mantén un registro breve con ID, impacto, evidencia, dueño, mitigación y estado. Inicialmente:

- Que el profesor interprete M–M como escritura libre de la misma fila.
- Que el primer cliente necesite movimientos entre sedes o inventario inicial histórico.
- Que los documentos/pesajes reales no permitan reconstruir el costo individual sin asignación aprobada.
- Que el problema prioritario del cliente sea otro o el precio propuesto no se sostenga.
- Que el plazo efectivo/capacidad del equipo sea menor al supuesto.
- Que la recuperación o la convergencia no cumplan los objetivos propuestos.
- Que una integración tenga costo, permiso o API diferente a lo supuesto.

Cada riesgo debe tener una acción concreta; no lo conviertas en una lista genérica que nunca influya en el backlog.

## 20.4 Cierre de cada incremento

Al terminar cada incremento informa:

- Qué existe y funciona, con evidencia.
- Qué decisiones/cambios se documentaron.
- Qué pruebas se ejecutaron y cuáles no.
- Qué fuentes o hipótesis cambiaron.
- Qué estado tiene el grafo y a qué revisión corresponde.
- Qué tarea sigue para Aldo y para Jared.
- Qué limitación real afecta la entrega o el piloto.

No resumas este megaprompt de forma que pierda reglas antes de usarlo. Conserva la especificación como referencia y distribuye su contexto en los documentos especializados. El objetivo es construir un proyecto defendible por su modelo, sus datos y su funcionamiento.







