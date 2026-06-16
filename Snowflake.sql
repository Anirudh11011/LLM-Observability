-- Created Database
CREATE DATABASE AI_OBSERVABILITY_DB;
USE DATABASE AI_OBSERVABILITY_DB;


-- Created new schema called RAW inside the databse
CREATE SCHEMA RAW;



-- Created file format for the RAW schema
CREATE OR REPLACE FILE FORMAT PARQUET_FORMAT
TYPE = PARQUET;

-- Created stage for the RAW schema
CREATE OR REPLACE STAGE OPENASSISTANT_STAGE
FILE_FORMAT = PARQUET_FORMAT;



-- Created a new table called RAW_MESSAGES inside RAW schema
CREATE OR REPLACE TABLE RAW_MESSAGES (AI_OBSERVABILITY_DB.RAW.RAW_MESSAGES
    raw_data VARIANT
);

-- Data Analysis of RAW_MESSAGES table
SELECT COUNT(*)
FROM RAW.RAW_MESSAGES;

SELECT *
FROM RAW.RAW_MESSAGES
LIMIT 10;

SELECT raw_data
FROM RAW_MESSAGES
LIMIT 5;



-- Created new schema called TRANSFORM
CREATE SCHEMA IF NOT EXISTS AI_OBSERVABILITY_DB.TRANSFORM;

-- Created new table called FACT_MESSAGES inside TRANSFORM Schema
CREATE OR REPLACE TABLE AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES AS
SELECT
    raw_data:message_id::STRING AS message_id,
    raw_data:parent_id::STRING AS parent_id,
    raw_data:text::STRING AS text,
    CEIL(LENGTH(raw_data:text::STRING) / 4) AS token_usage,
    raw_data:role::STRING AS role,
    raw_data:lang::STRING AS lang
FROM AI_OBSERVABILITY_DB.RAW.RAW_MESSAGES
WHERE raw_data:message_id IS NOT NULL
  AND raw_data:text IS NOT NULL;

-- Created new table called FACT_MESSAGE_LABELS inside TRANSFORM Schema
CREATE OR REPLACE TABLE AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGE_LABELS AS
SELECT
    raw_data:message_id::STRING AS message_id,

    raw_data:labels:value[ARRAY_POSITION('spam'::VARIANT, raw_data:labels:name)]::FLOAT AS spam,
    raw_data:labels:value[ARRAY_POSITION('lang_mismatch'::VARIANT, raw_data:labels:name)]::FLOAT AS lang_mismatch,
    raw_data:labels:value[ARRAY_POSITION('pii'::VARIANT, raw_data:labels:name)]::FLOAT AS pii,
    raw_data:labels:value[ARRAY_POSITION('not_appropriate'::VARIANT, raw_data:labels:name)]::FLOAT AS not_appropriate,
    raw_data:labels:value[ARRAY_POSITION('hate_speech'::VARIANT, raw_data:labels:name)]::FLOAT AS hate_speech,
    raw_data:labels:value[ARRAY_POSITION('sexual_content'::VARIANT, raw_data:labels:name)]::FLOAT AS sexual_content,
    raw_data:labels:value[ARRAY_POSITION('quality'::VARIANT, raw_data:labels:name)]::FLOAT AS quality,
    raw_data:labels:value[ARRAY_POSITION('toxicity'::VARIANT, raw_data:labels:name)]::FLOAT AS toxicity,
    raw_data:labels:value[ARRAY_POSITION('humor'::VARIANT, raw_data:labels:name)]::FLOAT AS humor,
    raw_data:labels:value[ARRAY_POSITION('creativity'::VARIANT, raw_data:labels:name)]::FLOAT AS creativity,
    raw_data:labels:value[ARRAY_POSITION('violence'::VARIANT, raw_data:labels:name)]::FLOAT AS violence

FROM AI_OBSERVABILITY_DB.RAW.RAW_MESSAGES
WHERE raw_data:message_id IS NOT NULL;




-- Data Analysis of the two tables inside TRANSFORM Schema
SELECT COUNT(*) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES;
SELECT COUNT(*) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGE_LABELS;

SELECT COUNT(DISTINCT LANG) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES;

SELECT DISTINCT ROLE FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES;

SELECT AVG(TOKEN_USAGE) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES;

SELECT HATE_SPEECH FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGE_LABELS
WHERE MESSAGE_ID='4313860a-cd2c-4b45-ab6d-737b1bec463a';



-- Created new table in TRANSFORM schema called FACT_Conversations
-- The main purpose of this table is to calculate the conversation tree 
-- Used Common Table Expression (CTE) for quering table
CREATE OR REPLACE TABLE AI_OBSERVABILITY_DB.TRANSFORM.FACT_CONVERSATIONS AS
WITH RECURSIVE message_tree AS (
    -- Base case: root messages (no parent)
    SELECT
        MESSAGE_ID,
        PARENT_ID,
        MESSAGE_ID AS CONVERSATION_ID,
        1 AS DEPTH
    FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES
    WHERE PARENT_ID IS NULL

    UNION ALL

    -- Recursive case: child messages
    SELECT
        m.MESSAGE_ID,
        m.PARENT_ID,
        t.CONVERSATION_ID,
        t.DEPTH + 1 AS DEPTH
    FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES m
    JOIN message_tree t ON m.PARENT_ID = t.MESSAGE_ID
)
SELECT
    CONVERSATION_ID,
    COUNT(*) AS CONVERSATION_LENGTH,
    MAX(DEPTH) AS CONVERSATION_DEPTH
FROM message_tree
GROUP BY CONVERSATION_ID;

-- Testing and analysis of new table created 
SELECT COUNT(CONVERSATION_ID) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_CONVERSATIONS;

SELECT COUNT(MESSAGE_ID) FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES
WHERE PARENT_ID IS NULL;
