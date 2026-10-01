# Business Growth Analysis

## Sobre el proyecto

Este proyecto analiza el desempeño de un **e-commerce de food & groceries** con el objetivo de entender el comportamiento de los clientes, el ciclo de vida, la frecuencia de compra, la retencion y las oportunidades de crecimiento.

El análisis combina **Python y Power BI** para transformar datos de negocio en información útil para la toma de decisiones y el desarrollo de estrategias de crecimiento y CRM.

## Preguntas de análisis

* ¿Cómo evolucionan los pedidos y la facturacion a lo largo del tiempo?
* ¿Cuantos clientes y pedidos genera el negocio?
* ¿Como se distribuyen los clientes segun su frecuencia de compra?
* ¿Que porcentaje de clientes realiza una segunda compra?
* ¿Cuanto tiempo pasa entre la primera y la segunda compra?
* ¿Como se comporta la retencion a 7, 14, 30 y 60 dias?
* ¿Cuanto tiempo tarda un usuario registrado en realizar su primera compra?
* ¿Como se distribuye el ciclo de vida de los clientes?
* ¿Como varian el comportamiento y la retencion segun el canal de primera compra?
* ¿Que segmentos de clientes generan mayor facturacion?
* ¿Que oportunidades existen para mejorar la activacion, la recompra y la frecuencia de compra?

## Principales resultados

* Se analizaron **310.153 pedidos** y **26.597 clientes unicos**.
* La facturacion total analizada fue de aproximadamente **11,16 millones**.
* El valor promedio por pedido fue de aproximadamente **35,97**.
* El **50,3%** de los usuarios registrados en la base de signups realizó al menos una compra.
* El tiempo promedio desde el registro hasta la primera compra fue de aproximadamente **11,5 dias**.
* El **41,6%** de los clientes realizó solamente una compra, mientras que el **58,4%** realizó dos o mas compras.
* Los clientes con **6 o mas compras** representan aproximadamente el **31,2%** de los clientes analizados.
* Se analizaron ventanas de retencion de **7, 14, 30 y 60 dias** para estudiar la transicion hacia una segunda compra.
* El canal **Market** concentra la mayor parte de la facturacion analizada, mientras que **Eats** presenta un valor promedio por pedido menor.
* El analisis de ciclo de vida permite identificar oportunidades para mejorar la transicion entre la primera y segunda compra y aumentar la frecuencia de compra.

## Procesamiento de datos

Los datasets originales fueron limpiados y procesados utilizando **Python y Pandas**.

El procesamiento incluyo:

* Conversion de las columnas de fechas al formato datetime.
* Calculo de pedidos, clientes, facturacion y valor promedio por pedido.
* Agrupacion de pedidos a nivel cliente.
* Identificacion de la primera y ultima compra de cada cliente.
* Calculo de la frecuencia de compra y facturacion por cliente.
* Clasificacion de clientes segun su etapa del ciclo de vida.
* Calculo del tiempo entre compras.
* Analisis del tiempo hasta la segunda compra.
* Calculo de retencion temporal a 7, 14, 30 y 60 dias.
* Analisis de cohortes segun el mes de primera compra.
* Segmentacion de clientes segun frecuencia de compra.
* Analisis del comportamiento de los clientes segun su canal de primera compra.
* Preparacion de datasets derivados para su utilizacion en Power BI.

Los datos originales del negocio no se incluyen en el repositorio debido a cuestiones de privacidad y confidencialidad.

## Analisis de negocio

El proyecto incluye analisis para entender:

* Desempeño general del negocio.
* Evolucion de pedidos y facturacion.
* Comportamiento de los clientes.
* Frecuencia de compra.
* Activacion de usuarios.
* Transicion de primera a segunda compra.
* Retencion de clientes.
* Ciclo de vida.
* Analisis de cohortes.
* Segmentacion de clientes.
* Desempeño por canal.
* Oportunidades de crecimiento y CRM.

## Dashboard en Power BI

Se desarrollaron dashboards en **Power BI** para visualizar los principales indicadores del negocio y del ciclo de vida de los clientes.

Los dashboards incluyen:

* Evolucion de pedidos y facturacion.
* KPIs generales del negocio.
* Distribucion de clientes segun cantidad de compras.
* Activacion de usuarios.
* Tiempo hasta la primera compra.
* Retencion a diferentes ventanas temporales.
* Transiciones entre compras.
* Analisis del ciclo de vida.
* Segmentacion de clientes.
* Retencion segun canal.
* Frecuencia de compra.
* Indicadores de CRM y lifecycle.

## Estrategia de crecimiento

A partir de los resultados del analisis se identificaron oportunidades relacionadas con:

* Mejorar la activacion de nuevos usuarios.
* Reducir el tiempo hasta la primera compra.
* Aumentar la conversion de primera a segunda compra.
* Mejorar la retencion durante los primeros 30 dias.
* Incrementar la frecuencia de compra.
* Desarrollar estrategias diferenciadas segun el ciclo de vida del cliente.
* Utilizar CRM y comunicaciones personalizadas para acompañar las diferentes etapas del customer journey.

## Estructura del proyecto

### Seccion 1 - Business Analysis

* `business_insights`: principales hallazgos del analisis de negocio.
* `growth_dashboard`: dashboard de performance y growth.
* `growth_strategy`: estrategia y oportunidades de crecimiento.
* `seccion_1_business_analysis.py`: procesamiento y analisis de datos con Python.

### Seccion 2 - CRM & Lifecycle

* `crm_analysis`: analisis de CRM y comportamiento de clientes.
* `crm_insights`: principales hallazgos del analisis de lifecycle.
* `crm_lifecycle_dashboard`: dashboard de CRM, retencion y ciclo de vida.
* `lifecycle_strategy`: estrategia de CRM y lifecycle.

## Herramientas

* Python
* Pandas
* Power BI
* Git / GitHub
* Data analysis
* Customer segmentation
* CRM
* Lifecycle analysis
* Growth strategy
