# ARCH-001 — Arquitectura técnica

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | ARCH-001 |
| Versión | 0.1 |
| Estado | Aprobada |
| Ejecución | Local |

## 1. Arquitectura general

Arquitectura cliente-servidor local:

- Frontend: React + Vite, JavaScript, JSX, HTML5 y CSS3.
- Backend: Python, FastAPI y Pydantic.
- Persistencia: archivo JSON local `datos_compras.json`, administrado exclusivamente por el backend.
- El frontend no accede directamente al archivo JSON.
- Backend y frontend se ejecutan como procesos independientes; el usuario accede mediante navegador.

## 2. Persistencia y seguridad de escritura

- Escritura segura mediante archivo temporal y sustitución atómica.
- Bloqueo de escritura para operaciones simultáneas.
- Validación de datos mediante Pydantic.
- Cálculos monetarios con Decimal, sin `float`.
- CORS limitado a los orígenes frontend configurados.
- La estructura exacta de carpetas puede ajustarse sin romper contratos.

## 3. Estructura modular

### Backend

Capas previstas:

- `api/`
- `schemas/`
- `services/`
- `repositories/`
- `models/`
- `core/`
- `tests/`

Persistencia principal prevista bajo `backend/data/datos_compras.json`.

### Frontend

Estructura prevista:

- `components/`
- `pages/`
- `features/`
- `services/`
- `hooks/`
- `context/`
- `utils/`
- `styles/`
- `assets/`

## 4. Copias de seguridad

- Copias de seguridad semanales mediante tarea programada local gestionada por el backend.
- Destino independiente: `backend/backups/`.
- Formato JSON, nombre con fecha y hora.
- Verificar integridad antes de considerar completado el respaldo.
- Si el equipo estuvo apagado y se perdió la ejecución semanal, generar el respaldo pendiente al iniciar el backend.
- Un fallo de respaldo no debe sustituir ni dañar el archivo principal.
- Documentar el procedimiento de restauración.

## 5. Zona horaria y ejecución

- Zona horaria: `system`, utilizar la zona configurada en el equipo.
- Ejecución local.
- Frontend y backend como procesos independientes.

## 6. Estrategia de pruebas

Se contemplan:

- Pruebas unitarias.
- Pruebas de integración.
- Pruebas de API.
- Pruebas de frontend.
- Pruebas end-to-end.
- Pruebas de regresión.

## 7. Restricciones tecnológicas

- No utilizar base de datos externa.
- No utilizar Bootstrap ni Tailwind.
- No permitir acceso directo del frontend al archivo JSON.
- No utilizar `float` para cálculos financieros.
- No modificar el repositorio del Programa 1 para reutilizar componentes.

## 8. Reutilización visual

El proyecto puede reutilizar selectivamente componentes del Programa 1 (`Gastos_Familiares`), adaptándolos a DA-001. La reutilización no debe introducir dependencias ni CSS innecesario y no debe modificar el Programa 1.
