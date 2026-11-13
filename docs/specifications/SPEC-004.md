# SPEC-004 — Contratos API

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-004 |
| Versión | 0.2 |
| Estado | Aprobada y refinada |
| Prefijo | `/api/v1` |

## 1. Convenciones recuperadas

- API REST.
- JSON UTF-8.
- Identificadores UUID.
- Decimales y cantidades representados como cadenas decimales en la API.
- Filtros de productos: `categoria`, `estado`, `buscar`.
- Estructura uniforme de errores:

```json
{
  "error": {
    "codigo": "...",
    "mensaje": "...",
    "detalles": []
  }
}
```

Códigos HTTP identificados: `200`, `201`, `204`, `400`, `404`, `409`, `422`, `500`.

La asignación exacta de cada código a cada escenario debe conservarse conforme a los criterios API-001 a API-020 aprobados.

## 2. Inventario de endpoints recuperados

| N.º | Método | Ruta | Propósito recuperado |
|---:|---|---|---|
| 1 | POST | `/anios` | Crear año. |
| 2 | GET | `/anios` | Listar años. |
| 3 | GET | `/anios/{anio}` | Consultar año. |
| 4 | GET | `/anios/{anio}/resumen` | Consultar resumen anual. |
| 5 | PUT | `/anios/{anio}/presupuesto-general` | Configurar presupuesto general. |
| 6 | PUT | `/anios/{anio}/celebraciones/{tipo}/presupuesto` | Configurar presupuesto de una celebración. |
| 7 | GET | `/anios/{anio}/celebraciones/{tipo}/productos` | Listar productos de una celebración. |
| 8 | POST | `/anios/{anio}/celebraciones/{tipo}/productos` | Registrar producto. |
| 9 | GET | `/productos/{producto_id}` | Consultar producto. |
| 10 | PUT | `/productos/{producto_id}` | Editar producto pendiente. |
| 11 | DELETE | `/productos/{producto_id}` | Eliminar producto pendiente. |
| 12 | PATCH | `/productos/{producto_id}/comprar` | Marcar producto como comprado. |
| 13 | PATCH | `/productos/{producto_id}/correccion-compra` | Corregir producto comprado conforme a RN-063. |
| 14 | GET | `/anios/{anio}/dashboard` | Consultar dashboard anual. |
| 15 | GET | `/anios/{anio}/celebraciones/{tipo}/resumen` | Consultar resumen de celebración. |
| 16 | GET | `/anios/{anio}/estadisticas/categorias` | Consultar estadísticas por categoría. |
| 17 | GET | `/catalogos` | Consultar catálogos controlados. |

## 3. Reglas de separación de responsabilidades

- `PUT /productos/{producto_id}` corresponde a la edición ordinaria de productos pendientes.
- `PATCH /productos/{producto_id}/correccion-compra` permite corregir los campos de negocio editables de productos comprados, excepto ID, celebración y estado.
- La ruta de eliminación solo admite productos pendientes.
- La ruta de compra debe exigir cantidad mayor que cero y precio real registrado; el precio real cero es válido.
- Las operaciones de escritura deben respetar la condición de año histórico de solo lectura.
- Las respuestas y cálculos deben respetar las reglas de SPEC-002 y el modelo SPEC-003.

## 4. Criterios API

En el historial consta que existían criterios identificados como API-001 a API-020. Sus enunciados literales y los esquemas completos de solicitudes y respuestas no se recuperaron. No se reconstruyen ni inventan aquí.

## 5. Estado y limitación documental

SPEC-004 v0.2 está aprobada y refinada. Esta actualización corrige la metadata documental para reflejar la decisión de producto ya confirmada; no reabre la aprobación ni modifica los contratos acordados.

La copia de este archivo en GitHub todavía no reproduce íntegramente todos los esquemas request/response ni el texto completo de los criterios API-001 a API-020. Por tanto, debe completarse la transcripción documental a partir de los contratos aprobados y del historial del proyecto. Esta limitación del archivo no invalida ni suspende la aprobación de SPEC-004 v0.2.

Los contratos vigentes se implementan bajo el prefijo `/api/v1`; las decisiones de refinamiento aprobadas prevalecen sobre cualquier metadata o nota desactualizada que hubiera quedado en esta copia documental.
