# Software FJ - Sistema de Clientes, Servicios y Reservas

## Fase 4 - Componente Práctico

Curso: Programación  
Código: 213023  
Universidad Nacional Abierta y a Distancia - UNAD  

## Descripción general

Este proyecto presenta una aplicación desarrollada en Python para gestionar clientes, servicios y reservas de la empresa Software FJ. La solución fue construida aplicando programación orientada a objetos y manejo avanzado de excepciones.

El programa no utiliza bases de datos. Toda la información se administra mediante objetos y listas internas durante la ejecución. Además, los eventos importantes y los errores controlados se registran en el archivo `eventos.log`.

## Objetivo del sistema

Implementar un sistema funcional que permita registrar clientes, crear servicios, generar reservas, confirmar operaciones, realizar cobros y controlar errores sin detener la ejecución del programa.

## Conceptos aplicados

- Programación orientada a objetos.
- Clases abstractas.
- Herencia.
- Polimorfismo.
- Encapsulamiento.
- Métodos sobrescritos.
- Métodos con parámetros opcionales.
- Excepciones personalizadas.
- Bloques `try/except`.
- Bloques `try/except/else/finally`.
- Encadenamiento de excepciones.
- Registro de eventos mediante `logging`.
- Uso de listas internas.
- Uso de `Enum` para estados de reserva.
- Uso de `dataclass` para organizar pruebas.

## Estructura del proyecto

```text
fase4_programacion/
│
├── main.py
├── eventos.log
└── README.md