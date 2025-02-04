#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
# Categories:
#   Tools
#   Misc Nodes
#   Reroute Nodes
#   ControlNet Nodes
#   LoRA Nodes
#   Embedding Nodes
#   Loader Nodes
#   Pipe Nodes
#   Image Nodes
#   Mask Nodes
#   Animation Nodes
#   Logic switches Nodes
#   ComfyMath Fix Nodes
#   ComfyMath Nodes
#   Simple Evaluate Nodes
#   3D Nodes
#---------------------------------------------------------------------------------------------------------------------#
import os
import sys
import torch
import numpy
import hashlib
import io
import json
import folder_paths
import comfy.controlnet
import comfy.sd
import comfy.utils
import math
import random
import re
import cv2
import piexif
import piexif.helper
import torchvision.transforms.functional as TF
from nodes import MAX_RESOLUTION, ControlNetApply, ControlNetApplyAdvanced
from pathlib import Path
from typing import Any, Callable, Mapping, TypeAlias, List, Union
from PIL import Image, ImageOps, ImageEnhance
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
from server import PromptServer
from ..categories import icons
from .sd_prompt_reader.image_data_reader import ImageDataReader

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))

#---------------------------------------------------------------------------------------------------------------------#
# Tools
#---------------------------------------------------------------------------------------------------------------------#
def parse_name(path_name):
    path = path_name
    filename = path.split("/")[-1]
    filename = path.split("\\")[-1]
    filename = filename.split(".")[:-1]
    filename = ".".join(filename)
    return filename

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read the file in chunks to avoid loading the entire file into memory
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()

def handle_whitespace(string: str):
    return string.strip().replace("\n", " ").replace("\r", " ").replace("\t", " ")

def get_timestamp(time_format):
    now = datetime.now()
    try:
        timestamp = now.strftime(time_format)
    except:
        timestamp = now.strftime("%Y-%m-%d-%H%M%S")

    return timestamp

def make_pathname(filename, seed, modelname, counter):
    filename = filename.replace("%date", get_timestamp("%Y-%m-%d"))
    filename = filename.replace("%time", get_timestamp("%H%M%S"))
    filename = filename.replace("%model", modelname)
    filename = filename.replace("%seed", str(seed))
    filename = filename.replace("%counter", str(counter))
    return filename

def make_filename(filename, seed, modelname, counter):
    filename = make_pathname(filename, seed, modelname, counter)

    return get_timestamp("%Y-%m-%d") if filename == "" else filename

def get_resolution(resolution):

    if resolution == "SD15 512x512":
        width, height = 512, 512
    elif resolution == "SD15 680x512":
        width, height = 680, 512
    elif resolution == "SD15 768x512":
        width, height = 768, 512
    elif resolution == "SD15 912x512":
        width, height = 912, 512
    elif resolution == "SD15 952x512":
        width, height = 952, 512
    elif resolution == "SD15 1024x512":
        width, height = 1024, 512
    elif resolution == "SD15 1224x512":
        width, height = 1224, 512
    elif resolution == "SD15 768x432":
        width, height = 768, 432
    elif resolution == "SD15 768x416":
        width, height = 768, 416
    elif resolution == "SD15 768x384":
        width, height = 768, 384
    elif resolution == "SD15 768x320":
        width, height = 768, 320
    elif resolution == "SDXL 1024x1024":
        width, height = 1024, 1024
    elif resolution == "SDXL 1024x960":
        width, height = 1024, 960
    elif resolution == "SDXL 1088x960":
        width, height = 1088, 960
    elif resolution == "SD3 1088x896":
        width, height = 1088, 896
    elif resolution == "SDXL 1152x896":
        width, height = 1152, 896
    elif resolution == "SDXL 1152x832":
        width, height = 1152, 832
    elif resolution == "SD3 1216x832":
        width, height = 1216, 832
    elif resolution == "SDXL 1280x768":
        width, height = 1280, 768
    elif resolution == "SD3 1344x768":
        width, height = 1344, 768
    elif resolution == "SDXL 1344x704":
        width, height = 1344, 704
    elif resolution == "SDXL 1408x704":
        width, height = 1408, 704
    elif resolution == "SDXL 1472x704":
        width, height = 1472, 704
    elif resolution == "SD3 1536x640":
        width, height = 1536, 640
    elif resolution == "SDXL 1600x640":
        width, height = 1600, 640
    elif resolution == "SDXL 1664x576":
        width, height = 1664, 576
    elif resolution == "SDXL 1728x576":
        width, height = 1728, 576
    
    return (width, height)

def get_sd3_resolution(ratio):

    if ratio == "1:1":
        width, height = 1024, 1024
    elif ratio == "5:4":
        width, height = 1088, 896
    elif ratio == "3:2":
        width, height = 1216, 832
    elif ratio == "16:9":
        width, height = 1344, 768
    elif ratio == "21:9":
        width, height = 1536, 640
    elif ratio == "4:5":
        width, height = 896, 1088
    elif ratio == "2:3":
        width, height = 832, 1216
    elif ratio == "9:16":
        width, height = 768, 1344
    elif ratio == "9:21":
        width, height = 640, 1536
    
    return (width, height)

def get_sd3_core_resolution(ratio):

    if ratio == "1:1":
        width, height = 1536, 1536
    elif ratio == "5:4":
        width, height = 1632, 1344
    elif ratio == "3:2":
        width, height = 1824, 1248
    elif ratio == "16:9":
        width, height = 2016, 1152
    elif ratio == "21:9":
        width, height = 2304, 960
    elif ratio == "4:5":
        width, height = 1344, 1632
    elif ratio == "2:3":
        width, height = 1248, 1824
    elif ratio == "9:16":
        width, height = 1152, 2016
    elif ratio == "9:21":
        width, height = 960, 2304
    
    return (width, height)

# A special class that is always equal in not equal comparisons. Credit to pythongosssss
class AnyType(str):

  def __ne__(self, __value: object) -> bool:
    return False

any_type = AnyType("*")

def tensor2pil(t_image: torch.Tensor)  -> Image:
    return Image.fromarray(numpy.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))

def pil2tensor(image:Image) -> torch.Tensor:
    return torch.from_numpy(numpy.array(image).astype(numpy.float32) / 255.0).unsqueeze(0)

upscalemodels = {
    "1xPSNR.pth": float(1.0),
    "2xPSNR.pth": float(2.0),
    "4xPSNR.pth": float(4.0),
    "8xPSNR.pth": float(8.0),
    "16xPSNR.pth": float(16.0),
    "1x-ITF-SkinDiffDetail-Lite-v1.pth": float(1.0),
    "4x_NMKD-Siax_200k.pth": float(4.0),
    "4x_Nickelback_70000G.pth": float(4.0),
    "4xFaceUpDAT.pth": float(4.0),
    "8x_NMKD-Superscale_150000_G.pth": float(8.0),
    "BSRGANx2.pth": float(2.0),
    "BSRGANx4.pth": float(4.0),
    "DF2K_JPEGx4.pth": float(4.0),
    "ESRGANx4.pth": float(4.0),
    "Foolhardy-4xRemacri.pth": float(4.0),
    "Kim2091-4xAnimeSharp.pth": float(4.0),
    "Kim2091-4xUltraSharp.pth": float(4.0),
    "LyonHrt-4xlollypop.pth": float(4.0),
    "RealESR-animevideo-x4v3.pth": float(4.0),
    "RealESR-general-wdn-x4v3": float(4.0),
    "RealESR-general-x4v3": float(4.0),
    "RealESRGAN_x2plus.pth": float(2.0),
    "RealESRGAN_x4plus.pth": float(4.0),
    "RealESRGAN_x4plus_anime_6B.pth": float(4.0),
    "SwinIR_4x.pth": float(4.0),
    "SwinIR_4x.v2.pth": float(4.0),
}

#---------------------------------------------------------------------------------------------------------------------#
# Misc Nodes
#---------------------------------------------------------------------------------------------------------------------#
class CR_AspectRatioSD15_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
    
        return {
            "required": {
                "resolution": (["Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320"],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
            }
        }
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")

    def Aspect_Ratio(self, custom_width, custom_height, resolution, swap_dimensions):

        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        if swap_dimensions == True:
            return(height, width,)
        else:
            return(width, height,)  

class CR_AspectRatioSDXL_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "resolution": (["Custom", "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 16384, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 64, "max": 16384, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
            }
        }
    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")

    def Aspect_Ratio(self, custom_width, custom_height, resolution, swap_dimensions):
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
            
        if swap_dimensions == True:
            return(height, width,)
        else:
            return(width, height,)

class CR_AspectRatioSD3_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
    
        return {
            "required": {
                "aspect_ratio": (["1:1", "5:4", "3:2", "16:9", "21:9", "4:5", "2:3", "9:16", "9:21"],),
            }
        }
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("AspectRatio", "width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")

    def Aspect_Ratio(self, aspect_ratio):

        width, height = get_sd3_resolution(aspect_ratio)

        return(aspect_ratio, width, height,)  

class CR_AspectRatio_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "resolution": (["Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                                "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320", 
                                "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                                "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
            }
        }
    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")

    def Aspect_Ratio(self, custom_width, custom_height, resolution, swap_dimensions):
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
            
        if swap_dimensions == True:
            return(height, width,)
        else:
            return(width, height,)

class TilingMode_JK:
  
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tiling": (["enable", "x_only", "y_only", "disable"], {"default": "disable"}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("TILING",)
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")

    def get_value(self, tiling):
        return (tiling,)

class EmptyLatentColor_JK:
  
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
        }
    
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("SD15", "SDXL", "SD3", "FLUX")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")

    def get_value(self,):
        return (8548961, 9077127, 9214099, 8618319)

# functions from KJ nodes with modification: https://github.com/kijai/ComfyUI-KJNodes
def get_bounding_box(mask):

    _mask = tensor2pil(mask)
    non_zero_indices = numpy.nonzero(numpy.array(_mask))

    if len(non_zero_indices[0]) == 0:
        return (0, 0, 0, 0)
    
    min_x, max_x = numpy.min(non_zero_indices[1]).astype(int), numpy.max(non_zero_indices[1]).astype(int)
    min_y, max_y = numpy.min(non_zero_indices[0]).astype(int), numpy.max(non_zero_indices[0]).astype(int)
    
    return (int(min_x), int(min_y), int(max_x), int(max_y))

def multipleOfInt(original_int, multiple_of, mode=True):
    
    return ((math.ceil(original_int / multiple_of) if mode else math.floor(original_int / multiple_of)) * multiple_of)

class SDXL_TargetRes_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"forceInput": True}),
                "height": ("INT", {"forceInput": True}),
                "target_res_scale": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("target_width", "target_height")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, width, height, target_res_scale):
        
        target_width = multipleOfInt(width * target_res_scale, 8)
        target_height = multipleOfInt(height * target_res_scale, 8)
        
        return (target_width, target_height)

class GetSize_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE", ),
                "latent": ("LATENT", ),
                "mask": ("MASK",),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, image=None, latent=None, mask=None):
        
        if image != None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent != None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        elif mask != None:
            image_width = mask.shape[2]
            image_height = mask.shape[1]
        else:
            image_width = 0
            image_height = 0
        
        return (image_width, image_height)

class ImageCropByMaskResolution_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE", ),
                "latent": ("LATENT", ),
            },
            "required": {
                "mask": ("MASK",),
                "custom_width": ("INT", {"default": 1024, "min": 8, "max": 4096, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 8, "max": 4096, "step": 8}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "use_image_res": ("BOOLEAN", {"default": False},),
                "use_target_res": ("BOOLEAN", {"default": False},),
                "target_res": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False},),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
                "multiple_of": ("INT", {"default": 8, "min": 0, "max": 16, "step": 8}),
                "image_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],{"default": "lanczos"}),
                "latent_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "bislerp"],{"default": "bilinear"}),
            },
        }
    
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("crop_width", "crop_height", "offset_x", "offset_y", "target_width", "target_height", "image_upscale_method", "latent_upscale_method")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, mask, padding, custom_width, custom_height, use_image_res, use_target_mega_pixel, target_mega_pixel, 
                    use_target_res, target_res, multiple_of, image_upscale_method, latent_upscale_method, image=None, latent=None):
        
        multiple_of = 1 if multiple_of == 0 else multiple_of
        
        bbox = []
        
        if image != None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent != None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        else:
            image_width = custom_width
            image_height = custom_height
        
        min_x, min_y, max_x, max_y = get_bounding_box(mask)
        minimum_crop_size = min(128, image_width)
        # cropped_mask_width = max(multipleOfInt((max_x - min_x), multiple_of), minimum_crop_size)
        # cropped_mask_height = max(multipleOfInt((max_y - min_y), multiple_of), minimum_crop_size)
        cropped_mask_width = max((max_x - min_x), minimum_crop_size)
        cropped_mask_height = max((max_y - min_y), minimum_crop_size)
        
        if (max_x - min_x) < minimum_crop_size:
            offset = int((minimum_crop_size - (max_x - min_x)) / 2)
            if min_x <= offset:
                min_x = 0
                max_x = min_x + cropped_mask_width
            else:
                max_x = image_width
                min_x = max_x - cropped_mask_width
        
        if (max_y - min_y) < minimum_crop_size:
            offset = int((minimum_crop_size - (max_y - min_y)) / 2)
            if min_y <= offset:
                min_y = 0
                max_y = min_y + cropped_mask_height
            else:
                max_y = image_height
                min_y = max_y - cropped_mask_height
        
        if padding >0:
            min_x = min_x - min(min_x, padding)
            max_x = max_x + min((image_width - max_x), padding)
            min_y = min_y - min(min_y, padding)
            max_y = max_y + min((image_height - max_y), padding)
            
            cropped_mask_width = max_x - min_x
            cropped_mask_height = max_y - min_y
        
        bbox.append((min_x, min_y, cropped_mask_width, cropped_mask_height))
        
        if use_image_res:
            
            if cropped_mask_width >= cropped_mask_height:
                base_res = multipleOfInt(image_width, multiple_of)
            else:
                base_res = multipleOfInt(image_height, multiple_of)
        
        elif use_target_res:
            
            base_res = multipleOfInt(target_res, multiple_of)
        
        elif use_target_mega_pixel:
             
            scale_factor = math.sqrt(target_mega_pixel* 1000000 / (cropped_mask_width * cropped_mask_height))
            
            if cropped_mask_width >= cropped_mask_height:
                base_res = multipleOfInt(cropped_mask_width * scale_factor, multiple_of)
            else:
                base_res = multipleOfInt(cropped_mask_height * scale_factor, multiple_of)
        
        else:
        
            if cropped_mask_width >= cropped_mask_height:
                base_res = multipleOfInt(cropped_mask_width, multiple_of)
            else:
                base_res = multipleOfInt(cropped_mask_height, multiple_of)
        
        if cropped_mask_width >= cropped_mask_height:
            target_width = multipleOfInt(base_res, multiple_of)
            target_height = multipleOfInt(target_width *(cropped_mask_height / cropped_mask_width), multiple_of)
        else:
            target_height = multipleOfInt(base_res, multiple_of)
            target_width = multipleOfInt(target_height *(cropped_mask_width / cropped_mask_height), multiple_of)
        
        return (cropped_mask_width, cropped_mask_height, min_x, min_y, target_width, target_height, image_upscale_method, latent_upscale_method)

class ImageCropByMaskParams_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "inpaint_crop_and_stitch": ("BOOLEAN", {"default": False},),
                "padding": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "use_image_res": ("BOOLEAN", {"default": False},),
                "use_target_res": ("BOOLEAN", {"default": False},),
                "target_res": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False},),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("BOOLEAN", "INT", "BOOLEAN", "BOOLEAN", "INT", "BOOLEAN", "FLOAT")
    RETURN_NAMES = ("inpaint_crop_and_stitch", "padding", "use_image_res", "use_target_res", "target_res", "use_target_mega_pixel", "target_mega_pixel")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, inpaint_crop_and_stitch, padding, use_image_res, use_target_res, target_res, use_target_mega_pixel, target_mega_pixel):
        
        return (inpaint_crop_and_stitch, padding, use_image_res, use_target_res, target_res, use_target_mega_pixel, target_mega_pixel)

class UpscaleMethod_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],{"default": "lanczos"}),
                "latent_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "bislerp"],{"default": "bilinear"}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_upscale_method", "latent_upscale_method")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, image_upscale_method, latent_upscale_method):
        
        return (image_upscale_method, latent_upscale_method)

class LatentCropOffset_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_offset": ("INT", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("INT", )
    RETURN_NAMES = ("latent_offset",)
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, image_offset=0):

        return ((image_offset + 8),)

class ScaleToResolution_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE", ),
                "latent": ("LATENT", ),
            },
            "required": {
                "custom_width": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 8}),
                "direction": ("BOOLEAN", {"default": False, "label_on": "height", "label_off": "width"}),
                "target_resolution": ("INT", {"default": 512, "min": 8, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False},),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
                "multiple_of": ("INT", {"default": 8, "min": 0, "max": 16, "step": 8}),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("target_width", "target_height")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")

    def get_value(self, custom_width, custom_height, direction, target_resolution, use_target_mega_pixel, target_mega_pixel, multiple_of, image=None, latent=None):
        
        if image != None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent != None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        else:
            image_width = custom_width
            image_height = custom_height
        
        multiple_of = 1 if multiple_of == 0 else multiple_of
        
        if use_target_mega_pixel:
             
            scale_factor = math.sqrt(target_mega_pixel * 1000000 / (image_width * image_height))
            width = math.ceil((image_width * scale_factor) / multiple_of) * multiple_of
            height = math.ceil((image_height * scale_factor) / multiple_of) * multiple_of
            return (width, height)
        
        elif direction:
        
            height = math.ceil(target_resolution / multiple_of) * multiple_of
            width = math.ceil((image_width / image_height * target_resolution) / multiple_of) * multiple_of
            return (width, height)
        
        else:
            
            width = math.ceil(target_resolution / multiple_of) * multiple_of
            height = math.ceil((image_height / image_width * target_resolution) / multiple_of) * multiple_of
            return (width, height)

class Inject_Noise_Params_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "noise_strength": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step":0.01, "round": 0.01}),
                "normalize": (["false", "true"], {"default": "false"}),
            },
        }
    
    RETURN_TYPES = ("INT", "FLOAT", ["false", "true"])
    RETURN_NAMES = ("Seed", "Strength", "Normalize")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, noise_seed, noise_strength, normalize):

        return (noise_seed, noise_strength, normalize)

class SD3_Prompts_Switch_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_l": ("STRING", {"default": '', "multiline": True}),
                "clip_g": ("STRING", {"default": '', "multiline": True}),
                "t5xxl": ("STRING", {"default": '', "multiline": True}),
                "clip_l_prompt": (["clip_l", "clip_g", "t5xxl"], {"default": "clip_l"}),
                "clip_g_prompt": (["clip_l", "clip_g", "t5xxl"], {"default": "clip_g"}),
                "t5xxl_prompt": (["clip_l", "clip_g", "t5xxl"], {"default": "t5xxl"}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("clip_l", "clip_g", "t5xxl")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    
    def get_value(self, clip_l, clip_g, t5xxl, clip_l_prompt, clip_g_prompt, t5xxl_prompt):
        
        _clip_l = clip_l if clip_l_prompt == "clip_l" else (clip_g if clip_l_prompt == "clip_g" else t5xxl)
        _clip_g = clip_l if clip_g_prompt == "clip_l" else (clip_g if clip_g_prompt == "clip_g" else t5xxl)
        _t5xxl = clip_l if t5xxl_prompt == "clip_l" else (clip_g if t5xxl_prompt == "clip_g" else t5xxl)
        
        return (_clip_l, _clip_g, _t5xxl)

#---------------------------------------------------------------------------------------------------------------------#
# Reroute Nodes
#---------------------------------------------------------------------------------------------------------------------#
class RerouteList_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),{"forceInput": True}),
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"],{"forceInput": True}),
                "sampler": (comfy.samplers.KSampler.SAMPLERS,{"forceInput": True}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,{"forceInput": True}),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),{"forceInput": True}),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"), folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"], comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, folder_paths.get_filename_list("upscale_models"))
    RETURN_NAMES = ("CHECKPOINT", "VAE", "SAMPLER", "SCHEDULAR", "UPSCALE_MODEL")
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, checkpoint=None, vae=None, sampler=None, scheduler=None, upscale_model=None, image_resize=None):
        return (checkpoint, vae, sampler, scheduler, upscale_model, image_resize)

class RerouteCkpt_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),{"forceInput": True}),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),)
    RETURN_NAMES = ("CHECKPOINT",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, checkpoint=None):
        return (checkpoint,)

class RerouteVae_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"] + ["taef1"],{"forceInput": True}),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"] + ["taef1"],)
    RETURN_NAMES = ("VAE",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, vae=None):
        return (vae,)

class RerouteSampler_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS,{"forceInput": True}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,{"forceInput": True}),
            },
        }

    RETURN_TYPES = (comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS,)
    RETURN_NAMES = ("SAMPLER", "SCHEDULAR",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, sampler=None, scheduler=None):
        return (sampler, scheduler,)

class RerouteUpscale_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),{"forceInput": True}),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("upscale_models"),)
    RETURN_NAMES = ("UPSCALE_MODEL",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, upscale_model=None):
        return (upscale_model,)

class RerouteResize_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_resize": (["Just Resize", "Crop and Resize", "Resize and Fill"], {"default": "Crop and Resize", "forceInput": True}),
            }
        }

    RETURN_TYPES = (["Just Resize", "Crop and Resize", "Resize and Fill"],)
    RETURN_NAMES = ("IMAGE_RESIZE",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, image_resize=None):
        return (image_resize,)

class RerouteString_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING",{"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, string=None):
        return (string,)

# copied from https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Conversion-Nodes#cr-string-to-combo
class StringToCombo_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": False, "default": "", "forceInput": True}),
            },
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("any",)
    FUNCTION = "convert"
    CATEGORY = icons.get("JK/Reroute")
    
    def convert(self, string):
    
        text_list = list()
        
        if string != "":
            values = string.split(',')
            text_list = values[0]
        
        return (text_list,)

#---------------------------------------------------------------------------------------------------------------------#
# ControlNet Nodes
#---------------------------------------------------------------------------------------------------------------------#
UNION_CONTROLNET_TYPES = {
    "sdxl_xinsir_openpose": 0,
    "sdxl_xinsir_depth": 1,
    "sdxl_xinsir_hed/pidi/scribble/ted": 2,
    "sdxl_xinsir_canny/lineart/anime_lineart/mlsd": 3,
    "sdxl_xinsir_normal": 4,
    "sdxl_xinsir_segment": 5,
    "sdxl_xinsir_tile": 6,
    "sdxl_xinsir_repaint": 7,
    "flux_shakker_canny": 0,
    "flux_shakker_tile": 1,
    "flux_shakker_depth": 2,
    "flux_shakker_blur": 3,
    "flux_shakker_pose": 4,
    "flux_shakker_gray": 5,
    "flux_shakker_low quality": 6,
}

class CR_ControlNetLoader_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_name": (["None"] + folder_paths.get_filename_list("controlnet"), ),
                "union_type": (["None"] + ["auto"] + list(UNION_CONTROLNET_TYPES.keys()),)
            }
        }

    RETURN_TYPES = ("CONTROL_NET",)
    FUNCTION = "load_controlnet"
    CATEGORY = icons.get("JK/ControlNet")

    def load_controlnet(self, control_net_name, union_type):
        
        if control_net_name == "None":
            
            return ("",)
        
        else:
            controlnet_path = folder_paths.get_full_path_or_raise("controlnet", control_net_name)
            controlnet_load = comfy.controlnet.load_controlnet(controlnet_path)
            
            type_number = UNION_CONTROLNET_TYPES.get(union_type, -2)
                        
            if type_number >= -1:
                controlnet_load = controlnet_load.copy()
            
                if type_number >= 0:
                    controlnet_load.set_extra_arg("control_type", [type_number])
                else:
                    controlnet_load.set_extra_arg("control_type", [])

            return (controlnet_load,)

class CR_ControlNetStack_JK:
    
    modes = ["simple", "advanced"]
    controlnets = ["None"] + folder_paths.get_filename_list("controlnet")
    
    @classmethod
    def INPUT_TYPES(cls):
        
        inputs = {
            "optional": {
                "image_0": ("IMAGE",),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_MetaData_0": ("STRING", {"forceInput": True},),
                "image_MetaData_1": ("STRING", {"forceInput": True},),
                "image_MetaData_2": ("STRING", {"forceInput": True},),
                "image_MetaData_3": ("STRING", {"forceInput": True},),
                "image_MetaData_4": ("STRING", {"forceInput": True},),
                "image_MetaData_5": ("STRING", {"forceInput": True},),
            },
            "required": {
                "control_switch": ("BOOLEAN", {"default": False},),
                "input_mode": (cls.modes,),
                "controlnet_count": ("INT", {"default": 3, "min": 1, "max": 6, "step": 1}),
            },
        }
        
        for i in range(0, 6):
            #inputs["required"][f"image_{i}"] = ("IMAGE",)
            inputs["required"][f"ControlNet_Unit_{i}"] = ("BOOLEAN", {"default": False},)
            inputs["required"][f"controlnet_{i}"] = (cls.controlnets,)
            inputs["required"][f"union_type_{i}"] = (["None"] + ["auto"] + list(UNION_CONTROLNET_TYPES.keys()),)
            inputs["required"][f"controlnet_strength_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"start_percent_{i}"] = ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001})
            inputs["required"][f"end_percent_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001})

        inputs["required"][f"save_hash"] = ("BOOLEAN", {"default": False},)
        
        return inputs

    RETURN_TYPES = ("CONTROL_NET_STACK", "STRING", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("CONTROLNET_STACK", "ControlNet_MetaData", "ContrlNet_Switch", "ContrlNet0_Switch", "ContrlNet1_Switch", "ContrlNet2_Switch", "ContrlNet3_Switch", "ContrlNet4_Switch", "ContrlNet5_Switch")
    FUNCTION = "controlnet_stacker"
    CATEGORY = icons.get("JK/ControlNet")

    def controlnet_stacker(self, control_switch, input_mode, controlnet_count, save_hash, **kwargs):

        # Initialise the list
        controlnet_list = []
        metadataout = ""
        
        if control_switch == True:
            j = 0
            for i in range (0, controlnet_count + 1):
                if kwargs.get(f"controlnet_{i}") != "None" and  kwargs.get(f"ControlNet_Unit_{i}") == True and kwargs.get(f"image_{i}") is not None:
                    
                    controlnet_path = folder_paths.get_full_path("controlnet", kwargs.get(f"controlnet_{i}"))
                    controlnet_name = Path(kwargs.get(f"controlnet_{i}")).stem
                    controlnet_hash = f" [{calculate_sha256(controlnet_path)[:8]}]" if save_hash == True else ""
                    controlnet_load = comfy.controlnet.load_controlnet(controlnet_path)
                    
                    type_number = UNION_CONTROLNET_TYPES.get(kwargs.get(f"union_type_{i}"), -2)
                    
                    if type_number >= -1:
                        controlnet_load = controlnet_load.copy()
                    
                        if type_number >= 0:
                            controlnet_load.set_extra_arg("control_type", [type_number])
                        else:
                            controlnet_load.set_extra_arg("control_type", [])
                    
                    controlnet_list.extend([(controlnet_load, kwargs.get(f"image_{i}"), kwargs.get(f"controlnet_strength_{i}"), kwargs.get(f"start_percent_{i}") if input_mode == "simple" else 0.0, kwargs.get(f"end_percent_{i}") if input_mode == "simple" else 1.0)])
                    
                    controlnet_str = f"{kwargs.get(f'controlnet_strength_{i}'):.3f}"
                    controlnet_sta = f"{kwargs.get(f'start_percent_{i}'):.3f}" if input_mode == "simple" else f"0.0"
                    controlnet_end = f"{kwargs.get(f'end_percent_{i}'):.3f}" if input_mode == "simple" else f"1.0"
                    metadatacommon = f"ControlNet {j}: \"Module: none, Model: {controlnet_name}{controlnet_hash}, Weight: {controlnet_str}, {kwargs.get(f'image_MetaData_{i}') if kwargs.get(f'image_MetaData_{i}') !=None else 'Resize Mode: Just Resize'}, Low Vram: True, Guidance Start: {controlnet_sta}, Guidance End: {controlnet_end}, Pixel Perfect: True, Control Mode: Balanced, Save Detected Map: True\", ",
                    
                    if j == 0:
                        metadataout = metadatacommon
                    else:
                        metadataout = f"{metadataout}{metadatacommon}"
                    j +=1
        
                    metadataout = f"{metadataout}".replace("('", "")
                    metadataout = f"{metadataout}".replace("',)", "")
        
        return (controlnet_list, metadataout, control_switch, 
                control_switch and kwargs.get(f"ControlNet_Unit_0"), 
                control_switch and kwargs.get(f"ControlNet_Unit_1") and controlnet_count >= 2, 
                control_switch and kwargs.get(f"ControlNet_Unit_2") and controlnet_count >= 3, 
                control_switch and kwargs.get(f"ControlNet_Unit_3") and controlnet_count >= 4, 
                control_switch and kwargs.get(f"ControlNet_Unit_4") and controlnet_count >= 5, 
                control_switch and kwargs.get(f"ControlNet_Unit_5") and controlnet_count == 6)

class CR_ControlNetParamStack_JK:
    
    modes = ["simple", "advanced"]
    controlnets = ["None"] + folder_paths.get_filename_list("controlnet")
    
    @classmethod
    def INPUT_TYPES(cls):
        
        inputs = {
            "optional": {
                "controlnet_0": ("CONTROL_NET",),
                "image_0": ("IMAGE",),
                "controlnet_1": ("CONTROL_NET",),
                "image_1": ("IMAGE",),
                "controlnet_2": ("CONTROL_NET",),
                "image_2": ("IMAGE",),
                "controlnet_3": ("CONTROL_NET",),
                "image_3": ("IMAGE",),
                "controlnet_4": ("CONTROL_NET",),
                "image_4": ("IMAGE",),
                "controlnet_5": ("CONTROL_NET",),
                "image_5": ("IMAGE",),
            },
            "required": {
                "control_switch": ("BOOLEAN", {"default": False},),
                "input_mode": (cls.modes,),
                "controlnet_count": ("INT", {"default": 3, "min": 1, "max": 6, "step": 1}),
            },
        }
        
        for i in range(0, 6):

            inputs["required"][f"ControlNet_Unit_{i}"] = ("BOOLEAN", {"default": False},)
            inputs["required"][f"controlnet_strength_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"start_percent_{i}"] = ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001})
            inputs["required"][f"end_percent_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001})

        return inputs

    RETURN_TYPES = ("CONTROL_NET_STACK", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("CONTROLNET_STACK", "ContrlNet_Switch", "ContrlNet0_Switch", "ContrlNet1_Switch", "ContrlNet2_Switch", "ContrlNet3_Switch", "ContrlNet4_Switch", "ContrlNet5_Switch")
    FUNCTION = "controlnet_stacker"
    CATEGORY = icons.get("JK/ControlNet")

    def controlnet_stacker(self, control_switch, input_mode, controlnet_count, **kwargs):

        # Initialise the list
        controlnet_list = []
        
        if control_switch == True:
            j = 0
            for i in range (0, controlnet_count + 1):
                if kwargs.get(f"controlnet_{i}") != None and kwargs.get(f"controlnet_{i}") != "" and kwargs.get(f"ControlNet_Unit_{i}") == True and kwargs.get(f"image_{i}") is not None:
                    
                    controlnet_list.extend([(kwargs.get(f"controlnet_{i}"), kwargs.get(f"image_{i}"), kwargs.get(f"controlnet_strength_{i}"), kwargs.get(f"start_percent_{i}") if input_mode == "simple" else 0.0, kwargs.get(f"end_percent_{i}") if input_mode == "simple" else 1.0)])
        
        return (controlnet_list, control_switch, 
                control_switch and kwargs.get(f"ControlNet_Unit_0"), 
                control_switch and kwargs.get(f"ControlNet_Unit_1") and controlnet_count >= 2, 
                control_switch and kwargs.get(f"ControlNet_Unit_2") and controlnet_count >= 3, 
                control_switch and kwargs.get(f"ControlNet_Unit_3") and controlnet_count >= 4, 
                control_switch and kwargs.get(f"ControlNet_Unit_4") and controlnet_count >= 5, 
                control_switch and kwargs.get(f"ControlNet_Unit_5") and controlnet_count == 6)

class CR_ApplyControlNet_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_positive": ("CONDITIONING",),
                "base_negative": ("CONDITIONING",),
                
                "effective_mask": ("BOOLEAN", {"default": False},),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
            },
            "optional": {
                "image": ("IMAGE", ),
                "mask": ("MASK", ),
                "vae": ("VAE",),
                "control_net": ("CONTROL_NET", ),
             }
        }
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING",)
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet"

    CATEGORY = icons.get("JK/ControlNet")

    def apply_controlnet(self, base_positive, base_negative, effective_mask, strength, start_percent, end_percent, image=None, vae=None, mask=None, control_net=None):
        
        if image is not None and control_net is not None and control_net != "" and strength != 0.0:
            
            from comfy_extras.nodes_compositing import SplitImageWithAlpha
            
            if type(control_net) == str:
                controlnet_path = folder_paths.get_full_path("controlnet", control_net)
                controlnet = comfy.sd.load_controlnet(controlnet_path)
            else:
                controlnet = control_net
            
            image, mask_from_image = SplitImageWithAlpha().split_image_with_alpha(image)
            
            # the mask from the image overrides the input mask
            if mask == None or torch.all(mask_from_image == 0).int().item() == 0:
                mask_cal = mask_from_image
            else:
                mask_cal = mask
            
            extra_concat = []
            if control_net.concat_mask:
                mask_cal = 1.0 - mask_cal.reshape((-1, 1, mask_cal.shape[-2], mask_cal.shape[-1]))
                mask_apply = comfy.utils.common_upscale(mask_cal, image.shape[2], image.shape[1], "bilinear", "center").round()
                image = image * mask_apply.movedim(1, -1).repeat(1, 1, 1, image.shape[3])
                extra_concat = [mask_cal]
                
            controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(base_positive, base_negative, controlnet, image, strength, start_percent, end_percent, vae=vae, extra_concat=extra_concat)
            
            if effective_mask and torch.all(mask_cal == 0).int().item() == 0:
                from node_helpers import conditioning_set_values
                base_positive = conditioning_set_values(controlnet_conditioning[0], {"mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0}) + conditioning_set_values(base_positive, {"mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0})
                base_negative = conditioning_set_values(controlnet_conditioning[1], {"mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0}) + conditioning_set_values(base_negative, {"mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0})
            else:
                base_positive, base_negative = controlnet_conditioning[0], controlnet_conditioning[1]
        
        return (base_positive, base_negative, )

class CR_ApplyControlNetStack_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_positive": ("CONDITIONING",),
                "base_negative": ("CONDITIONING",), 
            },
            "optional": {
                "controlnet_stack": ("CONTROL_NET_STACK", ),
            }
        }                    

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet_stack"
    CATEGORY = icons.get("JK/ControlNet")

    def apply_controlnet_stack(self, base_positive, base_negative, controlnet_stack=None):

        if controlnet_stack is not None and len(controlnet_stack) != 0:
        
            for controlnet_tuple in controlnet_stack:
                controlnet_name, image, strength, start_percent, end_percent  = controlnet_tuple
                
                if type(controlnet_name) == str:
                    controlnet_path = folder_paths.get_full_path("controlnet", controlnet_name)
                    controlnet = comfy.sd.load_controlnet(controlnet_path)
                else:
                    controlnet = controlnet_name
                
                controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(base_positive, base_negative, controlnet, image, strength, start_percent, end_percent)
                
        return (base_positive, base_negative, )

class CR_ApplyControlNetStackAdv_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_positive": ("CONDITIONING",),
                "base_negative": ("CONDITIONING",),
                "effective_mask": ("BOOLEAN", {"default": False},),
            },
             "optional": {
                "mask": ("MASK", ),
                "vae": ("VAE",),
                "controlnet_stack": ("CONTROL_NET_STACK", ),
             }
        }                    
    
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet_stack"
    CATEGORY = icons.get("JK/ControlNet")

    def apply_controlnet_stack(self, base_positive, base_negative, effective_mask, vae=None, mask=None, controlnet_stack=None):
        
        from comfy_extras.nodes_compositing import SplitImageWithAlpha
        
        if controlnet_stack is not None and len(controlnet_stack) != 0:
            for controlnet_tuple in controlnet_stack:
                controlnet_name, image, strength, start_percent, end_percent  = controlnet_tuple
                
                if type(controlnet_name) == str:
                    controlnet_path = folder_paths.get_full_path("controlnet", controlnet_name)
                    controlnet = comfy.sd.load_controlnet(controlnet_path)
                else:
                    controlnet = controlnet_name
                
                image, mask_from_image = SplitImageWithAlpha().split_image_with_alpha(image)
                
                # the mask from the image overrides the input mask
                if mask == None or torch.all(mask_from_image == 0).int().item() == 0:
                    mask_cal = mask_from_image
                else:
                    mask_cal = mask
                
                extra_concat = []
                if  controlnet.concat_mask:
                    mask_cal = 1.0 - mask_cal.reshape((-1, 1, mask_cal.shape[-2], mask_cal.shape[-1]))
                    mask_apply = comfy.utils.common_upscale(mask_cal, image.shape[2], image.shape[1], "bilinear", "center").round()
                    image = image * mask_apply.movedim(1, -1).repeat(1, 1, 1, image.shape[3])
                    extra_concat = [mask_cal]
                
                controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(base_positive, base_negative, controlnet, image, strength, start_percent, end_percent, vae=vae, extra_concat=extra_concat)
                
                if effective_mask and torch.all(mask_cal == 0).int().item() == 0:
                    from node_helpers import conditioning_set_values
                    base_positive = conditioning_set_values(controlnet_conditioning[0], {"mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0}) + conditioning_set_values(base_positive, {"mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0})
                    base_negative = conditioning_set_values(controlnet_conditioning[1], {"mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0}) + conditioning_set_values(base_negative, {"mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0})
                else:
                    base_positive, base_negative = controlnet_conditioning[0], controlnet_conditioning[1]
                
        return (base_positive, base_negative, )

#---------------------------------------------------------------------------------------------------------------------#
# LoRA Nodes
#---------------------------------------------------------------------------------------------------------------------#
class CR_LoraLoader_JK:

    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        file_list = folder_paths.get_filename_list("loras")
        file_list.insert(0, "None")
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "switch": ("BOOLEAN", {"default": False}),
                "input_mode": (['simple', 'advanced'], {"default": 'simple'}),
                "lora_name": (file_list, ),
                "lora_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "model_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "clip_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }
    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_lora"
    CATEGORY = icons.get("JK/LoRA")

    def load_lora(self, model, clip, switch, lora_name, model_weight, clip_weight):
        
        if input_mode == "simple" and switch == False or  lora_name == "None":
            return (model, clip)
        if input_mode == "advanced" and model_weight == 0 and clip_weight == 0:
            return (model, clip)

        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                del self.loaded_lora

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)
        
        if input_mode == "simple":
            model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, lora_weight, 0.0)
        elif input_mode == "advanced":
            model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, model_weight, clip_weight)
        
        return (model_lora, clip_lora)

class CR_LoRAStack_JK:
    
    modes = ["simple", "advanced"]
    
    @classmethod
    def INPUT_TYPES(cls):
    
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        inputs = {
            "required": {
                "input_mode": (cls.modes,),
                "lora_count": ("INT", {"default": 3, "min": 1, "max": 6, "step": 1}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
                "lora_prompt": ("STRING", {"forceInput": True}),
                "lora_metadata": ("STRING", {"forceInput": True}),
            },
        }
        
        for i in range (1, 7):
            inputs["required"][f"lora_{i}"] = ("BOOLEAN", {"default": False},)
            inputs["required"][f"lora_name_{i}"] = (loras,)
            inputs["required"][f"lora_weight_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"model_weight_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"clip_weight_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
        
        inputs["required"][f"save_hash"] = ("BOOLEAN", {"default": False},)
        
        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING",)
    RETURN_NAMES = ("LORA_STACK", "LORA_PROMPT", "LORA_MetaData",)
    FUNCTION = "lora_stacker"
    CATEGORY = icons.get("JK/LoRA")

    def lora_stacker(self, input_mode, lora_count, save_hash, lora_stack=None, lora_prompt=None, lora_metadata=None, **kwargs):

        # Initialise the list
        lora_list = list()
        lora_enable_check = False
        lorapromptout = ""
        lorametaout = ""
        
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])
        
        j = 0
        
        for i in range (1, lora_count+1):
            
            if input_mode == "simple":
                if kwargs.get(f"lora_{i}") == True and kwargs.get(f"lora_name_{i}") != "None" and kwargs.get(f"lora_weight_{i}") != 0:
                    lora_enable_check = True
                else:
                    lora_enable_check = False
            elif input_mode == "advanced": 
                if kwargs.get(f"lora_{i}") == True and kwargs.get(f"lora_name_{i}") != "None" and kwargs.get(f"model_weight_{i}") != 0 and kwargs.get(f"clip_weight_{i}") != 0:
                    lora_enable_check = True
                else:
                    lora_enable_check = False
            
            if lora_enable_check:
                
                if input_mode == "simple":
                    lora_list.extend([(kwargs.get(f"lora_name_{i}"), kwargs.get(f"lora_weight_{i}"), 0.0)]),
                elif input_mode == "advanced":
                    lora_list.extend([(kwargs.get(f"lora_name_{i}"), kwargs.get(f"model_weight_{i}"), kwargs.get(f"clip_weight_{i}"))]),
                
                lora_name = Path(kwargs.get(f"lora_name_{i}")).stem
                loraprompt = f"lora:{lora_name}"
                
                if input_mode == "simple":
                    loraweight = f"{kwargs.get(f'lora_weight_{i}'):.3f}"
                elif input_mode == "advanced":
                    loraweight = f"{kwargs.get(f'model_weight_{i}'):.3f}"
                
                loraprompt = f"<{loraprompt}:{loraweight}>"
                
                if (lora_prompt == None or lora_prompt == "") and j == 0:
                    lorapromptout = f"{loraprompt}"
                elif lora_prompt != None and lora_prompt != "" and j == 0:
                    lorapromptout = f"{lora_prompt},{loraprompt}"
                else:
                    lorapromptout = f"{lorapromptout},{loraprompt}"
                
                lora_path = folder_paths.get_full_path("loras", kwargs.get(f"lora_name_{i}"))
                lora_hash = f": [{calculate_sha256(lora_path)[:12]}]" if save_hash == True else ""
                lora_meta = f"{lora_name}{lora_hash}"
                
                if (lora_metadata == None or lora_metadata == "") and j == 0:
                    lorametaout = f"{lora_meta}"
                elif lora_metadata != None and lora_metadata != "" and j == 0:
                    lorametaout = f"{lora_metadata}, {lora_meta}"
                else:
                    lorametaout = f"{lorametaout}, {lora_meta}"
                
                j +=1
                
        return (lora_list, lorapromptout, lorametaout,)

# Copied from "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/LoRA-Nodes#cr-apply-lora-stack"
class CR_ApplyLoRAStack_JK:

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": ("MODEL",),
                            "clip": ("CLIP", ),
                            "lora_stack": ("LORA_STACK", ),
                            }
        }

    RETURN_TYPES = ("MODEL", "CLIP",)
    RETURN_NAMES = ("MODEL", "CLIP",)
    FUNCTION = "apply_lora_stack"
    CATEGORY = icons.get("JK/LoRA")

    def apply_lora_stack(self, model, clip, lora_stack=None,):
        
        lora_params = list()
 
        if lora_stack:
            lora_params.extend(lora_stack)
        else:
            return (model, clip,)

        model_lora = model
        clip_lora = clip

        for tup in lora_params:
            lora_name, strength_model, strength_clip = tup
            
            lora_path = folder_paths.get_full_path("loras", lora_name)
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            
            model_lora, clip_lora = comfy.sd.load_lora_for_models(model_lora, clip_lora, lora, strength_model, strength_clip)  

        return (model_lora, clip_lora,)

#---------------------------------------------------------------------------------------------------------------------#
# Embedding Nodes
#---------------------------------------------------------------------------------------------------------------------#
class EmbeddingPicker_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "embedding": (folder_paths.get_filename_list("embeddings"),),
                "emphasis": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05,},),
                "append": ("BOOLEAN", {"default": True},),
                "save_hash": ("BOOLEAN", {"default": True},),
            },
            "optional": {
                "text_in": ("STRING", {"forceInput": True}),
                "metadata_in": ("STRING", {"forceInput": True}),
            }
        }


    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Text", "METADATA",)
    FUNCTION = "concat_embedding"
    #OUTPUT_NODE = False

    CATEGORY = icons.get("JK/Embedding")

    def concat_embedding(self, embedding, emphasis, append, save_hash, text_in=None, metadata_in=None):
        if emphasis < 0.05:
            return (text_in if text_in !=None else '', metadata_in if metadata_in !=None else '')

        emb = "embedding:" + Path(embedding).stem
        emphasis = f"{emphasis:.3f}"
        if emphasis != "1.000":
            emb = f"({emb}:{emphasis})"
        if text_in == None:
            textout = f"{emb}"
        else:
            textout = f"{text_in}, {emb}" if append else f"{emb}, {text_in}"
            
        emb_path = folder_paths.get_full_path("embeddings", embedding)
        emb_name = Path(embedding).stem
        emb_hash = f": [{calculate_sha256(emb_path)[:12]}]" if save_hash == True else ""
        metadataout = f"{emb_name}{emb_hash}"
        metaout = f"{f'{metadata_in}, {metadataout}' if metadata_in !=None else f'{metadataout}'}"

        return (textout, metaout, )

class EmbeddingPicker_Multi_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        embeddingslist = ["None"] + folder_paths.get_filename_list("embeddings")
        
        inputs = {
            "required": {
                "input_mode": (['simple', 'advanced'], {"default": 'simple'}),
                "embedding_count": ("INT", {"default": 3, "min": 1, "max": 6, "step": 1}),
            },
            "optional": {
                "text_in": ("STRING", {"forceInput": True}),
                "metadata_in": ("STRING", {"forceInput": True}),
            }
        }
        
        for i in range(1, 7):
            inputs["required"][f"embedding_{i}"] = ("BOOLEAN", {"default": False},)
            inputs["required"][f"embedding_name_{i}"] = (embeddingslist,)
            inputs["required"][f"emphasis_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05,},)
            inputs["required"][f"append_{i}"] = ("BOOLEAN", {"default": True},)
        
        inputs["required"][f"save_hash"] = ("BOOLEAN", {"default": False},)
        
        return inputs

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Text", "METADATA",)
    FUNCTION = "concat_embedding"
    #OUTPUT_NODE = False

    CATEGORY = icons.get("JK/Embedding")

    def concat_embedding(self, input_mode, embedding_count, save_hash, text_in=None, metadata_in=None, **kwargs):
        
        embedding_enable = False
        
        for i in range(1, embedding_count + 1):
            if kwargs.get(f"embedding_{i}") == True and kwargs.get(f"embedding_name_{i}") != "None" and kwargs.get(f"emphasis_{i}") >= 0.05:
                embedding_enable = True
                break
        
        if text_in != None:
            if text_in != "":
                if embedding_enable:
                    if text_in[-1] == ",":
                        textout = f"{text_in}"
                    else:
                        textout = f"{text_in},"
                else:
                    textout = f"{text_in}"
            else:
                textout = ""
        else:
            textout = ""
        
        metaout = metadata_in if metadata_in != None else ""
        
        j = 0
        
        for i in range(1, embedding_count + 1):
            
            if kwargs.get(f"embedding_{i}") == True and kwargs.get(f"embedding_name_{i}") != "None" and kwargs.get(f"emphasis_{i}") >= 0.05:
                
                if input_mode == "simple":
                    append_check = True
                elif input_mode == "advanced":
                    append_check = kwargs.get(f"append_{i}")
                
                emb = "embedding:" + Path(kwargs.get(f"embedding_name_{i}")).stem
                emphasis = f"{kwargs.get(f'emphasis_{i}'):.3f}"
                emb = f"({emb}:{emphasis}),"
                
                textout = f"{textout}{emb}" if append_check else f"{emb}{textout}"
                
                emb_path = folder_paths.get_full_path("embeddings", kwargs.get(f"embedding_name_{i}"))
                emb_name = Path(kwargs.get(f"embedding_name_{i}")).stem
                emb_hash = f": [{calculate_sha256(emb_path)[:12]}]" if save_hash == True else ""
                emb_meta = f"{emb_name}{emb_hash}"
                
                if (metadata_in == None or metadata_in == "") and j == 0:
                    metaout = f"{emb_meta},"
                elif metadata_in != None and metadata_in != "" and j == 0:
                    metaout = f"{metadata_in}, {emb_meta}"
                else:
                    metaout = f"{metaout}, {emb_meta}"
                
                j += 1

        return (textout, metaout, )

#---------------------------------------------------------------------------------------------------------------------#
# Loader Nodes
#---------------------------------------------------------------------------------------------------------------------#
class CkptLoader_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),),
            },
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("checkpoints"))
    RETURN_NAMES = ("ckpt_name", "Checkpoint")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    
    def list(self, checkpoint):
        return (checkpoint, checkpoint)

class VaeLoader_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"] + ["taef1"],),
            },
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"] + ["taef1"])
    RETURN_NAMES = ("vae_name", "VAE")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    
    def list(self, vae):
        return (vae, vae)

class SamplerLoader_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            }
        }

    RETURN_TYPES = ("STRING", comfy.samplers.KSampler.SAMPLERS, "STRING", comfy.samplers.KSampler.SCHEDULERS)
    RETURN_NAMES = ("sampler_name", "Sampler", "schedular_name", "Schedular")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    
    def list(self, sampler, scheduler):
        return (sampler, sampler, scheduler, scheduler)

class UpscaleModelLoader_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
            }
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("upscale_models"))
    RETURN_NAMES = ("upscale_model_name", "Upscale_Model")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    
    def list(self, upscale_model):
        return (upscale_model, upscale_model)

#---------------------------------------------------------------------------------------------------------------------#
# Pipe Nodes
#---------------------------------------------------------------------------------------------------------------------#
class NodesState_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                    "node_id_list": ("STRING", {"default": '', "multiline": False}),
                    "mute_state": ("BOOLEAN", {"default": True, "label_on": "active", "label_off": "mute"}),
                    "bypass_state": ("BOOLEAN", {"default": True, "label_on": "active", "label_off": "bypass"}),
                    }
                }

    FUNCTION = "doit"

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    CATEGORY = icons.get("JK/Pipe")
    OUTPUT_NODE = True

    def doit(self, node_id_list, mute_state, bypass_state):
        node_ids = re.split('[.,;:]', node_id_list)
        
        for node_id in node_ids:
            node_id = int(node_id)
            
            if mute_state and bypass_state:
                PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 0})
            elif mute_state == False and bypass_state:
                PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 2})
            else:
                PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 4})
        
        return ()

class KsamplerParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"forceInput": True}),
                "stop_at_clip_layer": ("INT", {"default": -1, "min": -24, "max": -1}),
                "positive": ("STRING", {"default": '', "multiline": True}),
                "negative": ("STRING", {"default": '', "multiline": True}),
                "variation": ("STRING", {"default": '', "multiline": True}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "resolution": (["Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                                "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320", 
                                "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                                "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
            },
        }
    
    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING", "INT", "INT", "FLOAT", comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, "FLOAT", "INT", "INT", "INT")
    RETURN_NAMES = ("STOPLAYER", "POSITIVE", "NEGATIVE", "VARIATION", "SEED", "STEPS", "CFG", "SAMPLER", "SCHEDULAR", "DENOISE", "WIDTH", "HEIGHT", "BATCHSIZE")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, resolution, stop_at_clip_layer, custom_width, custom_height, swap_dimensions, batch_size):
        
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        if swap_dimensions == True:
            return (stop_at_clip_layer, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, width, height, batch_size)
        else:
            return (stop_at_clip_layer, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, height, width, batch_size)

class KsamplerParametersDefault_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("STEPS", "CFG", "DENOISE")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, steps, cfg, denoise):
    
        return (steps, cfg, denoise)

class GuidanceDefault_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            },
        }
    
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("GUIDANCE",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, guidance):
    
        return (guidance,)

class ProjectSetting_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": 'myproject', "multiline": False}),
                "image_name": ("STRING", {"default": f'v%counter_%seed_%time', "multiline": False}),
                "path_name": ("STRING", {"default": f'%date', "multiline": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("Image_Name", "Path_Name", "Counter")
    FUNCTION = "get_value"

    OUTPUT_NODE = True

    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, project_name, image_name, path_name, seed):
        
        image_name = project_name + "_" + image_name
        path_name = project_name + "/" + path_name
        
        random.seed(seed)
        number = random.randint (0, 18446744073709551615)

        return (image_name, path_name, seed)

class BaseModelParameters_JK:
  
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": ("STRING", {"forceInput": True}),
                "vae_name": ("STRING", {"forceInput": True}),
                "base_seed": ("INT", {"forceInput": True}),
                #
                "positive_clip_l": ("STRING", {"default": '', "multiline": True}),
                "positive_clip_g_or_t5xxl": ("STRING", {"default": '', "multiline": True}),
                "negative_clip_l": ("STRING", {"default": '', "multiline": True}),
                "negative_clip_g_or_t5xxl": ("STRING", {"default": '', "multiline": True}),
                "append_input_prompt": ("BOOLEAN", {"default": False},),
                "variation": ("STRING", {"default": '', "multiline": True}),
                "resolution": (["Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                                "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320", 
                                "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                                "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "cfg_or_flux_neg_scale": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "tiling": (["enable", "x_only", "y_only", "disable"], {"default": "disable"}),
                "specified_vae": ("BOOLEAN", {"default": True},),
                "stop_at_clip_layer": ("INT", {"default": -1, "min": -24, "max": -1}),
                #
                "img2img": ("BOOLEAN", {"default": False},),
                "image_resize": (["Just Resize", "Crop and Resize", "Resize and Fill"], {"default": "Crop and Resize", "forceInput": False}),
                "img2img_denoise": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                #
                "save_ckpt_hash": ("BOOLEAN", {"default": False},),
            },
            "optional": {
                "image": ("IMAGE",),
                "input_positive": ("STRING", {"forceInput": True}),
                "input_negative": ("STRING", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE", "PIPE_LINE")
    RETURN_NAMES = ("Base_Model_MetaData", "Base_Model_Pipe", "Base_Image_Pipe")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, ckpt_name, vae_name, base_seed, positive_clip_l, positive_clip_g_or_t5xxl, negative_clip_l, negative_clip_g_or_t5xxl, append_input_prompt, variation, resolution, custom_width, custom_height, swap_dimensions, steps, sampler_name, scheduler, cfg_or_flux_neg_scale, tiling, specified_vae, stop_at_clip_layer, img2img, image_resize, img2img_denoise, batch_size, save_ckpt_hash, image=None, input_positive=None, input_negative=None):
        
        if append_input_prompt == True and input_positive != None and input_negative != None:
            if input_positive != "":
                positive_clip_g_or_t5xxl = f"{input_positive},{positive_clip_g_or_t5xxl}"
            if input_negative != "":
                negative_clip_g_or_t5xxl = f"{input_negative},{negative_clip_g_or_t5xxl}"
        
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        img2img_denoise = 1.0 if img2img == False else img2img_denoise
        
        pipe_model = (ckpt_name, stop_at_clip_layer, positive_clip_l, positive_clip_g_or_t5xxl, negative_clip_l, negative_clip_g_or_t5xxl, variation, base_seed, steps, sampler_name, scheduler, cfg_or_flux_neg_scale, img2img_denoise, tiling, specified_vae, vae_name)
        pipe_image = (image, width, height, batch_size, image_resize, img2img)
        pipe_image_swap = (image, height, width, batch_size, image_resize, img2img)
        
        stop_layer_metadata = - stop_at_clip_layer
        img2img_denoise_metadata = f"{img2img_denoise:.3f}"
        size_metadata = f"{width}x{height}" if swap_dimensions == False else f"{height}x{width}"
        baseckpt_path = f"{folder_paths.get_full_path('checkpoints', ckpt_name)}"
        baseckpt_name = Path(f"{ckpt_name}").stem
        baseckpt_hash = f"Model hash: {calculate_sha256(baseckpt_path)[:10]}, " if save_ckpt_hash == True else ""
        if specified_vae == True:
            basevae_path = folder_paths.get_full_path("vae", vae_name)
            basevae_name = Path(f"{vae_name}").stem
            basevae_hash = f"VAE hash: {calculate_sha256(basevae_path)[:10]}, " if save_ckpt_hash == True else ""
            basevae_metadata = f"{basevae_hash}VAE: {basevae_name}, "
        else:
            basevae_metadata = ""
        
        base_model_metadata = f"Steps: {steps}, Sampler: {sampler_name}{f' {scheduler}' if scheduler != 'normal' else ''}, CFG scale: {cfg_or_flux_neg_scale}, Seed: {base_seed}, Size: {size_metadata}, {baseckpt_hash}Model: {baseckpt_name}, {basevae_metadata}{f'Denoising strength: {img2img_denoise_metadata}, ' if img2img == True else ''}Clip skip: {stop_layer_metadata}, RNG: CPU, "
        
        if swap_dimensions == True:
            return (base_model_metadata, pipe_model, pipe_image_swap)
        else:
            return (base_model_metadata, pipe_model, pipe_image)

class BaseModelParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_model_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "STRING", "STRING", "FLOAT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("Checkpoint", "Tiling", "Stop_Layer", "Positive_l", "Positive_g", "Negative_l", "Negative_g", "Variation", "Seed", "Steps", "Sampler", "Schedular", "Cfg", "Denoise", "Specified_VAE", "VAE")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, base_model_pipe=None):
        ckpt_name, stop_at_clip_layer, positive_l, positive_g, negative_l, negative_g, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, tiling, specified_vae, vae_name = base_model_pipe
        return (ckpt_name, tiling, stop_at_clip_layer, positive_l, positive_g, negative_l, negative_g, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, specified_vae, vae_name)

class BaseImageParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_image_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "STRING", "BOOLEAN")
    RETURN_NAMES = ("Image", "Width", "Height", "Batch_Size", "Image_Resize", "img2img")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, base_image_pipe=None):
        image, width, height, batch_size, image_resize, img2img = base_image_pipe
        return (image, width, height, batch_size, image_resize, img2img)

class BaseModelPipe_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive_conditioning": ("CONDITIONING", {"forceInput": True}),
                "negative_conditioning": ("CONDITIONING", {"forceInput": True}),
                "base_latent": ("LATENT",),
                "base_image": ("IMAGE",),
            },
            "optional": {
                "positive_prompt": ("STRING", {"forceInput": True}),
                "negative_prompt": ("STRING", {"forceInput": True}),
                "variation_prompt": ("STRING", {"forceInput": True}),
                "lora_prompt": ("STRING", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE", "STRING")
    RETURN_NAMES = ("Base_PIPE", "Base_Prompt")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, positive_conditioning=None, negative_conditioning=None, base_latent=None, base_image=None, positive_prompt=None, negative_prompt=None, variation_prompt=None, lora_prompt=None):
        
        positive_prompt = positive_prompt if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f",{variation_prompt}" if variation_prompt !=None and variation_prompt != "" else ""
        lora_prompt = f",{lora_prompt}" if lora_prompt !=None and lora_prompt != "" else ""
        base_prompt = f"{handle_whitespace(positive_prompt)}{handle_whitespace(variation_prompt)}{handle_whitespace(lora_prompt)}\nNegative prompt: {handle_whitespace(negative_prompt)}\n"
        
        base_pipe = (positive_conditioning, negative_conditioning, positive_prompt, negative_prompt, base_latent, base_image, base_prompt)
        
        return (base_pipe, base_prompt)

class BaseModelPipeExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("PIPE_LINE", "CONDITIONING", "CONDITIONING", "STRING", "STRING", "LATENT", "IMAGE", "STRING")
    RETURN_NAMES = ("Base_Pipe", "Positive_Conditioning", "Negative_Conditioning", "Positive_Prompt", "Negative_Prompt", "Base_Latent", "Base_Image", "Base_Prompt")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, base_pipe=None):
        if base_pipe == None:
            Positive_Conditioning = None
            Negative_Conditioning = None
            Positive_Prompt = ""
            Negative_Prompt = ""
            Base_Latent = None
            Base_Image = None
            Base_Prompt = ""
        else:
            Positive_Conditioning, Negative_Conditioning, Positive_Prompt, Negative_Prompt, Base_Latent, Base_Image, Base_Prompt = base_pipe
        return (base_pipe, Positive_Conditioning, Negative_Conditioning, Positive_Prompt, Negative_Prompt, Base_Latent, Base_Image, Base_Prompt)

class BaseModelParametersSD3API_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": ("STRING", {"default": '', "multiline": True}),
                "negative": ("STRING", {"default": '', "multiline": True}),
                "use_input_prompt": ("BOOLEAN", {"default": False},),
                "aspect_ratio": (["1:1", "5:4", "3:2", "16:9", "21:9", "4:5", "2:3", "9:16", "9:21"],),
            },
            "optional": {
                "input_positive": ("STRING", {"forceInput": True}),
                "input_negative": ("STRING", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("POSITIVE", "NEGATIVE", "ASPECT_RATIO", "WIDTH", "HEIGHT")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, positive, negative, use_input_prompt, aspect_ratio, input_positive=None, input_negative=None):
        
        if use_input_prompt == True and input_positive != None and input_negative != None:
            if input_positive != "":
                positive = input_positive
            if input_negative != "":
                negative = input_negative
        
        width, height = get_sd3_resolution(aspect_ratio)
        
        return (positive, negative, aspect_ratio, width, height)

class NoiseInjectionParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "variation_strength": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 1.0, "step": 0.01}),
                "variation_batch": ("INT", {"default": 4, "min": 1, "max": 0xffffffffffffffff}),
                "variation_batch_mode_Inspire": (["incremental", "comfy", "variation str inc:0.01", "variation str inc:0.05"], {"default": "variation str inc:0.05"}),
                "variation_method_Inspire": (["linear", "slerp"], {"default": "slerp"}),
                "img2img_injection_switch_at_Legacy": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "base_steps": ("INT", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE")
    RETURN_NAMES = ("Noise_Injection_MetaData", "Noise_Injection_Pipe")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, base_steps, seed, variation_strength, variation_batch, variation_batch_mode_Inspire, variation_method_Inspire, img2img_injection_switch_at_Legacy):
        
        base_steps = base_steps if base_steps != None else 30
        img2img_injection_1st_step_end = int(base_steps * img2img_injection_switch_at_Legacy)
        img2img_injection_2nd_step_start = img2img_injection_1st_step_end #+ 1
        
        noiseinjection_metadata = f"Noise Injection Strength: {variation_strength}, Noise Injection Seed: {seed}, "
        noiseinjection_pipe = (seed, variation_strength, variation_batch, variation_batch_mode_Inspire, variation_method_Inspire, img2img_injection_1st_step_end, img2img_injection_2nd_step_start)
        
        return (noiseinjection_metadata, noiseinjection_pipe)

class NoiseInjectionPipeExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "noise_injection_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("INT", "FLOAT", "INT", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("variation_seed", "variation_strength", "variation_batch", "variation_batch_mode", "variation_method", "img2img_injection_1st_step_end", "img2img_injection_2nd_step_start")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, noise_injection_pipe=None):
        if noise_injection_pipe == None:
            seed = 0
            variation_strength = 0.05
            variation_batch = 4
            variation_batch_mode = "variation str inc:0.05"
            variation_method = "slerp"
            img2img_injection_1st_step_end = 0.2
            img2img_injection_2nd_step_start = 0.2
        else:
            seed, variation_strength, variation_batch, variation_batch_mode, variation_method, img2img_injection_1st_step_end, img2img_injection_2nd_step_start = noise_injection_pipe
        return (seed, variation_strength, variation_batch, variation_batch_mode, variation_method, img2img_injection_1st_step_end, img2img_injection_2nd_step_start)

class RefineModelParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_ckpt_name": ("STRING", {"forceInput": True}),
                "base_steps": ("INT", {"forceInput": True}),
                "refine_ckpt_name": ("STRING", {"forceInput": True}),
                "refine_1_seed": ("INT", {"forceInput": True}),
                "refine_2_seed": ("INT", {"forceInput": True}),
                #
                "batch_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "refine_length": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                "Enable_refine_ckpt": ("BOOLEAN", {"default": False}),
                #
                "Enable_refine_1": ("BOOLEAN", {"default": False}),
                "Enable_refine_1_seed": ("BOOLEAN", {"default": True}),
                "Enable_refine_1_prompt": ("BOOLEAN", {"default": False}),
                "refine_1_positive": ("STRING", {"default": '', "multiline": True}),
                "refine_1_negative": ("STRING", {"default": '', "multiline": True}),
                "refine_1_variation": ("STRING", {"default": '', "multiline": True}),
                "refine_1_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "refine_1_switch_at": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "Enable_IPAdaptor_1": ("BOOLEAN", {"default": False}),
                #
                "Enable_refine_2": ("BOOLEAN", {"default": False}),
                "Enable_refine_2_seed": ("BOOLEAN", {"default": True}),
                "Enable_refine_2_prompt": ("BOOLEAN", {"default": False}),
                "refine_2_positive": ("STRING", {"default": '', "multiline": True}),
                "refine_2_negative": ("STRING", {"default": '', "multiline": True}),
                "refine_2_variation": ("STRING", {"default": '', "multiline": True}),
                "refine_2_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "refine_2_denoise": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "Enable_IPAdaptor_2": ("BOOLEAN", {"default": False}),
                #
                "save_ckpt_hash": ("BOOLEAN", {"default": False},),
            },
        }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE", "PIPE_LINE", "INT", "INT")
    RETURN_NAMES = ("Refine_MetaData", "refine_1_pipe", "refine_2_pipe", "Batch_Index", "Refine_Length")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, batch_index, refine_length,
                        Enable_refine_1, Enable_refine_1_seed, refine_1_seed, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_cfg, refine_1_switch_at, Enable_IPAdaptor_1, 
                        Enable_refine_2, Enable_refine_2_seed, refine_2_seed, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, refine_2_cfg, refine_2_denoise, Enable_IPAdaptor_2,
                        Enable_refine_ckpt, refine_ckpt_name, save_ckpt_hash, base_ckpt_name=None, base_steps=None):
        
        base_steps = base_steps if base_steps != None else 30
        base_step_end = int(base_steps * refine_1_switch_at)
        refine_step_start = base_step_end #+ 1
        
        if base_ckpt_name != None:
            baseckpt_path = f"{folder_paths.get_full_path('checkpoints', base_ckpt_name)}"
            baseckpt_name = Path(f"{base_ckpt_name}").stem
            baseckpt_hash = f" [{calculate_sha256(baseckpt_path)[:10]}]" if save_ckpt_hash == True else ""
        
        refine_2_denoise_metadata = f"{refine_2_denoise:.3f}"
        refineckpt_path = f"{folder_paths.get_full_path('checkpoints', refine_ckpt_name)}"
        refineckpt_name = Path(f"{refine_ckpt_name}").stem
        refineckpt_hash = f" [{calculate_sha256(refineckpt_path)[:10]}]" if save_ckpt_hash == True else ""
        refineckpt_metadata = f"Refiner: {refineckpt_name}{refineckpt_hash}" if Enable_refine_ckpt == True or base_ckpt_name == None else f"Refiner: {baseckpt_name}{baseckpt_hash}"
        refineprompt_metadata = f"Refine prompt: \"{handle_whitespace(refine_1_positive)},{handle_whitespace(refine_1_variation)}\", Refine negative prompt: \"{handle_whitespace(refine_1_negative)}\", " if Enable_refine_1_prompt == True else ""
        refineprompt_metadata_2 = f"Refine 2 prompt: \"{handle_whitespace(refine_2_positive)},{handle_whitespace(refine_2_variation)}\", Refine negative prompt: \"{handle_whitespace(refine_2_negative)}\", " if Enable_refine_2_prompt == True else ""
        refine_1_metadata = f"{refineckpt_metadata}, Refiner switch at: {refine_1_switch_at}, Base End: {base_step_end}, Refiner start: {refine_step_start}, Refine CFG scale: {refine_1_cfg}, {f'Refiner Seed 1: {refine_1_seed}, ' if Enable_refine_1_seed == True else ''}{refineprompt_metadata}{f'IPAdapter 1: Enabled, ' if Enable_IPAdaptor_1 == True else ''}" if Enable_refine_1 == True else ""
        refine_2_metadata = f"Refine 2 CFG scale: {refine_2_cfg}, Refine Denoising strength: {refine_2_denoise_metadata}, {f'Refiner Seed 2: {refine_2_seed}, ' if Enable_refine_2_seed == True else ''}{refineprompt_metadata_2}{f'IPAdapter 2: Enabled, ' if Enable_IPAdaptor_2 == True else ''}" if Enable_refine_2 == True else ""
        refine_metadata = f"{refine_1_metadata}{refine_2_metadata}"
        
        refine_1_pipe = (Enable_refine_1, Enable_refine_1_seed, refine_1_seed, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_cfg, base_step_end, refine_step_start, Enable_IPAdaptor_1)
        refine_2_pipe = (Enable_refine_2, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, Enable_refine_2_seed, refine_2_seed, refine_2_cfg, refine_2_denoise, Enable_IPAdaptor_2)
        
        return (refine_metadata, refine_1_pipe, refine_2_pipe, batch_index, refine_length)

class Refine1ParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"refine_1_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "INT", "INT", "BOOLEAN", "STRING", "BOOLEAN", "STRING", "STRING", "STRING", "INT", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("Enable_refine_1", "refine_1_cfg", "base_step_end", "refine_step_start", "Enable_Refine_Ckpt", "Refine_Ckpt_Name", "Enable_refine_1_Prompt", "refine_1_positive", "refine_1_negative", "refine_1_variation", "refine_1_seed", "Enable_refine_1_seed", "Enable_IPAdaptor_1")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, refine_1_pipe):
        Enable_refine_1, Enable_refine_1_seed, refine_1_seed, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_cfg, base_step_end, refine_step_start, Enable_IPAdaptor_1 = refine_1_pipe
        return (Enable_refine_1, refine_1_cfg, base_step_end, refine_step_start, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_seed, Enable_refine_1_seed, Enable_IPAdaptor_1)

class Refine2ParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"refine_2_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "FLOAT", "BOOLEAN", "STRING", "STRING", "STRING", "INT", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("Enable_refine_2", "refine_2_cfg", "refine_2_denoise", "Enable_refine_2_prompt", "refine_2_positive", "refine_2_negative", "refine_2_variation", "refine_2_seed", "Enable_refine_2_seed", "Enable_IPAdaptor_2")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, refine_2_pipe):
        Enable_refine_2, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, Enable_refine_2_seed, refine_2_seed, refine_2_cfg, refine_2_denoise, Enable_IPAdaptor_2 = refine_2_pipe
        return (Enable_refine_2, refine_2_cfg, refine_2_denoise, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, refine_2_seed, Enable_refine_2_seed, Enable_IPAdaptor_2)

class RefinePipe_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            "positive_conditioning": ("CONDITIONING", {"forceInput": True}),
            "negative_conditioning": ("CONDITIONING", {"forceInput": True}),
            "image_latent": ("LATENT",),
            "base_latent": ("LATENT",),
            "base_image": ("IMAGE",),
            },
            "optional": {
                "positive_prompt": ("STRING", {"forceInput": True}),
                "negative_prompt": ("STRING", {"forceInput": True}),
                "variation_prompt": ("STRING", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE",)
    RETURN_NAMES = ("Refine_PIPE",)
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, positive_conditioning=None, negative_conditioning=None, image_latent=None, base_latent=None, base_image=None, positive_prompt=None, negative_prompt=None, variation_prompt=None):
        
        positive_prompt = f"{positive_prompt}," if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f"{variation_prompt}," if variation_prompt !=None and variation_prompt != "" else ""
        
        refine_pipe = (positive_conditioning, negative_conditioning, image_latent, base_latent, base_image, positive_prompt, negative_prompt, variation_prompt)
        
        return (refine_pipe,)

class RefinePipeExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "refine_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("PIPE_LINE", "CONDITIONING", "CONDITIONING", "LATENT", "LATENT", "IMAGE", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("Refine_Pipe", "Positive_Conditioning", "Negative_Conditioning", "Image_Latent", "Base_Latent", "Base_Image", "Positive_Prompt", "Negative_Prompt", "Variation_Prompt",)
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, refine_pipe=None):
        if refine_pipe == None:
            Positive_Conditioning = None
            Negative_Conditioning = None
            Image_Latent = None
            Base_Latent = None
            Base_Image = None
            Positive_Prompt = ""
            Negative_Prompt = ""
            Variation_Prompt = ""
        else:
            Positive_Conditioning, Negative_Conditioning, Image_Latent, Base_Latent, Base_Image, Positive_Prompt, Negative_Prompt, Variation_Prompt = refine_pipe
        return (refine_pipe, Positive_Conditioning, Negative_Conditioning, Image_Latent, Base_Latent, Base_Image, Positive_Prompt, Negative_Prompt, Variation_Prompt,)

class UpscaleModelParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_ckpt_name": ("STRING", {"forceInput": True}),
                "upscale_ckpt_name": ("STRING", {"forceInput": True}),
                "upscale_seed": ("INT", {"forceInput": True}),
                #
                "batch_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "upscale_length": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                "Enable_Image_Upscale": ("BOOLEAN", {"default": False}),
                "Image_upscale_model_name": (folder_paths.get_filename_list("upscale_models"), {"default": 'Kim2091-4xUltraSharp.pth'}),
                "Image_upscale_method": (['nearest-exact', 'bilinear', 'area', 'bicubic', 'lanczos'],),
                "Image_scale_by": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                #
                "Enable_Latent_Upscale": ("BOOLEAN", {"default": False}),
                "Latent_upscale_method": (['nearest-exact', 'bilinear', 'area', 'bicubic', 'bislerp'],),
                "Latent_scale_by": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                #
                "Enable_upscale_prompt": ("BOOLEAN", {"default": False}),
                "upscale_positive": ("STRING", {"default": '', "multiline": True}),
                "upscale_negative": ("STRING", {"default": '', "multiline": True}),
                "upscale_steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "upscale_sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "upscale_scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "upscale_cfg": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "Enable_upscale_ckpt": ("BOOLEAN", {"default": False}),
                "upscale_denoise": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "Enable_upscale_seed": ("BOOLEAN", {"default": True}),
                #
                "save_ckpt_hash": ("BOOLEAN", {"default": False},),
            },
         }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE", "PIPE_LINE", "PIPE_LINE", "INT", "INT")
    RETURN_NAMES = ("Upscale_MetaData", "Image_Upscale_Pipe", "Latent_Upscale_Pipe", "Upscale_Model_Pipe", "Batch_Index", "Upscale_Length")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, batch_index, upscale_length, Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, Image_scale_by, Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by, 
                  Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, Enable_upscale_ckpt, upscale_ckpt_name, upscale_denoise, Enable_upscale_seed, upscale_seed, save_ckpt_hash, 
                  base_ckpt_name=None):
        
        if Enable_Image_Upscale == True:
            upscalemodelfactor = upscalemodels.get(f"{Image_upscale_model_name}")
            if upscalemodelfactor != None:
                image_rescale_by = Image_scale_by / upscalemodelfactor
            else:
                image_rescale_by = Image_scale_by / 4.0
                print(f"\033[92mNo scale amount data for {Image_upscale_model_name}, please update upscalemodels list in jake_upgrade.py\033[0m")
        else:
            Image_scale_by = 1.0
            image_rescale_by = 1.0
        
        if Enable_Latent_Upscale == False:
            Latent_scale_by = 1.0
        
        if Enable_Image_Upscale == True and Enable_Latent_Upscale == True:
            upscaleamount_metadata = f"Hires upscale image: {Image_scale_by}, Hires upscale latent: {Latent_scale_by}, "
        else:
            upscaleamount_metadata = ""
        
        scale_amount = Image_scale_by * Latent_scale_by
        
        pipe_imageupscale = (Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, image_rescale_by)
        pipe_latentupscale = (Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by)
        pipe_upscalemodel = (Enable_upscale_ckpt, upscale_ckpt_name, Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, upscale_denoise, Enable_upscale_seed)
        
        if base_ckpt_name != None:
            baseckpt_path = f"{folder_paths.get_full_path('checkpoints', base_ckpt_name)}"
            baseckpt_name = Path(f"{base_ckpt_name}").stem
            baseckpt_hash = f" [{calculate_sha256(baseckpt_path)[:10]}]" if save_ckpt_hash == True else ""
        
        upscale_denoise_metadata = f"{upscale_denoise:.3f}"
        upscaleckpt_path = f"{folder_paths.get_full_path('checkpoints', upscale_ckpt_name)}"
        upscaleckpt_name = Path(f"{upscale_ckpt_name}").stem
        upscaleckpt_hash = f" [{calculate_sha256(upscaleckpt_path)[:10]}]" if save_ckpt_hash == True else ""
        upscaleckpt_metadata = f"Hires checkpoint: {upscaleckpt_name}{upscaleckpt_hash}" if Enable_upscale_ckpt == True or base_ckpt_name == None else f"Hires checkpoint: {baseckpt_name}{baseckpt_hash}"
        upscaleprompt_metadata = f"Hires prompt: \"{handle_whitespace(upscale_positive)}\", Hires negative prompt: \"{handle_whitespace(upscale_negative)}\", " if Enable_upscale_prompt == True else ""
        upscaleseed_metadata = f"Upscale Seed: {upscale_seed}, " if Enable_upscale_seed == True else ""
        imageupscalemodel_name = Path(f"{Image_upscale_model_name}").stem
        imageupscalemodel_metadata = f"Hires upscaler: {imageupscalemodel_name} ({Image_upscale_method}), " if Enable_Image_Upscale == True else ""
        latentupscalemodel_metadata = f"Hires upscaler: Latent ({Latent_upscale_method}), " if Enable_Latent_Upscale == True else ""
       #Auto1111 shares img2img Denoising strength with upscale_denoise
       #upscale_metadata = f"{upscaleckpt_metadata}, Hires sampler: {upscale_sampler_name}{f'_{upscale_scheduler}' if upscale_scheduler != 'normal' else ''}, {upscaleprompt_metadata}Hires upscale: {scale_amount}, {upscaleamount_metadata}Hires steps: {upscale_steps}, Hires CFG scale: {upscale_cfg}, Hires Denoising strength: {upscale_denoise_metadata}, upscaleseed_metadata{imageupscalemodel_metadata}{latentupscalemodel_metadata}" if Enable_Image_Upscale == True or Enable_Latent_Upscale == True else ""
        upscale_metadata = f"{upscaleckpt_metadata}, Hires sampler: {upscale_sampler_name}{f'_{upscale_scheduler}' if upscale_scheduler != 'normal' else ''}, {upscaleprompt_metadata}Hires upscale: {scale_amount}, {upscaleamount_metadata}Hires steps: {upscale_steps}, Hires CFG scale: {upscale_cfg}, Denoising strength: {upscale_denoise_metadata}, {upscaleseed_metadata}{imageupscalemodel_metadata}{latentupscalemodel_metadata}" if Enable_Image_Upscale == True or Enable_Latent_Upscale == True else ""
        
        return (upscale_metadata, pipe_imageupscale, pipe_latentupscale, pipe_upscalemodel, batch_index, upscale_length)
        
class ImageUpscaleParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"image_upscale_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("Enable_Image_Upscale", "Image_upscale_model_name", "Image_upscale_method", "Image_rescale_by")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, image_upscale_pipe):
        Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, image_rescale_by = image_upscale_pipe
        return (Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, image_rescale_by)

class LatentUpscaleParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"latent_upscale_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "FLOAT")
    RETURN_NAMES = ("Enable_Latent_Upscale", "Latent_upscale_method", "Latent_scale_by")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, latent_upscale_pipe):
        Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by = latent_upscale_pipe
        return (Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by)

class UpscaleModelParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"upscale_model_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "BOOLEAN", "STRING", "STRING", "INT", "STRING", "STRING", "FLOAT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("Enable_upscale_ckpt", "upscale_ckpt_name", "Enable_upscale_prompt", "upscale_positive", "upscale_negative", "upscale_steps", "upscale_sampler_name", "upscale_scheduler", "upscale_cfg", "upscale_denoise", "Enable_upscale_seed")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, upscale_model_pipe):
        Enable_upscale_ckpt, upscale_ckpt_name, Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, upscale_denoise, Enable_upscale_seed = upscale_model_pipe
        return (Enable_upscale_ckpt, upscale_ckpt_name, Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, upscale_denoise, Enable_upscale_seed)

class DetailerParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "detailer_length": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                "refiner_on_ratio": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
         }
    
    RETURN_TYPES = ("INT", "INT", "FLOAT")
    RETURN_NAMES = ("Batch_Index", "Detailer_Length", "Refiner_On_Ratio")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, batch_index, detailer_length, refiner_on_ratio):
        
        return (batch_index, detailer_length, refiner_on_ratio)

class PipeEnd_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                    "any_in": (any_type,),
                    }
                }

    FUNCTION = "doit"

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    CATEGORY = icons.get("JK/Pipe")
    OUTPUT_NODE = True

    def doit(self, any_in=None):
        return ()

class MetadataPipe_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_model_prompt": ("STRING", {"forceInput": True}),
                "base_model_metadata": ("STRING", {"forceInput": True}),
                "lora_metadata": ("STRING", {"forceInput": True}),
                "positive_embedding_metadata": ("STRING", {"forceInput": True}),
                "negative_embedding_metadata": ("STRING", {"forceInput": True}),
                "controlnet_metadata": ("STRING", {"forceInput": True}),
                "refine_metadata": ("STRING", {"forceInput": True}),
                "upscale_metadata": ("STRING", {"forceInput": True}),
                "noise_injection_metadata": ("STRING", {"forceInput": True}),
                "image_name": ("STRING", {"forceInput": True}),
                "path_name": ("STRING", {"forceInput": True}),
                "counter": ("INT", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("META_PIPE",)
    RETURN_NAMES = ("META_PIPE",)
    FUNCTION = "doit"
    CATEGORY = icons.get("JK/Pipe")
    OUTPUT_NODE = True

    def doit(self, base_model_prompt=None, base_model_metadata=None, lora_metadata=None, positive_embedding_metadata=None, negative_embedding_metadata=None, 
                   controlnet_metadata=None, refine_metadata=None, upscale_metadata=None, noise_injection_metadata=None,
                   image_name=None, path_name=None, counter=0):
        
        meta_pipe = (base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata,
                    controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata,
                    image_name, path_name, counter)
        
        return (meta_pipe,)

class MetadataPipeExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "meta_pipe": ("META_PIPE",)
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING","STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("BASE_MODEL_PROMPT", "BASE_MODEL_METADATA", "LORA_METADATA", "POSITIVE_EMBEDDING_METADATA", "NEGATIVE_EMBEDDING_METADATA",
                    "CONTROLNET_METADATA", "REFINE_METADATA", "UPSCALE_METADATA", "NOISE_INJECTION_METADATA",
                    "IMAGE_NAME", "PATH_NAME", "COUNTER")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, meta_pipe):

        base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata, controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata, image_name, path_name, counter = meta_pipe
        
        return (base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata,
                    controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata,
                    image_name, path_name, counter)

#---------------------------------------------------------------------------------------------------------------------#
# Image Nodes
#---------------------------------------------------------------------------------------------------------------------#
class ImageSaveWithMetadata_JK:
    def __init__(self):
        self.output_dir = folder_paths.output_directory

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", ),
            },
            "optional": {
                "lora_prompt": ("STRING", {"forceInput": True}),
                "positive_embedding_prompt": ("STRING", {"forceInput": True}),
                "negative_embedding_prompt": ("STRING", {"forceInput": True}),
                "lora_metadata": ("STRING", {"forceInput": True}),
                "positive_embedding_metadata": ("STRING", {"forceInput": True}),
                "negative_embedding_metadata": ("STRING", {"forceInput": True}),
                "controlnet_metadata": ("STRING", {"forceInput": True}),
                #
                "positive": ("STRING", {"default": '', "multiline": True}),
                "negative": ("STRING", {"default": '', "multiline": True}),
                "variation": ("STRING", {"default": '', "multiline": True}),
                "seed_value": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "width": ("INT", {"default": 512, "min": 1, "max": MAX_RESOLUTION, "step": 8}),
                "height": ("INT", {"default": 512, "min": 1, "max": MAX_RESOLUTION, "step": 8}),
                #
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
                "specified_vae": ("BOOLEAN", {"default": True},),
                "vae_name": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"],),
                "stop_at_clip_layer": ("INT", {"default": -1, "min": -24, "max": -1}),
                "img2img": ("BOOLEAN", {"default": False},),
                "img2img_denoise": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                #
                "Enable_Noise_Injection": ("BOOLEAN", {"default": False}),
                "Noise_Injection_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "noisy_latent_strength": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 1.0, "step": 0.01}),
                "img2img_injection_switch_at": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                #
                "Enable_refine_ckpt": ("BOOLEAN", {"default": False}),
                "refine_ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
                "Enable_refine_1": ("BOOLEAN", {"default": False}),
                "Enable_refine_1_seed": ("BOOLEAN", {"default": True}),
                "refine_1_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "Enable_refine_1_prompt": ("BOOLEAN", {"default": False}),
                "refine_1_positive": ("STRING", {"default": '', "multiline": True}),
                "refine_1_negative": ("STRING", {"default": '', "multiline": True}),
                "refine_1_variation": ("STRING", {"default": '', "multiline": True}),
                "refine_1_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "refine_1_switch_at": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "Enable_IPAdaptor_1": ("BOOLEAN", {"default": False}),
                "Enable_refine_2": ("BOOLEAN", {"default": False}),
                "Enable_refine_2_prompt": ("BOOLEAN", {"default": False}),
                "refine_2_positive": ("STRING", {"default": '', "multiline": True}),
                "refine_2_negative": ("STRING", {"default": '', "multiline": True}),
                "refine_2_variation": ("STRING", {"default": '', "multiline": True}),
                "Enable_refine_2_seed": ("BOOLEAN", {"default": True}),
                "refine_2_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "refine_2_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "refine_2_denoise": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "Enable_IPAdaptor_2": ("BOOLEAN", {"default": False}),
                #
                "Enable_Image_Upscale": ("BOOLEAN", {"default": False}),
                "Image_upscale_model_name": (folder_paths.get_filename_list("upscale_models"),),
                "Image_upscale_method": (['nearest-exact', 'bilinear', 'area', 'bicubic', 'lanczos'],),
                "Image_scale_by": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "Enable_Latent_Upscale": ("BOOLEAN", {"default": False}),
                "Latent_upscale_method": (['nearest-exact', 'bilinear', 'area', 'bicubic', 'bislerp'],),
                "Latent_scale_by": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                #
                "Enable_upscale_prompt": ("BOOLEAN", {"default": False}),
                "upscale_positive": ("STRING", {"default": '', "multiline": True}),
                "upscale_negative": ("STRING", {"default": '', "multiline": True}),
                "upscale_steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "upscale_sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "upscale_scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "upscale_cfg": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.05}),
                "Enable_upscale_ckpt": ("BOOLEAN", {"default": False}),
                "upscale_ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
                "upscale_denoise": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "upscale_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                #
                "other_prompt": ("STRING", {"default": '', "multiline": True}),
                "save_hash": ("BOOLEAN", {"default": False},),
                #
                "image_name": ("STRING", {"default": f'_v%counter_%seed_%time', "multiline": False}),
                "path_name": ("STRING", {"default": f'%date', "multiline": False}),
                "counter": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff }),
                "extension": (['png', 'jpeg', 'webp'],),
                "lossless_webp": ("BOOLEAN", {"default": True}),
                "quality_jpeg_or_webp": ("INT", {"default": 100, "min": 1, "max": 100}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("METADATA",)
    FUNCTION = "save_files"

    OUTPUT_NODE = True

    CATEGORY = icons.get("JK/Image")

    def save_files(self, images, positive, negative, variation, seed_value, width, height, steps, sampler_name, scheduler, cfg, ckpt_name, specified_vae, vae_name, stop_at_clip_layer, img2img, img2img_denoise, 
                   Enable_Noise_Injection, Noise_Injection_seed, noisy_latent_strength, img2img_injection_switch_at, 
                   Enable_refine_1, Enable_refine_1_seed, refine_1_seed, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_cfg, refine_1_switch_at, Enable_IPAdaptor_1, 
                   Enable_refine_2, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, Enable_refine_2_seed, refine_2_seed, refine_2_cfg, refine_2_denoise, Enable_IPAdaptor_2, 
                   Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, Image_scale_by, Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by,
                   Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, Enable_upscale_ckpt, upscale_ckpt_name, upscale_denoise, upscale_seed,
                   other_prompt, save_hash, image_name, path_name, counter, extension, lossless_webp, quality_jpeg_or_webp, 
                   lora_prompt=None, positive_embedding_prompt=None, negative_embedding_prompt=None, lora_metadata=None, positive_embedding_metadata=None, negative_embedding_metadata=None, controlnet_metadata=None, prompt=None, extra_pnginfo=None):
        
        filename = make_filename(image_name, seed_value, ckpt_name, counter)
        path = make_pathname(path_name, seed_value, ckpt_name, counter)
        #
        variation = f",{variation}" if variation != "" else ""
        lora_prompt = f",{lora_prompt}" if lora_prompt != None else ""
        lora_metadata = f"Lora hashes: \"{lora_metadata}\", " if lora_metadata != None else ""
        positive_embedding_prompt = f",{positive_embedding_prompt}" if positive_embedding_prompt != None else ""
        negative_embedding_prompt = f",{negative_embedding_prompt}" if negative_embedding_prompt != None else ""
        if positive_embedding_metadata != None and negative_embedding_metadata != None:
            embedding_metadata = f"TI hashes: \"{positive_embedding_metadata}, {negative_embedding_metadata}\", "
        elif positive_embedding_metadata == None and negative_embedding_metadata!= None:
            embedding_metadata = f"TI hashes: \"{negative_embedding_metadata}\", "
        else:
            embedding_metadata = f"TI hashes: \"{positive_embedding_metadata}\", "
        #
        controlnet_metadata = controlnet_metadata if controlnet_metadata!= None else ""
        stop_at_clip_layer = - stop_at_clip_layer
        img2img_denoise_metadata = f"{img2img_denoise:.3f}"
        refine_2_denoise_metadata = f"{refine_2_denoise:.3f}"
        upscale_denoise_metadata = f"{upscale_denoise:.3f}"
        #
        baseckpt_path = f"{folder_paths.get_full_path('checkpoints', ckpt_name)}"
        baseckpt_name = Path(f"{ckpt_name}").stem
        baseckpt_hash = f"Model hash: {calculate_sha256(baseckpt_path)[:10]}, " if save_hash == True else ""
        baseckpt_hash_2 = f" [{calculate_sha256(baseckpt_path)[:10]}]" if save_hash == True else ""
        if specified_vae == True:
            basevae_path = folder_paths.get_full_path("vae", vae_name)
            basevae_name = Path(f"{vae_name}").stem
            basevae_hash = calculate_sha256(basevae_path)[:10]
            basevae_metadata = f"VAE hash: {basevae_hash}, VAE: {basevae_name}, " if save_hash == True else f"VAE: {basevae_name}, "
        else:
            basevae_metadata = ""
        base_metadata = f"{handle_whitespace(positive)}{handle_whitespace(variation)}{handle_whitespace(positive_embedding_prompt)}{handle_whitespace(lora_prompt)}\nNegative prompt: {handle_whitespace(negative)}{handle_whitespace(negative_embedding_prompt)}\nSteps: {steps}, Sampler: {sampler_name}{f' {scheduler}' if scheduler != 'normal' else ''}, CFG scale: {cfg}, Seed: {seed_value}, Size: {width}x{height}, {baseckpt_hash}Model: {baseckpt_name}, {basevae_metadata}{f'Denoising strength: {img2img_denoise_metadata}, ' if img2img == True else ''}Clip skip: {stop_at_clip_layer}, RNG: CPU, "
        #
        noiseinjection_metadata = f"Noise Injection Strength: {noisy_latent_strength}, Noise Injection Seed: {Noise_Injection_seed}, " if img2img == False else f"img2img Noise Injection switch at: {img2img_injection_switch_at}, "
        noiseinjection_metadata = noiseinjection_metadata if Enable_Noise_Injection == True else ""
        #
        base_step_end = int(steps * refine_1_switch_at)
        refine_step_start = base_step_end #+ 1
        refineckpt_path = f"{folder_paths.get_full_path('checkpoints', refine_ckpt_name)}"
        refineckpt_name = Path(f"{refine_ckpt_name}").stem
        refineckpt_hash = f" [{calculate_sha256(refineckpt_path)[:10]}]" if save_hash == True else ""
        refineckpt_metadata = f"Refiner: {refineckpt_name}{refineckpt_hash}" if Enable_refine_ckpt == True else f"Refiner: {baseckpt_name}{baseckpt_hash_2}"
        refineprompt_metadata = f"Refine prompt: \"{handle_whitespace(refine_1_positive)},{handle_whitespace(refine_1_variation)}\", Refine negative prompt: \"{handle_whitespace(refine_1_negative)}\", " if Enable_refine_1_prompt == True else ""
        refineprompt_metadata_2 = f"Refine 2 prompt: \"{handle_whitespace(refine_2_positive)},{handle_whitespace(refine_2_variation)}\", Refine 2 negative prompt: \"{handle_whitespace(refine_2_negative)}\", " if Enable_refine_2_prompt == True else ""
        refine_1_metadata = f"{refineckpt_metadata}, Refiner switch at: {refine_1_switch_at}, Base End: {base_step_end}, Refiner start: {refine_step_start}, Refine CFG scale: {refine_1_cfg}, {f'Refiner Seed 1: {refine_1_seed}, ' if Enable_refine_1_seed == True else ''}{refineprompt_metadata}{f'IPAdapter 1: Enabled, ' if Enable_IPAdaptor_1 == True else ''}" if Enable_refine_1 == True else ""
        refine_2_metadata = f"Refine 2 CFG scale: {refine_2_cfg}, Refine Denoising strength: {refine_2_denoise_metadata}, {f'Refiner Seed 2: {refine_2_seed}, ' if Enable_refine_2_seed == True else ''}{refineprompt_metadata_2}{f'IPAdapter 2: Enabled, ' if Enable_IPAdaptor_2 == True else ''}" if Enable_refine_2 == True else ""
        refine_metadata = f"{refine_1_metadata}{refine_2_metadata}"
        #
        upscaleckpt_path = f"{folder_paths.get_full_path('checkpoints', upscale_ckpt_name)}"
        upscaleckpt_name = Path(f"{upscale_ckpt_name}").stem
        upscaleckpt_hash = f" [{calculate_sha256(upscaleckpt_path)[:10]}]" if save_hash == True else ""
        upscaleckpt_metadata = f"Hires checkpoint: {upscaleckpt_name}{upscaleckpt_hash}" if Enable_upscale_ckpt == True else f"Hires checkpoint: {baseckpt_name}{baseckpt_hash_2}"
        upscaleprompt_metadata = f"Hires prompt: \"{handle_whitespace(upscale_positive)}\", Hires negative prompt: \"{handle_whitespace(upscale_negative)}\", " if Enable_upscale_prompt == True else ""
        upscaleseed_metadata = f"Upscale Seed: {upscale_seed}, "
        #
        imageupscalemodel_name = Path(f"{Image_upscale_model_name}").stem
        imageupscalemodel_metadata = f"Hires upscaler: {imageupscalemodel_name} ({Image_upscale_method}), " if Enable_Image_Upscale == True else ""
        latentupscalemodel_metadata = f"Hires upscaler: Latent ({Latent_upscale_method}), " if Enable_Latent_Upscale == True else ""
        if Enable_Image_Upscale == True:
            '''
            upscalemodelfactor = upscalemodels.get(f"{Image_upscale_model_name}")
            if upscalemodelfactor != None:
                image_rescale_by = Image_scale_by / upscalemodelfactor
            else:
                image_rescale_by = Image_scale_by / 4.0
                print(f"\033[92mNo scale amount data for {Image_upscale_model_name}, please update upscalemodels list in jake_upgrade.py\033[0m")
            '''
        else:
            Image_scale_by = 1.0
            #image_rescale_by = 1.0
        if Enable_Latent_Upscale == False:
            Latent_scale_by = 1.0
        scale_amount = Image_scale_by * Latent_scale_by
        if Enable_Image_Upscale == True and Enable_Latent_Upscale == True:
            upscaleamount_metadata = f"Hires upscale image: {Image_scale_by}, Hires upscale latent: {Latent_scale_by}, "
        else:
            upscaleamount_metadata = ""
       #Auto1111 shares img2img Denoising strength with upscale_denoise
       #upscale_metadata = f"{upscaleckpt_metadata}, Hires sampler: {upscale_sampler_name}{f'_{upscale_scheduler}' if upscale_scheduler != 'normal' else ''}, {upscaleprompt_metadata}Hires upscale: {scale_amount}, {upscaleamount_metadata}Hires steps: {upscale_steps}, Hires CFG scale: {upscale_cfg}, Hires Denoising strength: {upscale_denoise_metadata}, {upscaleseed_metadata}{imageupscalemodel_metadata}{latentupscalemodel_metadata}" if Enable_Image_Upscale == True or Enable_Latent_Upscale == True else ""
        upscale_metadata = f"{upscaleckpt_metadata}, Hires sampler: {upscale_sampler_name}{f'_{upscale_scheduler}' if upscale_scheduler != 'normal' else ''}, {upscaleprompt_metadata}Hires upscale: {scale_amount}, {upscaleamount_metadata}Hires steps: {upscale_steps}, Hires CFG scale: {upscale_cfg}, Denoising strength: {upscale_denoise_metadata}, {upscaleseed_metadata}{imageupscalemodel_metadata}{latentupscalemodel_metadata}" if Enable_Image_Upscale == True or Enable_Latent_Upscale == True else ""
        #
        other_metadata = f"{handle_whitespace(other_prompt)}, " if other_prompt !="" else ""
        comment = f"{base_metadata}{upscale_metadata}{controlnet_metadata}{lora_metadata}{embedding_metadata}{refine_metadata}{noiseinjection_metadata}{other_metadata}Version: ComfyUI"
        output_path = os.path.join(self.output_dir, path)

        if output_path.strip() != '':
            if not os.path.exists(output_path.strip()):
                print(f'The path `{output_path.strip()}` specified doesn\'t exist! Creating directory.')
                os.makedirs(output_path, exist_ok=True)    

        filenames = self.save_images(images, output_path, filename, comment, extension, quality_jpeg_or_webp, lossless_webp, prompt, extra_pnginfo)

        subfolder = os.path.normpath(path)
        return {"ui": {"images": map(lambda filename: {"filename": filename, "subfolder": subfolder if subfolder != '.' else '', "type": 'output'}, filenames)}, "result": (comment,)}

    def save_images(self, images, output_path, filename_prefix, comment, extension, quality_jpeg_or_webp, lossless_webp, prompt=None, extra_pnginfo=None) -> list[str]:
        img_count = 1
        paths = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(numpy.clip(i, 0, 255).astype(numpy.uint8))
            if images.size()[0] > 1:
                filename_prefix += "_{:02d}".format(img_count)

            if extension == 'png':
                metadata = PngInfo()
                metadata.add_text("parameters", comment)

                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

                filename = f"{filename_prefix}.png"
                img.save(os.path.join(output_path, filename), pnginfo=metadata, optimize=True)
            else:
                filename = f"{filename_prefix}.{extension}"
                file = os.path.join(output_path, filename)
                img.save(file, optimize=True, quality=quality_jpeg_or_webp, lossless=lossless_webp)
                exif_bytes = piexif.dump({
                    "Exif": {
                        piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(comment, encoding="unicode")
                    },
                })
                piexif.insert(exif_bytes, file)

            paths.append(filename)
            img_count += 1
        return paths

class ImageSaveWithMetadata_Flow_JK:
    def __init__(self):
        self.output_dir = folder_paths.output_directory

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", ),
            },
            "optional": {
                "base_model_prompt": ("STRING", {"forceInput": True}),
                "base_model_metadata": ("STRING", {"forceInput": True}),
                "lora_metadata": ("STRING", {"forceInput": True}),
                "positive_embedding_metadata": ("STRING", {"forceInput": True}),
                "negative_embedding_metadata": ("STRING", {"forceInput": True}),
                "controlnet_metadata": ("STRING", {"forceInput": True}),
                "refine_metadata": ("STRING", {"forceInput": True}),
                "upscale_metadata": ("STRING", {"forceInput": True}),
                "noise_injection_metadata": ("STRING", {"forceInput": True}),
                "other_prompt": ("STRING", {"default": '', "multiline": True}),
                #
                "image_name": ("STRING", {"default": f'_v%counter_%seed_%time', "multiline": False}),
                "path_name": ("STRING", {"default": f'%date', "multiline": False}),
                "counter": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff }),
                "extension": (['png', 'jpeg', 'webp'],),
                "lossless_webp": ("BOOLEAN", {"default": True}),
                "quality_jpeg_or_webp": ("INT", {"default": 100, "min": 1, "max": 100}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("METADATA",)
    FUNCTION = "save_files"

    OUTPUT_NODE = True

    CATEGORY = icons.get("JK/Image")

    def save_files(self, images, other_prompt, image_name, path_name, counter, extension, lossless_webp, quality_jpeg_or_webp, 
                   base_model_prompt=None, base_model_metadata=None, lora_metadata=None, positive_embedding_metadata=None, negative_embedding_metadata=None, 
                   controlnet_metadata=None, refine_metadata=None, upscale_metadata=None, noise_injection_metadata=None, prompt=None, extra_pnginfo=None):
        
        if base_model_prompt != None and base_model_prompt != "":
            start_index = base_model_metadata.find("Seed: ") + len("Seed: ")
            end_index = base_model_metadata.find(", Size: ", start_index)
            seed_value = base_model_metadata[start_index:end_index]
            start_index = base_model_metadata.find("Model: ") + len("Model: ")
            end_index = base_model_metadata.find(", VAE hash: ", start_index)
            ckpt_name = base_model_metadata[start_index:end_index]
        else:
            seed_value = "-1"
            ckpt_name = ""
        
        filename = make_filename(image_name, seed_value, ckpt_name, counter)
        path = make_pathname(path_name, seed_value, ckpt_name, counter)
        #
        base_model_prompt = base_model_prompt if base_model_prompt !=None else ""
        base_model_metadata = base_model_metadata if base_model_metadata !=None else ""
        lora_metadata = f"Lora hashes: \"{lora_metadata}\", " if lora_metadata != None and lora_metadata != "" else ""
        if positive_embedding_metadata != None and positive_embedding_metadata != "" and negative_embedding_metadata != None and negative_embedding_metadata != "":
            embedding_metadata = f"TI hashes: \"{positive_embedding_metadata}, {negative_embedding_metadata}\", "
        elif (positive_embedding_metadata == None or positive_embedding_metadata == "") and negative_embedding_metadata != None and negative_embedding_metadata != "":
            embedding_metadata = f"TI hashes: \"{negative_embedding_metadata}\", "
        elif positive_embedding_metadata != None and positive_embedding_metadata != "" and (negative_embedding_metadata == None or negative_embedding_metadata == ""):
            embedding_metadata = f"TI hashes: \"{positive_embedding_metadata}\", "
        else:
            embedding_metadata = ""
        controlnet_metadata = controlnet_metadata if controlnet_metadata != None and controlnet_metadata != "" else ""
        other_metadata = f"{handle_whitespace(other_prompt)}, " if other_prompt !="" else ""
        refine_metadata = refine_metadata if refine_metadata != None else ""
        upscale_metadata = upscale_metadata if upscale_metadata !=None else ""
        noise_injection_metadata = noise_injection_metadata if noise_injection_metadata !=None else ""
        comment = f"{base_model_prompt}{base_model_metadata}{upscale_metadata}{controlnet_metadata}{lora_metadata}{embedding_metadata}{refine_metadata}{noise_injection_metadata}{other_metadata}Version: ComfyUI"
        output_path = os.path.join(self.output_dir, path)

        if output_path.strip() != '':
            if not os.path.exists(output_path.strip()):
                print(f'The path `{output_path.strip()}` specified doesn\'t exist! Creating directory.')
                os.makedirs(output_path, exist_ok=True)    

        filenames = self.save_images(images, output_path, filename, comment, extension, quality_jpeg_or_webp, lossless_webp, prompt, extra_pnginfo)

        subfolder = os.path.normpath(path)
        
        return (comment,)

    def save_images(self, images, output_path, filename_prefix, comment, extension, quality_jpeg_or_webp, lossless_webp, prompt=None, extra_pnginfo=None) -> list[str]:
        img_count = 1
        paths = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(numpy.clip(i, 0, 255).astype(numpy.uint8))
            if images.size()[0] > 1:
                filename_prefix += "_{:02d}".format(img_count)

            if extension == 'png':
                metadata = PngInfo()
                metadata.add_text("parameters", comment)

                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

                filename = f"{filename_prefix}.png"
                img.save(os.path.join(output_path, filename), pnginfo=metadata, optimize=True)
            else:
                filename = f"{filename_prefix}.{extension}"
                file = os.path.join(output_path, filename)
                img.save(file, optimize=True, quality=quality_jpeg_or_webp, lossless=lossless_webp)
                exif_bytes = piexif.dump({
                    "Exif": {
                        piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(comment, encoding="unicode")
                    },
                })
                piexif.insert(exif_bytes, file)

            paths.append(filename)
            img_count += 1
        return paths

class LoadImageWithMetadata_JK:
    files = []

    @classmethod
    def INPUT_TYPES(s):

        input_dir = folder_paths.get_input_directory()
        LoadImageWithMetadata_JK.files = sorted(
            [
                f
                for f in os.listdir(input_dir)
                if os.path.isfile(os.path.join(input_dir, f))
            ]
        )
        return {
            "required": {
                "image": (LoadImageWithMetadata_JK.files, {"image_upload": True}),
                "load_metadata": ("BOOLEAN", {"default": False},),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("IMAGE", "MASK", "Prompt")

    FUNCTION = "load_image"
    CATEGORY = icons.get("JK/Image")
    OUTPUT_NODE = True

    def load_image(self, image, load_metadata):
        if image in LoadImageWithMetadata_JK.files:
            image_path = folder_paths.get_annotated_filepath(image)
        else:
            image_path = image
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = numpy.array(image).astype(numpy.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        
        if "A" in i.getbands():
            mask = numpy.array(i.getchannel("A")).astype(numpy.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        
        if load_metadata == True:
            file_path = Path(image_path)
            
            with open(file_path, "rb") as f:
                image_data = ImageDataReader(f)
            
            prompt = f"Positive:\n{image_data.positive}\n\nNegative:\n{image_data.negative}\n\nSettings:\n{image_data.setting}"
            
            return {"result": (image, mask, prompt), "ui": {"text": (image_data.positive, image_data.negative, image_data.setting)}, }
        else:
            prompt = ""
            return {"result": (image, mask, prompt),}

    @classmethod
    def IS_CHANGED(s, image, load_metadata):
        image_path = folder_paths.get_annotated_filepath(image)
        with open(Path(image_path), "rb") as f:
            image_data = ImageDataReader(f)
        return image_data.props

    @classmethod
    def VALIDATE_INPUTS(s, image, load_metadata):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        return True

class LoadImageWithAlpha_JK:
    files = []

    @classmethod
    def INPUT_TYPES(s):

        input_dir = folder_paths.get_input_directory()
        LoadImageWithMetadata_JK.files = sorted(
            [
                f
                for f in os.listdir(input_dir)
                if os.path.isfile(os.path.join(input_dir, f))
            ]
        )
        return {
            "required": {
                "image": (LoadImageWithMetadata_JK.files, {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)

    FUNCTION = "load_image"
    CATEGORY = icons.get("JK/Image")
    OUTPUT_NODE = True

    def load_image(self, image):
        if image in LoadImageWithMetadata_JK.files:
            image_path = folder_paths.get_annotated_filepath(image)
        else:
            image_path = image
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        image = numpy.array(image).astype(numpy.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        
        return {"result": (image,),}

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        return True

#---------------------------------------------------------------------------------------------------------------------#
# Image Nodes from 3D Pack
#---------------------------------------------------------------------------------------------------------------------#
def torch_imgs_to_pils(images, masks=None, alpha_min=0.1):
    """
        images (torch): [N, H, W, C] or [H, W, C]
        masks (torch): [N, H, W] or [H, W]
    """
    if len(images.shape) == 3:
        images = images.unsqueeze(0)

    if masks is not None:
        masks = masks.to(dtype=images.dtype, device=images.device)
        
        if len(masks.shape) == 2:
            masks = masks.unsqueeze(0)

        inv_mask_index = masks < alpha_min
        images[inv_mask_index] = 0.
        
        masks = masks.unsqueeze(3)
        images = torch.cat((images, masks), dim=3)
        mode="RGBA"
    else:
        mode="RGB"

    pil_image_list = [Image.fromarray((images[i].detach().cpu().numpy() * 255).astype(numpy.uint8), mode=mode) for i in range(images.shape[0])]

    return pil_image_list

def pils_to_torch_imgs(pils: Union[Image.Image, List[Image.Image]], dtype=torch.float16, device="cuda", force_rgb=True):
    if isinstance(pils, Image.Image):
        pils = [pils]
    
    images = []
    for pil in pils:
        if pil.mode == "RGBA" and force_rgb:
            pil = pil.convert('RGB')

        images.append(TF.to_tensor(pil).permute(1, 2, 0))

    images = torch.stack(images, dim=0).to(dtype=dtype, device=device)

    return images

def pil_split_image(image, rows=None, cols=None):
    """
        inverse function of make_image_grid
    """
    # image is in square
    if rows is None and cols is None:
        # image.size [W, H]
        rows = 1
        cols = image.size[0] // image.size[1]
        assert cols * image.size[1] == image.size[0]
        subimg_size = image.size[1]
    elif rows is None:
        subimg_size = image.size[0] // cols
        rows = image.size[1] // subimg_size
        assert rows * subimg_size == image.size[1]
    elif cols is None:
        subimg_size = image.size[1] // rows
        cols = image.size[0] // subimg_size
        assert cols * subimg_size == image.size[0]
    else:
        subimg_size = image.size[1] // rows
        assert cols * subimg_size == image.size[0]
    subimgs = []
    for i in range(rows):
        for j in range(cols):
            subimg = image.crop((j*subimg_size, i*subimg_size, (j+1)*subimg_size, (i+1)*subimg_size))
            subimgs.append(subimg)
    return subimgs

def pil_make_image_grid(images, rows=None, cols=None):
    if rows is None and cols is None:
        rows = 1
        cols = len(images)
    if rows is None:
        rows = len(images) // cols
        if len(images) % cols != 0:
            rows += 1
    if cols is None:
        cols = len(images) // rows
        if len(images) % rows != 0:
            cols += 1
    total_imgs = rows * cols
    if total_imgs > len(images):
        images += [Image.new(images[0].mode, images[0].size) for _ in range(total_imgs - len(images))]

    w, h = images[0].size
    grid = Image.new(images[0].mode, size=(cols * w, rows * h))

    for i, img in enumerate(images):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid

class MakeImageGrid_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "grid_side": ("BOOLEAN", {"default": True, "label_on": "rows", "label_off": "columns"},),
                "grid_side_num": ("INT", {"default": 1, "min": 1, "max": 8192}),
            },
        }
        
    RETURN_TYPES = (
        "IMAGE",
    )
    RETURN_NAMES = (
        "image_grid",
    )
    
    FUNCTION = "make_image_grid"
    CATEGORY = icons.get("JK/Image")
    
    def make_image_grid(self, images, grid_side_num, grid_side):
        pil_image_list = torch_imgs_to_pils(images)

        if grid_side:
            rows = grid_side_num
            clos = None
        else:
            clos = grid_side_num
            rows = None

        image_grid = pil_make_image_grid(pil_image_list, rows, clos)

        image_grid = TF.to_tensor(image_grid).permute(1, 2, 0).unsqueeze(0)  # [1, H, W, 3]

        return (image_grid,)

class SplitImageGrid_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "grid_side": ("BOOLEAN", {"default": True, "label_on": "rows", "label_off": "columns"},),
                "grid_side_num": ("INT", {"default": 1, "min": 1, "max": 8192}),
            },
        }
        
    RETURN_TYPES = (
        "IMAGE",
    )
    RETURN_NAMES = (
        "images",
    )
    
    FUNCTION = "split_image_grid"
    CATEGORY = icons.get("JK/Image")
    
    def split_image_grid(self, image, grid_side_num, grid_side):
        images = []
        for image_pil in torch_imgs_to_pils(image):

            if grid_side:
                rows = grid_side_num
                clos = None
            else:
                clos = grid_side_num
                rows = None

            image_pils = pil_split_image(image_pil, rows, clos)

            images.append(pils_to_torch_imgs(image_pils, image.dtype, image.device))
            
        images = torch.cat(images, dim=0)
        return (images,)

#---------------------------------------------------------------------------------------------------------------------#
# Image Nodes from Layer Style
#---------------------------------------------------------------------------------------------------------------------#
def image_gray_offset(image:Image, offset:int) -> Image:
    image = image.convert('L')
    width = image.width
    height = image.height
    ret_image = Image.new('L', size=(width, height), color='black')
    for x in range(width):
        for y in range(height):
                pixel = image.getpixel((x, y))
                _pixel = pixel + offset
                if _pixel > 255:
                    _pixel = 255
                if _pixel < 0:
                    _pixel = 0
                ret_image.putpixel((x, y), _pixel)
    return ret_image

def RGB2RGBA(image:Image, mask:Image) -> Image:
    (R, G, B) = image.convert('RGB').split()
    return Image.merge('RGBA', (R, G, B, mask.convert('L')))

def image_channel_merge(channels:tuple, mode = 'RGB' ) -> Image:
    channel1 = channels[0].convert('L')
    channel2 = channels[1].convert('L')
    channel3 = channels[2].convert('L')
    channel4 = Image.new('L', size=channel1.size, color='white')
    if mode == 'RGBA':
        if len(channels) > 3:
            channel4 = channels[3].convert('L')
        ret_image = Image.merge('RGBA',[channel1, channel2, channel3, channel4])
    elif mode == 'RGB':
        ret_image = Image.merge('RGB', [channel1, channel2, channel3])
    elif mode == 'YCbCr':
        ret_image = Image.merge('YCbCr', [channel1, channel2, channel3]).convert('RGB')
    elif mode == 'LAB':
        ret_image = Image.merge('LAB', [channel1, channel2, channel3]).convert('RGB')
    elif mode == 'HSV':
        ret_image = Image.merge('HSV', [channel1, channel2, channel3]).convert('RGB')
    return ret_image

class ImageRemoveAlpha_JK:
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(self):

        return {
            "required": {
                "RGBA_image": ("IMAGE", ),
            }
        }
    
    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("RGB_image", )
    FUNCTION = "image_remove_alpha"
    CATEGORY = icons.get("JK/Image")
    
    def image_remove_alpha(self, RGBA_image):

        ret_images = []

        for index, img in enumerate(RGBA_image):
        
            _image = tensor2pil(img)
            ret_images.append(pil2tensor(tensor2pil(img).convert('RGB')))
        
        return (torch.cat(ret_images, dim=0), )

class ColorGrading_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):

        return {
            "required": {
                "image": ("IMAGE", ),
                "brightness": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "contrast": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "saturation": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "R": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
                "G": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
                "B": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "color_grading"
    CATEGORY = icons.get("JK/Image")

    def color_grading(self, image, brightness, contrast, saturation, R, G, B):

        ret_images = []

        for i in image:
            i = torch.unsqueeze(i,0)
            __image = tensor2pil(i)
            ret_image = __image.convert('RGB')
            if brightness != 1:
                brightness_image = ImageEnhance.Brightness(ret_image)
                ret_image = brightness_image.enhance(factor=brightness)
            if contrast != 1:
                contrast_image = ImageEnhance.Contrast(ret_image)
                ret_image = contrast_image.enhance(factor=contrast)
            if saturation != 1:
                color_image = ImageEnhance.Color(ret_image)
                ret_image = color_image.enhance(factor=saturation)
            
            if R != 0 or G != 0 or B != 0:
                _r, _g, _b = ret_image.split()
                if R != 0 :
                    _r = image_gray_offset(_r, R)
                if G != 0 :
                    _g = image_gray_offset(_g, G)
                if B != 0 :
                    _b = image_gray_offset(_b, B)
                ret_image = image_channel_merge((_r, _g, _b), 'RGB')
            
            if __image.mode == 'RGBA':
                ret_image = RGB2RGBA(ret_image, __image.split()[-1])
            ret_images.append(pil2tensor(ret_image))
        
        return (torch.cat(ret_images, dim=0),)

#---------------------------------------------------------------------------------------------------------------------#
# Image Resize from ControlNet AUX
# High Quality Edge Thinning using Pure Python
# Written by Lvmin Zhang
# 2023 April
# Stanford University
#---------------------------------------------------------------------------------------------------------------------#
RESIZE_MODES = ["Just Resize", "Crop and Resize", "Resize and Fill"]

lvmin_kernels_raw = [
    numpy.array([
        [-1, -1, -1],
        [0, 1, 0],
        [1, 1, 1]
    ], dtype=numpy.int32),
    numpy.array([
        [0, -1, -1],
        [1, 1, -1],
        [0, 1, 0]
    ], dtype=numpy.int32)
]

lvmin_kernels = []
lvmin_kernels += [numpy.rot90(x, k=0, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=1, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=2, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=3, axes=(0, 1)) for x in lvmin_kernels_raw]

lvmin_prunings_raw = [
    numpy.array([
        [-1, -1, -1],
        [-1, 1, -1],
        [0, 0, -1]
    ], dtype=numpy.int32),
    numpy.array([
        [-1, -1, -1],
        [-1, 1, -1],
        [-1, 0, 0]
    ], dtype=numpy.int32)
]

lvmin_prunings = []
lvmin_prunings += [numpy.rot90(x, k=0, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=1, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=2, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=3, axes=(0, 1)) for x in lvmin_prunings_raw]


def remove_pattern(x, kernel):
    objects = cv2.morphologyEx(x, cv2.MORPH_HITMISS, kernel)
    objects = numpy.where(objects > 127)
    x[objects] = 0
    return x, objects[0].shape[0] > 0


def thin_one_time(x, kernels):
    y = x
    is_done = True
    for k in kernels:
        y, has_update = remove_pattern(y, k)
        if has_update:
            is_done = False
    return y, is_done


def lvmin_thin(x, prunings=True):
    y = x
    for i in range(32):
        y, is_done = thin_one_time(y, lvmin_kernels)
        if is_done:
            break
    if prunings:
        y, _ = thin_one_time(y, lvmin_prunings)
    return y


def nake_nms(x):
    f1 = numpy.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]], dtype=numpy.uint8)
    f2 = numpy.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=numpy.uint8)
    f3 = numpy.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=numpy.uint8)
    f4 = numpy.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]], dtype=numpy.uint8)
    y = numpy.zeros_like(x)
    for f in [f1, f2, f3, f4]:
        numpy.putmask(y, cv2.dilate(x, kernel=f) == x, x)
    return y

#https://github.com/Mikubill/sd-webui-controlnet/blob/e67e017731aad05796b9615dc6eadce911298ea1/scripts/controlnet.py#L404
def safe_numpy(x):
    # A very safe method to make sure that Apple/Mac works
    y = x

    # below is very boring but do not change these. If you change these Apple or Mac may fail.
    y = y.copy()
    y = numpy.ascontiguousarray(y)
    y = y.copy()
    return y

#https://github.com/Mikubill/sd-webui-controlnet/blob/e67e017731aad05796b9615dc6eadce911298ea1/scripts/utils.py#L140
def get_unique_axis0(data):
    arr = numpy.asanyarray(data)
    idxs = numpy.lexsort(arr.T)
    arr = arr[idxs]
    unique_idxs = numpy.empty(len(arr), dtype=numpy.bool_)
    unique_idxs[:1] = True
    unique_idxs[1:] = numpy.any(arr[:-1, :] != arr[1:, :], axis=-1)
    return arr[unique_idxs]

class HintImageEnchance_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hint_image": ("IMAGE", ),
                "image_gen_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "image_gen_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                #https://github.com/comfyanonymous/ComfyUI/blob/c910b4a01ca58b04e5d4ab4c747680b996ada02b/nodes.py#L854
                "resize_mode": (RESIZE_MODES, {"default": "Just Resize"})
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("IMAGE", "METADATA", "MODE")
    FUNCTION = "execute"

    CATEGORY = "🐉 JK/🛩️ Image"
    def execute(self, hint_image, image_gen_width, image_gen_height, resize_mode):
        outs = []
        for single_hint_image in hint_image:
            np_hint_image = numpy.asarray(single_hint_image * 255., dtype=numpy.uint8)

            if resize_mode == "Just Resize":
                np_hint_image = self.execute_resize(np_hint_image, image_gen_width, image_gen_height)
                METADATA = "Resize Mode: Just Resize"
            elif resize_mode == "Resize and Fill":
                np_hint_image = self.execute_outer_fit(np_hint_image, image_gen_width, image_gen_height)
                METADATA = "Resize Mode: Resize and Fill"
            else:
                np_hint_image = self.execute_inner_fit(np_hint_image, image_gen_width, image_gen_height)
                METADATA = "Resize Mode: Crop and Resize"
            
            outs.append(torch.from_numpy(np_hint_image.astype(numpy.float32) / 255.0))
        
        return (torch.stack(outs, dim=0), METADATA, resize_mode)
    
    def execute_resize(self, detected_map, w, h):
        detected_map = self.high_quality_resize(detected_map, (w, h))
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def execute_outer_fit(self, detected_map, w, h):
        old_h, old_w, _ = detected_map.shape
        old_w = float(old_w)
        old_h = float(old_h)
        k0 = float(h) / old_h
        k1 = float(w) / old_w
        safeint = lambda x: int(numpy.round(x))
        k = min(k0, k1)
        
        borders = numpy.concatenate([detected_map[0, :, :], detected_map[-1, :, :], detected_map[:, 0, :], detected_map[:, -1, :]], axis=0)
        high_quality_border_color = numpy.median(borders, axis=0).astype(detected_map.dtype)
        if len(high_quality_border_color) == 4:
            # Inpaint hijack
            high_quality_border_color[3] = 255
        high_quality_background = numpy.tile(high_quality_border_color[None, None], [h, w, 1])
        detected_map = self.high_quality_resize(detected_map, (safeint(old_w * k), safeint(old_h * k)))
        new_h, new_w, _ = detected_map.shape
        pad_h = max(0, (h - new_h) // 2)
        pad_w = max(0, (w - new_w) // 2)
        high_quality_background[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = detected_map
        detected_map = high_quality_background
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def execute_inner_fit(self, detected_map, w, h):
        old_h, old_w, _ = detected_map.shape
        old_w = float(old_w)
        old_h = float(old_h)
        k0 = float(h) / old_h
        k1 = float(w) / old_w
        safeint = lambda x: int(numpy.round(x))
        k = max(k0, k1)

        detected_map = self.high_quality_resize(detected_map, (safeint(old_w * k), safeint(old_h * k)))
        new_h, new_w, _ = detected_map.shape
        pad_h = max(0, (new_h - h) // 2)
        pad_w = max(0, (new_w - w) // 2)
        detected_map = detected_map[pad_h:pad_h+h, pad_w:pad_w+w]
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def high_quality_resize(self, x, size):
        # Written by lvmin
        # Super high-quality control map up-scaling, considering binary, seg, and one-pixel edges

        inpaint_mask = None
        if x.ndim == 3 and x.shape[2] == 4:
            inpaint_mask = x[:, :, 3]
            x = x[:, :, 0:3]

        if x.shape[0] != size[1] or x.shape[1] != size[0]:
            new_size_is_smaller = (size[0] * size[1]) < (x.shape[0] * x.shape[1])
            new_size_is_bigger = (size[0] * size[1]) > (x.shape[0] * x.shape[1])
            unique_color_count = len(get_unique_axis0(x.reshape(-1, x.shape[2])))
            is_one_pixel_edge = False
            is_binary = False
            if unique_color_count == 2:
                is_binary = numpy.min(x) < 16 and numpy.max(x) > 240
                if is_binary:
                    xc = x
                    xc = cv2.erode(xc, numpy.ones(shape=(3, 3), dtype=numpy.uint8), iterations=1)
                    xc = cv2.dilate(xc, numpy.ones(shape=(3, 3), dtype=numpy.uint8), iterations=1)
                    one_pixel_edge_count = numpy.where(xc < x)[0].shape[0]
                    all_edge_count = numpy.where(x > 127)[0].shape[0]
                    is_one_pixel_edge = one_pixel_edge_count * 2 > all_edge_count

            if 2 < unique_color_count < 200:
                interpolation = cv2.INTER_NEAREST
            elif new_size_is_smaller:
                interpolation = cv2.INTER_AREA
            else:
                interpolation = cv2.INTER_CUBIC  # Must be CUBIC because we now use nms. NEVER CHANGE THIS

            y = cv2.resize(x, size, interpolation=interpolation)
            if inpaint_mask is not None:
                inpaint_mask = cv2.resize(inpaint_mask, size, interpolation=interpolation)

            if is_binary:
                y = numpy.mean(y.astype(numpy.float32), axis=2).clip(0, 255).astype(numpy.uint8)
                if is_one_pixel_edge:
                    y = nake_nms(y)
                    _, y = cv2.threshold(y, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    y = lvmin_thin(y, prunings=new_size_is_bigger)
                else:
                    _, y = cv2.threshold(y, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                y = numpy.stack([y] * 3, axis=2)
        else:
            y = x

        if inpaint_mask is not None:
            inpaint_mask = (inpaint_mask > 127).astype(numpy.float32) * 255.0
            inpaint_mask = inpaint_mask[:, :, None].clip(0, 255).astype(numpy.uint8)
            y = numpy.concatenate([y, inpaint_mask], axis=2)

        return y

class ImageResizeMode_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "resize_mode": (RESIZE_MODES, {"default": "Just Resize"})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("MODE",)
    FUNCTION = "execute"

    CATEGORY = "🐉 JK/🛩️ Image"
    def execute(self, resize_mode):
        
        return (resize_mode,)

#---------------------------------------------------------------------------------------------------------------------#
# Mask Nodes
#---------------------------------------------------------------------------------------------------------------------#
class IsMaskEmpty_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mask": ("MASK",),
            },
        }
    RETURN_TYPES = ["BOOLEAN"]
    RETURN_NAMES = ["BOOLEAN"]

    FUNCTION = "main"
    CATEGORY = icons.get("JK/Mask")

    def main(self, mask):
    
        a = torch.all(mask == 0).int().item() != 0
        
        return (a,)

#---------------------------------------------------------------------------------------------------------------------#
# Animation Nodes
#---------------------------------------------------------------------------------------------------------------------#
class AnimPrompt_JK:
    modes = ["simple", "advanced"]
    
    @classmethod
    def INPUT_TYPES(cls):
        
        inputs = {
            "required": {
                "input_mode": (cls.modes,),
                "prompt_pos_pre": ("STRING", {"default": '', "multiline": False}),
                "prompt_neg_pre": ("STRING", {"default": '', "multiline": False}),
                "prompt_pos_app": ("STRING", {"default": '', "multiline": False}),
                "prompt_neg_app": ("STRING", {"default": '', "multiline": False}),
                "keyframe_count": ("INT", {"default": 3, "min": 1, "max": 20, "step": 1}),
            }
        }

        for i in range(1, 21):
            inputs["required"][f"keyframe_frame_{i}"] = ("INT", {"default": (i-1) * 8, "min": 0, "max": 0xffffffffffffffff})
            inputs["required"][f"prompt_pos_{i}"] = ("STRING", {"default": '', "multiline": False})
            inputs["required"][f"prompt_neg_{i}"] = ("STRING", {"default": '', "multiline": False})

        return inputs

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("PROMPT_PRE", "PROMPT_APP", "ANIMATE_PROMPT",)
    FUNCTION = "animate_prompt"
    CATEGORY = icons.get("JK/Animation")

    def animate_prompt(self, input_mode, prompt_pos_pre, prompt_neg_pre, prompt_pos_app, prompt_neg_app, keyframe_count, **kwargs):
        
        pre_prompt = ""
        post_prompt = ""
        animate_prompt = ""
        ani_prompt_pos = ""
        ani_prompt_neg = ""
        
        if input_mode == "simple":
            
            for j in range(1, keyframe_count + 1):
                if j == 1:
                    ani_prompt_pos = f"\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\","
                elif j == keyframe_count:
                    ani_prompt_pos = f"{ani_prompt_pos}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\""
                else:
                    ani_prompt_pos = f"{ani_prompt_pos}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\","
            
            return (prompt_pos_pre, prompt_pos_app, ani_prompt_pos,)
        
        else:
        
            for j in range(1, keyframe_count + 1):
                if j == 1:
                    ani_prompt_pos = f"\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\","
                    ani_prompt_neg = f"\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_neg_{j}')}\","
                elif j == keyframe_count:
                    ani_prompt_pos = f"{ani_prompt_pos}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\""
                    ani_prompt_neg = f"{ani_prompt_neg}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_neg_{j}')}\""
                else:
                    ani_prompt_pos = f"{ani_prompt_pos}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_pos_{j}')}\","
                    ani_prompt_neg = f"{ani_prompt_neg}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{kwargs.get(f'prompt_neg_{j}')}\","
        
            pre_prompt = f"{prompt_pos_pre}\n\"--neg\"\n{prompt_neg_pre}"
            post_prompt = f"{prompt_pos_app}\n\"--neg\"\n{prompt_neg_app}"
            animate_prompt = f"{ani_prompt_pos}\n\"--neg\"\n{ani_prompt_neg}"
            
            return (pre_prompt, post_prompt, animate_prompt,)

class AnimValue_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        
        inputs = {
            "required": {
                "keyframe_count": ("INT", {"default": 3, "min": 1, "max": 20, "step": 1}),
            }
        }

        for i in range(1, 21):
            inputs["required"][f"keyframe_frame_{i}"] = ("INT", {"default": (i-1) * 8, "min": 0, "max": 0xffffffffffffffff})
            inputs["required"][f"keyframe_value_{i}"] = ("FLOAT", {"default": 0.0})

        return inputs

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("ANIMATE_VALUE",)
    FUNCTION = "animate_value"
    CATEGORY = icons.get("JK/Animation")

    def animate_value(self, keyframe_count, **kwargs):
        
        pre_prompt = ""
        post_prompt = ""
        animate_prompt = ""
        ani_prompt_pos = ""
        ani_prompt_neg = ""
        
        for j in range(1, keyframe_count + 1):
            if j == 1:
                ani_value = f"\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{str(kwargs.get(f'keyframe_value_{j}'))}\","
            elif j == keyframe_count:
                ani_value = f"{ani_value}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{str(kwargs.get(f'keyframe_value_{j}'))}\""
            else:
                ani_value = f"{ani_value}\n\"{kwargs.get(f'keyframe_frame_{j}')} \":\"{str(kwargs.get(f'keyframe_value_{j}'))}\","
        
        return (ani_value,)

#---------------------------------------------------------------------------------------------------------------------#
# Logic Switches Nodes
#---------------------------------------------------------------------------------------------------------------------#
class CR_Boolean_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "NUMBER", "INT")
    FUNCTION = "return_boolean"

    CATEGORY = icons.get("JK/Logic")

    def return_boolean(self, boolean_value):
        return (boolean_value, 1 if boolean_value==True else 0, 1 if boolean_value==True else 0)

class CR_IntInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "int_false": ("INT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            },
            "optional": {
                "int_true": ("INT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            },
        }

    RETURN_TYPES = ("INT", "BOOLEAN",)
    FUNCTION = "InputInt"
    CATEGORY = icons.get("JK/Logic")

    def InputInt(self, boolean_value, int_false, int_true=None):
        if int_true != None and boolean_value == True:
            return (int_true, boolean_value,)
        else:
            return (int_false, boolean_value,)

class CR_FloatInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "float_false": ("FLOAT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            },
            "optional": {
                "float_true": ("FLOAT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            },
        }

    RETURN_TYPES = ("FLOAT", "BOOLEAN",)
    FUNCTION = "InputFloat"
    CATEGORY = icons.get("JK/Logic")

    def InputFloat(self, boolean_value, float_false, float_true=None):
        if float_true != None and boolean_value == True:
            return (float_true, boolean_value,)
        else:
            return (float_false, boolean_value,)

class CR_ImageInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "image_false": ("IMAGE",),
            },
            "optional": {
                "image_true": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN",)
    FUNCTION = "InputImages"
    CATEGORY = icons.get("JK/Logic")

    def InputImages(self, boolean_value, image_false, image_true=None):
        if image_true != None and boolean_value == True:
            return (image_true, boolean_value,)
        else:
            return (image_false, boolean_value,)

class CR_MaskInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "mask_false": ("MASK",),
            },
            "optional": {
                "mask_true": ("MASK",)
            },
        }

    RETURN_TYPES = ("MASK", "BOOLEAN",)
    FUNCTION = "InputMasks"
    CATEGORY = icons.get("JK/Logic")

    def InputMasks(self, boolean_value, mask_false, mask_true=None):
        if mask_true != None and boolean_value == True:
            return (mask_true, boolean_value,)
        else:
            return (mask_false, boolean_value,)

class CR_LatentInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "latent_false": ("LATENT",),
            },
            "optional": {
                "latent_true": ("LATENT",),
            },
        }

    RETURN_TYPES = ("LATENT", "BOOLEAN",)
    FUNCTION = "InputLatents"
    CATEGORY = icons.get("JK/Logic")

    def InputLatents(self, boolean_value, latent_false, latent_true=None):
        if latent_true != None and boolean_value == True:
            return (latent_true, boolean_value,)
        else:
            return (latent_false, boolean_value,)

class CR_ConditioningInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "conditioning_false": ("CONDITIONING",),
            },
            "optional": {
                "conditioning_true": ("CONDITIONING",),
            },
        }

    RETURN_TYPES = ("CONDITIONING", "BOOLEAN",)
    FUNCTION = "InputConditioning"
    CATEGORY = icons.get("JK/Logic")

    def InputConditioning(self, boolean_value, conditioning_false, conditioning_true=None):
        if conditioning_true != None and boolean_value == True:
            return (conditioning_true, boolean_value,)
        else:
            return (conditioning_false, boolean_value,)

class CR_ClipInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "clip_false": ("CLIP",),
            },
            "optional": {
                "clip_true": ("CLIP",),
            },
        }

    RETURN_TYPES = ("CLIP", "BOOLEAN",)
    FUNCTION = "InputClip"
    CATEGORY = icons.get("JK/Logic")

    def InputClip(self, boolean_value, clip_false, clip_true=None):
        if clip_true != None and boolean_value == True:
            return (clip_true, boolean_value,)
        else:
            return (clip_false, boolean_value,)

class CR_ModelInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "model_false": ("MODEL",),
            },
            "optional": {
                "model_true": ("MODEL",),
            },
        }

    RETURN_TYPES = ("MODEL", "BOOLEAN",)
    FUNCTION = "InputModel"
    CATEGORY = icons.get("JK/Logic")

    def InputModel(self, boolean_value, model_false, model_true=None):
        if model_true != None and boolean_value == True:
            return (model_true, boolean_value,)
        else:
            return (model_false, boolean_value,)

class CR_ControlNetInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "control_net_false": ("CONTROL_NET",),
            },
            "optional": {
                "control_net_true": ("CONTROL_NET",),
            },
        }
        
    RETURN_TYPES = ("CONTROL_NET", "BOOLEAN",)
    FUNCTION = "InputControlNet"
    CATEGORY = icons.get("JK/Logic")

    def InputControlNet(self, boolean_value, control_net_false, control_net_true=None):
        if control_net_true != None and boolean_value == True:
            return (control_net_true, boolean_value,)
        else:
            return (control_net_false, boolean_value,)

class CR_ControlNetStackInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "control_net_stack_false": ("CONTROL_NET_STACK",),
            },
            "optional": {
                "control_net_stack_true": ("CONTROL_NET_STACK",),
            },
        }
        
    RETURN_TYPES = ("CONTROL_NET_STACK", "BOOLEAN",)
    FUNCTION = "InputControlNetStack"
    CATEGORY = icons.get("JK/Logic")

    def InputControlNetStack(self, boolean_value, control_net_stack_false, control_net_stack_true=None):
        if control_net_stack_true != None and boolean_value == True:
            return (control_net_stack_true, boolean_value,)
        else:
            return (control_net_stack_false, boolean_value,)

class CR_TextInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "text_false": ("STRING", {"default": ""}),
            },
            "optional": {
                "text_true": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN",)
    FUNCTION = "text_input_switch"
    CATEGORY = icons.get("JK/Logic")

    def text_input_switch(self, boolean_value, text_false, text_true=None):
        if text_true != None and boolean_value == True:
            return (text_true, boolean_value,)
        else:
            return (text_false, boolean_value,)

class CR_VAEInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "VAE_false": ("VAE", {"forceInput": True}),
            },
            "optional": {
                "VAE_true": ("VAE", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("VAE", "BOOLEAN",)   
    FUNCTION = "vae_switch"
    CATEGORY = icons.get("JK/Logic")

    def vae_switch(self, boolean_value, VAE_false, VAE_true=None):
        if VAE_true != None and boolean_value == True:
            return (VAE_true, boolean_value)
        else:
            return (VAE_false, boolean_value)

class CR_PipeInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "pipe_false": ("PIPE_LINE", {"forceInput": True}),
                
            },
            "optional": {
                "pipe_true": ("PIPE_LINE", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Logic")

    def pipe_switch(self, boolean_value, pipe_false, pipe_true=None):
        if pipe_true != None and boolean_value == True:
            return (pipe_true, boolean_value)
        else:
            return (pipe_false, boolean_value)

class CR_ImpactPipeInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "pipe_false": ("BASIC_PIPE", {"forceInput": True}),
            },
            "optional": {
                "pipe_true": ("BASIC_PIPE", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("BASIC_PIPE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Logic")

    def pipe_switch(self, boolean_value, pipe_false, pipe_true=None):
        if pipe_true != None and boolean_value == True:
            return (pipe_true, boolean_value)
        else:
            return (pipe_false, boolean_value)

class CR_NoiseInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "noise_false": ("NOISE", {"forceInput": True}),
            },
            "optional": {
                "noise_true": ("NOISE", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("NOISE", "BOOLEAN",)   
    FUNCTION = "noise_switch"
    CATEGORY = icons.get("JK/Logic")

    def noise_switch(self, boolean_value, noise_false, noise_true=None):
        if noise_true != None and boolean_value == True:
            return (noise_true, boolean_value)
        else:
            return (noise_false, boolean_value)

class CR_GuiderInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "guider_false": ("GUIDER", {"forceInput": True}),
            },
            "optional": {
                "guider_true": ("GUIDER", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("GUIDER", "BOOLEAN",)   
    FUNCTION = "guider_switch"
    CATEGORY = icons.get("JK/Logic")

    def guider_switch(self, boolean_value, guider_false, guider_true=None):
        if guider_true != None and boolean_value == True:
            return (guider_true, boolean_value)
        else:
            return (guider_false, boolean_value)

class CR_SamplerInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "sampler_false": ("SAMPLER", {"forceInput": True}),
            },
            "optional": {
                "sampler_true": ("SAMPLER", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("SAMPLER", "BOOLEAN",)
    FUNCTION = "sampler_switch"
    CATEGORY = icons.get("JK/Logic")

    def sampler_switch(self, boolean_value, sampler_false, sampler_true=None):
        if sampler_true != None and boolean_value == True:
            return (sampler_true, boolean_value)
        else:
            return (sampler_false, boolean_value)

class CR_SigmasInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "sigmas_false": ("SIGMAS", {"forceInput": True}),
            },
            "optional": {
                "sigmas_true": ("SIGMAS", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("SIGMAS", "BOOLEAN",)
    FUNCTION = "sigmas_switch"
    CATEGORY = icons.get("JK/Logic")

    def sigmas_switch(self, boolean_value, sigmas_false, sigmas_true=None):
        if sigmas_true != None and boolean_value == True:
            return (sigmas_true, boolean_value)
        else:
            return (sigmas_false, boolean_value)

class CR_MeshInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "mesh_false": ("MESH", {"forceInput": True}),
            },
            "optional": {
                "mesh_true": ("MESH", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("MESH", "BOOLEAN",)   
    FUNCTION = "mesh_switch"
    CATEGORY = icons.get("JK/Logic")

    def mesh_switch(self, boolean_value, mesh_false, mesh_true=None):
        if mesh_true != None and boolean_value == True:
            return (mesh_true, boolean_value)
        else:
            return (mesh_false, boolean_value)

class CR_PlyInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "ply_false": ("GS_PLY", {"forceInput": True}),
            },
            "optional": {
                "ply_true": ("GS_PLY", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("GS_PLY", "BOOLEAN",)   
    FUNCTION = "ply_switch"
    CATEGORY = icons.get("JK/Logic")

    def mesh_switch(self, boolean_value, ply_false, ply_true=None):
        if ply_true != None and boolean_value == True:
            return (ply_true, boolean_value)
        else:
            return (ply_false, boolean_value)

class CR_OrbitPoseInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "orbit_camposes_false": ("ORBIT_CAMPOSES", {"forceInput": True}),
            },
            "optional": {
                "orbit_camposes_true": ("ORBIT_CAMPOSES", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES", "BOOLEAN",)   
    FUNCTION = "orbit_switch"
    CATEGORY = icons.get("JK/Logic")

    def orbit_switch(self, boolean_value, orbit_camposes_false, orbit_camposes_true=None):
        if orbit_camposes_true != None and boolean_value == True:
            return (orbit_camposes_true, boolean_value)
        else:
            return (orbit_camposes_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# ComfyMath Fix Nodes
#---------------------------------------------------------------------------------------------------------------------#
DEFAULT_BOOL = ("BOOLEAN", {"default": False})
DEFAULT_STRING = ("STRING", {"default": ""})
DEFAULT_FLOAT = ("FLOAT", {"default": 0.0, "step": 0.0001})
DEFAULT_INT = ("INT", {"default": 0})
DEFAULT_NUMBER = ("NUMBER", {"default": 0.0, "step": 0.0001})
number: TypeAlias = int | float
Vec2: TypeAlias = tuple[float, float]
VEC2_ZERO = (0.0, 0.0)
DEFAULT_VEC2 = ("VEC2", {"default": VEC2_ZERO})
Vec3: TypeAlias = tuple[float, float, float]
VEC3_ZERO = (0.0, 0.0, 0.0)
DEFAULT_VEC3 = ("VEC3", {"default": VEC3_ZERO})
Vec4: TypeAlias = tuple[float, float, float, float]
VEC4_ZERO = (0.0, 0.0, 0.0, 0.0)
DEFAULT_VEC4 = ("VEC4", {"default": VEC4_ZERO})

BOOL_UNARY_OPERATIONS: Mapping[str, Callable[[bool], bool]] = {
    "Not": lambda a: not a,
}

BOOL_BINARY_OPERATIONS: Mapping[str, Callable[[bool, bool], bool]] = {
    "Or": lambda a, b: a or b,
    "Nor": lambda a, b: not (a or b),
    "Xor": lambda a, b: a ^ b,
    "Nand": lambda a, b: not (a and b),
    "And": lambda a, b: a and b,
    "Xnor": lambda a, b: not (a ^ b),
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
}

STRING_BINARY_CONDITIONS: Mapping[str, Callable[[str, str], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
}

FLOAT_UNARY_CONDITIONS: Mapping[str, Callable[[float], bool]] = {
    "IsZero": lambda a: a == 0.0,
    "IsPositive": lambda a: a > 0.0,
    "IsNegative": lambda a: a < 0.0,
    "IsNonZero": lambda a: a != 0.0,
    "IsPositiveInfinity": lambda a: math.isinf(a) and a > 0.0,
    "IsNegativeInfinity": lambda a: math.isinf(a) and a < 0.0,
    "IsNaN": lambda a: math.isnan(a),
    "IsFinite": lambda a: math.isfinite(a),
    "IsInfinite": lambda a: math.isinf(a),
    "IsEven": lambda a: a % 2 == 0.0,
    "IsOdd": lambda a: a % 2 != 0.0,
}

FLOAT_BINARY_CONDITIONS: Mapping[str, Callable[[float, float], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
    "Gt": lambda a, b: a > b,
    "Gte": lambda a, b: a >= b,
    "Lt": lambda a, b: a < b,
    "Lte": lambda a, b: a <= b,
}

FLOAT_UNARY_OPERATIONS: Mapping[str, Callable[[float], float]] = {
    "Neg": lambda a: -a,
    "Inc": lambda a: a + 1,
    "Dec": lambda a: a - 1,
    "Abs": lambda a: abs(a),
    "Sqr": lambda a: a * a,
    "Cube": lambda a: a * a * a,
    "Sqrt": lambda a: math.sqrt(a),
    "Exp": lambda a: math.exp(a),
    "Ln": lambda a: math.log(a),
    "Log10": lambda a: math.log10(a),
    "Log2": lambda a: math.log2(a),
    "Sin": lambda a: math.sin(a),
    "Cos": lambda a: math.cos(a),
    "Tan": lambda a: math.tan(a),
    "Asin": lambda a: math.asin(a),
    "Acos": lambda a: math.acos(a),
    "Atan": lambda a: math.atan(a),
    "Sinh": lambda a: math.sinh(a),
    "Cosh": lambda a: math.cosh(a),
    "Tanh": lambda a: math.tanh(a),
    "Asinh": lambda a: math.asinh(a),
    "Acosh": lambda a: math.acosh(a),
    "Atanh": lambda a: math.atanh(a),
    "Round": lambda a: round(a),
    "Floor": lambda a: math.floor(a),
    "Ceil": lambda a: math.ceil(a),
    "Trunc": lambda a: math.trunc(a),
    "Erf": lambda a: math.erf(a),
    "Erfc": lambda a: math.erfc(a),
    "Gamma": lambda a: math.gamma(a),
    "Radians": lambda a: math.radians(a),
    "Degrees": lambda a: math.degrees(a),
}

FLOAT_BINARY_OPERATIONS: Mapping[str, Callable[[float, float], float]] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a / b,
    "Mod": lambda a, b: a % b,
    "Pow": lambda a, b: a**b,
    "FloorDiv": lambda a, b: a // b,
    "Max": lambda a, b: max(a, b),
    "Min": lambda a, b: min(a, b),
    "Log": lambda a, b: math.log(a, b),
    "Atan2": lambda a, b: math.atan2(a, b),
}

INT_UNARY_CONDITIONS: Mapping[str, Callable[[int], bool]] = {
    "IsZero": lambda a: a == 0,
    "IsNonZero": lambda a: a != 0,
    "IsPositive": lambda a: a > 0,
    "IsNegative": lambda a: a < 0,
    "IsEven": lambda a: a % 2 == 0,
    "IsOdd": lambda a: a % 2 == 1,
}

INT_BINARY_CONDITIONS: Mapping[str, Callable[[int, int], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
    "Gt": lambda a, b: a > b,
    "Lt": lambda a, b: a < b,
    "Geq": lambda a, b: a >= b,
    "Leq": lambda a, b: a <= b,
}

INT_UNARY_OPERATIONS: Mapping[str, Callable[[int], int]] = {
    "Neg": lambda a: -a,
    "Abs": lambda a: abs(a),
    "Inc": lambda a: a + 1,
    "Dec": lambda a: a - 1,
    "Sqr": lambda a: a * a,
    "Cube": lambda a: a * a * a,
    "Not": lambda a: ~a,
    "Factorial": lambda a: math.factorial(a),
}

INT_BINARY_OPERATIONS: Mapping[str, Callable[[int, int], int]] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a // b,
    "Mod": lambda a, b: a % b,
    "Pow": lambda a, b: a**b,
    "And": lambda a, b: a & b,
    "Nand": lambda a, b: ~a & b,
    "Or": lambda a, b: a | b,
    "Nor": lambda a, b: ~a & b,
    "Xor": lambda a, b: a ^ b,
    "Xnor": lambda a, b: ~a ^ b,
    "Shl": lambda a, b: a << b,
    "Shr": lambda a, b: a >> b,
    "Max": lambda a, b: max(a, b),
    "Min": lambda a, b: min(a, b),
}

VEC_UNARY_OPERATIONS: Mapping[str, Callable[[numpy.ndarray], numpy.ndarray]] = {
    "Neg": lambda a: -a,
    "Normalize": lambda a: a / numpy.linalg.norm(a),
}

VEC_BINARY_OPERATIONS: Mapping[
    str, Callable[[numpy.ndarray, numpy.ndarray], numpy.ndarray]
    ] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Cross": lambda a, b: numpy.cross(a, b),
}

VEC_UNARY_CONDITIONS: Mapping[str, Callable[[numpy.ndarray], bool]] = {
    "IsZero": lambda a: not numpy.any(a).astype(bool),
    "IsNotZero": lambda a: numpy.any(a).astype(bool),
    "IsNormalized": lambda a: numpy.allclose(a, a / numpy.linalg.norm(a)),
    "IsNotNormalized": lambda a: not numpy.allclose(a, a / numpy.linalg.norm(a)),
}

VEC_BINARY_CONDITIONS: Mapping[str, Callable[[numpy.ndarray, numpy.ndarray], bool]] = {
    "Eq": lambda a, b: numpy.allclose(a, b),
    "Neq": lambda a, b: not numpy.allclose(a, b),
}

VEC_TO_FLOAT_UNARY_OPERATION: Mapping[str, Callable[[numpy.ndarray], float]] = {
    "Norm": lambda a: numpy.linalg.norm(a).astype(float),
}

VEC_TO_FLOAT_BINARY_OPERATION: Mapping[
    str, Callable[[numpy.ndarray, numpy.ndarray], float]
    ] = {
    "Dot": lambda a, b: numpy.dot(a, b),
    "Distance": lambda a, b: numpy.linalg.norm(a - b).astype(float),
}

VEC_FLOAT_OPERATION: Mapping[str, Callable[[numpy.ndarray, float], numpy.ndarray]] = {
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a / b,
}

def _vec2_from_numpy(a: numpy.ndarray) -> Vec2:
    return (
        float(a[0]),
        float(a[1]),
    )

def _vec3_from_numpy(a: numpy.ndarray) -> Vec3:
    return (
        float(a[0]),
        float(a[1]),
        float(a[2]),
    )

def _vec4_from_numpy(a: numpy.ndarray) -> Vec4:
    return (
        float(a[0]),
        float(a[1]),
        float(a[2]),
        float(a[3]),
    )

class BoolToInt_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("BOOLEAN", {"default": False})}}

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: bool) -> tuple[int]:
        return (int(a),)

class IntToBool_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("INT", {"default": 0})}}

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: int) -> tuple[bool]:
        return (a != 0,)

class BoolUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {"op": (list(BOOL_UNARY_OPERATIONS.keys()),), "a": DEFAULT_BOOL}
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")

    def op(self, op: str, a: bool) -> tuple[bool]:
        return (BOOL_UNARY_OPERATIONS[op](a),)

class BoolBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(BOOL_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_BOOL,
                "b": DEFAULT_BOOL,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")

    def op(self, op: str, a: bool, b: bool) -> tuple[bool]:
        return (BOOL_BINARY_OPERATIONS[op](a, b),)

class BoolBinaryAnd_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("BOOLEAN", {"forceInput": True}),
                "b": ("BOOLEAN", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")

    def op(self, a: bool, b: bool) -> tuple[bool]:
        return (BOOL_BINARY_OPERATIONS["And"](a, b),)

class BoolBinaryOR_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("BOOLEAN", {"forceInput": True}),
                "b": ("BOOLEAN", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")

    def op(self, a: bool, b: bool) -> tuple[bool]:
        return (BOOL_BINARY_OPERATIONS["Or"](a, b),)

class StringBinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(STRING_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_STRING,
                "b": DEFAULT_STRING,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/String")

    def op(self, op: str, a: str, b: str) -> tuple[bool]:
        return (STRING_BINARY_CONDITIONS[op](a, b),)

class PromptCombine_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt_1": ("STRING", {"forceInput": True}),
                "prompt_2": ("STRING", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Prompt",)
    FUNCTION = "combine"
    CATEGORY = icons.get("JK/Math/String")
    
    def combine(self, prompt_1=None, prompt_2=None):
        
        if prompt_1 != None:
            if prompt_1 != "":
                if prompt_1[-1] == ",":
                    prompt_output = f"{prompt_1}{prompt_2}" if prompt_2 !=None and prompt_2 !="" else prompt_1
                else:
                    prompt_output = f"{prompt_1},{prompt_2}" if prompt_2 !=None and prompt_2 !="" else prompt_1
            else:
                prompt_output = prompt_2 if prompt_2 !=None and prompt_2 !="" else ""
        else:
            prompt_output = prompt_2 if prompt_2 !=None and prompt_2 !="" else ""
        
        return (prompt_output,)

class FloatUnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_CONDITIONS.keys()),),
                "a": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")

    def op(self, op: str, a: float) -> tuple[bool]:
        return (FLOAT_UNARY_CONDITIONS[op](a),)

class FloatBinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_FLOAT,
                "b": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")

    def op(self, op: str, a: float, b: float) -> tuple[bool]:
        return (FLOAT_BINARY_CONDITIONS[op](a, b),)

class IntUnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {"op": (list(INT_UNARY_CONDITIONS.keys()),), "a": DEFAULT_INT}
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")

    def op(self, op: str, a: int) -> tuple[bool]:
        return (INT_UNARY_CONDITIONS[op](a),)

class IntBinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_INT,
                "b": DEFAULT_INT,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")

    def op(self, op: str, a: int, b: int) -> tuple[bool]:
        return (INT_BINARY_CONDITIONS[op](a, b),)

class NumberUnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_CONDITIONS.keys()),),
                "a": DEFAULT_NUMBER,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Number")

    def op(self, op: str, a: number) -> tuple[bool]:
        return (FLOAT_UNARY_CONDITIONS[op](float(a)),)

class NumberBinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_NUMBER,
                "b": DEFAULT_NUMBER,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Number")

    def op(self, op: str, a: number, b: number) -> tuple[bool]:
        return (FLOAT_BINARY_CONDITIONS[op](float(a), float(b)),)

class Vec2UnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2) -> tuple[bool]:
        return (VEC_UNARY_CONDITIONS[op](numpy.array(a)),)

class Vec2BinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC2,
                "b": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2, b: Vec2) -> tuple[bool]:
        return (VEC_BINARY_CONDITIONS[op](numpy.array(a), numpy.array(b)),)

class Vec2ToFloatUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_UNARY_OPERATION.keys()),),
                "a": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2) -> tuple[float]:
        return (VEC_TO_FLOAT_UNARY_OPERATION[op](numpy.array(a)),)

class Vec2ToFloatBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_BINARY_OPERATION.keys()),),
                "a": DEFAULT_VEC2,
                "b": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2, b: Vec2) -> tuple[float]:
        return (VEC_TO_FLOAT_BINARY_OPERATION[op](numpy.array(a), numpy.array(b)),)

class Vec2FloatOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_FLOAT_OPERATION.keys()),),
                "a": DEFAULT_VEC2,
                "b": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("VEC2",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2, b: float) -> tuple[Vec2]:
        return (_vec2_from_numpy(VEC_FLOAT_OPERATION[op](numpy.array(a), b)),)

class Vec3UnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3) -> tuple[bool]:
        return (VEC_UNARY_CONDITIONS[op](numpy.array(a)),)

class Vec3BinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC3,
                "b": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3, b: Vec3) -> tuple[bool]:
        return (VEC_BINARY_CONDITIONS[op](numpy.array(a), numpy.array(b)),)

class Vec3ToFloatUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_UNARY_OPERATION.keys()),),
                "a": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3) -> tuple[float]:
        return (VEC_TO_FLOAT_UNARY_OPERATION[op](numpy.array(a)),)

class Vec3ToFloatBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_BINARY_OPERATION.keys()),),
                "a": DEFAULT_VEC3,
                "b": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3, b: Vec3) -> tuple[float]:
        return (VEC_TO_FLOAT_BINARY_OPERATION[op](numpy.array(a), numpy.array(b)),)

class Vec3FloatOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_FLOAT_OPERATION.keys()),),
                "a": DEFAULT_VEC3,
                "b": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("VEC3",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3, b: float) -> tuple[Vec3]:
        return (_vec3_from_numpy(VEC_FLOAT_OPERATION[op](numpy.array(a), b)),)

class Vec4UnaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4) -> tuple[bool]:
        return (VEC_UNARY_CONDITIONS[op](numpy.array(a)),)

class Vec4BinaryCondition_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_CONDITIONS.keys()),),
                "a": DEFAULT_VEC4,
                "b": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4, b: Vec4) -> tuple[bool]:
        return (VEC_BINARY_CONDITIONS[op](numpy.array(a), numpy.array(b)),)

class Vec4ToFloatUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_UNARY_OPERATION.keys()),),
                "a": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4) -> tuple[float]:
        return (VEC_TO_FLOAT_UNARY_OPERATION[op](numpy.array(a)),)

class Vec4ToFloatBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_TO_FLOAT_BINARY_OPERATION.keys()),),
                "a": DEFAULT_VEC4,
                "b": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4, b: Vec4) -> tuple[float]:
        return (VEC_TO_FLOAT_BINARY_OPERATION[op](numpy.array(a), numpy.array(b)),)

class Vec4FloatOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_FLOAT_OPERATION.keys()),),
                "a": DEFAULT_VEC4,
                "b": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("VEC4",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4, b: float) -> tuple[Vec4]:
        return (_vec4_from_numpy(VEC_FLOAT_OPERATION[op](numpy.array(a), b)),)

#---------------------------------------------------------------------------------------------------------------------#
# ComfyMath Nodes
#---------------------------------------------------------------------------------------------------------------------#
class FloatToInt_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("FLOAT", {"default": 0.0})}}

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[int]:
        return (int(a),)


class IntToFloat_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("INT", {"default": 0})}}

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: int) -> tuple[float]:
        return (float(a),)


class IntToNumber_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("INT", {"default": 0})}}

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: int) -> tuple[number]:
        return (a,)


class NumberToInt_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("NUMBER", {"default": 0.0})}}

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: number) -> tuple[int]:
        return (int(a),)


class FloatToNumber_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("FLOAT", {"default": 0.0, "step": 0.0001})}}

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[number]:
        return (a,)


class NumberToFloat_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("NUMBER", {"default": 0.0, "step": 0.0001})}}

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: number) -> tuple[float]:
        return (float(a),)


class ComposeVec2_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "x": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "y": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC2",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, x: float, y: float) -> tuple[Vec2]:
        return ((x, y),)


class FillVec2_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC2",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[Vec2]:
        return ((a, a),)


class BreakoutVec2_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC2", {"default": VEC2_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: Vec2) -> tuple[float, float]:
        return (a[0], a[1])


class ComposeVec3_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "x": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "y": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "z": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC3",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, x: float, y: float, z: float) -> tuple[Vec3]:
        return ((x, y, z),)


class FillVec3_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC3",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[Vec3]:
        return ((a, a, a),)


class BreakoutVec3_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC3", {"default": VEC3_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: Vec3) -> tuple[float, float, float]:
        return (a[0], a[1], a[2])


class ComposeVec4_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "x": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "y": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "z": ("FLOAT", {"default": 0.0, "step": 0.0001}),
                "w": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC4",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, x: float, y: float, z: float, w: float) -> tuple[Vec4]:
        return ((x, y, z, w),)


class FillVec4_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("VEC4",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[Vec4]:
        return ((a, a, a, a),)


class BreakoutVec4_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC4", {"default": VEC4_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: Vec4) -> tuple[float, float, float, float]:
        return (a[0], a[1], a[2], a[3])

class FloatUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_OPERATIONS.keys()),),
                "a": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")

    def op(self, op: str, a: float) -> tuple[float]:
        return (FLOAT_UNARY_OPERATIONS[op](a),)

class FloatBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_FLOAT,
                "b": DEFAULT_FLOAT,
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")

    def op(self, op: str, a: float, b: float) -> tuple[float]:
        return (FLOAT_BINARY_OPERATIONS[op](a, b),)

class IntUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {"op": (list(INT_UNARY_OPERATIONS.keys()),), "a": DEFAULT_INT}
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")

    def op(self, op: str, a: int) -> tuple[int]:
        return (INT_UNARY_OPERATIONS[op](a),)

class IntBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_INT,
                "b": DEFAULT_INT,
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")

    def op(self, op: str, a: int, b: int) -> tuple[int]:
        return (INT_BINARY_OPERATIONS[op](a, b),)

class NumberUnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_OPERATIONS.keys()),),
                "a": DEFAULT_NUMBER,
            }
        }

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Number")

    def op(self, op: str, a: number) -> tuple[float]:
        return (FLOAT_UNARY_OPERATIONS[op](float(a)),)

class NumberBinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_NUMBER,
                "b": DEFAULT_NUMBER,
            }
        }

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Number")

    def op(self, op: str, a: number, b: number) -> tuple[float]:
        return (FLOAT_BINARY_OPERATIONS[op](float(a), float(b)),)

class Vec2UnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("VEC2",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2) -> tuple[Vec2]:
        return (_vec2_from_numpy(VEC_UNARY_OPERATIONS[op](numpy.array(a))),)

class Vec2BinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC2,
                "b": DEFAULT_VEC2,
            }
        }

    RETURN_TYPES = ("VEC2",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec2, b: Vec2) -> tuple[Vec2]:
        return (
            _vec2_from_numpy(VEC_BINARY_OPERATIONS[op](numpy.array(a), numpy.array(b))),
        )

class Vec3UnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("VEC3",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3) -> tuple[Vec3]:
        return (_vec3_from_numpy(VEC_UNARY_OPERATIONS[op](numpy.array(a))),)

class Vec3BinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC3,
                "b": DEFAULT_VEC3,
            }
        }

    RETURN_TYPES = ("VEC3",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec3, b: Vec3) -> tuple[Vec3]:
        return (
            _vec3_from_numpy(VEC_BINARY_OPERATIONS[op](numpy.array(a), numpy.array(b))),
        )

class Vec4UnaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_UNARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("VEC4",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4) -> tuple[Vec4]:
        return (_vec4_from_numpy(VEC_UNARY_OPERATIONS[op](numpy.array(a))),)

class Vec4BinaryOperation_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(VEC_BINARY_OPERATIONS.keys()),),
                "a": DEFAULT_VEC4,
                "b": DEFAULT_VEC4,
            }
        }

    RETURN_TYPES = ("VEC4",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Vector")

    def op(self, op: str, a: Vec4, b: Vec4) -> tuple[Vec4]:
        return (
            _vec4_from_numpy(VEC_BINARY_OPERATIONS[op](numpy.array(a), numpy.array(b))),
        )

#---------------------------------------------------------------------------------------------------------------------#
# Simple Evaluate Nodes from Efficiency Nodes
#---------------------------------------------------------------------------------------------------------------------#
import simpleeval

class EvaluateInts_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "python_expression": ("STRING", {"default": "((a + b) - c) / 2", "multiline": False}), },
            "optional": {
                "a": ("INT", {"default": 0, "min": -48000, "max": 48000, "step": 1}),
                "b": ("INT", {"default": 0, "min": -48000, "max": 48000, "step": 1}),
                "c": ("INT", {"default": 0, "min": -48000, "max": 48000, "step": 1}), },
        }

    RETURN_TYPES = ("INT", "FLOAT", "STRING",)
    OUTPUT_NODE = True
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")

    def evaluate(self, python_expression, a=0, b=0, c=0):
        result = simpleeval.simple_eval(python_expression, names={'a': a, 'b': b, 'c': c})
        int_result = int(result)
        float_result = float(result)
        string_result = str(result)
        return (int_result, float_result, string_result,)

class EvaluateFloats_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "python_expression": ("STRING", {"default": "((a + b) - c) / 2", "multiline": False}), },
            "optional": {
                "a": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 0.0001}),
                "b": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 0.0001}),
                "c": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 0.0001}), },
        }

    RETURN_TYPES = ("INT", "FLOAT", "STRING",)
    OUTPUT_NODE = True
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")

    def evaluate(self, python_expression, a=0, b=0, c=0):
        result = simpleeval.simple_eval(python_expression, names={'a': a, 'b': b, 'c': c})
        int_result = int(result)
        float_result = float(result)
        string_result = str(result)
        return (int_result, float_result, string_result,)

class EvaluateStrs_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "python_expression": ("STRING", {"default": "a + b + c", "multiline": False}), },
            "optional": {
                "a": ("STRING", {"default": "Hello", "multiline": False}),
                "b": ("STRING", {"default": " World", "multiline": False}),
                "c": ("STRING", {"default": "!", "multiline": False}), }
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")

    def evaluate(self, python_expression, a="", b="", c=""):
        variables = {'a': a, 'b': b, 'c': c}  # Define the variables for the expression
        functions = simpleeval.DEFAULT_FUNCTIONS.copy()
        functions.update({"len": len})  # Add the functions for the expression
        result = simpleeval.simple_eval(python_expression, names=variables, functions=functions)
        return (str(result),)  # Convert result to a string before returning

class EvalExamples_JK:
    @classmethod
    def INPUT_TYPES(cls):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SimpleEval_Node_Examples.txt')
        with open(filepath, 'r') as file:
            examples = file.read()
        return {"required": {"models_text": ("STRING", {"default": examples, "multiline": True}), }, }

    RETURN_TYPES = ()
    CATEGORY = icons.get("JK/Math")

#---------------------------------------------------------------------------------------------------------------------#
# 3D Nodes
#---------------------------------------------------------------------------------------------------------------------#
ORBITPOSE_PRESET = ["Custom", "CRM(6)", "Zero123Plus(6)", "Wonder3D(6)", "Era3D(6)", "MVDream(4)", "Unique3D(4)", "CharacterGen(4)"]

OrbitPosesList = {
    "Custom":           [[-90.0, 0.0, 180.0, 90.0, 0.0, 0.0], [0.0, 90.0, 0.0, 0.0, -90.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "CRM(6)":           [[-90.0, 0.0, 180.0, 90.0, 0.0, 0.0], [0.0, 90.0, 0.0, 0.0, -90.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Wonder3D(6)":      [[0.0, 45.0, 90.0, 180.0, -90.0, -45.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Zero123Plus(6)":   [[30.0, 90.0, 150.0, -150.0, -90.0, -30.0], [-20.0, 10.0, -20.0, 10.0, -20.0, 10.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Era3D(6)":         [[0.0, 45.0, 90.0, 180.0, -90.0, -45.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], #[[radius], [radius], [radius], [radius], [radius], [radius]], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    "Hunyuan3D(6)":     [[0.0, 60.0, 120.0, 180.0, -120.0, -60.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], #[[radius], [radius], [radius], [radius], [radius], [radius]], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    "MVDream(4)":       [[0.0, 90.0, 180.0, -90.0], [0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
    "Unique3D(4)":      [[0.0, 90.0, 180.0, -90.0], [0.0, 0.0, 0.0, 0.0]], #[[radius], [radius], [radius], [radius]], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]
    "CharacterGen(4)":  [[-90.0, 180.0, 90.0, 0.0], [0.0, 0.0, 0.0, 0.0]], #[[radius], [radius], [radius], [radius]], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]
}

class OrbitPoses_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbitpose_preset": (ORBITPOSE_PRESET, {"default": "Custom"}),
                "azimuths": ("STRING", {"default": "-90.0, 0.0, 180.0, 90.0, 0.0, 0.0"}),
                "elevations": ("STRING", {"default": "0.0, 90.0, 0.0, 0.0, -90.0, 0.0"}),
                "radius": ("STRING", {"default": "4.0, 4.0, 4.0, 4.0, 4.0, 4.0"}),
                "center": ("STRING", {"default": "0.0, 0.0, 0.0, 0.0, 0.0, 0.0"}),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES", "ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_lists", "orbit_camposes",)
    
    FUNCTION = "get_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    
    def get_orbit_poses(self, orbitpose_preset, azimuths, elevations, radius, center):
        
        orbit_lists = OrbitPosesList.get(f"{orbitpose_preset}")
        
        if orbitpose_preset == "Custom":
            azimuths = azimuths.split(",")
            elevations = elevations.split(",")
            radius = radius.split(",")
            center = center.split(",")
            orbit_azimuths = [float(item) for item in azimuths]
            orbit_elevations = [float(item) for item in elevations]
            orbit_radius = [float(item) for item in radius]
            orbit_center = [float(item) for item in center]
            orbit_lists = [orbit_azimuths, orbit_elevations, orbit_radius, orbit_center, orbit_center, orbit_center]
        elif orbitpose_preset == "Era3D(6)" or orbitpose_preset == "Hunyuan3D(6)":
            radius = radius.split(",")
            orbit_radius = [float(item) for item in radius]
            orbit_center = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            orbit_lists = [orbit_lists[0], orbit_lists[1], orbit_radius, orbit_center, orbit_center, orbit_center]
        elif orbitpose_preset == "Unique3D(4)" or orbitpose_preset == "CharacterGen(4)":
            radius = radius.split(",")
            orbit_radius = [float(item) for item in radius]
            orbit_radius.pop(4)
            orbit_radius.pop(4)
            orbit_center = [0.0, 0.0, 0.0, 0.0]
            orbit_lists = [orbit_lists[0], orbit_lists[1], orbit_radius, orbit_center, orbit_center, orbit_center]
        
        orbit_camposes = []

        for i in range(0, len(orbit_lists[0])):
            orbit_camposes.append([orbit_lists[2][i], orbit_lists[1][i], orbit_lists[0][i], orbit_lists[3][i], orbit_lists[4][i], orbit_lists[5][i]])
        
        return (orbit_lists, orbit_camposes,)

class OrbitLists_to_OrbitPoses_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbit_lists": ("ORBIT_CAMPOSES",),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_camposes",)
    
    FUNCTION = "convert_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    
    def convert_orbit_poses(self, orbit_lists):
        
        orbit_camposes = []

        for i in range(0, len(orbit_lists[0])):
            orbit_camposes.append([orbit_lists[2][i], orbit_lists[1][i], orbit_lists[0][i], orbit_lists[3][i], orbit_lists[4][i], orbit_lists[5][i]])
        
        return (orbit_camposes,)

class OrbitPoses_to_OrbitLists_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbit_camposes": ("ORBIT_CAMPOSES",),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_lists",)
    
    FUNCTION = "convert_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    
    def convert_orbit_poses(self, orbit_camposes):
        
        orbit_azimuths = []
        orbit_elevations = []
        orbit_radius = []
        orbit_center0 = []
        orbit_center1 = []
        orbit_center2 = []

        for i in range(0, len(orbit_camposes)):
            orbit_azimuths.append(orbit_camposes[i][2])
            orbit_elevations.append(orbit_camposes[i][1])
            orbit_radius.append(orbit_camposes[i][0])
            orbit_center0.append(orbit_camposes[i][3])
            orbit_center1.append(orbit_camposes[i][4])
            orbit_center2.append(orbit_camposes[i][5])
        
        orbit_lists = [orbit_azimuths, orbit_elevations, orbit_radius, orbit_center0, orbit_center1, orbit_center2]
        
        return (orbit_lists,)

#---------------------------------------------------------------------------------------------------------------------#
# Test Nodes
#---------------------------------------------------------------------------------------------------------------------#
class RandomBeats_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
    
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff}),
                "X_start": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff}),
                "X_end": ("INT", {"default": 4, "min": 1, "max": 0xffffffffffffffff}),
                "Y_start": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff}),
                "Y_end": ("INT", {"default": 4, "min": 1, "max": 0xffffffffffffffff}),
                "Z_start": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff}),
                "Z_end": ("INT", {"default": 23, "min": 1, "max": 0xffffffffffffffff}),
                "max_items_per_count": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                "max_items_odds": ("INT", {"default": 5, "min": 0, "max": 10}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("BEATSTEXT", )
    FUNCTION = "gen_beats"
    CATEGORY = icons.get("JK/Misc")

    def gen_beats(self, count, X_start, X_end, Y_start, Y_end, Z_start, Z_end, max_items_per_count, max_items_odds):
    
        beatstext = ""
        
        for i in range(0, count):
            
            if max_items_per_count == 1 or max_items_odds == 0:
                randomItem = 1
            else:
                randomItemOdds = random.randint(1, 10)
                randomItem = random.randint(1, max_items_per_count if randomItemOdds <= max_items_odds else 1)
            
            for j in range(0, randomItem):
            
                randomX = random.randint(X_start, X_end)
                randomY = random.randint(Y_start, Y_end)
                randomZ = random.randint(Z_start, Z_end)
                
                pretext = "  - mTextVal: " if j == 0 else ""
                endtext = "\n" if j == (randomItem-1) else ""
                beatstext = f"{beatstext}{pretext}{randomX}_{randomY}_{randomZ},{endtext}"
        
        print(beatstext)
        return(beatstext,)

#---------------------------------------------------------------------------------------------------------------------#
# MAPPINGS
#---------------------------------------------------------------------------------------------------------------------#
# For reference only, actual mappings are in __init__.py
'''
NODE_CLASS_MAPPINGS = { 
    ### Misc Nodes
    "CR SD1.5 Aspect Ratio JK": CR_AspectRatioSD15_JK,
    "CR SDXL Aspect Ratio JK": CR_AspectRatioSDXL_JK,
    "CR SD3 Aspect Ratio JK": CR_AspectRatioSD3_JK,
    "CR Aspect Ratio JK": CR_AspectRatio_JK,
    "Tiling Mode JK": TilingMode_JK,
    "Empty Latent Color JK": EmptyLatentColor_JK,
    "Random Beats JK": RandomBeats_JK,
    "SDXL Target Res JK": SDXL_TargetRes_JK,
    "Get Size JK": GetSize_JK,
    "Image Crop by Mask Resolution JK": ImageCropByMaskResolution_JK,
    "Image Crop by Mask Params JK": ImageCropByMaskParams_JK,
    "Upscale Method JK": UpscaleMethod_JK,
    "Latent Crop Offset JK": LatentCropOffset_JK,
    "Scale To Resolution JK": ScaleToResolution_JK,
    "Inject Noise Params JK": Inject_Noise_Params_JK,
    "SD3 Prompts Switch JK": SD3_Prompts_Switch_JK,
    ### Reroute Nodes
    "Reroute List JK": RerouteList_JK,
    "Reroute Ckpt JK": RerouteCkpt_JK,
    "Reroute Vae JK": RerouteVae_JK,
    "Reroute Sampler JK": RerouteSampler_JK,
    "Reroute Upscale JK": RerouteUpscale_JK,
    "Reroute Resize JK": RerouteResize_JK,
    "Reroute String JK": RerouteString_JK,
    "String To Combo JK": StringToCombo_JK,
    ### ControlNet Nodes
    "CR ControlNet Loader JK": CR_ControlNetLoader_JK,
    "CR Multi-ControlNet Stack JK": CR_ControlNetStack_JK,
    "CR Multi-ControlNet Param Stack JK": CR_ControlNetParamStack_JK,
    "CR Apply ControlNet JK": CR_ApplyControlNet_JK,
    "CR Apply Multi-ControlNet JK": CR_ApplyControlNetStack_JK,
    "CR Apply Multi-ControlNet Adv JK": CR_ApplyControlNetStackAdv_JK,
    ### LoRA Nodes
    "CR Load LoRA JK": CR_LoraLoader_JK,
    "CR LoRA Stack JK": CR_LoRAStack_JK,
    "CR Apply LoRA Stack JK": CR_ApplyLoRAStack_JK,
    ### Embedding Nodes
    "Embedding Picker JK": EmbeddingPicker_JK,
    "Embedding Picker Multi JK": EmbeddingPicker_Multi_JK,
    ### Loader Nodes
    "Ckpt Loader JK": CkptLoader_JK,
    "Vae Loader JK": VaeLoader_JK,
    "Sampler Loader JK": SamplerLoader_JK,
    "Upscale Model Loader JK": UpscaleModelLoader_JK,
    ### Pipe Nodes
    "NodesState JK": NodesState_JK,
    "Ksampler Parameters JK": KsamplerParameters_JK,
    "Ksampler Parameters Default JK": KsamplerParametersDefault_JK,
    "Guidance Default JK": GuidanceDefault_JK,
    "Project Setting JK": ProjectSetting_JK,
    "Base Model Parameters JK": BaseModelParameters_JK,
    "Base Model Parameters Extract JK": BaseModelParametersExtract_JK,
    "Base Image Parameters Extract JK": BaseImageParametersExtract_JK,
    "Base Model Pipe JK": BaseModelPipe_JK,
    "Base Model Pipe Extract JK": BaseModelPipeExtract_JK,
    "Base Model Parameters SD3API JK": BaseModelParametersSD3API_JK,
    "Refine Pipe JK": RefinePipe_JK,
    "Refine Pipe Extract JK": RefinePipeExtract_JK,
    "Noise Injection Parameters JK": NoiseInjectionParameters_JK,
    "Noise Injection Pipe Extract JK": NoiseInjectionPipeExtract_JK,
    "Refine Model Parameters JK": RefineModelParameters_JK,
    "Refine 1 Parameters Extract JK": Refine1ParametersExtract_JK,
    "Refine 2 Parameters Extract JK": Refine2ParametersExtract_JK,
    "Upscale Model Parameters JK": UpscaleModelParameters_JK,
    "Image Upscale Parameters Extract JK": ImageUpscaleParametersExtract_JK,
    "Latent Upscale Parameters Extract JK": LatentUpscaleParametersExtract_JK,
    "Upscale Model Parameters Extract JK": UpscaleModelParametersExtract_JK,
    "Detailer Parameters JK": DetailerParameters_JK,
    "Pipe End JK": PipeEnd_JK,
    "Metadata Pipe JK": MetadataPipe_JK,
    "Metadata Pipe Extract JK": MetadataPipeExtract_JK,
    ### Image Nodes
    "Save Image with Metadata JK": ImageSaveWithMetadata_JK,
    "Save Image with Metadata Flow JK": ImageSaveWithMetadata_Flow_JK,
    "Load Image With Metadata JK": LoadImageWithMetadata_JK,
    "Load Image With Alpha JK": LoadImageWithAlpha_JK,
    "Make Image Grid JK": MakeImageGrid_JK,
    "Split Image Grid JK": SplitImageGrid_JK,
    "HintImageEnchance JK": HintImageEnchance_JK,
    "Image Resize Mode JK": ImageResizeMode_JK,
    "Image Remove Alpha JK": ImageRemoveAlpha_JK,
    "Color Grading JK": ColorGrading_JK,
    ### Mask Nodes
    "Is Mask Empty JK": IsMaskEmpty_JK,
    ### Animation Nodes
    "Animation Prompt JK": AnimPrompt_JK,
    "Animation Value JK": AnimValue_JK,
    ### Logic Switches Nodes
    "CR Boolean JK": CR_Boolean_JK,
    "CR Int Input Switch JK": CR_IntInputSwitch_JK,
    "CR Float Input Switch JK": CR_FloatInputSwitch_JK,
    "CR Image Input Switch JK": CR_ImageInputSwitch_JK,
    "CR Mask Input Switch JK": CR_MaskInputSwitch_JK,
    "CR Latent Input Switch JK": CR_LatentInputSwitch_JK,
    "CR Conditioning Input Switch JK": CR_ConditioningInputSwitch_JK,
    "CR Clip Input Switch JK": CR_ClipInputSwitch_JK,
    "CR Model Input Switch JK": CR_ModelInputSwitch_JK,
    "CR ControlNet Input Switch JK": CR_ControlNetInputSwitch_JK,
    "CR ControlNet Stack Input Switch JK": CR_ControlNetStackInputSwitch_JK,
    "CR Text Input Switch JK": CR_TextInputSwitch_JK,
    "CR VAE Input Switch JK": CR_VAEInputSwitch_JK,
    "CR Pipe Input Switch JK": CR_PipeInputSwitch_JK,
    "CR Impact Pipe Input Switch JK": CR_ImpactPipeInputSwitch_JK,
    "CR Noise Input Switch JK": CR_NoiseInputSwitch_JK,
    "CR Guider Input Switch JK": CR_GuiderInputSwitch_JK,
    "CR Sampler Input Switch JK": CR_SamplerInputSwitch_JK,
    "CR Sigmas Input Switch JK": CR_SigmasInputSwitch_JK,
    "CR Mesh Input Switch JK": CR_MeshInputSwitch_JK,
    "CR Ply Input Switch JK": CR_PlyInputSwitch_JK,
    "CR Obit Pose Input Switch JK": CR_ObitPoseInputSwitch_JK,
    ### ComfyMath Fix Nodes
    "CM_BoolToInt JK": BoolToInt_JK,
    "CM_IntToBool JK": IntToBool_JK,
    "CM_BoolUnaryOperation JK": BoolUnaryOperation_JK,
    "CM_BoolBinaryOperation JK": BoolBinaryOperation_JK,
    "Bool Binary And JK": BoolBinaryAnd_JK,
    "Bool Binary OR JK": BoolBinaryOR_JK,
    "CM_StringBinaryCondition_JK": StringBinaryCondition_JK,
    "CM_PromptCombine_JK": PromptCombine_JK,
    "CM_FloatUnaryCondition JK": FloatUnaryCondition_JK,
    "CM_FloatBinaryCondition JK": FloatBinaryCondition_JK,
    "CM_IntUnaryCondition JK": IntUnaryCondition_JK,
    "CM_IntBinaryCondition JK": IntBinaryCondition_JK,
    "CM_NumberUnaryCondition JK": NumberUnaryCondition_JK,
    "CM_NumberBinaryCondition JK": NumberBinaryCondition_JK,
    "CM_Vec2UnaryCondition JK": Vec2UnaryCondition_JK,
    "CM_Vec2BinaryCondition JK": Vec2BinaryCondition_JK,
    "CM_Vec2ToFloatUnaryOperation JK": Vec2ToFloatUnaryOperation_JK,
    "CM_Vec2ToFloatBinaryOperation JK": Vec2ToFloatBinaryOperation_JK,
    "CM_Vec2FloatOperation_JK": Vec2FloatOperation_JK,
    "CM_Vec3UnaryCondition JK": Vec3UnaryCondition_JK,
    "CM_Vec3BinaryCondition JK": Vec3BinaryCondition_JK,
    "CM_Vec3ToFloatUnaryOperation JK": Vec3ToFloatUnaryOperation_JK,
    "CM_Vec3ToFloatBinaryOperation JK": Vec3ToFloatBinaryOperation_JK,
    "CM_Vec3FloatOperation_JK": Vec3FloatOperation_JK,
    "CM_Vec4UnaryCondition JK": Vec4UnaryCondition_JK,
    "CM_Vec4BinaryCondition JK": Vec4BinaryCondition_JK,
    "CM_Vec4ToFloatUnaryOperation JK": Vec4ToFloatUnaryOperation_JK,
    "CM_Vec4ToFloatBinaryOperation JK": Vec4ToFloatBinaryOperation_JK,
    "CM_Vec4FloatOperation_JK": Vec4FloatOperation_JK,
    ### ComfyMath Nodes
    "CM_FloatToInt JK": FloatToInt_JK,
    "CM_IntToFloat JK": IntToFloat_JK,
    "CM_IntToNumber JK": IntToNumber_JK,
    "CM_NumberToInt JK": NumberToInt_JK,
    "CM_FloatToNumber JK": FloatToNumber_JK,
    "CM_NumberToFloat JK": NumberToFloat_JK,
    "CM_ComposeVec2 JK": ComposeVec2_JK,
    "CM_ComposeVec3 JK": ComposeVec3_JK,
    "CM_ComposeVec4 JK": ComposeVec4_JK,
    "CM_BreakoutVec2 JK": BreakoutVec2_JK,
    "CM_BreakoutVec3 JK": BreakoutVec3_JK,
    "CM_BreakoutVec4 JK": BreakoutVec4_JK,
    "CM_FloatUnaryOperation JK": FloatUnaryOperation_JK,
    "CM_FloatBinaryOperation JK": FloatBinaryOperation_JK,
    "CM_IntUnaryOperation JK": IntUnaryOperation_JK,
    "CM_IntBinaryOperation JK": IntBinaryOperation_JK,
    "CM_NumberUnaryOperation JK": NumberUnaryOperation_JK,
    "CM_NumberBinaryOperation JK": NumberBinaryOperation_JK,
    "CM_Vec2UnaryOperation JK": Vec2UnaryOperation_JK,
    "CM_Vec2BinaryOperation JK": Vec2BinaryOperation_JK,
    "CM_Vec3UnaryOperation JK": Vec3UnaryOperation_JK,
    "CM_Vec3BinaryOperation JK": Vec3BinaryOperation_JK,
    "CM_Vec4UnaryOperation JK": Vec4UnaryOperation_JK,
    "CM_Vec4BinaryOperation JK": Vec4BinaryOperation_JK,
    ### Simple Evaluate Nodes
    "Evaluate Ints JK": EvaluateInts_JK,
    "Evaluate Floats JK": EvaluateFloats_JK,
    "Evaluate Strings JK": EvaluateStrs_JK,
    "Evaluate Examples JK": EvalExamples_JK,
    ### 3D Nodes
    "Orbit Poses JK": OrbitPoses_JK,
    "OrbitLists to OrbitPoses JK": OrbitLists_to_OrbitPoses_JK,
    "OrbitPoses to OrbitLists JK": OrbitPoses_to_OrbitLists_JK,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    ### Misc Nodes
    "CR SD1.5 Aspect Ratio JK": "SD1.5 Aspect Ratio JK🐉",
    "CR SDXL Aspect Ratio JK": "SDXL Aspect Ratio JK🐉",
    "CR SD3 Aspect Ratio JK": "SD3 Aspect Ratio JK🐉",
    "CR Aspect Ratio JK": "Aspect Ratio JK🐉",
    "Tiling Mode JK": "Tiling Mode JK🐉",
    "Empty Latent Color JK": "Empty Latent Color JK🐉",
    "Random Beats JK": "Random Beats JK🐉",
    "SDXL Target Res JK": "SDXL Target Res JK🐉",
    "Get Size JK": "Get Size JK🐉",
    "Image Crop by Mask Resolution JK": "Image Crop by Mask Resolution JK🐉",
    "Image Crop by Mask Params JK": "Image Crop by Mask Params JK🐉",
    "Upscale Method JK": "Upscale Method JK🐉",
    "Latent Crop Offset JK": "Latent Crop Offset JK🐉",
    "Scale To Resolution JK": "Scale To Resolution JK🐉",
    "Inject Noise Params JK": "Inject Noise Params JK🐉",
    "SD3 Prompts Switch JK": "SD3 Prompts Switch JK🐉",
    ### Reroute Nodes
    "Reroute List JK": "Reroute List JK🐉",
    "Reroute Ckpt JK": "Reroute Ckpt JK🐉",
    "Reroute Vae JK": "Reroute Vae JK🐉",
    "Reroute Sampler JK": "Reroute Sampler JK🐉",
    "Reroute Upscale JK": "Reroute Upscale JK🐉",
    "Reroute Resize JK": "Reroute Resize JK🐉",
    "Reroute String JK": "Reroute String JK🐉",
    "String To Combo JK": "String To Combo JK🐉",
    ### ControlNet Nodes
    "CR ControlNet Loader JK": "ControlNet Loader JK🐉",
    "CR Multi-ControlNet Stack JK": "Multi-ControlNet Stack JK🐉",
    "CR Multi-ControlNet Param Stack JK": "Multi-ControlNet Param Stack JK🐉",
    "CR Apply ControlNet JK": "Apply ControlNet JK🐉",
    "CR Apply Multi-ControlNet JK": "Apply Multi-ControlNet JK🐉",
    "CR Apply Multi-ControlNet Adv JK": "Apply Multi-ControlNet Adv JK🐉",
    ### LoRA Nodes
    "CR Load LoRA JK": "Load LoRA JK🐉",
    "CR LoRA Stack JK": "LoRA Stack JK🐉",
    "CR Apply LoRA Stack JK": "Apply LoRA Stack JK🐉",
    ### Embedding Nodes
    "Embedding Picker JK": "Embedding Picker JK🐉",
    "Embedding Picker Multi JK": "Embedding Picker Multi JK🐉",
    ### Loader Nodes
    "Ckpt Loader JK": "Ckpt Loader JK🐉",
    "Vae Loader JK": "Vae Loader JK🐉",
    "Sampler Loader JK": "Sampler Loader JK🐉",
    "Upscale Model Loader JK": "Upscale Model Loader JK🐉",
    ### Pipe Nodes
    "NodesState JK": "Nodes State JK🐉",
    "Ksampler Parameters JK": "Ksampler Parameters JK🐉",
    "Ksampler Parameters Default JK": "Ksampler Parameters Default JK🐉",
    "Guidance Default JK": "Guidance Default JK🐉",
    "Project Setting JK": "Project Setting JK🐉",
    "Base Model Parameters JK": "Base Model Parameters JK🐉",
    "Base Model Parameters Extract JK": "Base Model Parameters Extract JK🐉",
    "Base Image Parameters Extract JK": "Base Image Parameters Extract JK🐉",
    "Base Model Pipe JK": "Base Model Pipe JK🐉",
    "Base Model Pipe Extract JK": "Base Model Pipe Extract JK🐉",
    "Base Model Parameters SD3API JK": "Base Model Parameters SD3API JK🐉",
    "Refine Pipe JK": "Refine Pipe JK🐉",
    "Refine Pipe Extract JK": "Refine Pipe Extract JK🐉",
    "Noise Injection Parameters JK": "Noise Injection Parameters JK🐉",
    "Noise Injection Pipe Extract JK": "Noise Injection Pipe Extract JK🐉",
    "Refine Model Parameters JK": "Refine Model Parameters JK🐉",
    "Refine 1 Parameters Extract JK": "Refine 1 Parameters Extract JK🐉",
    "Refine 2 Parameters Extract JK": "Refine 2 Parameters Extract JK🐉",
    "Upscale Model Parameters JK":"Upscale Model Parameters JK🐉",
    "Image Upscale Parameters Extract JK": "Image Upscale Parameters Extract JK🐉",
    "Latent Upscale Parameters Extract JK": "Latent Upscale Parameters Extract JK🐉",
    "Upscale Model Parameters Extract JK": "Upscale Model Parameters Extract JK🐉",
    "Detailer Parameters JK": "Detailer Parameters JK🐉",
    "Pipe End JK": "Pipe End JK🐉",
    "Metadata Pipe JK": "Metadata Pipe JK🐉",
    "Metadata Pipe Extract JK": "Metadata Pipe Extract JK🐉",
    ### Image Nodes
    "Save Image with Metadata JK": "Save Image With Metadata JK🐉",
    "Save Image with Metadata Flow JK": "Save Image With Metadata Flow JK🐉",
    "Load Image With Metadata JK": "Load Image With Metadata JK🐉",
    "Load Image With Alpha JK": "Load Image With Alpha JK🐉",
    "Make Image Grid JK": "Make Image Grid JK🐉",
    "Split Image Grid JK": "Split Image Grid JK🐉",
    "HintImageEnchance JK": "Enchance And Resize Hint Images JK🐉",
    "Image Resize Mode JK": "Image Resize Mode JK🐉",
    "Image Remove Alpha JK": "Image Remove Alpha JK🐉",
    "Color Grading JK": "Color Grading JK🐉",
    ### Mask Nodes
    "Is Mask Empty JK": "Is Mask Empty JK🐉",
    ### Animation Nodes
    "Animation Prompt JK": "Animation Prompt JK🐉",
    "Animation Value JK": "Animation Value JK🐉",
    ### Logic Switches Nodes
    "CR Boolean JK": "Boolean JK🐉",
    "CR Image Input Switch JK": "Image Input Switch JK🐉",
    "CR Mask Input Switch JK": "Mask Input Switch JK🐉",
    "CR Int Input Switch JK": "Int Input Switch JK🐉",
    "CR Float Input Switch JK": "Float Input Switch JK🐉",
    "CR Latent Input Switch JK": "Latent Input Switch JK🐉",
    "CR Conditioning Input Switch JK": "Conditioning Input Switch JK🐉",
    "CR Clip Input Switch JK": "Clip Input Switch JK🐉",
    "CR Model Input Switch JK": "Model Input Switch JK🐉",
    "CR ControlNet Input Switch JK": "ControlNet Input Switch JK🐉",
    "CR ControlNet Stack Input Switch JK": "ControlNet Stack Input Switch JK🐉",
    "CR Text Input Switch JK": "Text Input Switch JK🐉",
    "CR VAE Input Switch JK": "VAE Input Switch JK🐉",
    "CR Pipe Input Switch JK": "Pipe Input Switch JK🐉",
    "CR Impact Pipe Input Switch JK": "Impact Pipe Input Switch JK🐉",
    "CR Noise Input Switch JK": "Noise Input Switch JK🐉",
    "CR Guider Input Switch JK": "Guider Input Switch JK🐉",
    "CR Sampler Input Switch JK": "Sampler Input Switch JK🐉",
    "CR Sigmas Input Switch JK": "Sigmas Input Switch JK🐉",
    "CR Mesh Input Switch JK": "Mesh Input Switch JK🐉",
    "CR Ply Input Switch JK": "Ply Input Switch JK🐉",
    "CR Orbit Pose Input Switch JK": "Orbit Pose Input Switch JK🐉",
    ### ComfyMath Fix Nodes
    "CM_BoolToInt JK": "BoolToInt JK🐉",
    "CM_IntToBool JK": "IntToBool JK🐉",
    "CM_BoolUnaryOperation JK": "BoolUnaryOp JK🐉",
    "CM_BoolBinaryOperation JK": "BoolBinaryOp JK🐉",
    "Bool Binary And JK": "Bool And JK🐉",
    "Bool Binary OR JK": "Bool OR JK🐉",
    "CM_StringBinaryCondition_JK": "StringBinaryCon JK🐉",
    "CM_PromptCombine_JK": "Prompt Combine JK🐉",
    "CM_FloatUnaryCondition JK": "FloatUnaryCon JK🐉",
    "CM_FloatBinaryCondition JK": "FloatBinaryCon JK🐉",
    "CM_IntUnaryCondition JK": "IntUnaryCon JK🐉",
    "CM_IntBinaryCondition JK": "IntBinaryCon JK🐉",
    "CM_NumberUnaryCondition JK": "NumberUnaryCon JK🐉",
    "CM_NumberBinaryCondition JK": "NumberBinaryCon JK🐉",
    "CM_Vec2UnaryCondition JK": "Vec2UnaryCon JK🐉",
    "CM_Vec2BinaryCondition JK": "Vec2BinaryCon JK🐉",
    "CM_Vec2ToFloatUnaryOperation JK": "Vec2ToFloatUnaryOp JK🐉",
    "CM_Vec2ToFloatBinaryOperation JK": "Vec2ToFloatBinaryOp JK🐉",
    "CM_Vec2FloatOperation_JK": "Vec2FloatOp JK🐉",
    "CM_Vec3UnaryCondition JK": "Vec3UnaryCon JK🐉",
    "CM_Vec3BinaryCondition JK": "Vec3BinaryCon JK🐉",
    "CM_Vec3ToFloatUnaryOperation JK": "Vec3ToFloatUnaryOp JK🐉",
    "CM_Vec3ToFloatBinaryOperation JK": "Vec3ToFloatBinaryOp JK🐉",
    "CM_Vec3FloatOperation_JK": "Vec3FloatOp JK🐉",
    "CM_Vec4UnaryCondition JK": "Vec4UnaryCon JK🐉",
    "CM_Vec4BinaryCondition JK": "Vec4BinaryCon JK🐉",
    "CM_Vec4ToFloatUnaryOperation JK": "Vec4ToFloatUnaryOp JK🐉",
    "CM_Vec4ToFloatBinaryOperation JK": "Vec4ToFloatBinaryOp JK🐉",
    "CM_Vec4FloatOperation_JK": "Vec4FloatOp JK🐉",
    ### ComfyMath Nodes
    "CM_FloatToInt JK": "FloatToInt JK🐉",
    "CM_IntToFloat JK": "IntToFloat JK🐉",
    "CM_IntToNumber JK": "IntToNumber JK🐉",
    "CM_NumberToInt JK": "NumberToInt JK🐉",
    "CM_FloatToNumber JK": "FloatToNumber JK🐉",
    "CM_NumberToFloat JK": "NumberToFloat JK🐉",
    "CM_ComposeVec2 JK": "ComposeVec2 JK🐉",
    "CM_ComposeVec3 JK": "ComposeVec3 JK🐉",
    "CM_ComposeVec4 JK": "ComposeVec4 JK🐉",
    "CM_BreakoutVec2 JK": "BreakoutVec2 JK🐉",
    "CM_BreakoutVec3 JK": "BreakoutVec3 JK🐉",
    "CM_BreakoutVec4 JK": "BreakoutVec4 JK🐉",
    "CM_FloatUnaryOperation JK": "FloatUnaryOp JK🐉",
    "CM_FloatBinaryOperation JK": "FloatBinaryOp JK🐉",
    "CM_IntUnaryOperation JK": "IntUnaryOp JK🐉",
    "CM_IntBinaryOperation JK": "IntBinaryOp JK🐉",
    "CM_NumberUnaryOperation JK": "NumberUnaryOp JK🐉",
    "CM_NumberBinaryOperation JK": "NumberBinaryOp JK🐉",
    "CM_Vec2UnaryOperation JK": "Vec2UnaryOp JK🐉",
    "CM_Vec2BinaryOperation JK": "Vec2BinaryOp JK🐉",
    "CM_Vec3UnaryOperation JK": "Vec3UnaryOp JK🐉",
    "CM_Vec3BinaryOperation JK": "Vec3BinaryOp JK🐉",
    "CM_Vec4UnaryOperation JK": "Vec4UnaryOp JK🐉",
    "CM_Vec4BinaryOperation JK": "Vec4BinaryOp JK🐉",
    ### Simple Evaluate Nodes
    "Evaluate Ints JK": "Evaluate Ints JK🐉",
    "Evaluate Floats JK": "Evaluate Floats JK🐉",
    "Evaluate Strings JK": "Evaluate Strings JK🐉",
    "Evaluate Examples JK": "Evaluate Examples JK🐉",
    ### 3D Nodes
    "Orbit Poses JK": "Orbit Poses JK🐉",
    "OrbitLists to OrbitPoses JK": "OrbitLists to OrbitPoses JK🐉",
    "OrbitPoses to OrbitLists JK": "OrbitPoses to OrbitLists JK🐉",
}    
'''