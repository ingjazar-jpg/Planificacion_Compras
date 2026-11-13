# SPEC-003 — Modelo de datos

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-003 |
| Versión | 0.2 |
| Estado | Aprobada |
| Entidades | Año, Celebración y Producto |
| Persistencia | `datos_compras.json` |

## 1. Modelo conceptual

Se definen tres entidades principales y una estructura de metadatos.

- **Año:** identifica el período de planificación.
- **Celebración:** cada año tiene exactamente dos celebraciones: Navidad y Fin de Año.
- **Producto:** cada celebración administra su propia lista de compras.
- Relación: Año → dos Celebraciones → N Productos por celebración.

## 2. Entidades y atributos

### 2.1. Entidad Año

Representa un período anual de planificación.

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---:|---|
| `id` | UUID | Sí | Identificador único. |
| `anio` | Integer | Sí | Año de planificación. |
| `presupuesto_general` | Decimal / null | Sí | Presupuesto general; `null` si no está configurado. |
| `fecha_creacion` | Datetime | Sí | Fecha de creación. |
| `fecha_actualizacion` | Datetime | Sí | Última actualización. |

Restricciones:
- El año no podrá repetirse.
- Cada año tendrá exactamente dos celebraciones: Navidad y Fin de Año.
- Un presupuesto de cero se normalizará como no configurado (`null`).
- El presupuesto general no podrá ser negativo.
- Los años no se eliminan.

### 2.2. Entidad Celebración

Representa una de las dos listas de compras de cada año.

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---:|---|
| `id` | UUID | Sí | Identificador único. |
| `tipo` | String | Sí | Navidad o Fin de Año. |
| `presupuesto` | Decimal / null | Sí | Presupuesto individual. |
| `productos` | Array | Sí | Productos de la celebración. |

Restricciones:
- Cada año tendrá una celebración de Navidad.
- Cada año tendrá una celebración de Fin de Año.
- No se podrán duplicar celebraciones del mismo tipo dentro de un año.
- El presupuesto cero se considerará no configurado.
- La celebración no podrá pertenecer a más de un año.

### 2.3. Entidad Producto

Representa un elemento que se desea comprar para una celebración.

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---:|---|
| `id` | UUID | Sí | Identificador único. |
| `nombre` | String | Sí | Nombre del producto. |
| `descripcion` | String / null | No | Descripción adicional. |
| `categoria` | String | Sí | Categoría del producto. |
| `cantidad` | Decimal | Sí | Cantidad requerida. |
| `unidad` | String | Sí | Unidad de medida. |
| `precio_unitario_estimado` | Decimal | Sí | Precio previsto. |
| `precio_unitario_real` | Decimal / null | Según estado | Precio real de compra. |
| `estado` | String | Sí | Pendiente o Comprado. |
| `fecha_creacion` | Datetime | Sí | Fecha de registro. |
| `fecha_actualizacion` | Datetime | Sí | Última modificación. |

Restricciones:
- La cantidad debe ser mayor que cero.
- El precio estimado no puede ser negativo.
- El precio real puede ser cero o superior.
- Un producto pendiente tendrá precio real `null`.
- Un producto comprado deberá tener precio real registrado, incluso si es cero.
- El estado comprado no podrá revertirse.
- Los productos comprados podrán editarse, pero no eliminarse, conforme a RN-063 de SPEC-002 v0.3.

## 3. Catálogos controlados

### 3.1. Categorías

1. Alimentos.
2. Bebidas.
3. Ingredientes.
4. Decoración.
5. Desechables y utensilios.
6. Otros.

### 3.2. Unidades de medida

1. Unidad.
2. Kilogramo.
3. Gramo.
4. Litro.
5. Mililitro.
6. Paquete.
7. Botella.
8. Docena.
9. Otro.

### 3.3. Estados del producto

| Valor interno | Etiqueta visible |
|---|---|
| `pendiente` | Pendiente |
| `comprado` | Comprado |

Los valores internos se utilizan en el backend y las etiquetas visibles en la interfaz.

## 4. Modelo físico y persistencia recuperados

Las siguientes decisiones físicas constan en el historial de aprobación de SPEC-003 v0.2:

- Persistencia en archivo JSON local `datos_compras.json`, administrado exclusivamente por el backend.
- Estructura jerárquica Año → Celebraciones → Productos.
- Estructura de metadatos con `metadata.schema_version: "1.0"`.
- Identificadores UUID.
- Importes y cantidades decimales: `Decimal` en backend; no utilizar `float` para cálculos financieros.
- Fechas en formato ISO.
- Presupuestos cero normalizados a `null`.
- Productos pendientes con precio real `null`; productos comprados con precio real registrado, incluso cero.
- Cálculos derivados no se almacenan; se calculan dinámicamente.
- Se definieron restricciones de integridad y validación MD-001 a MD-013.

## 5. Ejemplo estructural de referencia

El ejemplo siguiente ilustra la estructura jerárquica y los nombres de metadatos recuperados. Los valores son demostrativos; el ejemplo no sustituye el ejemplo JSON original ni define campos adicionales.

```json
{
  "metadata": {
    "schema_version": "1.0"
  },
  "anios": [
    {
      "id": "UUID",
      "anio": 2026,
      "presupuesto_general": null,
      "fecha_creacion": "2026-01-01T10:00:00",
      "fecha_actualizacion": "2026-01-01T10:00:00",
      "celebraciones": [
        {
          "id": "UUID",
          "tipo": "Navidad",
          "presupuesto": null,
          "productos": []
        },
        {
          "id": "UUID",
          "tipo": "Fin de Año",
          "presupuesto": null,
          "productos": []
        }
      ]
    }
  ]
}
```

## 6. Restricciones y referencias

- MD-001 a MD-013 existen en el documento aprobado; sus enunciados literales no están recuperados en el contexto disponible.
- El modelo físico fue realizado y aprobado en SPEC-003 v0.2. Este archivo consolida los atributos compartidos por la usuaria y las decisiones físicas recuperadas; no debe interpretarse como reproducción literal de todas las tablas originales.
- La estructura exacta de los metadatos más allá de `schema_version` no se amplía sin cotejar el texto original.
