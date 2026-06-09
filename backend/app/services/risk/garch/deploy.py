import os
import subprocess
from datetime import datetime, timezone

PROJECT_ID = os.environ["PROJECT_ID"]
REGION = "europe-west1"

SERVICE = "risklens-garch"
REPO = "risklens"
IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{SERVICE}"


def run(cmd: str):
    print(f"\n>>> {cmd}\n")
    subprocess.check_call(cmd, shell=True)


def build_image(tag: str):
    cmd = (
        f"gcloud builds submit . "
        f"--project {PROJECT_ID} "
        f"--config backend/app/services/risk/garch/cloudbuild.yaml "
        f"--substitutions TAG_NAME={IMAGE}:{tag}"
    )
    run(cmd)


def deploy(tag: str):
    cmd = (
        f"gcloud run deploy {SERVICE} "
        f"--project {PROJECT_ID} "
        f"--region {REGION} "
        f"--image {IMAGE}:{tag} "
        f"--platform managed "
        f"--no-allow-unauthenticated "
        f"--port 8080 "
        f"--memory 1Gi "
        f"--cpu 1"
    )
    run(cmd)


def main():
    tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    print("Deploying risklens-garch")
    print("Image:", f"{IMAGE}:{tag}")
    build_image(tag)
    deploy(tag)
    print("\nDONE")


if __name__ == "__main__":
    main()