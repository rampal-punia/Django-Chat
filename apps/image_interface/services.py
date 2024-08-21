import asyncio
import requests
import io

import cv2
import numpy as np
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile


API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


class ImageModalHandler:
    def __init__(self):
        pass

    async def process_image(self, image_content):
        # Convert image content to numpy array
        img_arr = np.frombuffer(image_content, np.int8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        # Resize image
        img_resized = cv2.resize(img, (720, int(720*9/16)))

        # Convert back to bytes
        is_success, im_buf_arr = cv2.imencode(".png", img_resized)
        byte_im = im_buf_arr.tobytes()

        # Get image description
        image_description = await self.query_image_model(byte_im)

        return img_resized, image_description

    async def query_image_model(self, image_bytes):
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            data=image_bytes
        )
        return response.json()[0]['generated_text']

    @staticmethod
    def update_image_message(image_message, image_array, image_description):
        print(
            type(image_message),
            type(image_array),
            type(image_description),
        )
        # Convert numpy array to PIL Image
        img = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))

        # Save to BytesIO object
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')

        # Create a Django ContentFile
        image_content = ContentFile(
            img_io.getvalue(), name=f"image_{image_message.id}.png")

        # Update ImageMessage
        image_message.image = image_content
        image_message.width, image_message.height = img.size
        image_message.description = image_description
        image_message.save()
