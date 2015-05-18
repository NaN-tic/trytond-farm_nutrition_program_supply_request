#:after:stock_supply_request/supply_request:section:crear_solicitud#

Rellenar una las solicitudes de abastecimiento de forma automática
------------------------------------------------------------------

La cantidad de producto a solicitar se puede introducir de forma
**automática** si estamos trabajando con programas de alimentación. Para
que el  sistema nos calcule automáticamente la cantidad de producto a pedir.
Para ello debemos indicar en |days| el número de días para los que  queremos
pedir producto y accionamos el botón *Rellenar solicitud*.

Este proceso nos rellenará de forma automática todas las líneas con los
productos, cantidades y las ubicaciones destino.

El método de cálculo se basa en los siguientes parámetros:

 * Número total de animales en las diferentes ubicaciones del almacén destino
 * El stock de producto en el almacén destino para cada una de las ubicaciones
 * El programa de alimentación asociado a cada especie (Ver programas de
   alimentación)

El sistema calcula el producto necesario de cada tipo, restando el
existente  en el almacén destino y creará las líneas necesarias en la
solicitud.

Para calcular la cantidad de producto suministrado a los animales se usará
tanto eventos de pienso como líneas de inventario provisional. De esta forma
tiene en cuenta la información más nueva posible aunque sea un poco menos
exacta.

.. |days| field:: stock.supply_request/days
