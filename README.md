# Sistema de Planificación y Presupuesto de Compras

Aplicación web para planificar y controlar las compras de Navidad y Fin de Año, administrar presupuestos por año y celebración, registrar productos y hacer seguimiento al gasto estimado y real.

## Estado del proyecto

El MVP del frontend está implementado en la rama `feat/frontend-mvp` e integrado con la API REST del backend.

- Frontend: React, JavaScript, Vite y CSS3.
- Backend: Python, FastAPI y Pydantic.
- Persistencia: repositorio JSON local gestionado por el backend.
- Visualización: Recharts.
- API versionada bajo el prefijo `/api/v1`.

Las especificaciones aprobadas son la fuente de verdad del proyecto. No se deben modificar reglas ni contratos sin el proceso de cambio correspondiente.

## Funcionalidades del MVP

- Crear y consultar años de planificación.
- Configurar presupuesto general y presupuestos para Navidad y Fin de Año.
- Consultar dashboard anual con indicadores generales y por celebración.
- Registrar, consultar, editar y eliminar productos pendientes.
- Filtrar productos por categoría, estado y texto de búsqueda.
- Marcar productos como comprados registrando cantidad y precio real.
- Corregir información permitida de compras registradas.
- Proteger productos comprados frente a eliminación o reversión a pendientes.
- Mantener los años anteriores en modo de solo lectura.
- Consultar catálogos desde la API.

## Estructura del proyecto

```text
backend/
  app/                 # API, modelos, esquemas, servicios y persistencia
  data/                # Datos JSON locales
  tests/               # Pruebas automatizadas
  requirements.txt
frontend/
  src/                 # Aplicación React, servicios y estilos
  package.json
  vite.config.js
docs/
  architecture/        # Arquitectura técnica
  implementation/     # Plan y seguimiento de implementación
  specifications/      # Especificaciones aprobadas
```

## Requisitos previos

- Python 3.11 o superior.
- Node.js y npm compatibles con la versión de Vite definida en `frontend/package.json`.

## Ejecución en entorno local

### 1. Backend

Desde la raíz del repositorio, en PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La API queda disponible en:

- API: http://127.0.0.1:8000
- Documentación interactiva: http://127.0.0.1:8000/docs

### 2. Frontend

En una segunda terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite mostrará en la terminal la dirección local para abrir la aplicación.

### 3. Pruebas del backend

Con el entorno virtual activado y ubicados en la carpeta `backend`:

```powershell
python -m pytest -v
```

### 4. Compilación de producción del frontend

Desde la carpeta `frontend`:

```powershell
npm run build
```

Los archivos compilados se generan en `frontend/dist/`.

## Integración y reglas técnicas

- El frontend consume la API REST; no accede directamente a los archivos JSON.
- Las solicitudes del frontend utilizan el prefijo `/api/v1`.
- Los importes y cantidades respetan los tipos y formatos definidos por los esquemas de la API.
- Los cálculos de negocio y las reglas de integridad corresponden al backend.
- La persistencia local es administrada por el backend.

## Documentación del proyecto

- [Especificaciones funcionales](docs/specifications/)
- [Arquitectura técnica](docs/architecture/)
- [Plan de implementación del frontend](docs/implementation/FRONTEND-PLAN.md)

Las especificaciones aprobadas constituyen la fuente única de verdad para el alcance, las reglas de negocio y los contratos del sistema.
