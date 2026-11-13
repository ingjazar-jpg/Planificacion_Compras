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

## Desviaciones detectadas para resolver

1. El endpoint de catálogos publica valores slug como `alimentos` y `kilogramo`, pero los schemas de producto validan valores de enum como `Alimentos` y `Kilogramo`. Debe alinearse el catálogo con el contrato de escritura y cubrirse con pruebas.
2. El contrato aprobado contempla filtros `categoria`, `estado` y `buscar`, pero la implementación actual del endpoint de listado no recibe esos parámetros. Debe implementarse y probarse en backend antes de activar filtros remotos en UI.
3. El archivo documental SPEC-004 en GitHub tiene metadata y secciones incompletas. Su estado aprobado/refinado ya fue confirmado por la responsable del producto; actualizar la documentación sin alterar el contrato funcional ni reabrir su aprobación.

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
- [ ] Gestión de años y presupuestos.
- [ ] Gestión de productos y filtros.
- [ ] Flujos de compra y corrección.
- [ ] Correcciones de integración backend.
- [ ] Pruebas funcionales y build local.
- [ ] Documentación final y publicación.
