# Phase 1 Summary — Data Ingestion Layer

## Objective

Build the ingestion layer of the AI Observability Platform by automatically loading the OpenAssistant dataset from a local Parquet file into Snowflake using Apache Airflow.

---

# Architecture Implemented

```text
OpenAssistant Parquet File
        ↓
Apache Airflow DAG
        ↓
Snowflake Internal Stage
        ↓
Snowflake RAW Layer
        ↓
RAW_MESSAGES Table
```

---

# Technologies Used

* Snowflake
* Apache Airflow
* Astro CLI
* GitHub Codespaces
* Snowflake Connector for Python

---

# Snowflake Objects Created

## Database

```sql
AI_OBSERVABILITY_DB
```

Purpose:

* Main project database.
* Contains all future schemas and analytical assets.

---

## Schema

```sql
RAW
```

Purpose:

* Stores raw ingested data exactly as received.
* No transformations applied.

---

## File Format

```sql
PARQUET_FORMAT
```

Purpose:

* Tells Snowflake how to interpret Parquet files.

---

## Stage

```sql
OPENASSISTANT_STAGE
```

Purpose:

* Temporary storage location for files before loading into tables.

---

## Raw Table

```sql
RAW_MESSAGES
```

Schema:

```sql
CREATE OR REPLACE TABLE RAW_MESSAGES (
    raw_data VARIANT
);
```

Purpose:

* Stores complete Parquet records as semi-structured objects.
* Preserves original source data.
* Prevents schema mismatch issues during ingestion.

---

# Airflow Setup Completed

## Astro CLI

Installed successfully inside GitHub Codespaces.

Commands used:

```bash
astro dev init
astro dev start
astro dev restart
```

---

## Airflow Project Structure

```text
project/
│
├── dags/
├── include/
├── plugins/
├── requirements.txt
└── Dockerfile
```

---

## Dataset Placement

Dataset stored in:

```text
include/train.parquet
```

---

## Snowflake Connection Created

Airflow Connection ID:

```text
snowflake_conn
```

Connection stores:

* Account
* Username
* Password
* Warehouse
* Database
* Schema
* Role

---

# DAG Implemented

DAG Responsibilities:

## Step 1

Upload Parquet file to Snowflake Stage

```sql
PUT file://...
```

Result:

```text
train.parquet
        ↓
OPENASSISTANT_STAGE
```

---

## Step 2

Load data from Stage into RAW table

```sql
COPY INTO RAW_MESSAGES
```

Result:

```text
OPENASSISTANT_STAGE
        ↓
RAW_MESSAGES
```

---

# Data Flow Achieved

```text
Local Parquet File
        ↓
GitHub Codespaces
        ↓
Airflow DAG
        ↓
Snowflake Stage
        ↓
RAW_MESSAGES
```

---

# Why VARIANT Was Used

Instead of immediately creating relational columns:

```sql
message_id
parent_id
lang
text
...
```

we used:

```sql
raw_data VARIANT
```

because:

* Raw schema was unknown initially.
* Prevents ingestion failures.
* Stores complete records safely.
* Supports semi-structured data.
* Matches Data Lake / Medallion architecture patterns.

---

# Phase 1 Deliverables Completed

✅ Snowflake account setup

✅ Database creation

✅ RAW schema creation

✅ Parquet file format creation

✅ Internal stage creation

✅ Airflow environment setup

✅ Snowflake connection setup

✅ DAG creation

✅ Automated file upload

✅ Automated COPY INTO execution

✅ Successful ingestion into RAW_MESSAGES

✅ Verification through Snowflake queries

---

# Phase 2 Objective

Transform raw semi-structured records into analytical tables.

---

# Phase 2 Planned Architecture

```text
RAW_MESSAGES
        ↓
Data Transformation
        ↓
FACT_MESSAGES
        ↓
FACT_CONVERSATIONS
        ↓
DIM_USERS
```

---

# Phase 2 Tasks

## 1. Explore Raw Schema

Inspect:

```sql
SELECT raw_data
FROM RAW_MESSAGES
LIMIT 10;
```

Identify:

* message_id
* parent_id
* user_id
* text
* role
* language
* review information
* timestamps

---

## 2. Create Structured Tables

### FACT_MESSAGES

One row per message.

Potential columns:

```text
message_id
parent_id
user_id
text
role
language
created_date
```

---

### FACT_CONVERSATIONS

Conversation-level metrics.

Potential columns:

```text
conversation_id
conversation_length
conversation_depth
```

---

### DIM_USERS

User dimension table.

Potential columns:

```text
user_id
message_count
language_usage
```

---

## 3. Data Cleaning

Handle:

* Nulls
* Duplicate message IDs
* Deleted messages
* Invalid relationships

---

## 4. Conversation Modeling

Using:

```text
message_id
parent_id
```

Build conversation chains.

Example:

```text
A
└── B
    └── C
```

Calculate:

* Conversation depth
* Conversation length

---

## 5. Feature Engineering

Generate:

### Quality Metrics

* Average quality
* Average helpfulness
* Average creativity

### Governance Metrics

* Toxicity rate
* PII rate
* Hate speech rate
* Violence rate

### Language Metrics

* Failure rate by language
* Quality by language
* Helpfulness by language

### Cost Metrics

* Estimated token count
* Estimated API cost

---

# End Goal of Phase 2

Create clean structured tables that become the foundation for Cortex AI enrichment and dashboard development.
