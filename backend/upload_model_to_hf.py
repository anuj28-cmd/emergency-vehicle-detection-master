"""
Script to upload your emergency vehicle detection model to Hugging Face Hub
"""

from huggingface_hub import HfApi, create_repo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_model_to_huggingface():
    # Get your Hugging Face username from env or input
    hf_username = os.environ.get('HF_USERNAME')
    if not hf_username:
        hf_username = input("Enter your Hugging Face username: ")
    
    # Create repository name
    repo_id = f"{hf_username}/emergency-vehicle-detection"
    
    # Path to model file (adjust as needed)
    model_path = "../main/models_backup/emergency_vehicle_model.h5"
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}")
        model_path = input("Enter the path to your model.h5 file: ")
    
    # Path to config file
    config_path = "config.json"
    
    # Create API client
    api = HfApi()
    
    # Create repository (if it doesn't exist)
    print(f"Creating repository: {repo_id}")
    create_repo(repo_id=repo_id, exist_ok=True)
    
    # Upload files
    print(f"Uploading model from {model_path}")
    api.upload_file(
        path_or_fileobj=model_path,
        path_in_repo="model.h5",
        repo_id=repo_id,
    )
    
    print(f"Uploading config from {config_path}")
    api.upload_file(
        path_or_fileobj=config_path,
        path_in_repo="config.json",
        repo_id=repo_id,
    )
    
    # Create README content
    readme_content = f"""# Emergency Vehicle Detection Model

MobileNetV2-based model for detecting emergency vehicles in traffic images.

## Model Details
- Architecture: MobileNetV2
- Input Size: 224x224x3
- Classes: Emergency Vehicle, No Emergency Vehicle
- Framework: TensorFlow/Keras

## Usage
```python
from huggingface_hub import hf_hub_download
import tensorflow as tf

model_path = hf_hub_download(repo_id="{repo_id}", filename="model.h5")
model = tf.keras.models.load_model(model_path)
```
"""
    
    # Upload README
    print("Uploading README.md")
    api.upload_file(
        path_or_fileobj=readme_content.encode(),
        path_in_repo="README.md",
        repo_id=repo_id,
    )
    
    print(f"Model successfully uploaded to https://huggingface.co/{repo_id}")
    print("To use it in your Vercel deployment, set the environment variable:")
    print(f"HF_MODEL_REPO={repo_id}")

if __name__ == "__main__":
    upload_model_to_huggingface()
