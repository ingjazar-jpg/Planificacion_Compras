# SPEC-002 — Reglas de negocio

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Planificación y Presupuesto de Compras para Navidad y Fin de Año |
| Identificador | SPEC-002 |
| Versión | 0.3 |
| Estado | Aprobada |
| Enmienda incorporada | EN-001 / RN-063 |
| Fecha de aprobación de EN-001 | 12-11-2026 |

> Este documento consolida las reglas de negocio confirmadas en el historial. RN-063 se reproduce como regla aprobada mediante EN-001. Los identificadores RB-01 a RB-11 utilizados en la matriz de trazabilidad son referencias temporales y no sustituyen los identificadores oficiales del documento original.

## 1. Gestión de años

- Cada año tiene un presupuesto general y dos presupuestos individuales: Navidad y Fin de Año.
- Los datos de cada año son independientes.
- Los años anteriores al año calendario actual son históricos y solo permiten consulta.
- No se permite crear años anteriores al año calendario actual.
- Se permite crear años futuros.
- Los años no se eliminan.
- La comparación con el año actual debe ser dinámica; no codificar un año fijo.

## 2. Presupuestos

- El presupuesto general y los presupuestos individuales se controlan independientemente.
- Un presupuesto con valor cero se normaliza como no configurado (`null`).
- Cuando no existe presupuesto configurado, la interfaz muestra «Sin presupuesto configurado».
- Un presupuesto no configurado no se interpreta como presupuesto cero.
- No se calculan porcentajes de ejecución ni se generan alertas de ejecución cuando el presupuesto correspondiente no está configurado.
- Los presupuestos no pueden ser negativos.

## 3. Productos y precios

- La cantidad debe ser mayor que cero; se permiten cantidades decimales.
- El precio estimado no puede ser negativo.
- El precio real puede ser cero o superior.
- Un producto pendiente tiene precio real `null`.
- Para marcar un producto como comprado se requiere precio real registrado, incluso si es cero.
- El gasto real se calcula exclusivamente con productos comprados y sus precios reales.
- Los productos pendientes pueden participar en proyecciones estimadas, pero no se incluyen en el gasto real.
- Los cálculos financieros deben utilizar Decimal en backend; no utilizar `float` para operaciones monetarias.

## 4. Estado y edición de productos

- Los productos pueden estar Pendientes o Comprados.
- Un producto comprado no puede volver a Pendiente.
- Un producto comprado no puede eliminarse.
- Un producto comprado puede corregirse en sus campos de negocio editables, excepto ID, celebración y estado.
- Las correcciones deben conservar la identidad, asociación y estado del producto.
- Las correcciones deben reflejarse en los cálculos y estadísticas dependientes.

## 5. Cálculos y alertas

- El total real de cada celebración suma exclusivamente productos comprados, usando el precio real registrado.
- El saldo se calcula a partir del gasto real, no del gasto estimado.
- Los presupuestos general e individuales se controlan de forma independiente.
- Se genera alerta únicamente cuando `gasto_real > presupuesto`.
- Si el gasto es igual al presupuesto, no se genera alerta.
- Las alertas general, Navidad y Fin de Año son independientes y pueden coexistir.
- Una alerta desaparece cuando deja de cumplirse su condición.
- El avance de compra se calcula como productos comprados / total de productos registrados × 100.
- Si no hay productos, el avance es cero.
- Las métricas derivadas se calculan dinámicamente y no se almacenan como datos persistidos.

## 6. RN-063 — Corrección de productos comprados

> Un producto que haya sido marcado como comprado conservará permanentemente su estado Comprado y no podrá volver al estado Pendiente ni eliminarse.
>
> El sistema permitirá corregir todos los campos de negocio editables del producto comprado, de acuerdo con el contrato API vigente, excepto los siguientes:
> - Identificador del producto (`id`).
> - Celebración a la que pertenece.
> - Estado del producto.
>
> Toda corrección deberá conservar la condición de producto comprado, sin alterar su identidad ni su asociación con la celebración original.
>
> Las correcciones deberán reflejarse en los cálculos, resúmenes, saldos, indicadores y estadísticas que dependan de los datos actualizados.

## 7. Nota de integridad documental

El texto íntegro original de SPEC-002 v0.2 no está disponible en el contexto recuperado. Este archivo consolida las decisiones confirmadas y la enmienda RN-063 aprobada para v0.3. No se inventan identificadores adicionales de reglas ni se afirma que esta reconstrucción sea una transcripción literal del documento original.
