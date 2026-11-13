# Plan de implementación del frontend

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Fecha objetivo | 13 de noviembre de 2026 |
| Rama de trabajo | `feat/frontend-mvp` |
| Especificación funcional | SPEC-004 v0.2 aprobada y refinada |
| Stack | React, Vite, JavaScript, CSS3, Recharts |

## Objetivo

Entregar un frontend funcional integrado exclusivamente con la API REST de FastAPI, respetando SPEC-004, ARCH-001 y DA-001. La reutilización del Programa 1 será selectiva y no modificará ese repositorio.

## Entregas

1. **Base técnica:** React/Vite, proxy hacia FastAPI, cliente HTTP centralizado, manejo uniforme de errores y formato de datos.
2. **Dashboard anual:** selector de año, presupuesto general, gasto real, saldo, gasto estimado, indicadores por celebración y alertas.
3. **Años y presupuestos:** creación y consulta de años, presupuesto general y presupuestos de Navidad y Fin de Año; históricos en modo lectura.
4. **Productos:** consulta, registro, edición y eliminación de productos pendientes; filtros por categoría, estado y búsqueda.
5. **Compras:** marcar como comprado y corregir compras conservando ID, celebración y estado; no permitir eliminar comprados ni devolverlos a pendientes.
6. **Calidad y cierre:** validación de flujos, estados de carga/vacío/error, diseño responsive, documentación y publicación.

## Reglas de integración no negociables

- Todas las solicitudes usan el prefijo `/api/v1`.
- No se accede directamente al archivo JSON ni a la persistencia.
- Cantidades, precios y presupuestos se envían como cadenas decimales.
- No se realizan cálculos de negocio en el frontend.
- Las reglas de años históricos y estados de producto se aplican según el backend y SPEC-004.
- Los errores se presentan desde la estructura uniforme `error.codigo`, `error.mensaje`, `error.detalles`.
- No se inventan rutas, parámetros ni propiedades que no estén en el contrato.

## Verificaciones y ajustes de integración

1. Se confirmó que los schemas de producto de la rama aceptan los valores slug publicados por `/catalogos` y los normalizan a los enums internos.
2. Se confirmó que el listado de productos admite los filtros `categoria`, `estado` y `buscar`, utilizados por la interfaz.
3. Se alineó la generación de alertas con SPEC-002 v0.3: solo se genera alerta cuando el gasto real supera el presupuesto correspondiente. Se retiraron las alertas preventivas al 80% y las alertas por asignación superior al presupuesto general.
4. La metadata y el contenido documental de SPEC-004 requieren una actualización final, sin modificar su contrato aprobado ni reabrir su aprobación.

## Criterios de aceptación

- La aplicación instala dependencias y ejecuta `npm run dev`.
- `npm run build` finaliza sin errores.
- Dashboard y módulos consumen datos reales de FastAPI.
- Los contratos JSON respetan tipos, nombres y validaciones de SPEC-004.
- Los estados pendientes/comprados y años históricos se protegen en UI y backend.
- Se validan escenarios de carga, vacío, error y éxito.
- El diseño respeta DA-001 y funciona en escritorio y móvil.
- La documentación y la rama de trabajo quedan actualizadas.

## Estado de ejecución

- [x] Rama de trabajo creada.
- [x] Base React/Vite y proxy de API.
- [x] Cliente API centralizado.
- [x] Dashboard anual inicial conectado a la API.
- [x] Gestión de años y presupuestos.
- [x] Gestión de productos y filtros.
- [x] Flujos de compra y corrección.
- [x] Alineación de alertas backend con SPEC-002 v0.3.
- [ ] Pruebas funcionales y build local.
- [ ] Actualización documental final, validación y publicación.
