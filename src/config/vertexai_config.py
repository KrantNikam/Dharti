from google.oauth2.service_account import Credentials
import vertexai
from google.cloud import aiplatform
import os


api_key_path = os.path.join(os.path.dirname(__file__), "myprojectkisaan-6abc0b1cc097.json")
credentials = Credentials.from_service_account_file(
    api_key_path, scopes = ["https://www.googleapis.com/auth/cloud-platform"]
)

PROJECT_ID = "myprojectkisaan"
REGION = "us-central1"

def initializer():
    vertexai.init(
        project=PROJECT_ID,
        location=REGION,
        credentials=credentials
    )

    aiplatform.init(project=PROJECT_ID, location=REGION,credentials=credentials)