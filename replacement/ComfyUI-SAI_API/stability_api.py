import requests
from requests.models import PreparedRequest
from PIL import Image
import numpy as np
import torch
from torchvision.transforms import ToPILImage
from io import BytesIO
import os
import time

ROOT_API = "https://api.stability.ai/v2beta/"
API_KEY = os.environ.get("SAI_API_KEY")

def get_api_key():
    global API_KEY
    if API_KEY is not None:
        return API_KEY

    # Check for API key in file as a backup, not recommended
    try:
        if not API_KEY:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "sai_platform_key.txt"), "r") as f:
                API_KEY = f.read().strip()
            # Validate the key is not empty
            if API_KEY.strip() == "":
                raise Exception(f"API Key is required to use the Stability API. \nPlease set the SAI_API_KEY environment variable to your API key or place in {dir_path}/sai_platform_key.txt.")

    except Exception as e:
        print(f"\n\n***API Key is required to use the Stability API. Please set the SAI_API_KEY environment variable to your API key or place in {dir_path}/sai_platform_key.txt.***\n\n")

    return API_KEY

class StabilityBase:
    API_ENDPOINT = ""
    POLL_ENDPOINT = ""
    ACCEPT = ""

    @classmethod
    def INPUT_TYPES(cls):
        return cls.INPUT_SPEC

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "call"
    CATEGORY = "Stability"

    def call(self, *args, **kwargs):

        buffered = BytesIO()
        files = {'none': None}
        data = None

        image = kwargs.get('image', None)
        if image is not None:
            if self.API_ENDPOINT != "stable-image/control/style":
                kwargs["mode"] = "image-to-image"
                kwargs.pop("aspect_ratio", None)
            image = ToPILImage()(image.squeeze(0).permute(2,0,1))
            image.save(buffered, format="PNG")
            files = self._get_files(buffered, **kwargs)
        else:
            kwargs.pop("strength", None)
        
        image_subject = kwargs.get('subject_image', None)
        if image_subject is not None:
            buffered_sub = BytesIO() 
            image_subject = ToPILImage()(image_subject.squeeze(0).permute(2,0,1))
            image_subject.save(buffered_sub, format="PNG")
            files["subject_image"] = buffered_sub.getvalue()
        
        image_bg_ref = kwargs.get('background_reference', None)
        if image_bg_ref is not None:
            buffered_bg_ref = BytesIO()
            image_bg_ref = ToPILImage()(image_bg_ref.squeeze(0).permute(2,0,1))
            image_bg_ref.save(buffered_bg_ref, format="PNG")
            files["background_reference"] = buffered_bg_ref.getvalue()
        
        image_lt_ref = kwargs.get('light_reference', None)
        if image_lt_ref is not None:
            buffered_lt_ref = BytesIO()
            image_lt_ref = ToPILImage()(image_lt_ref.squeeze(0).permute(2,0,1))
            image_lt_ref.save(buffered_lt_ref, format="PNG")
            files["light_reference"] = buffered_lt_ref.getvalue()
        
        style = kwargs.get('style', False)
        if style is False:
            kwargs.pop('style_preset', None)

        headers = {}
        if kwargs.get("api_key_override"):
            headers["Authorization"] = kwargs.get("api_key_override")
        else:
            headers["Authorization"] = get_api_key()

        if headers.get("Authorization") is None:
            raise Exception(f"No Stability key set.\n\nUse your Stability AI API key by:\n1. Setting the SAI_API_KEY environment variable to your API key\n2. Placing inside sai_platform_key.txt\n3. Passing the API key as an argument to the function with the key 'api_key_override'")

        headers["Accept"] = self.ACCEPT

        data = self._get_data(**kwargs)
        
        if kwargs.get('aspect_ratio', None) is not None:
            data['aspect_ratio'] = data['aspect_ratio'].split("(", 1)[0]
        
        if kwargs.get('subject_image', None) is not None:
            if 'subject_image' in data:
                    del data['subject_image']
            
            if 'background_reference' in data:
                    del data['background_reference']
            
            if 'light_reference' in data:
                    del data['light_reference']
            
            if kwargs.get('light_reference', None) is not None:
                if 'light_source_direction' in data:
                    del data['light_source_direction']
            else:
                if 'light_source_direction' in data and data['light_source_direction'] == 'none':
                    if 'light_source_strength' in data:
                        del data['light_source_strength']
        
        req = PreparedRequest()
        req.prepare_method('POST')
        req.prepare_url(f"{ROOT_API}{self.API_ENDPOINT}", None)
        req.prepare_headers(headers)
        req.prepare_body(data=data, files=files)
        response = requests.Session().send(req)
        
        if response.status_code == 200:
            if self.POLL_ENDPOINT != "":
                id = response.json().get("id")
                timeout = 240
                start_time = time.time()
                while True:
                    response = requests.get(f"{ROOT_API}{self.POLL_ENDPOINT}{id}", headers=headers)
                    if response.status_code == 200:
                        if self.ACCEPT == "image/*" or self.ACCEPT == "*/*":
                            return self._return_image(response)
                        if self.ACCEPT == "video/*":
                            return self._return_video(response)
                        break
                    elif response.status_code == 202:
                        time.sleep(10)
                    elif time.time() - start_time > timeout:
                        raise Exception("Stability API Timeout: Request took too long to complete")
                    else:
                        error_info = response.json()
                        raise Exception(f"Stability API Error: {error_info}")
            else:
                result_image = Image.open(BytesIO(response.content))
                result_image = result_image.convert("RGBA")
                result_image = np.array(result_image).astype(np.float32) / 255.0
                result_image = torch.from_numpy(result_image)[None,]
                return (result_image,)
        else:
            error_info = response.json()
            if error_info.get("name") == "unauthorized":
                raise Exception("Stability API Error: Unauthorized.\n\nUse your Stability AI API key by:\n1. Setting the SAI_API_KEY environment variable to your API key\n2. Placing inside sai_platform_key.txt\n3. Passing the API key as an argument to the function with the key 'api_key_override'")
            if error_info.get("name") == "payment_required":
                raise Exception("Stability API Error: Not enough credits.\n\nPlease ensure your SAI API account has enough credits to complete this action.")
            if error_info.get("name") == "bad_request":
                errors = '\n'.join(error_info.get('errors'))
                raise Exception(f"Stability API Error: Bad request.\n\n{errors}")
            else:
                raise Exception(f"Stability API Error: {error_info}")

    def _return_image(self, response):
        result_image = Image.open(BytesIO(response.content))
        result_image = result_image.convert("RGBA")
        result_image = np.array(result_image).astype(np.float32) / 255.0
        result_image = torch.from_numpy(result_image)[None,]
        return (result_image,)

    def _return_video(self, response):
        result_video = response.content
        return (result_video,)

    def _get_files(self, buffered, **kwargs):
        return {
            "image": buffered.getvalue()
        }
    
    def _get_data(self, **kwargs):
        return {k: v for k, v in kwargs.items() if k != "image" and k != "mask"}


class StabilityCore(StabilityBase):
    API_ENDPOINT = "stable-image/generate/core"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "aspect_ratio": (["1:1(1536, 1536)", "5:4(1632, 1344)", "3:2(1824, 1248)", "16:9(2016, 1152)", "21:9(2304, 960)", "4:5(1344, 1632)", "2:3(1248, 1824)", "9:16(1152, 2016)", "9:21(960, 2304)"],),
            "style": ("BOOLEAN", {"default": False}),
            "style_preset": (["3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }


class StabilityImageUltra(StabilityBase):
    API_ENDPOINT = "stable-image/generate/ultra"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "image": ("IMAGE",),
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
            "aspect_ratio": (["1:1(1024, 1024)", "5:4(1088, 896)", "3:2(1216, 832)", "16:9(1344, 768)", "21:9(1536, 640)", "4:5(896, 1088)", "2:3(832, 1216)", "9:16(768, 1344)", "9:21(640, 1536)"],),
            "output_format": (["png", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }


class StabilityConservativeUpscale(StabilityBase):
    API_ENDPOINT = "stable-image/upscale/conservative"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "creativity": ("FLOAT", {"default": 0.35, "min": 0.2, "max": 0.5, "step": 0.01}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }


class StabilityCreativeUpscale(StabilityBase):
    API_ENDPOINT = "stable-image/upscale/creative"
    POLL_ENDPOINT  = "results/"
    ACCEPT = "*/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "creativity": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 0.35, "step": 0.01}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }


class StabilityRemoveBackground(StabilityBase):
    API_ENDPOINT = "stable-image/edit/remove-background"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
        },
    }


class StabilityInpainting(StabilityBase):
    API_ENDPOINT = "stable-image/edit/inpaint"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "default": ""}),
        },
        "optional": {
            "mask": ("MASK",),
            "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            "grow_mask": ("INT", {"default": 5, "min": 0, "max": 20}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }
    def _get_files(self, buffered, **kwargs):
        mask = kwargs.get("mask", None)
        if mask != None:
            mask = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
            mask = ToPILImage()(mask.squeeze(0).permute(2,0,1))
            buffered_mask = BytesIO()
            mask.save(buffered_mask, format="PNG")
            return {
                "image": buffered.getvalue(),
                "mask": buffered_mask.getvalue(),
            }
        else:
            return {
                "image": buffered.getvalue(),
            }


class StabilityErase(StabilityBase):
    API_ENDPOINT = "stable-image/edit/erase"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
        },
        "optional": {
            "mask": ("MASK",),
            "grow_mask": ("INT", {"default": 5, "min": 0, "max": 20}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }
    def _get_files(self, buffered, **kwargs):
        mask = kwargs.get("mask", None)
        if mask != None:
            mask = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
            mask = ToPILImage()(mask.squeeze(0).permute(2,0,1))
            buffered_mask = BytesIO()
            mask.save(buffered_mask, format="PNG")
            return {
                "image": buffered.getvalue(),
                "mask": buffered_mask.getvalue(),
            }
        else:
            return {
                "image": buffered.getvalue(),
            }


class StabilitySearchAndReplace(StabilityBase):
    API_ENDPOINT = "stable-image/edit/search-and-replace"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "search_prompt": ("STRING", {"multiline": True}),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "negative_prompt": ("STRING", {"multiline": True}),
            "grow_mask": ("INT", {"default": 3, "min": 0, "max": 20}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "api_key_override": ("STRING", {"multiline": False}),
            "output_format": (["png", "webp", "jpeg"],),
        },
    }


class StabilitySD3(StabilityBase):
    API_ENDPOINT = "stable-image/generate/sd3"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "model": (["sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium", "sd3-large", "sd3-large-turbo", "sd3-medium"],),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "image": ("IMAGE",),
            "negative_prompt": ("STRING", {"multiline": True}),
            "cfg_scale": ("FLOAT", {"default": 7.0, "min": 1.0, "max": 10.0, "step": 0.01}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
            "aspect_ratio": (["1:1(1024, 1024)", "5:4(1088, 896)", "3:2(1216, 832)", "16:9(1344, 768)", "21:9(1536, 640)", "4:5(896, 1088)", "2:3(832, 1216)", "9:16(768, 1344)", "9:21(640, 1536)"],),
            "output_format": (["png", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }


class StabilityOutpainting(StabilityBase):
    API_ENDPOINT = "stable-image/edit/outpaint"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "left": ("INT", {"default": 0, "min": 0, "max": 512}),
            "right": ("INT", {"default": 0, "min": 0, "max": 512}),
            "up": ("INT", {"default": 0, "min": 0, "max": 512}),
            "down": ("INT", {"default": 0, "min": 0, "max": 512}),\
        },
        "optional": {
            "prompt": ("STRING", {"multiline": True}),
            "creativity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }

class StabilityControlSketch(StabilityBase):
    API_ENDPOINT = "stable-image/control/sketch"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "control_strength": ("FLOAT", {"default": 0.7, "min": 0.01, "max": 1.0, "step": 0.01}),
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }


class StabilityControlStructure(StabilityBase):
    API_ENDPOINT = "stable-image/control/structure"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "control_strength": ("FLOAT", {"default": 0.7, "min": 0.01, "max": 1.0, "step": 0.01}),
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }


class StabilitySearchAndRecolor(StabilityBase):
    API_ENDPOINT = "stable-image/edit/search-and-recolor"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "select_prompt": ("STRING", {"multiline": True}),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "negative_prompt": ("STRING", {"multiline": True}),
            "grow_mask": ("INT", {"default": 3, "min": 0, "max": 20, "step": 1}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "api_key_override": ("STRING", {"multiline": False}),
            "output_format": (["png", "webp", "jpeg"],),
        },
    }


class StabilityControlStyle(StabilityBase):
    API_ENDPOINT = "stable-image/control/style"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True}),
        },
        "optional": {
            "aspect_ratio": (["1:1(1024, 1024)", "5:4(1144, 915)", "3:2(1254, 836)", "16:9(1365, 768)", "21:9(1564, 670)", "4:5(915, 1144)", "2:3(836, 1254)", "9:16(768, 1365)", "9:21(670, 1564)"],),
            "fidelity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            "negative_prompt": ("STRING", {"multiline": True}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        },
    }


class StabilityFastUpscale(StabilityBase):
    API_ENDPOINT = "stable-image/upscale/fast"
    ACCEPT = "image/*"
    INPUT_SPEC = {
        "required": {
            "image": ("IMAGE",),
        },
        "optional": {
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }

class StabilityReplaceRelight(StabilityBase):
    API_ENDPOINT = "stable-image/edit/replace-background-and-relight"
    POLL_ENDPOINT  = "results/"
    ACCEPT = "*/*"
    INPUT_SPEC = {
        "required": {
            "subject_image": ("IMAGE",),
        },
        "optional": {
            "background_reference": ("IMAGE",),
            "background_prompt": ("STRING", {"multiline": True}),
            "foreground_prompt": ("STRING", {"multiline": True}),
            "negative_prompt": ("STRING", {"multiline": True}),
            "preserve_original_subject": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
            "original_background_depth": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            "keep_original_background": ("BOOLEAN", {"default": False}),
            "light_source_direction": (["none", "above", "below", "left", "right"],),
            "light_reference": ("IMAGE",),
            "light_source_strength": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967294}),
            "output_format": (["png", "webp", "jpeg"],),
            "api_key_override": ("STRING", {"multiline": False}),
        }
    }