Proyecto: Tecnología de Cadenas de Bloques (Blockchain)   

Este repositorio contiene un resumen estructurado sobre la tecnología de cadenas de bloques, conocida como Blockchain, basado en el informe académico de la Universidad Autónoma del Beni “José Ballivián”.  
Descripción General

La tecnología Blockchain es un sistema de almacenamiento y gestión de información diseñado para registrar datos de manera distribuida, verificable e inmutable. Su propósito fundamental es permitir que múltiples participantes compartan una base de datos común sin necesidad de depender de una autoridad central que valide o controle la información. Formalmente, actúa como un libro mayor descentralizado donde los registros se agrupan en bloques enlazados criptográficamente.  
Componentes Fundamentales

La arquitectura del sistema se sostiene sobre cuatro pilares básicos:

    Bloques: Constituyen la unidad básica de almacenamiento e incluyen un identificador, marca temporal (timestamp), lista de transacciones, y los hashes tanto del bloque actual como del anterior.  

    Transacciones: Son las operaciones pendientes de validación que modifican el estado lógico del sistema, tales como transferencias de activos o ejecución de contratos inteligentes.  

    Hash Criptográfico: Es el resultado de aplicar una función matemática que transforma datos de entrada en una salida de longitud fija, lo que es vital para verificar la integridad de la información.  

    Nodos: Son los equipos participantes de la red encargados de almacenar la cadena, validar transacciones, propagar información y ejecutar algoritmos de consenso.  

Funcionamiento y Consenso

El flujo de información en Blockchain sigue un ciclo altamente estructurado:

    Creación y Difusión: Se genera una transacción y se transmite a la red, alojándose temporalmente en la mempool tras validar su firma criptográfica y formato.  

    Construcción del Bloque: Las transacciones se seleccionan y se agrupan en un bloque candidato.  

    Proceso de Consenso: La red determina qué bloque será aceptado para asegurar un historial coherente, utilizando mecanismos como:

        Proof of Work (PoW): Requiere resolver un problema computacional iterando un valor nonce hasta que el hash cumpla con un objetivo específico.  

        Proof of Stake (PoS): Selecciona validadores con base en la cantidad de activos bloqueados como garantía (stake), sin competencia computacional.  

    Validación y Replicación: Una vez que el bloque es validado colectivamente, se incorpora a la cadena dependiendo criptográficamente del anterior, y los nodos actualizan su copia local mediante sincronización continua.  

Características, Ventajas y Limitaciones
Características Principales

    Descentralización: No hay una autoridad única; la validación y el almacenamiento se distribuyen entre múltiples nodos.  

    Inmutabilidad y Seguridad: Los registros confirmados no pueden ser alterados sin invalidar toda la cadena, lo cual está respaldado por firmas digitales y funciones hash.  

    Transparencia y Trazabilidad: Las transacciones pueden ser consultadas por cualquier participante, manteniendo un seguimiento cronológico.  

Ventajas vs Limitaciones

    Ventajas: Eliminación de intermediarios, alta resistencia a la manipulación de datos, auditoría completa del historial y disponibilidad continua.  

    Limitaciones: Consumo energético considerable en modelos como PoW, capacidad de procesamiento inferior a bases de datos centralizadas, altas necesidades de almacenamiento y dificultad para corregir errores debido a su inmutabilidad.  

Aplicación Práctica: CAPICOIN

El informe expone una simulación de red P2P activa denominada CAPICOIN, donde es posible interactuar localmente con la cadena. Esta interfaz gráfica permite a los usuarios:  

    Generar transacciones aleatorias entre identidades.  

    Minar bloques mediante la búsqueda del nonce adecuado.  

    Validar el estado y la integridad de la cadena de bloques.  

    Realizar simulaciones de hackeo o borrar bloques para visualizar cómo se rompe la continuidad criptográfica de la red.  

Información Institucional

    Institución: Universidad Autónoma del Beni “José Ballivián”, Facultad de Ingeniería y Tecnología.  

    Materia: Tecnologías Emergentes.  

    Docente: Ing. Hermes Rodríguez Rivero.  

    Autores: Luis Andres Mariscal Farell, Guido Diogo Alaiza Gomez, Humberto Orellano Justiniano.  

    Lugar y Fecha: Beni - Bolivia, 16 de junio de 2026.
