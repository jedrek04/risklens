import subprocess
import sys
from datetime import datetime, timezone

from backend.app.config import PROJECT_ID

USAGE = "usage: python deploy.py api|pipeline"
REGION = "europe-west1"
REPO = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/risklens"

TARGETS = {
    "api": {
        "name": "risklens-api",
        "dockerfile": "backend/Dockerfile",
        "deploy": (
            "gcloud run deploy risklens-api --project {project} --region {region} "
            "--image {image} --no-allow-unauthenticated --port 8080 --memory 2Gi --cpu 2 --timeout 300 "
            "--set-secrets GNEWS_API_KEY=gnews-api-key:latest"
        ),
    },
    "pipeline": {
        "name": "market-data-load",
        "dockerfile": "backend/app/pipeline/Dockerfile",
        "deploy": (
            "gcloud run jobs update market-data-load --project {project} --region {region} "
            "--image {image} --memory 2Gi --cpu 2 --task-timeout 3600"
        ),
    },
}


def run(cmd: str):
    print(f"\n>>> {cmd}\n")
    subprocess.check_call(cmd, shell=True)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TARGETS:
        sys.exit(USAGE)

    target = TARGETS[sys.argv[1]]
    tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    image = f"{REPO}/{target['name']}:{tag}"

    run(
        f"gcloud builds submit . --project {PROJECT_ID} --config cloudbuild.yaml "
        f"--substitutions _IMAGE={image},_DOCKERFILE={target['dockerfile']}"
    )
    run(target["deploy"].format(project=PROJECT_ID, region=REGION, image=image))
    print("\nDONE")


if __name__ == "__main__":
    main()
