# SPEC-005 — Criterios de aceptación

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-005 |
| Versión | 0.1 |
| Estado | Aprobada |

## 1. Estado documental

En el historial consta la aprobación de SPEC-005 v0.1 y la existencia de criterios identificados CA-001 a CA-037. También consta CA-001.1, relacionado con impedir la creación de años anteriores al año calendario actual.

**Limitación:** el texto literal completo de CA-001 a CA-037 no está disponible en el contexto recuperado. No se reconstruyen descripciones como si fueran transcripciones aprobadas ni se asignan nuevos identificadores.

## 2. Decisiones de aceptación conocidas

- No se permite crear años anteriores al año calendario actual.
- Los años anteriores son históricos y solo permiten consulta.
- El presupuesto cero se normaliza a `null`.
- Si no hay presupuesto configurado, se muestra «Sin presupuesto configurado».
- El gasto real se calcula con productos comprados y precio real.
- Los productos comprados no se eliminan ni vuelven a pendientes.
- Se permite corregir los campos editables de productos comprados, excepto ID, celebración y estado, conforme a EN-001/RN-063.
- Las alertas se generan cuando el gasto real supera estrictamente el presupuesto configurado.
- Las alertas de presupuesto general y de cada celebración son independientes.
- La persistencia debe conservar los datos tras reiniciar la aplicación.

## 3. Criterio para uso durante el desarrollo

Este documento registra el estado de aprobación y las condiciones recuperadas. Para pruebas de aceptación que requieran trazabilidad literal, se debe cotejar el catálogo CA original. Los casos de prueba propuestos durante las auditorías no se incorporan automáticamente como criterios aprobados de SPEC-005.
