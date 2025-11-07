#---------------------------------------------------------------------------------------------------------------------#
# Jake Latent Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
from typing import Tuple, Dict
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Latent Nodes
#---------------------------------------------------------------------------------------------------------------------#

class EmptyLatentColor_JK:
    """Provide empty latent colors for different model types (SD15, SDXL, SD3, FLUX)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}
    
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("SD15", "SDXL", "SD3", "FLUX")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Latent")
    DESCRIPTION = "Provide empty latent colors for different model types (SD15, SDXL, SD3, FLUX)"
    DEPRECATED = True

    def get_value(self) -> Tuple[int, int, int, int]:
        """Get empty latent colors for different model types"""
        # Return predefined color values for different model types
        return (8548961, 9077127, 9214099, 8618319)

class LatentCropOffset_JK:
    """Calculate latent space offset from image space offset for cropping operations"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_offset": ("INT", {"default": 0}),
            },
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("latent_offset",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Latent")
    DESCRIPTION = "Calculate latent space offset from image space offset for cropping operations"
    DEPRECATED = True

    def get_value(self, image_offset=0):
        """Convert image offset to latent offset (adding 8 for alignment)"""
        return ((image_offset + 8),)
