import subprocess
from backend.app.config import PROJECT_ID

REGION = "europe-west1"
JOB_NAME = "market-data-load"

IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/risklens/{JOB_NAME}"


def run(cmd: str):
    print(f"\n>>> {cmd}\n")
    subprocess.check_call(cmd, shell=True)


def build_image():
    cmd = f"""
gcloud builds submit \
  --project {PROJECT_ID} \
  --tag {IMAGE} \
  .
"""
    run(cmd)


def deploy_job():
    update_cmd = f"""
gcloud run jobs update {JOB_NAME} \
  --image {IMAGE} \
  --region {REGION} \
  --memory 2Gi \
  --cpu 2 \
  --task-timeout 3600
"""

    create_cmd = f"""
gcloud run jobs create {JOB_NAME} \
  --image {IMAGE} \
  --region {REGION} \
  --memory 2Gi \
  --cpu 2 \
  --task-timeout 3600
"""

    try:
        run(update_cmd)
    except subprocess.CalledProcessError:
        run(create_cmd)


def main():
    build_image()
    deploy_job()
    print("\nDEPLOY DONE")


if __name__ == "__main__":
    main()