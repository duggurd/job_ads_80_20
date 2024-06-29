from airflow.decorators import dag, task
from datetime import datetime
from finn_ingestion_lib import get_ads_metadata, get_ads_content
# if os.environ.get("ENVIRONMENT") == "development":
#     from requests_cache import install_cache, NEVER_EXPIRE
#     install_cache(expire_after=NEVER_EXPIRE)


@dag(
    dag_id="finn_ads_ingestion", 
    start_date=datetime(2024, 1, 1), 
    schedule_interval="0 0 * * *",
    catchup=False, 
)
def dag():
    get_ads_metadata_task() >> get_ads_content_task()

@task.virtualenv(
    task_id="get_ads_metadata",
    requirements=["./requirements.txt"],
    system_site_packages=False,
    venv_cache_path="/tmp/venv"
)
def get_ads_metadata_task():
    from finn_ingestion_lib import get_ads_metadata
    get_ads_metadata()

@task.virtualenv(
    task_id="get_ads_content", 
    requirements=["./requirements.txt"], 
    system_site_packages=False,
    venv_cache_path="/tmp/venv"
)
def get_ads_content_task():
    from finn_ingestion_lib import get_ads_content
    get_ads_content()

# @task.virtualenv(
#     task_id="transform_data",
#     requirements=["./requirements.txt"], 
#     system_site_packages=False,
# )
# def transform_data_task():
#     from finn_ingestion_lib import transform_data
#     transform_data()

dag()