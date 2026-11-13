# SPEC-004 — Contratos API

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-004 |
| Versión | 0.2 |
| Estado | Aprobada y refinada |
| Prefijo | `/api/v1` |
| Formato | JSON UTF-8 |
| Implementación de referencia | Backend FastAPI, modelos Pydantic y pruebas de API |

> **Nota de trazabilidad:** esta transcripción documenta los contratos observables en los esquemas Pydantic, routers y pruebas de la rama `feat/frontend-mvp`. No sustituye ni reescribe el texto original de los criterios aprobados API-001 a API-020. Los enunciados literales de esos criterios quedan pendientes de cotejo con su fuente aprobada.

## 1. Convenciones generales

- La API utiliza JSON UTF-8.
- El prefijo de todas las rutas es `/api/v1`.
- Los identificadores de año y celebración son UUID en las respuestas; los identificadores de producto se reciben en la ruta como UUID.
- Los valores decimales enviados en solicitudes deben representarse como cadenas decimales JSON. No se admiten números JSON para los campos decimales.
- Las respuestas serializan importes y cantidades como cadenas. Los importes de presupuestos y los decimales de productos anidados en la respuesta del año se formatean con dos decimales; los precios/cantidades de `ProductoResponse` se serializan como cadenas decimales.
- Los campos adicionales no definidos en los modelos de solicitud se rechazan (`extra="forbid"`).
- Los valores de categoría y unidad admiten los valores visibles del catálogo en los contratos de producto. El endpoint de catálogo entrega sus valores normalizados tipo slug.
- Tipos de celebración en las rutas: `navidad` y `fin_anio`.
- Estados de producto: `pendiente` y `comprado`.
- La descripción del producto puede ser una cadena o `null`.
- Los campos de fecha se representan como fecha-hora ISO 8601.
- Los errores de aplicación utilizan la estructura uniforme descrita en la sección 3.

### 1.1 Catálogos controlados

**Categorías (valor de solicitud en producto / valor de catálogo):**

| Valor catálogo | Etiqueta / valor de dominio |
|---|---|
| `alimentos` | Alimentos |
| `bebidas` | Bebidas |
| `ingredientes` | Ingredientes |
| `decoracion` | Decoración |
| `desechables_utensilios` | Desechables y utensilios |
| `otros` | Otros |

**Unidades:**

| Valor catálogo | Etiqueta / valor de dominio |
|---|---|
| `unidad` | Unidad |
| `kilogramo` | Kilogramo |
| `gramo` | Gramo |
| `litro` | Litro |
| `mililitro` | Mililitro |
| `paquete` | Paquete |
| `botella` | Botella |
| `docena` | Docena |
| `otro` | Otro |

**Estados:** `pendiente` (Pendiente), `comprado` (Comprado).

## 2. Contrato uniforme de errores

La estructura de error de aplicación es:

```json
{
  "error": {
    "codigo": "CODIGO_ERROR",
    "mensaje": "Descripción del error",
    "detalles": []
  }
}
```

Campos:
- `error.codigo`: identificador textual del error.
- `error.mensaje`: descripción legible.
- `error.detalles`: arreglo de detalles; puede estar vacío.

Códigos HTTP identificados en el proyecto: `200`, `201`, `204`, `400`, `404`, `409`, `422` y `500`. La relación completa de todos los escenarios y códigos aprobados debe cotejarse con API-001 a API-020; no se asignan aquí escenarios no demostrados.

## 3. Contratos de años y presupuestos

### 3.1 Crear año

- **Método y ruta:** `POST /api/v1/anios`
- **Éxito:** `201 Created`
- **Solicitud:** todos los campos siguientes forman parte del modelo de solicitud. Los presupuestos aceptan cadena decimal o `null`.

```json
{
  "anio": 2027,
  "presupuesto_general": "1500000.00",
  "presupuesto_navidad": "1000000.00",
  "presupuesto_fin_anio": "500000.00"
}
```

- `anio`: entero.
- `presupuesto_general`, `presupuesto_navidad`, `presupuesto_fin_anio`: decimal no negativo como cadena o `null`.
- El servicio genera los UUID y fechas. Cada año contiene exactamente una celebración de Navidad y una de Fin de Año.
- La implementación impide crear años anteriores al año calendario actual y rechaza años duplicados.

**Respuesta:** objeto `AnioResponse`, conforme a la sección 3.3.

### 3.2 Listar años

- **Método y ruta:** `GET /api/v1/anios`
- **Éxito:** `200 OK`
- **Solicitud:** sin cuerpo.
- **Respuesta:**

```json
{
  "anios": [
    {
      "id": "UUID",
      "anio": 2027,
      "presupuesto_general": "1500000.00"
    }
  ]
}
```

Los registros se ordenan por año ascendente en el servicio. `presupuesto_general` puede ser `null`.

### 3.3 Consultar año

- **Método y ruta:** `GET /api/v1/anios/{anio}`
- **Éxito:** `200 OK`
- **Solicitud:** parámetro de ruta `anio` entero.
- **Respuesta:** `AnioResponse`.

```json
{
  "id": "UUID",
  "anio": 2027,
  "presupuesto_general": "1500000.00",
  "fecha_creacion": "2026-11-13T10:00:00",
  "fecha_actualizacion": "2026-11-13T10:00:00",
  "celebraciones": [
    {
      "id": "UUID",
      "tipo": "Navidad",
      "presupuesto": "1000000.00",
      "productos": []
    },
    {
      "id": "UUID",
      "tipo": "Fin de Año",
      "presupuesto": "500000.00",
      "productos": []
    }
  ]
}
```

Cada producto anidado en `celebraciones[].productos[]` contiene: `id`, `nombre`, `descripcion`, `categoria`, `cantidad`, `unidad`, `precio_unitario_estimado`, `precio_unitario_real`, `estado`, `fecha_creacion` y `fecha_actualizacion`. Los decimales de este producto anidado se serializan con dos decimales.

### 3.4 Actualizar presupuesto general

- **Método y ruta:** `PUT /api/v1/anios/{anio}/presupuesto-general`
- **Éxito:** `200 OK`
- **Solicitud:**

```json
{
  "presupuesto_general": "1800000.00"
}
```

El valor puede ser una cadena decimal no negativa o `null`. El cero se normaliza a presupuesto no configurado (`null`). La respuesta es `AnioResponse`.

### 3.5 Actualizar presupuesto de celebración

- **Método y ruta:** `PUT /api/v1/anios/{anio}/celebraciones/{tipo}/presupuesto`
- **Éxito:** `200 OK`
- **Parámetro `tipo`:** `navidad` o `fin_anio`.
- **Solicitud:**

```json
{
  "presupuesto": "750000.00"
}
```

El valor puede ser una cadena decimal no negativa o `null`. El cero se normaliza a `null`. La respuesta es `AnioResponse`.

## 4. Contratos de productos y compras

### 4.1 Estructura base de solicitud de producto

Los siguientes campos se utilizan al crear un producto, editar un pendiente y corregir una compra:

```json
{
  "nombre": "Cena navideña",
  "descripcion": "Productos para la celebración",
  "categoria": "Alimentos",
  "cantidad": "2",
  "unidad": "Unidad",
  "precio_unitario_estimado": "25.50"
}
```

Reglas de validación:
- `nombre`: cadena no vacía después de eliminar espacios laterales.
- `descripcion`: cadena o `null`; opcional.
- `categoria`: una de las seis categorías controladas.
- `cantidad`: cadena decimal finita estrictamente mayor que cero.
- `unidad`: una de las nueve unidades controladas.
- `precio_unitario_estimado`: cadena decimal finita mayor o igual a cero.
- No se admiten propiedades adicionales.

### 4.2 Registrar producto

- **Método y ruta:** `POST /api/v1/anios/{anio}/celebraciones/{tipo}/productos`
- **Éxito:** `201 Created`
- **Solicitud:** estructura base de producto (sección 4.1).
- **Respuesta:** `ProductoResponse`. El backend genera `id`, fechas, establece `estado="pendiente"` y `precio_unitario_real=null`.

### 4.3 Listar productos de celebración

- **Método y ruta:** `GET /api/v1/anios/{anio}/celebraciones/{tipo}/productos`
- **Éxito:** `200 OK`
- **Parámetros opcionales de consulta:**
  - `categoria`: slug de categoría (`alimentos`, `bebidas`, `ingredientes`, `decoracion`, `desechables_utensilios`, `otros`).
  - `estado`: `pendiente` o `comprado`.
  - `buscar`: texto de al menos un carácter; busca en nombre y descripción sin distinguir mayúsculas/minúsculas.
- **Respuesta:**

```json
{
  "productos": [
    {
      "id": "UUID",
      "nombre": "Cena navideña",
      "descripcion": "Productos para la celebración",
      "categoria": "Alimentos",
      "cantidad": "2",
      "unidad": "Unidad",
      "precio_unitario_estimado": "25.50",
      "precio_unitario_real": null,
      "estado": "pendiente",
      "fecha_creacion": "2026-11-13T10:00:00",
      "fecha_actualizacion": "2026-11-13T10:00:00"
    }
  ]
}
```

La respuesta completa contiene `productos: ProductoResponse[]`. El endpoint aplica los filtros recibidos en el backend.

### 4.4 Consultar producto

- **Método y ruta:** `GET /api/v1/productos/{producto_id}`
- **Éxito:** `200 OK`
- **Solicitud:** UUID del producto en la ruta.
- **Respuesta:** `ProductoResponse`, con los campos descritos en la sección 4.3 para cada producto.

### 4.5 Editar producto pendiente

- **Método y ruta:** `PUT /api/v1/productos/{producto_id}`
- **Éxito:** `200 OK`
- **Solicitud:** estructura base de producto (sección 4.1).
- **Respuesta:** `ProductoResponse`.
- Solo permite editar productos pendientes. Conserva el ID, la celebración y el estado. Un producto comprado no puede editarse mediante esta operación.

### 4.6 Eliminar producto pendiente

- **Método y ruta:** `DELETE /api/v1/productos/{producto_id}`
- **Éxito:** `204 No Content`
- **Solicitud:** UUID del producto en la ruta; sin cuerpo.
- **Respuesta:** sin cuerpo.
- Solo permite eliminar productos pendientes. La eliminación de un producto comprado se rechaza.

### 4.7 Marcar producto como comprado

- **Método y ruta:** `PATCH /api/v1/productos/{producto_id}/comprar`
- **Éxito:** `200 OK`
- **Solicitud:**

```json
{
  "precio_unitario_real": "24.00"
}
```

`precio_unitario_real` es obligatorio, debe ser cadena decimal finita mayor o igual a cero; el valor cero es válido.

- **Respuesta:** `ProductoResponse`, con `estado="comprado"` y el precio real registrado.
- La operación no admite volver a comprar un producto ya comprado.

### 4.8 Corregir producto comprado

- **Método y ruta:** `PATCH /api/v1/productos/{producto_id}/correccion-compra`
- **Éxito:** `200 OK`
- **Solicitud:** estructura base de producto (sección 4.1) más `precio_unitario_real` obligatorio como cadena decimal finita no negativa.

```json
{
  "nombre": "Cena navideña corregida",
  "descripcion": "Descripción actualizada",
  "categoria": "Alimentos",
  "cantidad": "3",
  "unidad": "Unidad",
  "precio_unitario_estimado": "28.00",
  "precio_unitario_real": "26.00"
}
```

- **Respuesta:** `ProductoResponse`.
- Solo aplica a productos comprados.
- Permite corregir nombre, descripción, categoría, cantidad, unidad, precio estimado y precio real.
- Conserva el ID, la celebración y el estado comprado. La validación se realiza antes de persistir.

## 5. Contratos de reportes

Todos los endpoints de reportes son consultas sin cuerpo de solicitud y devuelven `200 OK` cuando el año existe.

### 5.1 Resumen anual

- **Método y ruta:** `GET /api/v1/anios/{anio}/resumen`
- **Respuesta:**

```json
{
  "anio": 2027,
  "celebraciones": {
    "navidad": {
      "presupuesto": "1000000.00",
      "gasto_real": "200.00",
      "saldo": "999800.00"
    },
    "fin_anio": {
      "presupuesto": "500000.00",
      "gasto_real": "0.00",
      "saldo": "500000.00"
    }
  }
}
```

Los importes son cadenas decimales; presupuesto y saldo pueden ser `null` cuando no están configurados/calculables.

### 5.2 Dashboard anual

- **Método y ruta:** `GET /api/v1/anios/{anio}/dashboard`
- **Respuesta:** `DashboardResponse`.

Campos:
- `anio`: entero.
- `presupuesto_general`: cadena o `null`.
- `gasto_real_general`: cadena.
- `saldo_general`: cadena o `null`.
- `gasto_estimado_general`: cadena.
- `celebraciones`: objeto indexado por `navidad` y `fin_anio`; cada entrada contiene `presupuesto`, `gasto_real`, `saldo`, `gasto_estimado`, `productos_comprados`, `productos_pendientes` y `avance_compras`.
- `alertas`: arreglo de objetos con `codigo`, `tipo` (cadena o `null`), `alcance`, `mensaje` y `porcentaje_consumido` (cadena o `null`).

### 5.3 Resumen de celebración

- **Método y ruta:** `GET /api/v1/anios/{anio}/celebraciones/{tipo}/resumen`
- **Parámetro `tipo`:** `navidad` o `fin_anio`.
- **Respuesta:** objeto con `anio`, `tipo`, `presupuesto`, `gasto_real`, `saldo`, `gasto_estimado`, `productos_comprados`, `productos_pendientes`, `avance_compras` y `alertas`.
- Los importes, porcentajes y avances se representan como cadenas; el presupuesto y saldo pueden ser `null`.

### 5.4 Estadísticas por categoría

- **Método y ruta:** `GET /api/v1/anios/{anio}/estadisticas/categorias`
- **Respuesta:**

```json
{
  "anio": 2027,
  "gasto_real_general": "200.00",
  "categorias": [
    {
      "categoria": "Alimentos",
      "productos_total": 2,
      "productos_comprados": 1,
      "productos_pendientes": 1,
      "gasto_real": "200.00",
      "gasto_estimado": "210.00",
      "participacion_porcentual": "100.00"
    }
  ]
}
```

Cada elemento de `categorias` incluye `categoria`, `productos_total`, `productos_comprados`, `productos_pendientes`, `gasto_real`, `gasto_estimado` y `participacion_porcentual`.

## 6. Contrato de catálogos

- **Método y ruta:** `GET /api/v1/catalogos`
- **Éxito:** `200 OK`
- **Solicitud:** sin cuerpo.
- **Respuesta:** objeto con tres arreglos: `categorias`, `unidades` y `estados`. Cada opción contiene `valor` y `etiqueta`. Los valores y el orden son los establecidos en la sección 1.1.

## 7. Reglas de negocio reflejadas en los contratos

- Cada año contiene exactamente una celebración Navidad y una Fin de Año.
- No se permite crear años anteriores al año calendario actual.
- Los años históricos son de solo lectura para operaciones de escritura.
- Los presupuestos admiten `null` y valores no negativos; cero se normaliza a `null`.
- La cantidad del producto debe ser mayor que cero.
- Un producto pendiente no tiene precio real; un producto comprado debe tener precio real.
- El precio real puede ser cero.
- Los productos comprados no se eliminan, no vuelven a estado pendiente y no se editan por la ruta ordinaria.
- La corrección de compra mantiene ID, celebración y estado comprado.
- Los reportes se calculan a partir de los datos de dominio; no son endpoints de escritura.
- La API es la única vía de acceso del frontend a la persistencia JSON.

## 8. Matriz resumida de endpoints y respuestas

| Método | Ruta relativa al prefijo | Solicitud | Respuesta exitosa |
|---|---|---|---|
| POST | `/anios` | `CrearAnioRequest` | 201, `AnioResponse` |
| GET | `/anios` | Ninguna | 200, `ListaAniosResponse` |
| GET | `/anios/{anio}` | Parámetro de ruta | 200, `AnioResponse` |
| PUT | `/anios/{anio}/presupuesto-general` | `PresupuestoGeneralRequest` | 200, `AnioResponse` |
| PUT | `/anios/{anio}/celebraciones/{tipo}/presupuesto` | `PresupuestoCelebracionRequest` | 200, `AnioResponse` |
| POST | `/anios/{anio}/celebraciones/{tipo}/productos` | `CrearProductoRequest` | 201, `ProductoResponse` |
| GET | `/anios/{anio}/celebraciones/{tipo}/productos` | Filtros opcionales | 200, `ListaProductosResponse` |
| GET | `/productos/{producto_id}` | Parámetro de ruta | 200, `ProductoResponse` |
| PUT | `/productos/{producto_id}` | `ActualizarProductoRequest` | 200, `ProductoResponse` |
| DELETE | `/productos/{producto_id}` | Parámetro de ruta | 204, sin cuerpo |
| PATCH | `/productos/{producto_id}/comprar` | `MarcarCompradoRequest` | 200, `ProductoResponse` |
| PATCH | `/productos/{producto_id}/correccion-compra` | `CorregirCompraRequest` | 200, `ProductoResponse` |
| GET | `/anios/{anio}/resumen` | Parámetro de ruta | 200, `ResumenAnualResponse` |
| GET | `/anios/{anio}/dashboard` | Parámetro de ruta | 200, `DashboardResponse` |
| GET | `/anios/{anio}/celebraciones/{tipo}/resumen` | Parámetros de ruta | 200, `ResumenCelebracionResponse` |
| GET | `/anios/{anio}/estadisticas/categorias` | Parámetro de ruta | 200, `EstadisticasCategoriasResponse` |
| GET | `/catalogos` | Ninguna | 200, `CatalogosResponse` |

## 9. Criterios aprobados API-001 a API-020: cotejo pendiente

En el historial del proyecto consta la existencia y aprobación/refinamiento de los criterios API-001 a API-020. No se dispone en esta transcripción de sus enunciados literales completos. Por integridad documental:

- No se asignan identificadores API a las descripciones de este documento sin cotejo con la fuente aprobada.
- No se afirma que los ejemplos ilustrativos sustituyan los ejemplos originales aprobados.
- Se debe incorporar la redacción literal de API-001 a API-020 cuando se recupere su documento fuente.
- Esta limitación de transcripción no modifica ni invalida el estado aprobado de SPEC-004 v0.2.

## 10. Fuentes técnicas utilizadas para esta transcripción

Transcripción basada en la rama `feat/frontend-mvp` del repositorio:
- `backend/app/main.py`
- `backend/app/api/years.py`
- `backend/app/api/products.py`
- `backend/app/api/reports.py`
- `backend/app/api/catalogs.py`
- `backend/app/models/entities.py`
- `backend/app/schemas/year_schemas.py`
- `backend/app/schemas/product_schemas.py`
- `backend/app/schemas/report_schemas.py`
- `backend/app/schemas/catalog_schemas.py`
- Pruebas de API de productos, reportes y catálogos disponibles en la misma rama.

**Estado documental:** contratos request/response reconstruidos desde la implementación y sus modelos; cotejo literal de API-001 a API-020 aún pendiente. La versión aprobada SPEC-004 v0.2 se conserva.
