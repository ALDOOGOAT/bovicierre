\set ON_ERROR_STOP on
BEGIN;
SET ROLE bovi_app_a;
SELECT bovi.consultar('11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','99999999-9999-4999-8999-999999999999','contrapartes','{}');
SELECT bovi.cmd_ejecutar('11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','99999999-9999-4999-8999-999999999999','DEMO-smoke-party-0001',repeat('a',64),uuidv7(),'crear_contraparte','{"nombre":"DEMO vendedor"}');
SELECT bovi.cmd_ejecutar('11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','99999999-9999-4999-8999-999999999999','DEMO-smoke-animal-0001',repeat('b',64),uuidv7(),'registrar_animal','{"sexo":"M","identificaciones":[{"sistema":"INTERNO","codigo":"DEMO-001"}]}');
ROLLBACK;
