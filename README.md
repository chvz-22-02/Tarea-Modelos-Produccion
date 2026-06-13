# RAG Compliance API

Tarea Modelos en Producción: Solución para consultar esquemas de base de datos mediante RAG y generar instrucciones SQL con Gemini.

## 1. Qué hace este proyecto

Este servicio expone una API REST que:

- recibe una pregunta en lenguaje natural,
- recupera información relevante desde una colección ChromaDB,
- genera una respuesta útil (SQL/DDL contextualizado) con Gemini
- y puede ejecutarse en contenedor Docker.

---

## 2. Objetivo del proyecto

Construir una pequeña aplicación de IA/ML empaquetada en Docker, que:

1. reciba una pregunta o instrucción,
2. procese la consulta con un modelo de IA,
3. devuelva una respuesta útil,
4. se pueda levantar con un solo comando.

---

## 3. Arquitectura

- FastAPI: API REST principal.
- Gemini (Google AI): generación de respuestas y embeddings.
- ChromaDB: almacenamiento de documentos y recuperación semántica.
- Docker / Docker Compose: ejecución en contenedor.

### Endpoints principales

- GET /
  - Health check
- POST /ingest
  - Indexa documentos JSON con definiciones DDL
- POST /query/json
  - Consulta en JSON puro

La documentación interactiva de la API queda disponible en:

- http://localhost:8000/docs

---

## 4. Requisitos

- Docker Desktop o Docker Engine
- Python 3.11+
- Variable de entorno GOOGLE_API_KEY
- Dependencias del proyecto definidas en pyproject.toml

> Importante: la API key de Gemini NO debe incluirse en la imagen. Se debe inyectar en runtime con -e GOOGLE_API_KEY=...

---

## 5. Ejecutar con Docker

### Opción A: con Docker Compose

Desde la carpeta rag-api:

1. Exportar la clave de Gemini en el shell:

   set GOOGLE_API_KEY=tu_api_key_aqui

2. Levantar el stack:

   docker compose up --build

3. La API estará disponible en:

   http://localhost:8000

4. ChromaDB quedará disponible en:

   http://localhost:8001

Para detenerlo:

   docker compose down

### Opción B: con docker run (ejecución del notebook notebook_demostracion.ipynb)

Construir la imagen:

   docker build -t rag-compliance-api .

Correr la imagen:

   docker run --rm -p 8000:8000 -e GOOGLE_API_KEY=tu_api_key_aqui rag-compliance-api


---

## 6. Ejemplo de uso

### Ejemplo 1: consulta JSON

curl -X POST http://localhost:8000/query/json \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué productos hay disponibles?"}'

### Ejemplo de entrada → salida

Entrada:

  "¿Qué productos hay disponibles?"

Salida esperada:

  una respuesta generada por Gemini basada en el esquema DDL disponible, normalmente en formato SQL.

---

## 7. Datos de ejemplo

El proyecto incluye un archivo de ejemplo en:

- rag-api/data/ddl.json

Ese archivo contiene tres registros de ejemplo con:

- id: identificador interno de la tabla,
- nombre: nombre de la tabla,
- descripcion: explicación del propósito del conjunto de datos,
- ddl: esquema SQL completo de la tabla.

Ejemplo de estructura del JSON:

```json
[
  {
    "id": "tabla_1",
    "nombre": "productos",
    "descripcion": "Catálogo de productos disponibles en una tienda en línea. ...",
    "ddl": "CREATE TABLE productos (\n    id_producto SERIAL PRIMARY KEY,\n    nombre VARCHAR(150) NOT NULL,\n    categoria VARCHAR(80),\n    precio NUMERIC(10,2) NOT NULL,\n    stock INT DEFAULT 0,\n    creado_en TIMESTAMP DEFAULT NOW()\n);"
  }
]
```

Descripción de las tablas de ejemplo:

1. productos
   - Describe el catálogo de productos y su disponibilidad.
   - Esquema SQL:
     ```sql
     CREATE TABLE productos (
         id_producto SERIAL PRIMARY KEY,
         nombre VARCHAR(150) NOT NULL,
         categoria VARCHAR(80),
         precio NUMERIC(10,2) NOT NULL,
         stock INT DEFAULT 0,
         creado_en TIMESTAMP DEFAULT NOW()
     );
     ```

2. empleados
   - Describe el personal de la empresa y su información laboral.
   - Esquema SQL:
     ```sql
     CREATE TABLE empleados (
         id_empleado SERIAL PRIMARY KEY,
         nombre VARCHAR(100) NOT NULL,
         apellido VARCHAR(100) NOT NULL,
         departamento VARCHAR(80),
         cargo VARCHAR(80),
         salario NUMERIC(12,2),
         fecha_ingreso DATE
     );
     ```

3. reservas
   - Describe reservas de habitaciones en un hotel.
   - Esquema SQL:
     ```sql
     CREATE TABLE reservas (
         id_reserva SERIAL PRIMARY KEY,
         nombre_huesped VARCHAR(150) NOT NULL,
         fecha_entrada DATE NOT NULL,
         fecha_salida DATE NOT NULL,
         tipo_habitacion VARCHAR(60),
         estado VARCHAR(20) DEFAULT 'pendiente',
         creado_en TIMESTAMP DEFAULT NOW()
     );
     ```

Este archivo se usa para cargar definiciones de tablas y enriquecer la consulta con contexto de negocio.

---

## 8. Notas importantes para evaluación

- La imagen se levanta con un comando simple.
- La API key se pasa con -e GOOGLE_API_KEY=... en runtime.
- La documentación interactiva está disponible en /docs.
- El servicio está preparado para ser desplegado como API tipo clase y probado en contenedor.

---

## 9. Resumen rápido

Si quieres probarla rápidamente:

1. docker compose up --build
2. abre http://localhost:8000/docs
3. prueba un endpoint como /query/json

Esta documentación sigue la lógica del PDF para un proyecto de tipo API como la de clase: funcional, simple, ejecutable en Docker y con ejemplo de uso.
