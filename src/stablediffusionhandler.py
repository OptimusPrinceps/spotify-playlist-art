import base64
import io
import os
from datetime import datetime
from time import time
from urllib.parse import urljoin

import requests
from PIL import Image, PngImagePlugin

from src.spotifyhandler import AlbumImage


class SDImage:
    def __init__(self, image, png_info):
        self.image = image
        self.png_info = png_info

    def save(self, file_name):
        file_name += '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.png'
        if not os.path.exists('../images'):
            os.mkdir('../images')

        self.image.save(f'../images/{file_name}', pnginfo=self.png_info)

    def show(self):
        self.image.show()


class StableDiffusion:
    BASE_URL = 'http://127.0.0.1:7860/sdapi/v1/'

    @classmethod
    def txt2img(cls, prompt, negative_prompt, **kwargs) -> SDImage:
        return cls._generate_image('txt2img', prompt, negative_prompt, **kwargs)

    @classmethod
    def img2img(cls, init_image: AlbumImage, prompt, negative_prompt, denoising_strength=0.6, **kwargs):
        image_bytes_64 = base64.b64encode(init_image.image_bytes).decode('utf-8')
        return cls._generate_image('img2img', prompt, negative_prompt, init_images=[image_bytes_64],
                                   denoising_strength=denoising_strength, **kwargs)

    @classmethod
    def _generate_image(cls, mode: str, prompt: str, negative_prompt: str,
                        model_checkpoint='sd_xl_base_1.0.safetensors', width=1024, height=1024, steps=30, cfg_scale=7,
                        seed=-1, save_images=True,
                        **kwargs) -> SDImage:
        """
        mode: 'txt2img' or 'img2img'
        """
        t0 = time()
        print('\nGenerating image with Stable Diffusion...', end='')
        payload = {
            "sd_model_checkpoint": model_checkpoint,
            "enable_hr": False,
            "denoising_strength": 0,
            "prompt": prompt,
            "seed": seed,
            "sampler_name": "DPM++ 2M Karras",
            "batch_size": 1,
            "n_iter": 1,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": False,
            "negative_prompt": negative_prompt,
            "eta": 0,
            "send_images": True,
            "save_images": save_images,
            **kwargs
        }
        response = cls._make_request(mode, payload)
        image = cls._extract_image(response)
        print(f' Done! ({time() - t0:.2f}s)')
        return image

    @classmethod
    def _make_request(cls, route, payload):
        url = urljoin(cls.BASE_URL, route)
        response = requests.post(url, json=payload)
        return response.json()

    @classmethod
    def _extract_image(cls, api_response) -> SDImage:
        image_byte_str = api_response['images'][0]
        image_bytes = io.BytesIO(base64.b64decode(image_byte_str.split(",", 1)[0]))
        image = Image.open(image_bytes)

        png_payload = {
            "image": "data:image/png;base64," + image_byte_str
        }
        png_response = cls._make_request('png-info', png_payload)

        png_info = PngImagePlugin.PngInfo()
        png_info.add_text("parameters", png_response.get("info"))

        return SDImage(image, png_info)
