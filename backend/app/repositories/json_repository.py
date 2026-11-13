
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from threading import RLock

from pydantic import ValidationError

from app.models.entities import DatosCompras, Metadata


class JsonRepository:
    """
    Repositorio de persistencia JSON.

    Responsabilidades:
    - Cargar y validar los datos.
    - Inicializar el documento cuando no existe.
    - Guardar mediante escritura temporal y sustitución atómica.
    - Proteger las operaciones de escritura concurrentes
      dentro del proceso.
    """

    _lock = RLock()
    def __init__(self, file_path: Path | str | None = None):
        backend_dir = Path(__file__).resolve().parents[2]

        self.file_path = (
            Path(file_path)
            if file_path is not None
            else backend_dir / "data" / "datos_compras.json"
        )


    def load(self) -> DatosCompras:
        """Carga el documento y valida su estructura."""

        with self._lock:
            if not self.file_path.exists():
                documento = self._documento_vacio()
                self.save(documento)
                return documento

            try:
                contenido = self.file_path.read_text(encoding="utf-8")
                return DatosCompras.model_validate_json(contenido)

            except (ValueError, ValidationError) as error:
                raise ValueError(
                    f"El archivo de datos no es válido: {self.file_path}"
                ) from error

    def save(self, documento: DatosCompras) -> None:
        """
        Guarda el documento mediante un archivo temporal.

        os.replace realiza la sustitución atómica cuando el archivo
        temporal y el archivo destino están en el mismo sistema
        de archivos.
        """

        with self._lock:
            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            contenido = documento.model_dump_json(indent=2) + "\n"

            archivo_temporal = None

            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    newline="\n",
                    dir=self.file_path.parent,
                    prefix=f".{self.file_path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as temporal:
                    archivo_temporal = Path(temporal.name)

                    temporal.write(contenido)
                    temporal.flush()
                    os.fsync(temporal.fileno())

                os.replace(archivo_temporal, self.file_path)

            finally:
                if (
                    archivo_temporal is not None
                    and archivo_temporal.exists()
                ):
                    archivo_temporal.unlink()

    @staticmethod
    def _documento_vacio() -> DatosCompras:
        """Construye la estructura inicial del sistema."""

        return DatosCompras(
            metadata=Metadata(schema_version="1.0"),
            anios=[],
        )
