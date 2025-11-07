#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Deprecated Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
# This file contains all nodes marked as DEPRECATED for backward compatibility
#---------------------------------------------------------------------------------------------------------------------#
import torch
import re
import os
import numpy
import json
import hashlib
import comfy.samplers
import folder_paths
import piexif
import piexif.helper
from pathlib import Path
from typing import Any, Mapping, Tuple, Dict, Union, Callable, TypeAlias
from server import PromptServer
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
from .jake_tools import (
    any_type, get_resolution, get_sd3_resolution, 
    UNION_CONTROLNET_TYPES
)
from nodes import MAX_RESOLUTION, ControlNetApplyAdvanced
from ..categories import icons
from .sd_prompt_reader.image_data_reader import ImageDataReader

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Resolution Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_AspectRatioSD15_JK:
    """SD15 Aspect Ratio (Deprecated)."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": ([
                    "Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                    "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320"
                ],),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": 16384, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")
    DEPRECATED = True

    def Aspect_Ratio(self, custom_width: int, custom_height: int, resolution: str, swap_dimensions: bool) -> Tuple[int, int]:
        """Calculate SD15 aspect ratio (deprecated)."""
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        if swap_dimensions:
            return (height, width)
        else:
            return (width, height)

class CR_AspectRatioSDXL_JK:
    """SDXL Aspect Ratio (Deprecated)."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": ([
                    "Custom", "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                    "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576"
                ],),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 16384, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 64, "max": 16384, "step": 8}),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
            }
        }
    
    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")
    DEPRECATED = True

    def Aspect_Ratio(self, custom_width: int, custom_height: int, resolution: str, swap_dimensions: bool) -> Tuple[int, int]:
        """Calculate SDXL aspect ratio (deprecated)."""
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
            
        if swap_dimensions:
            return (height, width)
        else:
            return (width, height)

class CR_AspectRatioSD3_JK:
    """SD3 specific aspect ratio selector."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (["1:1", "5:4", "3:2", "16:9", "21:9", "4:5", "2:3", "9:16", "9:21"],),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("AspectRatio", "width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")
    DEPRECATED = True

    def Aspect_Ratio(self, aspect_ratio: str) -> Tuple[str, int, int]:
        """Get SD3 aspect ratio dimensions."""
        width, height = get_sd3_resolution(aspect_ratio)
        return (aspect_ratio, width, height)

class SDXL_TargetRes_JK:
    """Target resolution calculator for SDXL with scaling support"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1024,
                    "tooltip": "Original width to scale from"
                }),
                "height": ("INT", {
                    "default": 1024,
                    "tooltip": "Original height to scale from"
                }),
                "target_res_scale": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.01, 
                    "max": 16.0, 
                    "step": 0.01,
                    "tooltip": "Scale factor for target resolution"
                }),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("target_width", "target_height")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Target resolution calculator for SDXL with scaling support"
    DEPRECATED = True

    def get_value(self, width: int, height: int, target_res_scale: float) -> Tuple[int, int]:
        """Calculate target resolution with scaling and multiple-of-8 alignment"""
        target_width = multiple_of_int(width * target_res_scale, 8)
        target_height = multiple_of_int(height * target_res_scale, 8)
        
        return (target_width, target_height)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Image Processing Nodes
#---------------------------------------------------------------------------------------------------------------------#

class ImageCropByMaskResolution_JK:
    """Image Crop by Mask Resolution (Deprecated)."""
    
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
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Image")
    DEPRECATED = True
    
    def get_value(self, mask: torch.Tensor, padding: int, custom_width: int, custom_height: int, use_image_res: bool, 
                  use_target_mega_pixel: bool, target_mega_pixel: float, use_target_res: bool, target_res: int, 
                  multiple_of: int, image_upscale_method: str, latent_upscale_method: str, 
                  image: torch.Tensor = None, latent: Dict = None) -> Tuple[int, int, int, int, int, int, str, str]:
        """Calculate crop parameters from mask (deprecated)."""
        # This functionality is now available in ImageCropByMaskResolutionGrp_JK
        from .jake_misc_nodes import ImageCropByMaskResolutionGrp_JK
        
        # Use the new implementation
        crop_node = ImageCropByMaskResolutionGrp_JK()
        result = crop_node.get_value(
            mask, padding, use_image_res, use_target_mega_pixel, target_mega_pixel,
            use_target_res, target_res, image, latent
        )
        
        # Return with additional parameters for backward compatibility
        return result + (image_upscale_method, latent_upscale_method)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Reroute Nodes
#---------------------------------------------------------------------------------------------------------------------#

# Get VAE list with additional options
vae_list = folder_paths.get_filename_list("vae") + ["taesd"] + ["taesdxl"] + ["taesd3"] + ["taef1"]

class RerouteList_JK:
    """Reroute multiple model and sampler selections."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),),
                "vae": (vae_list,),
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
            }
        }

    RETURN_TYPES = (
        folder_paths.get_filename_list("checkpoints"), 
        vae_list, 
        comfy.samplers.KSampler.SAMPLERS, 
        comfy.samplers.KSampler.SCHEDULERS, 
        folder_paths.get_filename_list("upscale_models")
    )
    RETURN_NAMES = ("CHECKPOINT", "VAE", "SAMPLER", "SCHEDULAR", "UPSCALE_MODEL")
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, checkpoint=None, vae=None, sampler=None, scheduler=None, upscale_model=None):
        """Route multiple model and sampler selections."""
        return (checkpoint, vae, sampler, scheduler, upscale_model)

class RerouteCkpt_JK:
    """Reroute checkpoint selection."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),)
    RETURN_NAMES = ("CHECKPOINT",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, checkpoint=None):
        """Route checkpoint selection."""
        return (checkpoint,)

class RerouteVae_JK:
    """Reroute VAE selection."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae": (vae_list,),
            }
        }

    RETURN_TYPES = (vae_list,)
    RETURN_NAMES = ("VAE",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, vae=None):
        """Route VAE selection."""
        return (vae,)

class RerouteSampler_JK:
    """Reroute sampler and scheduler selections."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            },
        }

    RETURN_TYPES = (comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS,)
    RETURN_NAMES = ("SAMPLER", "SCHEDULAR",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, sampler=None, scheduler=None):
        """Route sampler and scheduler selections."""
        return (sampler, scheduler,)

class RerouteUpscale_JK:
    """Reroute upscale model selection."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("upscale_models"),)
    RETURN_NAMES = ("UPSCALE_MODEL",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, upscale_model=None):
        """Route upscale model selection."""
        return (upscale_model,)

class RerouteResize_JK:
    """Reroute image resize method selection."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_resize": (["Just Resize", "Crop and Resize", "Resize and Fill"], {"default": "Crop and Resize"}),
            }
        }

    RETURN_TYPES = (["Just Resize", "Crop and Resize", "Resize and Fill"],)
    RETURN_NAMES = ("IMAGE_RESIZE",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, image_resize=None):
        """Route image resize method selection."""
        return (image_resize,)

class RerouteString_JK:
    """Reroute string input."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING",{"default": ''}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "route"
    CATEGORY = icons.get("JK/Reroute")
    DEPRECATED = True

    def route(self, string=None):
        """Route string input."""
        return (string,)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated ControlNet Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_ControlNetStack_JK:
    
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
                "image_MetaData_0": ("STRING", {"default": ''},),
                "image_MetaData_1": ("STRING", {"default": ''},),
                "image_MetaData_2": ("STRING", {"default": ''},),
                "image_MetaData_3": ("STRING", {"default": ''},),
                "image_MetaData_4": ("STRING", {"default": ''},),
                "image_MetaData_5": ("STRING", {"default": ''},),
            },
            "required": {
                "control_switch": ("BOOLEAN", {"default": False},),
            },
        }
        
        for i in range(0, 6):
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
    DEPRECATED = True

    def controlnet_stacker(self, control_switch, save_hash, **kwargs):

        # Initialise the list
        controlnet_list = []
        metadataout = ""
        
        if control_switch == True:
            j = 0
            for i in range (0, 6):
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
                    controlnet_sta = f"{kwargs.get(f'start_percent_{i}'):.3f}"
                    controlnet_end = f"{kwargs.get(f'end_percent_{i}'):.3f}"
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
                control_switch and kwargs.get(f"ControlNet_Unit_1"), 
                control_switch and kwargs.get(f"ControlNet_Unit_2"), 
                control_switch and kwargs.get(f"ControlNet_Unit_3"), 
                control_switch and kwargs.get(f"ControlNet_Unit_4"), 
                control_switch and kwargs.get(f"ControlNet_Unit_5"))

class CR_ApplyControlNetStack_JK:
    @classmethod
    def INPUT_TYPES(cls):
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
    DEPRECATED = True

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

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated LoRA Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_LoraLoader_JK:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(cls):
        file_list = folder_paths.get_filename_list("loras")
        file_list.insert(0, "None")
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "switch": ("BOOLEAN", {"default": False}),
                "input_mode": (['model_only', 'advanced'], {"default": 'model_only'}),
                "lora_name": (file_list, ),
                "model_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "clip_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }
    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_lora"
    CATEGORY = icons.get("JK/LoRA")
    DEPRECATED = True

    def load_lora(self, model, clip, switch, lora_name, model_weight, clip_weight):
        
        if input_mode == "model_only" and (switch == False or lora_name == "None" or model_weight == 0):
            return (model, clip)
        if input_mode == "advanced" and (switch == False or lora_name == "None" or (model_weight == 0 and clip_weight == 0)):
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
        
        if input_mode == "model_only":
            model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, model_weight, 0.0)
        elif input_mode == "advanced":
            model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, model_weight, clip_weight)
        
        return (model_lora, clip_lora)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Embedding Nodes
#---------------------------------------------------------------------------------------------------------------------#

class EmbeddingPicker_JK:
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
                "text_in": ("STRING", {"default": ''}),
                "metadata_in": ("STRING", {"default": ''}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Text", "METADATA",)
    FUNCTION = "concat_embedding"
    CATEGORY = icons.get("JK/Embedding")
    DEPRECATED = True

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
    @classmethod
    def INPUT_TYPES(self):
        embeddingslist = ["None"] + folder_paths.get_filename_list("embeddings")
        
        inputs = {
            "required": {
            },
            "optional": {
                "text_in": ("STRING", {"default": ''}),
                "metadata_in": ("STRING", {"default": ''}),
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
    CATEGORY = icons.get("JK/Embedding")
    DEPRECATED = True

    def concat_embedding(self, save_hash, text_in=None, metadata_in=None, **kwargs):
        
        embedding_enable = False
        
        for i in range(1, 7):
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
        
        for i in range(1, 7):
            
            if kwargs.get(f"embedding_{i}") == True and kwargs.get(f"embedding_name_{i}") != "None" and kwargs.get(f"emphasis_{i}") >= 0.05:
                
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
# Deprecated Loader Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CkptLoader_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"),),
            },
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("checkpoints"))
    RETURN_NAMES = ("ckpt_name", "Checkpoint")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    DEPRECATED = True
    
    def list(self, checkpoint):
        return (checkpoint, checkpoint)

class VaeLoader_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae": (vae_list,),
            },
        }

    RETURN_TYPES = ("STRING", vae_list)
    RETURN_NAMES = ("vae_name", "VAE")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    DEPRECATED = True
    
    def list(self, vae):
        return (vae, vae)

class UpscaleModelLoader_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
            }
        }

    RETURN_TYPES = ("STRING", folder_paths.get_filename_list("upscale_models"))
    RETURN_NAMES = ("upscale_model_name", "Upscale_Model")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Loader")
    DEPRECATED = True
    
    def list(self, upscale_model):
        return (upscale_model, upscale_model)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Pipeline Nodes
#---------------------------------------------------------------------------------------------------------------------#

class PipeEnd_JK:
    """Pipe End (Deprecated)."""
    
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
    DEPRECATED = True

    def doit(self, any_in=None):
        """Pipe end operation (deprecated)."""
        return ()

class NodesState_JK:
    """Node State Control (Deprecated)."""
    
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
    DEPRECATED = True

    def doit(self, node_id_list: str, mute_state: bool, bypass_state: bool):
        """Control node states (deprecated)."""
        node_ids = re.split('[.,;:]', node_id_list)
        
        for node_id in node_ids:
            node_id = int(node_id)
            
            if mute_state and bypass_state:
                # PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 0})
                pass
            elif not mute_state and bypass_state:
                # PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 2})
                pass
            else:
                # PromptServer.instance.send_sync("jakeupgrade-node-state", {"node_id": node_id, "node_mode": 4})
                pass
        
        return ()

class KsamplerParameters_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
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
    DEPRECATED = True

    def get_value(self, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, resolution, stop_at_clip_layer, custom_width, custom_height, swap_dimensions, batch_size):
        
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            width, height = get_resolution(resolution)
        
        if swap_dimensions == True:
            return (stop_at_clip_layer, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, width, height, batch_size)
        else:
            return (stop_at_clip_layer, positive, negative, variation, seed, steps, cfg, sampler_name, scheduler, denoise, height, width, batch_size)

class BaseModelParameters_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": ("STRING", {"default": ''}),
                "vae_name": ("STRING", {"default": ''}),
                "base_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
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
                "image_resize": (["Just Resize", "Crop and Resize", "Resize and Fill"], {"default": "Crop and Resize"}),
                "img2img_denoise": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
                #
                "save_ckpt_hash": ("BOOLEAN", {"default": False},),
            },
            "optional": {
                "image": ("IMAGE",),
                "input_positive": ("STRING", {"default": ''}),
                "input_negative": ("STRING", {"default": ''}),
            },
        }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE", "PIPE_LINE")
    RETURN_NAMES = ("Base_Model_MetaData", "Base_Model_Pipe", "Base_Image_Pipe")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_model_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "STRING", "STRING", "FLOAT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("Checkpoint", "Tiling", "Stop_Layer", "Positive_l", "Positive_g", "Negative_l", "Negative_g", "Variation", "Seed", "Steps", "Sampler", "Schedular", "Cfg", "Denoise", "Specified_VAE", "VAE")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, base_model_pipe=None):
        ckpt_name, stop_at_clip_layer, positive_l, positive_g, negative_l, negative_g, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, tiling, specified_vae, vae_name = base_model_pipe
        return (ckpt_name, tiling, stop_at_clip_layer, positive_l, positive_g, negative_l, negative_g, variation, seed, steps, sampler_name, scheduler, cfg, img2img_denoise, specified_vae, vae_name)

class BaseImageParametersExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "STRING", "BOOLEAN")
    RETURN_NAMES = ("Image", "Width", "Height", "Batch_Size", "Image_Resize", "img2img")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, base_image_pipe=None):
        image, width, height, batch_size, image_resize, img2img = base_image_pipe
        return (image, width, height, batch_size, image_resize, img2img)

class BaseModelPipe_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive_conditioning": ("CONDITIONING", ),
                "negative_conditioning": ("CONDITIONING", ),
                "base_latent": ("LATENT",),
                "base_image": ("IMAGE",),
            },
            "optional": {
                "positive_prompt": ("STRING", {"default": ''}),
                "negative_prompt": ("STRING", {"default": ''}),
                "variation_prompt": ("STRING", {"default": ''}),
                "lora_prompt": ("STRING", {"default": ''}),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE", "STRING")
    RETURN_NAMES = ("Base_PIPE", "Base_Prompt")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

    def get_value(self, positive_conditioning=None, negative_conditioning=None, base_latent=None, base_image=None, positive_prompt=None, negative_prompt=None, variation_prompt=None, lora_prompt=None):
        
        positive_prompt = positive_prompt if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f",{variation_prompt}" if variation_prompt !=None and variation_prompt != "" else ""
        lora_prompt = f",{lora_prompt}" if lora_prompt !=None and lora_prompt != "" else ""
        base_prompt = f"{handle_whitespace(positive_prompt)}{handle_whitespace(variation_prompt)}{handle_whitespace(lora_prompt)}\nNegative prompt: {handle_whitespace(negative_prompt)}\n"
        
        base_pipe = (positive_conditioning, negative_conditioning, positive_prompt, negative_prompt, base_latent, base_image, base_prompt)
        
        return (base_pipe, base_prompt)

class BaseModelPipeExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("PIPE_LINE", "CONDITIONING", "CONDITIONING", "STRING", "STRING", "LATENT", "IMAGE", "STRING")
    RETURN_NAMES = ("Base_Pipe", "Positive_Conditioning", "Negative_Conditioning", "Positive_Prompt", "Negative_Prompt", "Base_Latent", "Base_Image", "Base_Prompt")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
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
                "base_steps": ("INT", {"default": 20}),
            }
        }
    
    RETURN_TYPES = ("STRING", "PIPE_LINE")
    RETURN_NAMES = ("Noise_Injection_MetaData", "Noise_Injection_Pipe")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

    def get_value(self, base_steps, seed, variation_strength, variation_batch, variation_batch_mode_Inspire, variation_method_Inspire, img2img_injection_switch_at_Legacy):
        
        base_steps = base_steps if base_steps != None else 30
        img2img_injection_1st_step_end = int(base_steps * img2img_injection_switch_at_Legacy)
        img2img_injection_2nd_step_start = img2img_injection_1st_step_end #+ 1
        
        noiseinjection_metadata = f"Noise Injection Strength: {variation_strength}, Noise Injection Seed: {seed}, "
        noiseinjection_pipe = (seed, variation_strength, variation_batch, variation_batch_mode_Inspire, variation_method_Inspire, img2img_injection_1st_step_end, img2img_injection_2nd_step_start)
        
        return (noiseinjection_metadata, noiseinjection_pipe)

class NoiseInjectionPipeExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise_injection_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("INT", "FLOAT", "INT", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("variation_seed", "variation_strength", "variation_batch", "variation_batch_mode", "variation_method", "img2img_injection_1st_step_end", "img2img_injection_2nd_step_start")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_ckpt_name": ("STRING", {"default": ''}),
                "base_steps": ("INT", {"default": 20}),
                "refine_ckpt_name": ("STRING", {"default": ''}),
                "refine_1_seed": ("INT", {"default": 0}),
                "refine_2_seed": ("INT", {"default": 0}),
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
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"refine_1_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "INT", "INT", "BOOLEAN", "STRING", "BOOLEAN", "STRING", "STRING", "STRING", "INT", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("Enable_refine_1", "refine_1_cfg", "base_step_end", "refine_step_start", "Enable_Refine_Ckpt", "Refine_Ckpt_Name", "Enable_refine_1_Prompt", "refine_1_positive", "refine_1_negative", "refine_1_variation", "refine_1_seed", "Enable_refine_1_seed", "Enable_IPAdaptor_1")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, refine_1_pipe):
        Enable_refine_1, Enable_refine_1_seed, refine_1_seed, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_cfg, base_step_end, refine_step_start, Enable_IPAdaptor_1 = refine_1_pipe
        return (Enable_refine_1, refine_1_cfg, base_step_end, refine_step_start, Enable_refine_ckpt, refine_ckpt_name, Enable_refine_1_prompt, refine_1_positive, refine_1_negative, refine_1_variation, refine_1_seed, Enable_refine_1_seed, Enable_IPAdaptor_1)

class Refine2ParametersExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"refine_2_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "FLOAT", "BOOLEAN", "STRING", "STRING", "STRING", "INT", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("Enable_refine_2", "refine_2_cfg", "refine_2_denoise", "Enable_refine_2_prompt", "refine_2_positive", "refine_2_negative", "refine_2_variation", "refine_2_seed", "Enable_refine_2_seed", "Enable_IPAdaptor_2")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, refine_2_pipe):
        Enable_refine_2, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, Enable_refine_2_seed, refine_2_seed, refine_2_cfg, refine_2_denoise, Enable_IPAdaptor_2 = refine_2_pipe
        return (Enable_refine_2, refine_2_cfg, refine_2_denoise, Enable_refine_2_prompt, refine_2_positive, refine_2_negative, refine_2_variation, refine_2_seed, Enable_refine_2_seed, Enable_IPAdaptor_2)

class RefinePipe_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            "positive_conditioning": ("CONDITIONING",),
            "negative_conditioning": ("CONDITIONING",),
            "image_latent": ("LATENT",),
            "base_latent": ("LATENT",),
            "base_image": ("IMAGE",),
            },
            "optional": {
                "positive_prompt": ("STRING", {"default": ''}),
                "negative_prompt": ("STRING", {"default": ''}),
                "variation_prompt": ("STRING", {"default": ''}),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE",)
    RETURN_NAMES = ("Refine_PIPE",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

    def get_value(self, positive_conditioning=None, negative_conditioning=None, image_latent=None, base_latent=None, base_image=None, positive_prompt=None, negative_prompt=None, variation_prompt=None):
        
        positive_prompt = f"{positive_prompt}," if positive_prompt !=None and positive_prompt != "" else ""
        negative_prompt = negative_prompt if negative_prompt !=None and negative_prompt != "" else ""
        variation_prompt = f"{variation_prompt}," if variation_prompt !=None and variation_prompt != "" else ""
        
        refine_pipe = (positive_conditioning, negative_conditioning, image_latent, base_latent, base_image, positive_prompt, negative_prompt, variation_prompt)
        
        return (refine_pipe,)

class RefinePipeExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "refine_pipe": ("PIPE_LINE",)
            }
        }

    RETURN_TYPES = ("PIPE_LINE", "CONDITIONING", "CONDITIONING", "LATENT", "LATENT", "IMAGE", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("Refine_Pipe", "Positive_Conditioning", "Negative_Conditioning", "Image_Latent", "Base_Latent", "Base_Image", "Positive_Prompt", "Negative_Prompt", "Variation_Prompt",)
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_ckpt_name": ("STRING", {"default": ''}),
                "upscale_ckpt_name": ("STRING", {"default": ''}),
                "upscale_seed": ("INT", {"default": 0}),
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
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"image_upscale_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("Enable_Image_Upscale", "Image_upscale_model_name", "Image_upscale_method", "Image_rescale_by")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, image_upscale_pipe):
        Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, image_rescale_by = image_upscale_pipe
        return (Enable_Image_Upscale, Image_upscale_model_name, Image_upscale_method, image_rescale_by)

class LatentUpscaleParametersExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"latent_upscale_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "FLOAT")
    RETURN_NAMES = ("Enable_Latent_Upscale", "Latent_upscale_method", "Latent_scale_by")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, latent_upscale_pipe):
        Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by = latent_upscale_pipe
        return (Enable_Latent_Upscale, Latent_upscale_method, Latent_scale_by)

class UpscaleModelParametersExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"upscale_model_pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("BOOLEAN", "STRING", "BOOLEAN", "STRING", "STRING", "INT", "STRING", "STRING", "FLOAT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("Enable_upscale_ckpt", "upscale_ckpt_name", "Enable_upscale_prompt", "upscale_positive", "upscale_negative", "upscale_steps", "upscale_sampler_name", "upscale_scheduler", "upscale_cfg", "upscale_denoise", "Enable_upscale_seed")
    FUNCTION = "flush"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True
    
    def flush(self, upscale_model_pipe):
        Enable_upscale_ckpt, upscale_ckpt_name, Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, upscale_denoise, Enable_upscale_seed = upscale_model_pipe
        return (Enable_upscale_ckpt, upscale_ckpt_name, Enable_upscale_prompt, upscale_positive, upscale_negative, upscale_steps, upscale_sampler_name, upscale_scheduler, upscale_cfg, upscale_denoise, Enable_upscale_seed)

class DetailerParameters_JK:
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
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

    def get_value(self, batch_index, detailer_length, refiner_on_ratio):
        
        return (batch_index, detailer_length, refiner_on_ratio)

class MetadataPipe_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_model_prompt": ("STRING", {"default": ''}),
                "base_model_metadata": ("STRING", {"default": ''}),
                "lora_metadata": ("STRING", {"default": ''}),
                "positive_embedding_metadata": ("STRING", {"default": ''}),
                "negative_embedding_metadata": ("STRING", {"default": ''}),
                "controlnet_metadata": ("STRING", {"default": ''}),
                "refine_metadata": ("STRING", {"default": ''}),
                "upscale_metadata": ("STRING", {"default": ''}),
                "noise_injection_metadata": ("STRING", {"default": ''}),
                "image_name": ("STRING", {"default": ''}),
                "path_name": ("STRING", {"default": ''}),
                "counter": ("INT", {"default": ''}),
            }
        }

    RETURN_TYPES = ("META_PIPE",)
    RETURN_NAMES = ("META_PIPE",)
    FUNCTION = "doit"
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

    def doit(self, base_model_prompt=None, base_model_metadata=None, lora_metadata=None, positive_embedding_metadata=None, negative_embedding_metadata=None, 
                   controlnet_metadata=None, refine_metadata=None, upscale_metadata=None, noise_injection_metadata=None,
                   image_name=None, path_name=None, counter=0):
        
        meta_pipe = (base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata,
                    controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata,
                    image_name, path_name, counter)
        
        return (meta_pipe,)

class MetadataPipeExtract_JK:
    @classmethod
    def INPUT_TYPES(cls):
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
    DEPRECATED = True
    
    def flush(self, meta_pipe):

        base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata, controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata, image_name, path_name, counter = meta_pipe
        
        return (base_model_prompt, base_model_metadata, lora_metadata, positive_embedding_metadata, negative_embedding_metadata,
                    controlnet_metadata, refine_metadata, upscale_metadata, noise_injection_metadata,
                    image_name, path_name, counter)

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
                "lora_prompt": ("STRING", {"default": ''}),
                "positive_embedding_prompt": ("STRING", {"default": ''}),
                "negative_embedding_prompt": ("STRING", {"default": ''}),
                "lora_metadata": ("STRING", {"default": ''}),
                "positive_embedding_metadata": ("STRING", {"default": ''}),
                "negative_embedding_metadata": ("STRING", {"default": ''}),
                "controlnet_metadata": ("STRING", {"default": ''}),
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
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
                "base_model_prompt": ("STRING", {"default": ''}),
                "base_model_metadata": ("STRING", {"default": ''}),
                "lora_metadata": ("STRING", {"default": ''}),
                "positive_embedding_metadata": ("STRING", {"default": ''}),
                "negative_embedding_metadata": ("STRING", {"default": ''}),
                "controlnet_metadata": ("STRING", {"default": ''}),
                "refine_metadata": ("STRING", {"default": ''}),
                "upscale_metadata": ("STRING", {"default": ''}),
                "noise_injection_metadata": ("STRING", {"default": ''}),
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
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
    def INPUT_TYPES(cls):

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
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
    def INPUT_TYPES(cls):

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
    CATEGORY = icons.get("JK/Pipe")
    DEPRECATED = True

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
# Deprecated Animation Nodes
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
    DEPRECATED = True

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
    DEPRECATED = True
    
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
# Deprecated Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_PipeInputSwitch_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "pipe_false": ("PIPE_LINE",),
                
            },
            "optional": {
                "pipe_true": ("PIPE_LINE",),
            },
        }
    
    RETURN_TYPES = ("PIPE_LINE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Switch")
    DEPRECATED = True

    def pipe_switch(self, boolean_value, pipe_false, pipe_true=None):
        if pipe_true != None and boolean_value == True:
            return (pipe_true, boolean_value)
        else:
            return (pipe_false, boolean_value)

class CR_ImpactPipeInputSwitch_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {"default": False}),
                "pipe_false": ("BASIC_PIPE",),
            },
            "optional": {
                "pipe_true": ("BASIC_PIPE",),
            },
        }
    
    RETURN_TYPES = ("BASIC_PIPE", "BOOLEAN",)   
    FUNCTION = "pipe_switch"
    CATEGORY = icons.get("JK/Switch")
    DEPRECATED = True

    def pipe_switch(self, boolean_value, pipe_false, pipe_true=None):
        if pipe_true != None and boolean_value == True:
            return (pipe_true, boolean_value)
        else:
            return (pipe_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated Math Nodes
#---------------------------------------------------------------------------------------------------------------------#

from .jake_node_math import (
    DEFAULT_FLOAT, 
    FLOAT_UNARY_CONDITIONS, FLOAT_BINARY_CONDITIONS,
    FLOAT_UNARY_OPERATIONS, FLOAT_BINARY_OPERATIONS
)

# 类型别名定义
number: TypeAlias = int | float
Vec2: TypeAlias = tuple[float, float]
Vec3: TypeAlias = tuple[float, float, float]
Vec4: TypeAlias = tuple[float, float, float, float]

# 默认值定义
VEC2_ZERO = (0.0, 0.0)
VEC3_ZERO = (0.0, 0.0, 0.0)
VEC4_ZERO = (0.0, 0.0, 0.0, 0.0)

DEFAULT_NUMBER = ("NUMBER", {"default": 0.0, "step": 0.0001})
DEFAULT_VEC2 = ("VEC2", {"default": VEC2_ZERO})
DEFAULT_VEC3 = ("VEC3", {"default": VEC3_ZERO})
DEFAULT_VEC4 = ("VEC4", {"default": VEC4_ZERO})

# 向量条件定义
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

# 向量运算定义
VEC_UNARY_OPERATIONS: Mapping[str, Callable[[numpy.ndarray], numpy.ndarray]] = {
    "Neg": lambda a: -a,
    "Normalize": lambda a: a / numpy.linalg.norm(a),
}

VEC_BINARY_OPERATIONS: Mapping[str, Callable[[numpy.ndarray, numpy.ndarray], numpy.ndarray]] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Cross": lambda a, b: numpy.cross(a, b),
}

VEC_TO_FLOAT_UNARY_OPERATION: Mapping[str, Callable[[numpy.ndarray], float]] = {
    "Norm": lambda a: numpy.linalg.norm(a).astype(float),
}

VEC_TO_FLOAT_BINARY_OPERATION: Mapping[str, Callable[[numpy.ndarray, numpy.ndarray], float]] = {
    "Dot": lambda a, b: numpy.dot(a, b),
    "Distance": lambda a, b: numpy.linalg.norm(a - b).astype(float),
}

VEC_FLOAT_OPERATION: Mapping[str, Callable[[numpy.ndarray, float], numpy.ndarray]] = {
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a / b,
}

# 向量转换函数
def _vec2_from_numpy(a: numpy.ndarray) -> Vec2:
    """Convert numpy array to Vec2 tuple"""
    return (float(a[0]), float(a[1]))

def _vec3_from_numpy(a: numpy.ndarray) -> Vec3:
    """Convert numpy array to Vec3 tuple"""
    return (float(a[0]), float(a[1]), float(a[2]))

def _vec4_from_numpy(a: numpy.ndarray) -> Vec4:
    """Convert numpy array to Vec4 tuple"""
    return (float(a[0]), float(a[1]), float(a[2]), float(a[3]))

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

    def op(self, op: str, a: Vec4, b: float) -> tuple[Vec4]:
        return (_vec4_from_numpy(VEC_FLOAT_OPERATION[op](numpy.array(a), b)),)

class IntToNumber_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("INT", {"default": 0})}}

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

    def op(self, a: int) -> tuple[number]:
        return (a,)

class NumberToInt_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("NUMBER", {"default": 0.0})}}

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

    def op(self, a: number) -> tuple[int]:
        return (int(a),)

class FloatToNumber_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("FLOAT", {"default": 0.0, "step": 0.0001})}}

    RETURN_TYPES = ("NUMBER",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

    def op(self, a: float) -> tuple[number]:
        return (a,)

class NumberToFloat_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("NUMBER", {"default": 0.0, "step": 0.0001})}}

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

    def op(self, a: float) -> tuple[Vec2]:
        return ((a, a),)

class BreakoutVec2_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC2", {"default": VEC2_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

    def op(self, a: float) -> tuple[Vec3]:
        return ((a, a, a),)

class BreakoutVec3_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC3", {"default": VEC3_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

    def op(self, a: float) -> tuple[Vec4]:
        return ((a, a, a, a),)

class BreakoutVec4_JK:
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"a": ("VEC4", {"default": VEC4_ZERO})}}

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT")
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DEPRECATED = True

    def op(self, a: Vec4) -> tuple[float, float, float, float]:
        return (a[0], a[1], a[2], a[3])

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

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
    DEPRECATED = True

    def op(self, op: str, a: Vec4, b: Vec4) -> tuple[Vec4]:
        return (
            _vec4_from_numpy(VEC_BINARY_OPERATIONS[op](numpy.array(a), numpy.array(b))),
        )

#---------------------------------------------------------------------------------------------------------------------#
# Deprecated 3D Nodes
#---------------------------------------------------------------------------------------------------------------------#

class Hy3DCamConfig20to21_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "camera_config": ("HY3DCAMERA",),
            },
        }
    
    RETURN_TYPES = ("HY3D21CAMERA",)
    FUNCTION = "get_camconfig"
    CATEGORY = icons.get("JK/3D")
    DEPRECATED = True
    
    def get_camconfig(self, camera_config):
        
        key_to_remove = 'camera_distance'
        if key_to_remove in camera_config:
            del camera_config[key_to_remove]

        return (camera_config,)
