-- V18 (DIV-14 / RN-019, DEC-24): una reserva no retiene inventario indefinidamente. vence_en lo envía el cliente
-- sin tope; se limita a 30 días desde creada_en (las reservas reales duran horas). Parámetro de negocio revisable.
-- La violación sale como 23514 *_check → 422 BV015 en la API. Las filas existentes cumplen (máximo ≈10 h).
ALTER TABLE bovi.reserva_venta ADD CONSTRAINT reserva_venta_vence_max_check CHECK (vence_en <= creada_en + interval '30 days');
