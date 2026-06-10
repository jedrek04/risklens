import os
import subprocess
from datetime import datetime

PROJECT_ID = os.getenv("PROJECT_ID", "risklens-498721")

IMAGE = (
    "europe-west1-docker.pkg.dev/"
    f"{PROJECT_ID}/risklens/risklens-portfolio:"
    f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
)


def run(cmd: str):
    print(">>>", cmd)
    subprocess.check_call(cmd, shell=True)


def build():
    run(
        f"gcloud builds submit . "
        f"--project {PROJECT_ID} "
        f"--config backend/app/services/risk/portfolio/cloudbuild.yaml "
        f"--substitutions _IMAGE={IMAGE}"
    )


def deploy():
    run(
        "gcloud run deploy risklens-portfolio "
        f"--project {PROJECT_ID} "
        "--region europe-west1 "
        f"--image {IMAGE} "
        "--platform managed "
        "--no-allow-unauthenticated "
        "--memory 1Gi "
        "--cpu 1 "
        "--port 8080"
    )


def main():
    print("Deploying risklens-portfolio")
    print("Image:", IMAGE)

    build()
    deploy()


if __name__ == "__main__":
    main()