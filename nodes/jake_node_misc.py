#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Misc Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import random
import json
import os
import comfy.samplers
from typing import Any, Tuple, List, Dict
from .jake_tools import any_type, get_resolution, get_sd3_resolution
from .jake_utils import multiple_of_int, parse_string_list
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Project & Settings Nodes
#---------------------------------------------------------------------------------------------------------------------#

class ProjectSetting_JK:
    """Project settings for workflow organization with customizable naming patterns"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {
                    "default": 'myproject', 
                    "multiline": False,
                    "tooltip": "Name of the project for organization"
                }),
                "image_name": ("STRING", {
                    "default": f'v%counter_%seed_%time', 
                    "multiline": False,
                    "tooltip": "Image naming pattern (supports %counter, %seed, %time variables)"
                }),
                "path_name": ("STRING", {
                    "default": f'%date', 
                    "multiline": False,
                    "tooltip": "Path naming pattern (supports %date variable)"
                }),
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Random seed for project"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("Image_Name", "Path_Name", "Counter")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Project settings for workflow organization with customizable naming patterns."

    def get_value(self, project_name: str, image_name: str, path_name: str, seed: int) -> Tuple[str, str, int]:
        """Get project settings values with pattern processing"""
        # Combine project name with patterns
        processed_image_name = project_name + "_" + image_name
        processed_path_name = project_name + "/" + path_name
        
        # Initialize random seed for counter generation
        random.seed(seed)
        number = random.randint(0, 18446744073709551615)

        return (processed_image_name, processed_path_name, seed)

class KsamplerParametersDefault_JK:
    """Default parameters for KSampler (steps, CFG scale, denoise strength)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {
                    "default": 20, 
                    "min": 1, 
                    "max": 10000,
                    "tooltip": "Number of sampling steps"
                }),
                "cfg": ("FLOAT", {
                    "default": 8.0, 
                    "min": 0.0, 
                    "max": 100.0, 
                    "step": 0.05,
                    "tooltip": "Classifier-Free Guidance scale"
                }),
                "denoise": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Denoising strength (1.0 = full denoise)"
                }),
            },
        }
    
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("STEPS", "CFG", "DENOISE")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Default parameters for KSampler (steps, CFG scale, denoise strength)."

    def get_value(self, steps: int, cfg: float, denoise: float) -> Tuple[int, float, float]:
        """Get KSampler parameter values"""
        return (steps, cfg, denoise)

class KsamplerAdvParametersDefault_JK:
    """Advanced KSampler parameters for step control and scheduling"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "switch_at_step": ("INT", {
                    "default": 10, 
                    "min": 1, 
                    "max": 10000,
                    "tooltip": "Step at which to switch samplers or settings"
                }),
            },
        }
    
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("start_at_step", "switch_at_step", "end_at_step", "enable", "disable")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Advanced KSampler parameters for step control and scheduling."

    def get_value(self, switch_at_step: int) -> Tuple[int, int, int, str, str]:
        """Get advanced KSampler parameter values with step ranges"""
        return (0, switch_at_step, 10000, "enable", "disable")

class BaseModelParametersSD3API_JK:
    """SD3 API compatible base model parameters with prompt management"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "Positive prompt text"
                }),
                "negative": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "Negative prompt text"
                }),
                "use_input_prompt": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable to use input prompts instead of default prompts"
                }),
                "aspect_ratio": (["1:1", "5:4", "3:2", "16:9", "21:9", "4:5", "2:3", "9:16", "9:21"], {
                    "tooltip": "Aspect ratio for SD3 model"
                }),
            },
            "optional": {
                "input_positive": ("STRING", {
                    "default": '',
                    "tooltip": "Optional positive prompt input (used when use_input_prompt is enabled)"
                }),
                "input_negative": ("STRING", {
                    "default": '',
                    "tooltip": "Optional negative prompt input (used when use_input_prompt is enabled)"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("POSITIVE", "NEGATIVE", "ASPECT_RATIO", "WIDTH", "HEIGHT")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "SD3 API compatible base model parameters with prompt management and aspect ratio selection."
    DEPRECATED = True

    def get_value(self, positive: str, negative: str, use_input_prompt: bool, aspect_ratio: str, 
                  input_positive: str = None, input_negative: str = None) -> Tuple[str, str, str, int, int]:
        """Get SD3 model parameters with optional input prompt override"""
        # Use input prompts if enabled and provided
        if use_input_prompt:
            if input_positive is not None and input_positive != "":
                positive = input_positive
            if input_negative is not None and input_negative != "":
                negative = input_negative
        
        # Get resolution from aspect ratio
        try:
            from .jake_tools import get_sd3_resolution
            width, height = get_sd3_resolution(aspect_ratio)
        except ImportError:
            # Fallback to default resolution if function not available
            width, height = 1024, 1024
        
        return (positive, negative, aspect_ratio, width, height)

class Inject_Noise_Params_JK:
    """Parameters for noise injection with seed and strength control"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise_seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Seed for noise generation"
                }),
                "noise_strength": ("FLOAT", {
                    "default": 1.0, 
                    "min": -20.0, 
                    "max": 20.0, 
                    "step": 0.01, 
                    "round": 0.01,
                    "tooltip": "Strength of noise injection"
                }),
                "normalize": (["false", "true"], {
                    "default": "false",
                    "tooltip": "Whether to normalize the noise"
                }),
            },
        }
    
    RETURN_TYPES = ("INT", "FLOAT", ["false", "true"])
    RETURN_NAMES = ("Seed", "Strength", "Normalize")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Parameters for noise injection with seed and strength control."

    def get_value(self, noise_seed: int, noise_strength: float, normalize: str) -> Tuple[int, float, str]:
        """Get noise injection parameters"""
        return (noise_seed, noise_strength, normalize)

class SD3_Prompts_Switch_JK:
    """Switch between different prompt types for SD3 (CLIP-L, CLIP-G, T5-XXL)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_l": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "CLIP-L prompt text"
                }),
                "clip_g": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "CLIP-G prompt text"
                }),
                "t5xxl": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "T5-XXL prompt text"
                }),
                "clip_l_prompt": (["clip_l", "clip_g", "t5xxl"], {
                    "default": "clip_l",
                    "tooltip": "Prompt type to use for CLIP-L output"
                }),
                "clip_g_prompt": (["clip_l", "clip_g", "t5xxl"], {
                    "default": "clip_g",
                    "tooltip": "Prompt type to use for CLIP-G output"
                }),
                "t5xxl_prompt": (["clip_l", "clip_g", "t5xxl"], {
                    "default": "t5xxl",
                    "tooltip": "Prompt type to use for T5-XXL output"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("clip_l", "clip_g", "t5xxl")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Switch between different prompt types for SD3 (CLIP-L, CLIP-G, T5-XXL)."

    def get_value(self, clip_l: str, clip_g: str, t5xxl: str, clip_l_prompt: str, 
                  clip_g_prompt: str, t5xxl_prompt: str) -> Tuple[str, str, str]:
        """Switch prompts between different SD3 prompt types"""
        _clip_l = self._select_prompt(clip_l, clip_g, t5xxl, clip_l_prompt)
        _clip_g = self._select_prompt(clip_l, clip_g, t5xxl, clip_g_prompt)
        _t5xxl = self._select_prompt(clip_l, clip_g, t5xxl, t5xxl_prompt)
        
        return (_clip_l, _clip_g, _t5xxl)
    
    def _select_prompt(self, clip_l: str, clip_g: str, t5xxl: str, prompt_type: str) -> str:
        """Select prompt based on type"""
        if prompt_type == "clip_l":
            return clip_l
        elif prompt_type == "clip_g":
            return clip_g
        else:  # t5xxl
            return t5xxl

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

class GuidanceDefault_JK:
    """Default guidance scale value for model conditioning"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "guidance": ("FLOAT", {
                    "default": 3.5, 
                    "min": 0.0, 
                    "max": 100.0, 
                    "step": 0.1,
                    "tooltip": "Guidance scale for model conditioning"
                }),
            },
        }
    
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("GUIDANCE",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Default guidance scale value for model conditioning."

    def get_value(self, guidance: float) -> Tuple[float]:
        """Get guidance scale value"""
        return (guidance,)

class ImageResizeMode_JK:
    """Image resize mode selection for various resizing strategies"""
    
    RESIZE_MODES = ["Just Resize", "Crop and Resize", "Resize and Fill"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resize_mode": (cls.RESIZE_MODES, {
                    "default": "Just Resize",
                    "tooltip": "Method for resizing images"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("MODE",)
    FUNCTION = "execute"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Image resize mode selection for various resizing strategies."

    def execute(self, resize_mode: str) -> Tuple[str]:
        """Get resize mode value"""
        return (resize_mode,)

class SamplerLoader_JK:
    """Sampler and scheduler selection with name output"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS, {
                    "tooltip": "Sampling algorithm selection"
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {
                    "tooltip": "Scheduling algorithm selection"
                }),
            }
        }

    RETURN_TYPES = ("STRING", comfy.samplers.KSampler.SAMPLERS, "STRING", comfy.samplers.KSampler.SCHEDULERS)
    RETURN_NAMES = ("sampler_name", "Sampler", "schedular_name", "Schedular")
    FUNCTION = "list"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Sampler and scheduler selection with name output."

    def list(self, sampler: str, scheduler: str) -> Tuple[str, str, str, str]:
        """Get sampler and scheduler with names"""
        return (sampler, sampler, scheduler, scheduler)

class UpscaleMethod_JK:
    """Upscale method selection for images and latents"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"], {
                    "default": "lanczos",
                    "tooltip": "Upscaling method for images"
                }),
                "latent_upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "bislerp"], {
                    "default": "bilinear",
                    "tooltip": "Upscaling method for latent representations"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_upscale_method", "latent_upscale_method")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Upscale method selection for images and latents."

    def get_value(self, image_upscale_method: str, latent_upscale_method: str) -> Tuple[str, str]:
        """Get upscale method values"""
        return (image_upscale_method, latent_upscale_method)

#---------------------------------------------------------------------------------------------------------------------#
# Resolution & Aspect Ratio Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_AspectRatio_JK:
    """Aspect ratio selector for various model types with custom resolution support"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": ([
                    "Custom", "SD15 512x512", "SD15 680x512", "SD15 768x512", "SD15 912x512", "SD15 952x512", "SD15 1024x512",
                    "SD15 1224x512", "SD15 768x432", "SD15 768x416", "SD15 768x384", "SD15 768x320", 
                    "SDXL 1024x1024", "SDXL 1024x960", "SDXL 1088x960", "SD3 1088x896", "SDXL 1152x896", "SDXL 1152x832", "SD3 1216x832", "SDXL 1280x768",
                    "QWen 1328x1328", "QWen 1328x800", "SD3 1344x768", "SDXL 1344x704", "SDXL 1408x704", "SDXL 1472x704", "SD3 1536x640", "SDXL 1600x640", "SDXL 1664x576", "SDXL 1728x576", "QWen 1920x1080"
                ], {
                    "tooltip": "Predefined resolution presets for different models"
                }),
                "custom_width": ("INT", {
                    "default": 512, 
                    "min": 64, 
                    "max": 16384, 
                    "step": 8,
                    "tooltip": "Custom width when resolution is set to Custom"
                }),
                "custom_height": ("INT", {
                    "default": 512, 
                    "min": 64, 
                    "max": 16384, 
                    "step": 8,
                    "tooltip": "Custom height when resolution is set to Custom"
                }),
                "swap_dimensions": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Swap width and height dimensions"
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height")
    FUNCTION = "Aspect_Ratio"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Aspect ratio selector for various model types with custom resolution support."

    def Aspect_Ratio(self, custom_width: int, custom_height: int, resolution: str, swap_dimensions: bool) -> Tuple[int, int]:
        """Calculate aspect ratio dimensions based on selection"""
        if resolution == "Custom":
            width, height = custom_width, custom_height
        else:
            try:
                width, height = get_resolution(resolution)
            except Exception as e:
                # Fallback to default resolution if get_resolution fails
                print(f"Warning: Failed to get resolution for {resolution}: {e}. Using default 512x512.")
                width, height = 512, 512
            
        if swap_dimensions:
            return (height, width)
        else:
            return (width, height)

#---------------------------------------------------------------------------------------------------------------------#
# String & Data Processing Nodes
#---------------------------------------------------------------------------------------------------------------------#

# copied from https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Conversion-Nodes#cr-string-to-combo
class StringToCombo_JK:
    """Convert comma-separated string to combo selection (first item)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {
                    "multiline": False, 
                    "default": "",
                    "tooltip": "Comma-separated string to convert to combo"
                }),
            },
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("any",)
    FUNCTION = "convert"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Convert comma-separated string to combo selection (first item)."

    def convert(self, string: str) -> Tuple[Any]:
        """Convert string to combo value (first item in comma-separated list)"""
        text_list = list()
        
        if string != "":
            values = string.split(',')
            text_list = values[0].strip()  # Take first item and strip whitespace
        
        return (text_list,)

class GetNthString_JK:
    """Get nth item from comma-separated string list with type conversion"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_list": ("STRING", {
                    "default": "1.0, 2.0, 3.0",
                    "multiline": True,
                    "tooltip": "Comma-separated list of values"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": -1,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Index of item to retrieve (negative values count from end)"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "INT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("string", "int", "float", "boolean")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Get nth item from comma-separated string list with type conversion."
    OUTPUT_NODE = False

    def process(self, string_list: str, index: int) -> Tuple[str, int, float, bool]:
        """Get nth item from string list with automatic type conversion"""
        try:
            items = parse_string_list(string_list)
        except Exception as e:
            raise ValueError(f"Error parsing string list: {str(e)}")
        
        # Handle negative indices (counting from end)
        if index < 0:
            index = len(items) + index
        
        # Check index bounds
        if index < 0 or index >= len(items):
            raise ValueError(f"Index {index} out of range (0-{len(items)-1})")
        
        selected_str = items[index]
        
        # Type conversions with error handling
        try:
            int_val = int(selected_str)
        except ValueError:
            int_val = 0
        
        try:
            float_val = float(selected_str)
        except ValueError:
            float_val = 0.0
        
        # Boolean conversion with common truthy/falsy values
        lower_str = selected_str.lower().strip()
        if lower_str in ("true", "1", "yes", "y", "on"):
            bool_val = True
        elif lower_str in ("false", "0", "no", "n", "off"):
            bool_val = False
        else:
            bool_val = bool(selected_str)
        
        return (selected_str, int_val, float_val, bool_val)

#---------------------------------------------------------------------------------------------------------------------#
# JSON Data Nodes
#---------------------------------------------------------------------------------------------------------------------#

class SaveStringListToJSON_JK:
    """Save string data to JSON file with overwrite control"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_input": ("STRING", {
                    "default": '',
                    "tooltip": "String data to save to JSON file"
                }), 
                "file_path": ("STRING", {
                    "default": '',
                    "tooltip": "Full path to JSON file for saving"
                }),
                "overwrite": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Overwrite existing file if True, skip if False"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string_output",) 
    FUNCTION = "save_strlist"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Save string data to JSON file with overwrite control and directory creation."

    def save_strlist(self, string_input: str, file_path: str, overwrite: bool) -> Tuple[str]:
        """Save string data to JSON file with error handling"""
        # Check if file path is empty
        if not file_path:
            print("Error: file_path is empty. Cannot save JSON.")
            return ("",)

        # Check if file exists and overwrite is disabled
        if os.path.exists(file_path) and not overwrite:
            print(f"File '{file_path}' already exists and overwrite is set to False. Skipping save.")
            return (string_input,)

        # Ensure directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
                print(f"Created directory: {parent_dir}")
            except Exception as e:
                print(f"Error creating directory {parent_dir}: {e}")
                return (string_input,)

        # Save to file with proper error handling
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(string_input, file, indent=4, ensure_ascii=False)
            print(f"Successfully saved JSON to {file_path}")
        except Exception as e:
            print(f"Error saving JSON to {file_path}: {e}")
            return (string_input,)
        
        return (string_input,)

class LoadStringListFromJSON_JK:
    """Load string data from JSON file with caching and force reload options"""
    
    def __init__(self):
        self._cached_file_path = None
        self._cached_file_hash = None
        self._cached_data = None
        self._last_force_reload_value = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": '',
                    "tooltip": "Full path to JSON file for loading"
                }),
            },
            "optional": {
                "force_reload": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 100000,
                    "tooltip": "Force reload when value changes (useful for triggering reloads)"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string_output",)
    FUNCTION = "load_strlist"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Load string data from JSON file with caching and force reload options."

    def load_strlist(self, file_path: str, force_reload: int = 0) -> Tuple[str]:
        """Load string data from JSON file with intelligent caching"""
        # Check if file path is empty
        if not file_path:
            print("Warning: file_path is empty. Returning empty JSON string.")
            self._clear_cache()
            return ("",)
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}. Returning empty JSON string.")
            self._clear_cache()
            return ("",)
        
        # Calculate current file hash for change detection
        try:
            from .jake_tools import calculate_sha256
            current_file_hash = calculate_sha256(file_path)
        except ImportError:
            # Fallback to file modification time if SHA256 not available
            current_file_hash = str(os.path.getmtime(file_path))
        
        # Check if reload is needed based on file changes or force_reload
        if (file_path != self._cached_file_path or
            current_file_hash != self._cached_file_hash or
            force_reload != self._last_force_reload_value):
            
            print(f"Loading JSON from {file_path} (reloaded due to change or force_reload).")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    str_lists = json.load(file)
                
                # Handle string list format compatibility
                if isinstance(str_lists, list) and all(isinstance(item, str) for item in str_lists):
                    try:
                        parsed_list = []
                        for s in str_lists:
                            # Try to parse each string as JSON, keep original if it fails
                            try:
                                parsed_list.append(json.loads(s))
                            except json.JSONDecodeError:
                                parsed_list.append(s)
                        str_lists = parsed_list
                    except Exception:
                        # Keep original if bulk parsing fails
                        pass
                
                # Update cache with new data
                self._cached_file_path = file_path
                self._cached_file_hash = current_file_hash
                self._cached_data = str_lists
                self._last_force_reload_value = force_reload
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {file_path}: {e}")
                self._clear_cache()
                return ("",)
                
            except Exception as e:
                print(f"An unexpected error occurred while reading {file_path}: {e}")
                self._clear_cache()
                return ("",)
        else:
            print(f"Using cached JSON data for {file_path} (no change detected).")
        
        # Return cached data as JSON string
        if self._cached_data is not None:
            try:
                return (json.dumps(self._cached_data, ensure_ascii=False),)
            except Exception as e:
                print(f"Error serializing cached data to JSON: {e}")
                return ("",)
        else:
            return ("",)
    
    def _clear_cache(self):
        """Clear cache data"""
        self._cached_file_path = None
        self._cached_file_hash = None
        self._cached_data = None

#---------------------------------------------------------------------------------------------------------------------#
# Simple Utility Nodes
#---------------------------------------------------------------------------------------------------------------------#
class TilingMode_JK:
    """Tiling mode selection for image generation"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tiling": (["enable", "x_only", "y_only", "disable"], {
                    "default": "disable",
                    "tooltip": "Tiling mode for image generation"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("TILING",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Tiling mode selection for image generation."

    def get_value(self, tiling: str) -> Tuple[str]:
        """Get tiling mode value"""
        return (tiling,)

class RemoveInput_JK:
    """Remove input and provide default values for any type"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {},
        }
    
    RETURN_TYPES = (any_type, "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("any", "TRUE", "FALSE")
    FUNCTION = "removeinput"
    CATEGORY = icons.get("JK/Misc")
    DESCRIPTION = "Remove input and provide default values for any type"
    DEPRECATED = True

    def removeinput(self) -> Tuple[Any, bool, bool]:
        """Remove input and return default values"""
        return (None, True, False)
