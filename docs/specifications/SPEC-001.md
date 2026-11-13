# SPEC-001 — Especificación funcional

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-001 |
| Versión | 0.2 |
| Estado | Aprobada |
| Fuente | Historial de conversaciones del proyecto |

## 1. Propósito

Desarrollar una aplicación web local para planificar y controlar las compras correspondientes a la Cena de Navidad del 24 de diciembre y la Cena de Fin de Año del 31 de diciembre, permitiendo administrar productos, presupuestos, compras realizadas, saldos y consultas por año.

## 2. Alcance funcional recuperado

El inventario funcional inicial del MVP está compuesto por los siguientes requisitos. Se conservan los identificadores RF-01 a RF-08 validados por la usuaria.

| ID | Requisito funcional |
|---|---|
| RF-01 | Agregar productos. |
| RF-02 | Registrar cantidad, unidad y precio unitario. |
| RF-03 | Calcular el costo por producto. |
| RF-04 | Calcular el total por celebración. |
| RF-05 | Administrar presupuestos máximos generales e individuales. |
| RF-06 | Generar alertas por exceso de presupuesto. |
| RF-07 | Gestionar los estados Comprado y Pendiente. |
| RF-08 | Consultar, modificar y eliminar productos, sujeto a las reglas de negocio. |

## 3. Contexto de uso

- Cada año de planificación contempla dos celebraciones: Navidad y Fin de Año.
- Cada celebración mantiene su propia lista de compras.
- El sistema permite consultar años anteriores en modo histórico de solo lectura.
- Los datos de cada año son independientes.

## 4. Alcance documental

Este archivo es una reconstrucción fiel de los elementos funcionales recuperados, no una transcripción íntegra del documento original SPEC-001 v0.2. No se agregan requisitos funcionales nuevos ni se atribuyen criterios de aceptación no recuperados al documento original.

Para las reglas detalladas, consultar `SPEC-002.md`; para entidades y atributos, `SPEC-003.md`; para contratos HTTP, `SPEC-004.md`; y para criterios de aceptación, `SPEC-005.md`.
