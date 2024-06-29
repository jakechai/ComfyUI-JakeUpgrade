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
#   Animation Nodes
#   Logic switches Nodes
#   ComfyMath Fix Nodes
#   ComfyMath Nodes
#   Simple Evaluate Nodes
#   3D Nodes (WIP)
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
from nodes import MAX_RESOLUTION, ControlNetApply, ControlNetApplyAdvanced
from pathlib import Path
from typing import Any, Callable, Mapping, TypeAlias
from PIL import Image, ImageOps
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
    elif resolution == "SDXL 1088x896":
        width, height = 1088, 896
    elif resolution == "SDXL 1152x896":
        width, height = 1152, 896
    elif resolution == "SDXL 1152x832":
        width, height = 1152, 832
    elif resolution == "SDXL 1216x832":
        width, height = 1216, 832
    elif resolution == "SDXL 1280x768":
        width, height = 1280, 768
    elif resolution == "SDXL 1344x768":
        width, height = 1344, 768
    elif resolution == "SDXL 1344x704":
        width, height = 1344, 704
    elif resolution == "SDXL 1408x704":
        width, height = 1408, 704
    elif resolution == "SDXL 1472x704":
        width, height = 1472, 704
    elif resolution == "SDXL 1536x640":
        width, height = 1536, 640
    elif resolution == "SDXL 1600x640":
        width, height = 1600, 640
    elif resolution == "SDXL 1664x576":
        width, height = 1664, 576
    elif resolution == "SDXL 1728x576":
        width, height = 1728, 576
    
    return (width, height)

# A special class that is always equal in not equal comparisons. Credit to pythongosssss
class AnyType(str):

  def __ne__(self, __value: object) -> bool:
    return False

any_type = AnyType("*")

upscalemodels = {
    "1xPSNR.pth": float(1.0),
    "2xPSNR.pth": float(2.0),
    "4xPSNR.pth": float(4.0),
    "8xPSNR.pth": float(8.0),
    "16xPSNR.pth": float(16.0),
    "1x-ITF-SkinDiffDetail-Lite-v1.pth": float(1.0),
    "4x_NMKD-Siax_200k.pth": float(4.0),
    "4x_Nickelback_70000G.pth": float(4.0),
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
                "custom_width": ("INT", {"default": 512, "min": 64, "max": 2048, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": 2048, "step": 8}),
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

class CR_SDXLAspectRatio_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "resolution": (["Custom", "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SDXL 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SDXL 1216x832", "SDXL 1280x768",
                "SDXL 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SDXL 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
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

#---------------------------------------------------------------------------------------------------------------------#
# Reroute Nodes
#---------------------------------------------------------------------------------------------------------------------#
class RerouteList_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),{"forceInput": True}),
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"],{"forceInput": True}),
                "sampler": (comfy.samplers.KSampler.SAMPLERS,{"forceInput": True}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,{"forceInput": True}),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),{"forceInput": True}),
            },
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
            },
            "optional": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),{"forceInput": True}),
            },
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
            },
            "optional": {
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"],{"forceInput": True}),
            },
        }

    RETURN_TYPES = (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"],)
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
            },
            "optional": {
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
            },
            "optional": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),{"forceInput": True}),
            },
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
            },
            "optional": {
                "image_resize": (["Just Resize", "Crop and Resize", "Resize and Fill"], {"default": "Crop and Resize", "forceInput": True}),
            },
        }

    RETURN_TYPES = (["Just Resize", "Crop and Resize", "Resize and Fill"],)
    RETURN_NAMES = ("IMAGE_RESIZE",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")

    def route(self, image_resize=None):
        return (image_resize,)

#---------------------------------------------------------------------------------------------------------------------#
# ControlNet Nodes
#---------------------------------------------------------------------------------------------------------------------#
class CR_ApplyControlNet_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
                "control_net": ("CONTROL_NET", ),
                "image": ("IMAGE", ),
                "switch": ("BOOLEAN", {"default": False},),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01})
            }
        }
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "apply_controlnet"

    CATEGORY = icons.get("JK/ControlNet")

    def apply_controlnet(self, conditioning, control_net, image, switch, strength):
        if strength == 0 or switch == False:
            return (conditioning, )

        c = []
        control_hint = image.movedim(-1,1)
        for t in conditioning:
            n = [t[0], t[1].copy()]
            c_net = control_net.copy().set_cond_hint(control_hint, strength)
            if 'control' in t[1]:
                c_net.set_previous_controlnet(t[1]['control'])
            n[1]['control'] = c_net
            c.append(n)
        return (c, )

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

class CR_ApplyControlNetStack_JK:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_positive": ("CONDITIONING",),
                "base_negative": ("CONDITIONING",),
                "ControlNet_switch": ("BOOLEAN", {"default": False},),
                "controlnet_stack": ("CONTROL_NET_STACK", ),
            }
        }                    

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet_stack"
    CATEGORY = icons.get("JK/ControlNet")

    def apply_controlnet_stack(self, base_positive, base_negative, ControlNet_switch, controlnet_stack=None,):

        if ControlNet_switch == False:
            return (base_positive, base_negative, )
    
        if controlnet_stack is not None:
            for controlnet_tuple in controlnet_stack:
                controlnet_name, image, strength, start_percent, end_percent  = controlnet_tuple
                
                if type(controlnet_name) == str:
                    controlnet_path = folder_paths.get_full_path("controlnet", controlnet_name)
                    controlnet = comfy.sd.load_controlnet(controlnet_path)
                else:
                    controlnet = controlnet_name
                
                controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(base_positive, base_negative,
                                                                                     controlnet, image, strength,
                                                                                     start_percent, end_percent)

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
                
                if loraweight != "1.000":
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

#---------------------------------------------------------------------------------------------------------------------#
# TI Nodes
#---------------------------------------------------------------------------------------------------------------------#
class EmbeddingPicker_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
            },
            "optional": {
                "text_in": ("STRING", {"forceInput": True}),
                "metadata_in": ("STRING", {"forceInput": True}),
                "embedding": (folder_paths.get_filename_list("embeddings"),),
                "emphasis": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05,},),
                "append": ("BOOLEAN", {"default": True},),
                "save_hash": ("BOOLEAN", {"default": True},),
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
    
        textout = f"{text_in}," if text_in != None else ","
        metaout = metadata_in if metadata_in != None else ""
        
        if input_mode == "simple":
            append_check = True
        elif input_mode == "advanced":
            append_check = kwargs.get(f"append_{i}")
        
        j = 0
        
        for i in range(1, embedding_count + 1):
            
            if kwargs.get(f"embedding_{i}") == True and kwargs.get(f"embedding_name_{i}") != "None" and kwargs.get(f"emphasis_{i}") >= 0.05:

                emb = "embedding:" + Path(kwargs.get(f"embedding_name_{i}")).stem
                emphasis = f"{kwargs.get(f'emphasis_{i}'):.3f}"
                if emphasis != "1.000":
                    emb = f"({emb}:{emphasis})"

                if (text_in == None or text_in == "") and j == 0:
                    textout = f"{emb}"
                elif text_in != None and text_in != "" and j == 0:
                    textout = f"{text_in},{emb}" if append_check else f"{emb},{text_in}"
                else:
                    textout = f"{textout},{emb}" if append_check else f"{emb},{textout}"
                
                emb_path = folder_paths.get_full_path("embeddings", kwargs.get(f"embedding_name_{i}"))
                emb_name = Path(kwargs.get(f"embedding_name_{i}")).stem
                emb_hash = f": [{calculate_sha256(emb_path)[:12]}]" if save_hash == True else ""
                emb_meta = f"{emb_name}{emb_hash}"
                
                if (metadata_in == None or metadata_in == "") and j == 0:
                    metaout = f"{emb_meta}"
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
                "vae": (folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"],),
            },
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"])
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
            },
            "optional": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            },
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
            },
            "optional": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
            },
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
                                "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SDXL 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SDXL 1216x832", "SDXL 1280x768",
                                "SDXL 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SDXL 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
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
                "positive": ("STRING", {"default": '', "multiline": True}),
                "positive_clip": ("STRING", {"default": '', "multiline": True}),
                "negative": ("STRING", {"default": '', "multiline": True}),
                "negative_clip": ("STRING", {"default": '', "multiline": True}),
                "append_input_prompt": ("BOOLEAN", {"default": False},),
                "variation": ("STRING", {"default": '', "multiline": True}),
                "resolution": (["Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                                "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320", 
                                "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SDXL 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SDXL 1216x832", "SDXL 1280x768",
                                "SDXL 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SDXL 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.05}),
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

    def get_value(self, ckpt_name, vae_name, base_seed, positive, positive_clip, negative, negative_clip, append_input_prompt, variation, resolution, custom_width, custom_height, swap_dimensions, steps, sampler_name, scheduler, cfg, tiling, specified_vae, stop_at_clip_layer, img2img, image_resize, img2img_denoise, batch_size, save_ckpt_hash, image=None, input_positive=None, input_negative=None):
        
        if append_input_prompt == True and input_positive != None and input_negative != None:
            if input_positive != "":
                positive = f"{input_positive},{positive}"
            if input_negative != "":
                negative = f"{input_negative},{negative}"
        
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        img2img_denoise = 1.0 if img2img == False else img2img_denoise
        
        pipe_model = (ckpt_name, stop_at_clip_layer, positive, positive_clip, negative, negative_clip, variation, base_seed, steps, sampler_name, scheduler, cfg, img2img_denoise, tiling, specified_vae, vae_name)
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
        
        base_model_metadata = f"Steps: {steps}, Sampler: {sampler_name}{f' {scheduler}' if scheduler != 'normal' else ''}, CFG scale: {cfg}, Seed: {base_seed}, Size: {size_metadata}, {baseckpt_hash}Model: {baseckpt_name}, {basevae_metadata}{f'Denoising strength: {img2img_denoise_metadata}, ' if img2img == True else ''}Clip skip: {stop_layer_metadata}, RNG: CPU, "
        
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
            },
            "optional": {
                "base_model_pipe": ("PIPE_LINE",)
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "STRING", "STRING", "FLOAT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("Checkpoint", "Tiling", "Stop_Layer", "Positive", "Positive_Clip", "Negative", "Negative_Clip", "Variation", "Seed", "Steps", "Sampler", "Schedular", "Cfg", "Denoise", "Specified_VAE", "VAE")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, base_model_pipe=None):
        ckpt_name, stop_at_clip_layer, positive_prompt, positive_clip, negative_prompt, negative_clip, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, tiling, specified_vae, vae_name = base_model_pipe
        return (ckpt_name, tiling, stop_at_clip_layer, positive_prompt, positive_clip, negative_prompt, negative_clip, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, specified_vae, vae_name)

class BaseImageParametersExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
            },
            "optional": {
                "base_image_pipe": ("PIPE_LINE",)
            },
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
        
        positive_prompt = f"{positive_prompt}," if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f"{variation_prompt}," if variation_prompt !=None and variation_prompt != "" else ""
        lora_prompt = lora_prompt if lora_prompt !=None and lora_prompt != "" else ""
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
            },
            "optional": {
                "base_pipe": ("PIPE_LINE",)
            },
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

class NoiseInjectionParameters_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "noisy_latent_strength": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 1.0, "step": 0.01}),
                "img2img_injection_switch_at": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "base_steps": ("INT", {"forceInput": True}),
                "img2img": ("BOOLEAN", {"forceInput": True},),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT", "FLOAT", "INT")
    RETURN_NAMES = ("Noise_Injection_MetaData", "Img2img_Injection_1st_step_end", "Img2img_Injection_2nd_step_start", "Noisy_Latent_Strength", "Noise_Latent_seed")
    OUTPUT_NODE = True
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")

    def get_value(self, base_steps, seed, noisy_latent_strength, img2img_injection_switch_at, img2img=None):
        
        base_steps = base_steps if base_steps != None else 30
        img2img_injection_1st_step_end = int(base_steps * img2img_injection_switch_at)
        img2img_injection_2nd_step_start = img2img_injection_1st_step_end #+ 1
        
        img2img = img2img if img2img != None else False
        noiseinjection_metadata = f"Noise Injection Strength: {noisy_latent_strength}, Noise Injection Seed: {seed}, " if img2img == False else f"img2img Noise Injection switch at: {img2img_injection_switch_at}, img2img Noise Injection 1st end: {img2img_injection_1st_step_end}, img2img Noise Injection 2nd start: {img2img_injection_2nd_step_start}, "
        
        return (noiseinjection_metadata, img2img_injection_1st_step_end, img2img_injection_2nd_step_start, noisy_latent_strength, seed)

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
            "base_latent": ("LATENT",),
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

    def get_value(self, positive_conditioning=None, negative_conditioning=None, base_latent=None, positive_prompt=None, negative_prompt=None, variation_prompt=None):
        
        positive_prompt = f"{positive_prompt}," if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f"{variation_prompt}," if variation_prompt !=None and variation_prompt != "" else ""
        
        refine_pipe = (positive_conditioning, negative_conditioning, base_latent, positive_prompt, negative_prompt, variation_prompt)
        
        return (refine_pipe,)

class RefinePipeExtract_JK:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
            },
            "optional": {
                "refine_pipe": ("PIPE_LINE",)
            },
        }

    RETURN_TYPES = ("PIPE_LINE", "CONDITIONING", "CONDITIONING", "LATENT", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("Refine_Pipe", "Positive_Conditioning", "Negative_Conditioning", "Base_Latent", "Positive_Prompt", "Negative_Prompt", "Variation_Prompt",)
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    
    def flush(self, refine_pipe=None):
        if refine_pipe == None:
            Positive_Conditioning = None
            Negative_Conditioning = None
            Base_Latent = None
            Positive_Prompt = ""
            Negative_Prompt = ""
            Variation_Prompt = ""
        else:
            Positive_Conditioning, Negative_Conditioning, Base_Latent, Positive_Prompt, Negative_Prompt, Variation_Prompt = refine_pipe
        return (refine_pipe, Positive_Conditioning, Negative_Conditioning, Base_Latent, Positive_Prompt, Negative_Prompt, Variation_Prompt,)

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
                "image_name": ("STRING", {"forceInput": True}),
                "path_name": ("STRING", {"forceInput": True}),
                "counter": ("INT", {"forceInput": True}),
            },
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

#---------------------------------------------------------------------------------------------------------------------#
# Image Resize from ControlNet AUX
#---------------------------------------------------------------------------------------------------------------------#
RESIZE_MODES = ["Just Resize", "Crop and Resize", "Resize and Fill"]

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
    
    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("IMAGE", "METADATA",)
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
        
        return (torch.stack(outs, dim=0), METADATA,)
    
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
                "int_true": ("INT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            }
        }

    RETURN_TYPES = ("INT", "BOOLEAN",)
    FUNCTION = "InputInt"
    CATEGORY = icons.get("JK/Logic")

    def InputInt(self, boolean_value, int_false, int_true):
        if boolean_value == True:
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
                "float_true": ("FLOAT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615}),
            }
        }

    RETURN_TYPES = ("FLOAT", "BOOLEAN",)
    FUNCTION = "InputFloat"
    CATEGORY = icons.get("JK/Logic")

    def InputFloat(self, boolean_value, float_false, float_true):
        if boolean_value == True:
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
                "image_true": ("IMAGE",)
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN",)
    FUNCTION = "InputImages"
    CATEGORY = icons.get("JK/Logic")

    def InputImages(self, boolean_value, image_false, image_true):
        if boolean_value == True:
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
                "mask_true": ("MASK",)
            }
        }

    RETURN_TYPES = ("MASK", "BOOLEAN",)
    FUNCTION = "InputMasks"
    CATEGORY = icons.get("JK/Logic")

    def InputMasks(self, boolean_value, mask_false, mask_true):
        if boolean_value == True:
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
                "latent_true": ("LATENT",)
            }
        }

    RETURN_TYPES = ("LATENT", "BOOLEAN",)
    FUNCTION = "InputLatents"
    CATEGORY = icons.get("JK/Logic")

    def InputLatents(self, boolean_value, latent_false, latent_true):
        if boolean_value == True:
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
                "conditioning_true": ("CONDITIONING",)
            }
        }

    RETURN_TYPES = ("CONDITIONING", "BOOLEAN",)
    FUNCTION = "InputConditioning"
    CATEGORY = icons.get("JK/Logic")

    def InputConditioning(self, boolean_value, conditioning_false, conditioning_true):
        if boolean_value == True:
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
                "clip_true": ("CLIP",)
            }
        }

    RETURN_TYPES = ("CLIP", "BOOLEAN",)
    FUNCTION = "InputClip"
    CATEGORY = icons.get("JK/Logic")

    def InputClip(self, boolean_value, clip_false, clip_true):
        if boolean_value == True:
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
                "model_true": ("MODEL",)
            }
        }

    RETURN_TYPES = ("MODEL", "BOOLEAN",)
    FUNCTION = "InputModel"
    CATEGORY = icons.get("JK/Logic")

    def InputModel(self, boolean_value, model_false, model_true):
        if boolean_value == True:
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
                "control_net_true": ("CONTROL_NET",)
            }
        }
        
    RETURN_TYPES = ("CONTROL_NET", "BOOLEAN",)
    FUNCTION = "InputControlNet"
    CATEGORY = icons.get("JK/Logic")

    def InputControlNet(self, boolean_value, control_net_false, control_net_true):
        if boolean_value == True:
            return (control_net_true, boolean_value,)
        else:
            return (control_net_false, boolean_value,)

class CR_TextInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "text_false": ("STRING", {"forceInput": True}),
                "text_true": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN",)
    FUNCTION = "text_input_switch"
    CATEGORY = icons.get("JK/Logic")

    def text_input_switch(self, boolean_value, text_false=None, text_true=None):
        text_false = text_false if text_false != None else ""
        text_true = text_true if text_true != None else ""
        if boolean_value == True:
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
                "VAE_true": ("VAE", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("VAE", "BOOLEAN",)   
    FUNCTION = "vae_switch"
    CATEGORY = icons.get("JK/Logic")

    def vae_switch(self, boolean_value, VAE_false, VAE_true):
        if boolean_value == True:
            return (VAE_true, boolean_value)
        else:
            return (VAE_false, boolean_value)

class CR_ModelAndCLIPInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "model_false": ("MODEL",),
                "clip_false": ("CLIP",),                
                "model_true": ("MODEL",),               
                "clip_true": ("CLIP",)
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "BOOLEAN",)
    FUNCTION = "switch"
    CATEGORY = icons.get("JK/Logic")

    def switch(self, boolean_value, model_false, clip_false, model_true, clip_true):
        if boolean_value == True:
            return (model_true, clip_true, boolean_value)
        else:
            return (model_false, clip_false, boolean_value)

class CR_PipeInputSwitch_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "pipe_false": ("PIPE_LINE", {"forceInput": True}),
                "pipe_true": ("PIPE_LINE", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("PIPE_LINE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Logic")

    def pipe_switch(self, boolean_value, pipe_false, pipe_true):
        if boolean_value == True:
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
                "pipe_true": ("BASIC_PIPE", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("BASIC_PIPE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Logic")

    def pipe_switch(self, boolean_value, pipe_false, pipe_true):
        if boolean_value == True:
            return (pipe_true, boolean_value)
        else:
            return (pipe_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# ComfyMath Fix Nodes
#---------------------------------------------------------------------------------------------------------------------#
DEFAULT_BOOL = ("BOOLEAN", {"default": False})
DEFAULT_FLOAT = ("FLOAT", {"default": 0.0})
DEFAULT_INT = ("INT", {"default": 0})
DEFAULT_NUMBER = ("NUMBER", {"default": 0.0})
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
    "Nor": lambda a, b: not (a or b),
    "Xor": lambda a, b: a ^ b,
    "Nand": lambda a, b: not (a and b),
    "And": lambda a, b: a and b,
    "Xnor": lambda a, b: not (a ^ b),
    "Or": lambda a, b: a or b,
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
    "Abs": lambda a: abs(a),
    "Neg": lambda a: -a,
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
        return {"required": {"a": ("FLOAT", {"default": 0.0})}}

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")

    def op(self, a: float) -> tuple[number]:
        return (a,)


class NumberToFloat_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("NUMBER", {"default": 0.0})}}

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
                "x": ("FLOAT", {"default": 0.0}),
                "y": ("FLOAT", {"default": 0.0}),
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
                "a": ("FLOAT", {"default": 0.0}),
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
                "x": ("FLOAT", {"default": 0.0}),
                "y": ("FLOAT", {"default": 0.0}),
                "z": ("FLOAT", {"default": 0.0}),
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
                "a": ("FLOAT", {"default": 0.0}),
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
                "x": ("FLOAT", {"default": 0.0}),
                "y": ("FLOAT", {"default": 0.0}),
                "z": ("FLOAT", {"default": 0.0}),
                "w": ("FLOAT", {"default": 0.0}),
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
                "a": ("FLOAT", {"default": 0.0}),
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
                "a": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 1}),
                "b": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 1}),
                "c": ("FLOAT", {"default": 0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 1}), },
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
# 3D Nodes (WIP)
#---------------------------------------------------------------------------------------------------------------------#
class OrbitPoses_JK:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "radius": ("FLOAT", {"default": 4.0, "min": 0.1, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_camposes",)
    
    FUNCTION = "get_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    
    def get_orbit_poses(self, radius):
    
        azimuths = [0, 45, 90, 180, -90, -45]
        elevations = [0.0] * 6
        radiuss = [radius] * 6
        center = [0.0] * 6
        
        orbit_camposes = [azimuths, elevations, radiuss, center, center, center]
        
        return (orbit_camposes,)
    
#---------------------------------------------------------------------------------------------------------------------#
# MAPPINGS
#---------------------------------------------------------------------------------------------------------------------#
# For reference only, actual mappings are in __init__.py
'''
NODE_CLASS_MAPPINGS = { 
    ### Misc Nodes
    "CR SD1.5 Aspect Ratio JK": CR_AspectRatioSD15_JK,
    "CR SDXL Aspect Ratio JK": CR_SDXLAspectRatio_JK,
    ### Reroute Nodes
    "Reroute List JK": RerouteList_JK,
    "Reroute Ckpt JK": RerouteCkpt_JK,
    "Reroute Vae JK": RerouteVae_JK,
    "Reroute Sampler JK": RerouteSampler_JK,
    "Reroute Upscale JK": RerouteUpscale_JK,
    "Reroute Resize JK": RerouteResize_JK,
    ### ControlNet Nodes
    "CR Apply ControlNet JK": CR_ApplyControlNet_JK,
    "CR Multi-ControlNet Stack JK": CR_ControlNetStack_JK,
    "CR Apply Multi-ControlNet JK": CR_ApplyControlNetStack_JK,
    ### LoRA Nodes
    "CR Load LoRA JK": CR_LoraLoader_JK,
    "CR LoRA Stack JK": CR_LoRAStack_JK,
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
    "Project Setting JK": ProjectSetting_JK,
    "Base Model Parameters JK": BaseModelParameters_JK,
    "Base Model Parameters Extract JK": BaseModelParametersExtract_JK,
    "Base Image Parameters Extract JK": BaseImageParametersExtract_JK,
    "Base Model Pipe JK": BaseModelPipe_JK,
    "Base Model Pipe Extract JK": BaseModelPipeExtract_JK,
    "Refine Pipe JK": RefinePipe_JK,
    "Refine Pipe Extract JK": RefinePipeExtract_JK,
    "Noise Injection Parameters JK": NoiseInjectionParameters_JK,
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
    "HintImageEnchance JK": HintImageEnchance_JK,
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
    "CR Text Input Switch JK": CR_TextInputSwitch_JK,
    "CR VAE Input Switch JK": CR_VAEInputSwitch_JK,
    "CR Switch Model and CLIP JK": CR_ModelAndCLIPInputSwitch_JK,
    "CR Pipe Input Switch JK": CR_PipeInputSwitch_JK,
    "CR Impact Pipe Input Switch JK": CR_ImpactPipeInputSwitch_JK,
    ### ComfyMath Fix Nodes
    "CM_BoolToInt JK": BoolToInt_JK,
    "CM_IntToBool JK": IntToBool_JK,
    "CM_BoolUnaryOperation JK": BoolUnaryOperation_JK,
    "CM_BoolBinaryOperation JK": BoolBinaryOperation_JK,
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
}
NODE_DISPLAY_NAME_MAPPINGS = {
    ### Misc Nodes
    "CR SD1.5 Aspect Ratio JK": "SD1.5 Aspect Ratio JK🐉",
    "CR SDXL Aspect Ratio JK": "SDXL Aspect Ratio JK🐉",
    ### Reroute Nodes
    "Reroute List JK": "Reroute List JK🐉",
    "Reroute Ckpt JK": "Reroute Ckpt JK🐉",
    "Reroute Vae JK": "Reroute Vae JK🐉",
    "Reroute Sampler JK": "Reroute Sampler JK🐉",
    "Reroute Upscale JK": "Reroute Upscale JK🐉",
    "Reroute Resize JK": "Reroute Resize JK🐉",
    ### ControlNet Nodes
    "CR Apply ControlNet JK": "Apply ControlNet JK🐉",
    "CR Multi-ControlNet Stack JK": "Multi-ControlNet Stack JK🐉",
    "CR Apply Multi-ControlNet JK": "Apply Multi-ControlNet JK🐉",
    ### LoRA Nodes
    "CR Load LoRA JK": "Load LoRA JK🐉",
    "CR LoRA Stack JK": "LoRA Stack JK🐉",
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
    "Project Setting JK": "Project Setting JK🐉",
    "Base Model Parameters JK": "Base Model Parameters JK🐉",
    "Base Model Parameters Extract JK": "Base Model Parameters Extract JK🐉",
    "Base Image Parameters Extract JK": "Base Image Parameters Extract JK🐉",
    "Base Model Pipe JK": "Base Model Pipe JK🐉",
    "Base Model Pipe Extract JK": "Base Model Pipe Extract JK🐉",
    "Refine Pipe JK": "Refine Pipe JK🐉",
    "Refine Pipe Extract JK": "Refine Pipe Extract JK🐉",
    "Noise Injection Parameters JK": "Noise Injection Parameters JK🐉",
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
    "HintImageEnchance JK": "Enchance And Resize Hint Images JK🐉",
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
    "CR Text Input Switch JK": "Text Input Switch JK🐉",
    "CR VAE Input Switch JK": "VAE Input Switch JK🐉",
    "CR Switch Model and CLIP JK": "Switch Model and CLIP JK🐉",
    "CR Pipe Input Switch JK": "Pipe Input Switch JK🐉",
    "CR Impact Pipe Input Switch JK": "Impact Pipe Input Switch JK🐉",
    ### ComfyMath Fix Nodes
    "CM_BoolToInt JK": "BoolToInt JK🐉",
    "CM_IntToBool JK": "IntToBool JK🐉",
    "CM_BoolUnaryOperation JK": "BoolUnaryOp JK🐉",
    "CM_BoolBinaryOperation JK": "BoolBinaryOp JK🐉",
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
}    
'''