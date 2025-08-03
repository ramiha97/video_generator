import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("LEONARDO_API_KEY")

def generate_leonardo_image(prompt, unique_id, model_id="photoreal", save_dir="./assets/scenes"):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "modelId": model_id,
        "width": 768,
        "height": 512,
        "num_images": 1,
        "photoReal": True
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    try:
        image_url = response.json()['generations_by_pk']['generated_images'][0]['url']
    except KeyError:
        print("⚠️ Error: Could not find image URL in response.")
        return None

    # Ensure save directory exists
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, f"{unique_id}_leonardo.jpg")

    # Download and save the image
    img_data = requests.get(image_url).content
    with open(image_path, 'wb') as f:
        f.write(img_data)

    return image_path