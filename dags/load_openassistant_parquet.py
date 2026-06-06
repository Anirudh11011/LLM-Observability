from datetime import datetime

from airflow.decorators import dag
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.python import PythonOperator


SNOWFLAKE_CONN_ID = "snowflake_connection"

LOCAL_PARQUET_FILE = "/usr/local/airflow/include/train.parquet"

STAGE_NAME = "OPENASSISTANT_STAGE"
TARGET_TABLE = "RAW_MESSAGES"


def upload_parquet_to_stage():
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            PUT file://{LOCAL_PARQUET_FILE}
            @{STAGE_NAME}
            AUTO_COMPRESS = FALSE
            OVERWRITE = TRUE;
        """)
    finally:
        cursor.close()
        conn.close()


def load_parquet_into_raw_table():
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            COPY INTO {TARGET_TABLE}
            FROM (
                SELECT $1
                FROM @{STAGE_NAME}/train.parquet
            )
            FILE_FORMAT = (TYPE = PARQUET);
        """)
    finally:
        cursor.close()
        conn.close()


@dag(
    dag_id="load_openassistant_parquet",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["snowflake", "openassistant", "phase_1"],
)
def load_openassistant_parquet():

    upload_task = PythonOperator(
        task_id="upload_parquet_to_snowflake_stage",
        python_callable=upload_parquet_to_stage,
    )

    copy_task = PythonOperator(
        task_id="copy_parquet_into_raw_messages",
        python_callable=load_parquet_into_raw_table,
    )

    upload_task >> copy_task


load_openassistant_parquet()