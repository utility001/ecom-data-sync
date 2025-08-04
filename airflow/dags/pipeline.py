# Import block
import awswrangler as wr
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator

from aws_utils import instantiate_boto3_session
from transaction_utils import generate_transaction_data

AWS_ACCESS_KEY = Variable.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = Variable.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = Variable.get("AWS_REGION")

AWS_BUCKET_NAME = Variable.get("AWS_BUCKET_NAME")
LAGOS_TIMEZONE = pendulum.timezone("Africa/Lagos")


def generate_and_upload(run_date, ti) -> str:
    """Generates syntetic transaction data and loads into s3
    Returns: s3 path where the transaction data was pushed to
    """
    df = generate_transaction_data(min_rows=500_000, max_rows=1_000_000)

    date_string = pendulum.parse(run_date).in_tz(LAGOS_TIMEZONE)
    s3_key = f"transactions/transaction-{date_string.to_date_string()}.parquet"
    s3_path = f"s3://{AWS_BUCKET_NAME}/{s3_key}"

    my_session = instantiate_boto3_session(
        access_key=AWS_ACCESS_KEY, secret_key=AWS_SECRET_KEY, region=AWS_REGION
    )
    print("Writing data so s3 bucket: ", s3_path)
    wr.s3.to_parquet(df=df, path=s3_path, boto3_session=my_session)
    print("Successfully written data to: ", s3_path)

    ti.xcom_push(key="s3_key", value=s3_key)


# Default arguments block
default_args = {
    "owner": "Data Engineering Team",
    "retries": 2,
    "retry_delay": pendulum.duration(minutes=5),
}

# Dag definition block
dag = DAG(
    dag_id="daily-ecomm-transactons-etl-v1",
    description=(
        "Generates synthetic transactions, Uploads to S3, "
        "loads into Redshift"
    ),
    schedule="@daily",
    start_date=pendulum.datetime(year=2025, month=8, day=1, tz=LAGOS_TIMEZONE),
    default_args=default_args,
    catchup=True,
)

task1 = PythonOperator(
    task_id="generate_and_upload_to_s3",
    python_callable=generate_and_upload,
    op_kwargs={"run_date": "{{ data_interval_start }}"},
    dag=dag,
)

task2 = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema="public",
    table="daily_transactions",
    s3_bucket=AWS_BUCKET_NAME,
    s3_key="{{ ti.xcom_pull(task_ids='generate_and_upload_to_s3', key='s3_key') }}",
    method="APPEND",
    redshift_conn_id="REDSHIFT_DEFAULT",  # Redshift conn-stores db credentials
    aws_conn_id="AWS_DEFAULT",  # AWS  connection - stores redshift role
    copy_options=["FORMAT AS PARQUET"],
    dag=dag,
)

task1 >> task2
