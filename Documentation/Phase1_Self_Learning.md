# Phase 1 Self Learning Notes

## New Technologies Introduced

* Snowflake
* Apache Airflow
* Astro CLI
* GitHub Codespaces
* Snowflake Connector

---

# Concepts Learned

## Snowflake

### Database

Acts as the top-level container for the project.

Example:

```text
AI_OBSERVABILITY_DB
```

---

### Schema

Logical grouping inside a database.

Example:

```text
RAW
```

Used to organize project layers.

---

### Table

Stores rows and columns.

Example:

```text
RAW_MESSAGES
```

---

### VARIANT Data Type

Special Snowflake datatype for:

* JSON
* Parquet
* Nested objects
* Semi-structured data

Used for raw ingestion.

---

### File Format

Defines how Snowflake reads files.

Example:

```text
PARQUET_FORMAT
```

---

### Stage

Temporary storage location inside Snowflake.

Purpose:

```text
File
 ↓
Stage
 ↓
Table
```

Used before loading data into tables.

---

### Warehouse

Compute engine.

Used to execute:

```sql
SELECT
COPY
INSERT
UPDATE
```

Storage and compute are separated in Snowflake.

---

# Airflow Concepts Learned

## DAG

Directed Acyclic Graph.

Represents a workflow.

Example:

```text
Upload File
     ↓
Load Table
```

---

## Task

Single unit of work inside a DAG.

Example:

* Upload file
* Execute SQL
* Send email

---

## Airflow Connection

Stores credentials.

Used so passwords are not hardcoded.

Example:

```text
snowflake_conn
```

---

## Astro CLI

Used to create and run Airflow locally.

Commands learned:

```bash
astro dev init
astro dev start
astro dev restart
```

---

## GitHub Codespaces

Cloud development environment.

Used instead of installing everything locally.

---

# Architectural Understanding Gained

Understanding of:

```text
Local File
     ↓
Airflow
     ↓
Snowflake Stage
     ↓
Snowflake Table
```

---

Understanding of:

```text
Raw Layer
     ↓
Transform Layer
     ↓
Analytics Layer
```

---

Understanding of:

```text
Storage Layer = Snowflake
Orchestration Layer = Airflow
```

---

# Learning Questions Asked During Phase 1

## About Project Architecture

* Can Airflow be used instead of manually uploading files?
* Where does Airflow fit in the architecture?
* Should ingestion be performed through Snowflake UI or Airflow?

---

## About Airflow

* Can Airflow code be written inside Snowflake?
* Should Airflow be developed locally or in GitHub Codespaces?
* How does Airflow access files stored on my machine?
* How does Airflow load a Parquet file into Snowflake?

---

## About Snowflake

* What is a Stage?
* Why is a Stage required?
* How is a Stage different from a Table?
* What is the role of File Formats?
* How is Snowflake structured internally?

---

## About Data Modeling

* Why create:

```sql
raw_data VARIANT
```

instead of creating relational columns immediately?

* Why was the COPY INTO logic changed?

* What happens internally when loading Parquet into a VARIANT column?

---

# Key Mental Models Learned

## Snowflake

```text
Database
   ↓
Schema
   ↓
Table / Stage / Views
```

---

## Ingestion Flow

```text
Parquet File
     ↓
Stage
     ↓
Table
```

---

## Project Flow

```text
Dataset
     ↓
Airflow
     ↓
Snowflake RAW Layer
     ↓
Transformations
     ↓
Analytics
     ↓
Dashboard
```

---

# Current Confidence Level

Comfortable With:

✅ Snowflake setup

✅ Creating databases and schemas

✅ Creating stages

✅ Creating file formats

✅ Understanding VARIANT

✅ Airflow project setup

✅ Astro CLI basics

✅ Airflow connections

✅ Building and running a DAG

✅ Automated ingestion into Snowflake

Need More Practice With:

🔶 Snowflake SQL transformations

🔶 Conversation hierarchy modeling

🔶 Fact and dimension table design

🔶 Snowflake Cortex AI

🔶 Streamlit dashboards

🔶 Production-grade Airflow patterns

These will be the primary focus areas for Phase 2 and beyond.
