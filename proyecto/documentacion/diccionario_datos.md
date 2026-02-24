# Diccionario de Datos - Terremotos USGS

Este documento describe las variables presentes en el dataset obtenido de la API de USGS.

| Variable | Tipo | Descripción |
| :--- | :--- | :--- |
| **time** | timestamp | Tiempo en que ocurrió el evento (UTC). |
| **latitude** | decimal | Latitud en grados decimales (-90 a 90). |
| **longitude** | decimal | Longitud en grados decimales (-180 a 180). |
| **depth** | decimal | Profundidad del evento en kilómetros. |
| **mag** | decimal | Magnitud del evento. |
| **magType** | string | Método o algoritmo usado para calcular la magnitud. |
| **nst** | integer | Número total de estaciones sísmicas usadas para determinar la ubicación. |
| **gap** | decimal | Brecha angular más grande entre estaciones adyacentes (en grados). |
| **dmin** | decimal | Distancia horizontal desde el epicentro hasta la estación más cercana (grados). |
| **rms** | decimal | Error cuadrático medio de los residuos del tiempo de viaje (segundos). |
| **net** | string | ID de la red que contribuyó con la información. |
| **id** | string | Identificador único del evento. |
| **updated** | timestamp | Última vez que se actualizó el evento. |
| **place** | string | Descripción textual de la región geográfica. |
| **type** | string | Tipo de evento sísmico (ej. 'earthquake'). |
| **horizontalError** | decimal | Incertidumbre de la ubicación reportada (km). |
| **depthError** | decimal | Incertidumbre de la profundidad reportada (km). |
| **magError** | decimal | Incertidumbre de la magnitud reportada. |
| **magNst** | integer | Número total de estaciones usadas para calcular la magnitud. |
| **status** | string | Indica si el evento ha sido revisado por un humano ('reviewed') o es automático. |
| **locationSource** | string | Red que reportó originalmente la ubicación. |
| **magSource** | string | Red que reportó originalmente la magnitud. |
