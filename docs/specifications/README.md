# Proyecto 2 — Sistema de Planificación y Presupuesto de Compras

## Documentación de especificaciones

Esta carpeta reúne los documentos Markdown disponibles para iniciar el desarrollo bajo Spec-Driven Development.

**Regla de integridad documental:** los documentos se han reconstruido únicamente con decisiones y contenido recuperados de las conversaciones del proyecto. Cuando no se dispone del texto aprobado íntegro, se indica expresamente. Los resúmenes reconstruidos no deben confundirse con transcripciones literales ni utilizarse para inventar campos, reglas o contratos.

## Estado documental

| Documento | Versión | Estado conocido | Observación |
|---|---:|---|---|
| SPEC-001 | 0.2 | Aprobada | Se conserva el inventario funcional RF-01 a RF-08; el texto íntegro no está disponible en el contexto recuperado. |
| SPEC-002 | 0.3 | Aprobada | Incluye RN-063 aprobada mediante EN-001. Se consolidan las reglas de negocio confirmadas; no se afirma transcripción literal íntegra. |
| SPEC-003 | 0.2 | Aprobada | Modelo conceptual y físico parcialmente recuperados. Incluye el modelo de entidades compartido por la usuaria y decisiones físicas conocidas. |
| SPEC-004 | 0.2 | En revisión / aprobación final no acreditada | Se conserva el inventario de 17 endpoints y los elementos contractuales recuperados. Faltan esquemas completos y criterios API-001 a API-020. |
| SPEC-005 | 0.1 | Aprobada | Se conoce que contiene criterios CA-001 a CA-037, pero no se recuperó el texto literal completo. No se reconstruyen criterios como si fueran originales. |
| ARCH-001 | 0.1 | Aprobada | Se consolidan las decisiones arquitectónicas y operativas recuperadas. |
| DA-001 | — | Aprobada | Identidad visual aprobada para reutilización selectiva del Programa 1. |
| EN-001 | — | Aprobada | Enmienda que incorpora RN-063 a SPEC-002 v0.3. |

## Documentos

- [SPEC-001 — Especificación funcional](SPEC-001.md)
- [SPEC-002 — Reglas de negocio](SPEC-002.md)
- [SPEC-003 — Modelo de datos](SPEC-003.md)
- [SPEC-004 — Contratos API](SPEC-004.md)
- [SPEC-005 — Criterios de aceptación](SPEC-005.md)
- [ARCH-001 — Arquitectura técnica](ARCH-001.md)
- [DA-001 — Identidad visual](DA-001.md)
- [EN-001 — Enmienda de reglas de negocio](EN-001.md)

## Criterio para comenzar el desarrollo

La base funcional, las reglas de negocio, la arquitectura y la identidad visual están definidas. El desarrollo puede comenzar por la estructura del backend, modelos y persistencia, usando SPEC-003 y ARCH-001 como referencias. Antes de considerar cerrada la capa API, debe cotejarse SPEC-004 con el texto original o completarse formalmente su contrato sin alterar decisiones aprobadas.

No se deben bloquear tareas iniciales de estructura, configuración, modelos ya definidos ni pruebas unitarias por la finalización de toda la matriz de trazabilidad.

## Convenciones

- Markdown es la fuente documental versionada en Git.
- Los cambios de requisitos se realizan mediante control de cambios y actualización explícita de versión.
- No modificar documentos aprobados silenciosamente.
- Distinguir siempre: aprobado, reconstruido desde historial, pendiente de cotejo y propuesta.
