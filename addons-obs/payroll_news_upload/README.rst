.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Employee Contract News
======================

Este modulo implementa novedades en los contratos de empleados en orden de producir las nominas.

Las novedades de los contratos de empleados pueden ser calculadas automaticamente en un punto especifico dentro de una
estructura salarial.
Tambien pueden ser calculadas utilizando el boton en el formulario de la nomina, dentro de la pestana 'Novedades'

Además, se pueden añadir manualmente en una nomina en especifico.

Si una novedad tiene 2 o mas lineas en el mismo periodo de nomina,
estas se se ponderaran por la fraccion de la nomina para las que aplican.


Configuracion
=============


Agregando novedades al contrato de empleado
-------------------------------------------
Vaya a Recursos Humanos --> Configuracion -- Contratos --> Conceptos de Novedades de Contratos.
Cree sus propias novedades.
Seleccione las reglas salariales sobre las que se calculara la novedad.

En el contrato de un empleado, añada las novedades correspondientes.
Seleccione la novedad, el monto, periodo de aplicacioon, frecuencia, etc..


Configurando la estructura salarial
-----------------------------------
En una regla de salario de la estructura de su nómina, puede llamar

payslip.compute_news()

Esto permite calcular las novedades de los empleados en un punto específico en la
estructura de la nómina.

Dentro de una regla salarial, es posible sumar las novedades desde una lista de codigos:

 - Ej:
    result = rule.sum_news(payslip, codes=['A1', 'B2'])

El parametro codes es la lista de las novedades a incluir.


Para sumar la novedad relacionada a la regla salarial actual utilice:

 - Ej:
    result = rule.sum_news(payslip)

Credits
=======

Contributors
------------
* Jose Ernesto Mendez Diaz