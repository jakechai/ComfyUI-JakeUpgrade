#---------------------------------------------------------------------------------------------------------------------#
# Jake Mask Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
from ..categories import icons

class IsMaskEmpty_JK:
    """Check if mask is completely empty (all zeros)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
        }
    
    RETURN_TYPES = ["BOOLEAN"]
    RETURN_NAMES = ["BOOLEAN"]
    FUNCTION = "main"
    CATEGORY = icons.get("JK/Mask")
    DESCRIPTION = "Check if mask is completely empty (contains only zeros)"

    def main(self, mask):
        """Check if mask contains only zeros"""
        is_empty = torch.all(mask == 0).int().item() != 0
        return (is_empty,)
