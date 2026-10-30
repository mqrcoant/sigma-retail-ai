-- Todas las comprobaciones deben devolver 0 o igualdad exacta.
SELECT 'huérfanos temporales' control,COUNT(*) incidencias FROM fact_ventas f LEFT JOIN dim_tiempo d ON f.tiempo_sk=d.tiempo_sk WHERE d.tiempo_sk IS NULL;
SELECT 'descuadre de ingreso' control,COUNT(*) incidencias FROM fact_ventas WHERE ingreso_neto_cent<>ingreso_bruto_cent-descuento_cent-devolucion_cent;
SELECT 'descuadre de margen' control,COUNT(*) incidencias FROM fact_ventas WHERE margen_bruto_cent<>ingreso_neto_cent-costo_cent;
SELECT 'conciliacion' control,(SELECT SUM(ingreso_neto_cent) FROM fact_ventas)-(SELECT neto_cent FROM conciliacion_fuente) diferencia_cent;
SELECT 'filas' control,(SELECT COUNT(*) FROM fact_ventas)-(SELECT lineas FROM conciliacion_fuente) diferencia;
SELECT 'solapamientos SCD2' control,COUNT(*) incidencias FROM dim_cliente a JOIN dim_cliente b ON a.cliente_nk=b.cliente_nk AND a.cliente_sk<b.cliente_sk AND a.vigente_desde<=b.vigente_hasta AND b.vigente_desde<=a.vigente_hasta;
SELECT 'cliente histórico incorrecto' control,COUNT(*) incidencias FROM fact_ventas f JOIN dim_cliente c ON f.cliente_sk=c.cliente_sk JOIN dim_tiempo t ON f.tiempo_sk=t.tiempo_sk WHERE t.fecha<c.vigente_desde OR t.fecha>c.vigente_hasta;
