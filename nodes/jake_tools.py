#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Tools for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import os
import torch
import numpy
import hashlib
import math
from PIL import Image
from pathlib import Path
from typing import Any, List, Tuple
from datetime import datetime

#---------------------------------------------------------------------------------------------------------------------#
# Core Tools
#---------------------------------------------------------------------------------------------------------------------#

def parse_name(path_name: str) -> str:
    """Parse filename from path."""
    path = path_name
    filename = path.split("/")[-1]
    filename = path.split("\\")[-1]
    filename = filename.split(".")[:-1]
    filename = ".".join(filename)
    return filename

def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    if not os.path.exists(file_path):
        print(f"Warning: File not found at {file_path}. Cannot calculate hash.")
        return None
    
    sha256_hash = hashlib.sha256()
    
    try:
        # Read file in binary mode, chunk by chunk for large files
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(8192), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    except IOError as e:
        print(f"Error reading file {file_path} for hash calculation: {e}")
        return None
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def handle_whitespace(string: str) -> str:
    """Normalize whitespace in string."""
    return string.strip().replace("\n", " ").replace("\r", " ").replace("\t", " ")

def get_timestamp(time_format: str) -> str:
    """Get formatted timestamp."""
    now = datetime.now()
    try:
        timestamp = now.strftime(time_format)
    except:
        timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    return timestamp

def make_pathname(filename: str, seed: int, modelname: str, counter: int) -> str:
    """Create pathname with template variables."""
    filename = filename.replace("%date", get_timestamp("%Y-%m-%d"))
    filename = filename.replace("%time", get_timestamp("%H%M%S"))
    filename = filename.replace("%model", modelname)
    filename = filename.replace("%seed", str(seed))
    filename = filename.replace("%counter", str(counter))
    return filename

def make_filename(filename: str, seed: int, modelname: str, counter: int) -> str:
    """Create filename with template variables."""
    filename = make_pathname(filename, seed, modelname, counter)
    return get_timestamp("%Y-%m-%d") if filename == "" else filename

#---------------------------------------------------------------------------------------------------------------------#
# Resolution Tools
#---------------------------------------------------------------------------------------------------------------------#

# Resolution presets organized by model type
RESOLUTION_PRESETS = {
    "SD15": {
        "512x512": (512, 512),
        "680x512": (680, 512),
        "768x512": (768, 512),
        "912x512": (912, 512),
        "952x512": (952, 512),
        "1024x512": (1024, 512),
        "1224x512": (1224, 512),
        "768x432": (768, 432),
        "768x416": (768, 416),
        "768x384": (768, 384),
        "768x320": (768, 320),
    },
    "SDXL": {
        "1024x1024": (1024, 1024),
        "1024x960": (1024, 960),
        "1088x960": (1088, 960),
        "1152x896": (1152, 896),
        "1152x832": (1152, 832),
        "1280x768": (1280, 768),
        "1344x704": (1344, 704),
        "1408x704": (1408, 704),
        "1472x704": (1472, 704),
    },
    "SD3": {
        "1088x896": (1088, 896),
        "1216x832": (1216, 832),
        "1344x768": (1344, 768),
        "1536x640": (1536, 640),
        "1600x640": (1600, 640),
        "1664x576": (1664, 576),
        "1728x576": (1728, 576),
    },
    "QWen": {
        "1328x1328": (1328, 1328),
        "1328x800": (1328, 800),
        "1920x1080": (1920, 1080),
    }
}

# SD3 aspect ratios
SD3_ASPECT_RATIOS = {
    "1:1": (1024, 1024),
    "5:4": (1088, 896),
    "3:2": (1216, 832),
    "16:9": (1344, 768),
    "21:9": (1536, 640),
    "4:5": (896, 1088),
    "2:3": (832, 1216),
    "9:16": (768, 1344),
    "9:21": (640, 1536),
}

# SD3 Core aspect ratios
SD3_CORE_ASPECT_RATIOS = {
    "1:1": (1536, 1536),
    "5:4": (1632, 1344),
    "3:2": (1824, 1248),
    "16:9": (2016, 1152),
    "21:9": (2304, 960),
    "4:5": (1344, 1632),
    "2:3": (1248, 1824),
    "9:16": (1152, 2016),
    "9:21": (960, 2304),
}

def get_resolution(resolution: str) -> Tuple[int, int]:
    """Get width and height for a given resolution preset."""
    # Check if it's a combined format like "SD15 512x512"
    if " " in resolution:
        model_type, res_key = resolution.split(" ", 1)
        if model_type in RESOLUTION_PRESETS and res_key in RESOLUTION_PRESETS[model_type]:
            return RESOLUTION_PRESETS[model_type][res_key]
    
    # Fallback to custom resolution
    return (512, 512)

def get_sd3_resolution(ratio: str) -> Tuple[int, int]:
    """Get SD3 resolution for aspect ratio."""
    return SD3_ASPECT_RATIOS.get(ratio, (1024, 1024))

def get_sd3_core_resolution(ratio: str) -> Tuple[int, int]:
    """Get SD3 Core resolution for aspect ratio."""
    return SD3_CORE_ASPECT_RATIOS.get(ratio, (1536, 1536))

#---------------------------------------------------------------------------------------------------------------------#
# Type System
#---------------------------------------------------------------------------------------------------------------------#

class AnyType(str):
    """A special class that is always equal in not equal comparisons."""
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

#---------------------------------------------------------------------------------------------------------------------#
# Image Conversion Tools
#---------------------------------------------------------------------------------------------------------------------#

def tensor2pil(t_image: torch.Tensor) -> 'Image':
    """Convert tensor to PIL Image."""
    return Image.fromarray(numpy.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))

def pil2tensor(image: 'Image') -> torch.Tensor:
    """Convert PIL Image to tensor."""
    return torch.from_numpy(numpy.array(image).astype(numpy.float32) / 255.0).unsqueeze(0)

# ControlNet Union types
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
