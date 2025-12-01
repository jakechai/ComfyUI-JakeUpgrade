#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Switch Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import sys
from typing import Any, Tuple
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Bool, Int, Float, and String Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_Boolean_JK:
    """Convert boolean value to multiple output types (boolean, number, integer)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Input boolean value to convert"
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "NUMBER", "INT")
    RETURN_NAMES = ("boolean", "number", "int")
    FUNCTION = "return_boolean"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Convert boolean value to multiple output types (boolean, number, integer)"

    def return_boolean(self, boolean_value: bool) -> Tuple[bool, float, int]:
        """Convert boolean to multiple output types"""
        numeric_value = 1 if boolean_value else 0
        return (boolean_value, float(numeric_value), numeric_value)

class CR_IntInputSwitch_JK:
    """Switch between two integer inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=int_true, False=int_false)"
                }),
                "int_false": ("INT", {
                    "default": 0, 
                    "min": -18446744073709551615, 
                    "max": 18446744073709551615, 
                    "step": 1,
                    "tooltip": "Integer value to return when condition is False"
                }),
            },
            "optional": {
                "int_true": ("INT", {
                    "default": 0, 
                    "min": -18446744073709551615, 
                    "max": 18446744073709551615, 
                    "step": 1,
                    "tooltip": "Integer value to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("INT", "BOOLEAN")
    RETURN_NAMES = ("int_output", "boolean")
    FUNCTION = "InputInt"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two integer inputs based on boolean condition"

    def InputInt(self, boolean_value: bool, int_false: int, int_true: int = None) -> Tuple[int, bool]:
        """Select integer input based on boolean condition"""
        if int_true is not None and boolean_value:
            return (int_true, boolean_value)
        else:
            return (int_false, boolean_value)

class CR_FloatInputSwitch_JK:
    """Switch between two float inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=float_true, False=float_false)"
                }),
                "float_false": ("FLOAT", {
                    "default": 0, 
                    "min": -sys.float_info.max, 
                    "max": sys.float_info.max, 
                    "step": 0.0001,
                    "tooltip": "Float value to return when condition is False"
                }),
            },
            "optional": {
                "float_true": ("FLOAT", {
                    "default": 0, 
                    "min": -sys.float_info.max, 
                    "max": sys.float_info.max, 
                    "step": 0.0001,
                    "tooltip": "Float value to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("FLOAT", "BOOLEAN")
    RETURN_NAMES = ("float_output", "boolean")
    FUNCTION = "InputFloat"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two float inputs based on boolean condition"

    def InputFloat(self, boolean_value: bool, float_false: float, float_true: float = None) -> Tuple[float, bool]:
        """Select float input based on boolean condition"""
        if float_true is not None and boolean_value:
            return (float_true, boolean_value)
        else:
            return (float_false, boolean_value)

class CR_TextInputSwitch_JK:
    """Switch between two text inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=text_true, False=text_false)"
                }),
                "text_false": ("STRING", {
                    "default": "",
                    "tooltip": "Text value to return when condition is False"
                }),
            },
            "optional": {
                "text_true": ("STRING", {
                    "default": "",
                    "tooltip": "Text value to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("string_output", "boolean")
    FUNCTION = "text_input_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two text inputs based on boolean condition"

    def text_input_switch(self, boolean_value: bool, text_false: str, text_true: str = None) -> Tuple[str, bool]:
        """Select text input based on boolean condition"""
        if text_true is not None and boolean_value:
            return (text_true, boolean_value)
        else:
            return (text_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Image and Media Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_ImageInputSwitch_JK:
    """Switch between two image inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=image_true, False=image_false)"
                }),
                "image_false": ("IMAGE", {
                    "tooltip": "Image to return when condition is False"
                }),
            },
            "optional": {
                "image_true": ("IMAGE", {
                    "tooltip": "Image to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN")
    RETURN_NAMES = ("image_output", "boolean")
    FUNCTION = "InputImages"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two image inputs based on boolean condition"

    def InputImages(self, boolean_value: bool, image_false: Any, image_true: Any = None) -> Tuple[Any, bool]:
        """Select image input based on boolean condition"""
        if image_true is not None and boolean_value:
            return (image_true, boolean_value)
        else:
            return (image_false, boolean_value)

class CR_MaskInputSwitch_JK:
    """Switch between two mask inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=mask_true, False=mask_false)"
                }),
                "mask_false": ("MASK", {
                    "tooltip": "Mask to return when condition is False"
                }),
            },
            "optional": {
                "mask_true": ("MASK", {
                    "tooltip": "Mask to return when condition is True (optional)"
                })
            },
        }

    RETURN_TYPES = ("MASK", "BOOLEAN")
    RETURN_NAMES = ("mask_output", "boolean")
    FUNCTION = "InputMasks"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two mask inputs based on boolean condition"

    def InputMasks(self, boolean_value: bool, mask_false: Any, mask_true: Any = None) -> Tuple[Any, bool]:
        """Select mask input based on boolean condition"""
        if mask_true is not None and boolean_value:
            return (mask_true, boolean_value)
        else:
            return (mask_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Model and Latent Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_LatentInputSwitch_JK:
    """Switch between two latent inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=latent_true, False=latent_false)"
                }),
                "latent_false": ("LATENT", {
                    "tooltip": "Latent to return when condition is False"
                }),
            },
            "optional": {
                "latent_true": ("LATENT", {
                    "tooltip": "Latent to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("LATENT", "BOOLEAN")
    RETURN_NAMES = ("latent_output", "boolean")
    FUNCTION = "InputLatents"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two latent inputs based on boolean condition"

    def InputLatents(self, boolean_value: bool, latent_false: Any, latent_true: Any = None) -> Tuple[Any, bool]:
        """Select latent input based on boolean condition"""
        if latent_true is not None and boolean_value:
            return (latent_true, boolean_value)
        else:
            return (latent_false, boolean_value)

class CR_ModelInputSwitch_JK:
    """Switch between two model inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=model_true, False=model_false)"
                }),
                "model_false": ("MODEL", {
                    "tooltip": "Model to return when condition is False"
                }),
            },
            "optional": {
                "model_true": ("MODEL", {
                    "tooltip": "Model to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("MODEL", "BOOLEAN")
    RETURN_NAMES = ("model_output", "boolean")
    FUNCTION = "InputModel"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two model inputs based on boolean condition"

    def InputModel(self, boolean_value: bool, model_false: Any, model_true: Any = None) -> Tuple[Any, bool]:
        """Select model input based on boolean condition"""
        if model_true is not None and boolean_value:
            return (model_true, boolean_value)
        else:
            return (model_false, boolean_value)

class CR_VAEInputSwitch_JK:
    """Switch between two VAE inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=VAE_true, False=VAE_false)"
                }),
                "VAE_false": ("VAE", {
                    "tooltip": "VAE to return when condition is False"
                }),
            },
            "optional": {
                "VAE_true": ("VAE", {
                    "tooltip": "VAE to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("VAE", "BOOLEAN")
    RETURN_NAMES = ("vae_output", "boolean")
    FUNCTION = "vae_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two VAE inputs based on boolean condition"

    def vae_switch(self, boolean_value: bool, VAE_false: Any, VAE_true: Any = None) -> Tuple[Any, bool]:
        """Select VAE input based on boolean condition"""
        if VAE_true is not None and boolean_value:
            return (VAE_true, boolean_value)
        else:
            return (VAE_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Conditioning and CLIP Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_ConditioningInputSwitch_JK:
    """Switch between two conditioning inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=conditioning_true, False=conditioning_false)"
                }),
                "conditioning_false": ("CONDITIONING", {
                    "tooltip": "Conditioning to return when condition is False"
                }),
            },
            "optional": {
                "conditioning_true": ("CONDITIONING", {
                    "tooltip": "Conditioning to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("CONDITIONING", "BOOLEAN")
    RETURN_NAMES = ("conditioning_output", "boolean")
    FUNCTION = "InputConditioning"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two conditioning inputs based on boolean condition"

    def InputConditioning(self, boolean_value: bool, conditioning_false: Any, conditioning_true: Any = None) -> Tuple[Any, bool]:
        """Select conditioning input based on boolean condition"""
        if conditioning_true is not None and boolean_value:
            return (conditioning_true, boolean_value)
        else:
            return (conditioning_false, boolean_value)

class CR_ClipInputSwitch_JK:
    """Switch between two CLIP inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=clip_true, False=clip_false)"
                }),
                "clip_false": ("CLIP", {
                    "tooltip": "CLIP to return when condition is False"
                }),
            },
            "optional": {
                "clip_true": ("CLIP", {
                    "tooltip": "CLIP to return when condition is True (optional)"
                }),
            },
        }

    RETURN_TYPES = ("CLIP", "BOOLEAN")
    RETURN_NAMES = ("clip_output", "boolean")
    FUNCTION = "InputClip"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two CLIP inputs based on boolean condition"

    def InputClip(self, boolean_value: bool, clip_false: Any, clip_true: Any = None) -> Tuple[Any, bool]:
        """Select CLIP input based on boolean condition"""
        if clip_true is not None and boolean_value:
            return (clip_true, boolean_value)
        else:
            return (clip_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# ControlNet Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_ControlNetInputSwitch_JK:
    """Switch between two ControlNet inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=control_net_true, False=control_net_false)"
                }),
                "control_net_false": ("CONTROL_NET", {
                    "tooltip": "ControlNet to return when condition is False"
                }),
            },
            "optional": {
                "control_net_true": ("CONTROL_NET", {
                    "tooltip": "ControlNet to return when condition is True (optional)"
                }),
            },
        }
        
    RETURN_TYPES = ("CONTROL_NET", "BOOLEAN")
    RETURN_NAMES = ("control_net_output", "boolean")
    FUNCTION = "InputControlNet"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two ControlNet inputs based on boolean condition"

    def InputControlNet(self, boolean_value: bool, control_net_false: Any, control_net_true: Any = None) -> Tuple[Any, bool]:
        """Select ControlNet input based on boolean condition"""
        if control_net_true is not None and boolean_value:
            return (control_net_true, boolean_value)
        else:
            return (control_net_false, boolean_value)

class CR_ControlNetStackInputSwitch_JK:
    """Switch between two ControlNet stack inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=control_net_stack_true, False=control_net_stack_false)"
                }),
                "control_net_stack_false": ("CONTROL_NET_STACK", {
                    "tooltip": "ControlNet stack to return when condition is False"
                }),
            },
            "optional": {
                "control_net_stack_true": ("CONTROL_NET_STACK", {
                    "tooltip": "ControlNet stack to return when condition is True (optional)"
                }),
            },
        }
        
    RETURN_TYPES = ("CONTROL_NET_STACK", "BOOLEAN")
    RETURN_NAMES = ("control_net_stack_output", "boolean")
    FUNCTION = "InputControlNetStack"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two ControlNet stack inputs based on boolean condition"

    def InputControlNetStack(self, boolean_value: bool, control_net_stack_false: Any, control_net_stack_true: Any = None) -> Tuple[Any, bool]:
        """Select ControlNet stack input based on boolean condition"""
        if control_net_stack_true is not None and boolean_value:
            return (control_net_stack_true, boolean_value)
        else:
            return (control_net_stack_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Sampling and Noise Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_NoiseInputSwitch_JK:
    """Switch between two noise inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=noise_true, False=noise_false)"
                }),
                "noise_false": ("NOISE", {
                    "tooltip": "Noise to return when condition is False"
                }),
            },
            "optional": {
                "noise_true": ("NOISE", {
                    "tooltip": "Noise to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("NOISE", "BOOLEAN")
    RETURN_NAMES = ("noise_output", "boolean")
    FUNCTION = "noise_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two noise inputs based on boolean condition"

    def noise_switch(self, boolean_value: bool, noise_false: Any, noise_true: Any = None) -> Tuple[Any, bool]:
        """Select noise input based on boolean condition"""
        if noise_true is not None and boolean_value:
            return (noise_true, boolean_value)
        else:
            return (noise_false, boolean_value)

class CR_GuiderInputSwitch_JK:
    """Switch between two guider inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=guider_true, False=guider_false)"
                }),
                "guider_false": ("GUIDER", {
                    "tooltip": "Guider to return when condition is False"
                }),
            },
            "optional": {
                "guider_true": ("GUIDER", {
                    "tooltip": "Guider to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("GUIDER", "BOOLEAN")
    RETURN_NAMES = ("guider_output", "boolean")
    FUNCTION = "guider_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two guider inputs based on boolean condition"

    def guider_switch(self, boolean_value: bool, guider_false: Any, guider_true: Any = None) -> Tuple[Any, bool]:
        """Select guider input based on boolean condition"""
        if guider_true is not None and boolean_value:
            return (guider_true, boolean_value)
        else:
            return (guider_false, boolean_value)

class CR_SamplerInputSwitch_JK:
    """Switch between two sampler inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=sampler_true, False=sampler_false)"
                }),
                "sampler_false": ("SAMPLER", {
                    "tooltip": "Sampler to return when condition is False"
                }),
            },
            "optional": {
                "sampler_true": ("SAMPLER", {
                    "tooltip": "Sampler to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("SAMPLER", "BOOLEAN")
    RETURN_NAMES = ("sampler_output", "boolean")
    FUNCTION = "sampler_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two sampler inputs based on boolean condition"

    def sampler_switch(self, boolean_value: bool, sampler_false: Any, sampler_true: Any = None) -> Tuple[Any, bool]:
        """Select sampler input based on boolean condition"""
        if sampler_true is not None and boolean_value:
            return (sampler_true, boolean_value)
        else:
            return (sampler_false, boolean_value)

class CR_SigmasInputSwitch_JK:
    """Switch between two sigmas inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=sigmas_true, False=sigmas_false)"
                }),
                "sigmas_false": ("SIGMAS", {
                    "tooltip": "Sigmas to return when condition is False"
                }),
            },
            "optional": {
                "sigmas_true": ("SIGMAS", {
                    "tooltip": "Sigmas to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("SIGMAS", "BOOLEAN")
    RETURN_NAMES = ("sigmas_output", "boolean")
    FUNCTION = "sigmas_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two sigmas inputs based on boolean condition"

    def sigmas_switch(self, boolean_value: bool, sigmas_false: Any, sigmas_true: Any = None) -> Tuple[Any, bool]:
        """Select sigmas input based on boolean condition"""
        if sigmas_true is not None and boolean_value:
            return (sigmas_true, boolean_value)
        else:
            return (sigmas_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# 3D and Mesh Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CR_MeshInputSwitch_JK:
    """Switch between two mesh inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=mesh_true, False=mesh_false)"
                }),
                "mesh_false": ("MESH", {
                    "tooltip": "Mesh to return when condition is False"
                }),
            },
            "optional": {
                "mesh_true": ("MESH", {
                    "tooltip": "Mesh to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("MESH", "BOOLEAN")
    RETURN_NAMES = ("mesh_output", "boolean")
    FUNCTION = "mesh_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two mesh inputs based on boolean condition"

    def mesh_switch(self, boolean_value: bool, mesh_false: Any, mesh_true: Any = None) -> Tuple[Any, bool]:
        """Select mesh input based on boolean condition"""
        if mesh_true is not None and boolean_value:
            return (mesh_true, boolean_value)
        else:
            return (mesh_false, boolean_value)

class CR_PlyInputSwitch_JK:
    """Switch between two PLY (point cloud) inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=ply_true, False=ply_false)"
                }),
                "ply_false": ("GS_PLY", {
                    "tooltip": "PLY file to return when condition is False"
                }),
            },
            "optional": {
                "ply_true": ("GS_PLY", {
                    "tooltip": "PLY file to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("GS_PLY", "BOOLEAN")
    RETURN_NAMES = ("ply_output", "boolean")
    FUNCTION = "ply_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two PLY (point cloud) inputs based on boolean condition"

    def ply_switch(self, boolean_value: bool, ply_false: Any, ply_true: Any = None) -> Tuple[Any, bool]:
        """Select PLY input based on boolean condition"""
        if ply_true is not None and boolean_value:
            return (ply_true, boolean_value)
        else:
            return (ply_false, boolean_value)

class CR_TriMeshInputSwitch_JK:
    """Switch between two triangle mesh inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=trimesh_true, False=trimesh_false)"
                }),
                "trimesh_false": ("TRIMESH", {
                    "tooltip": "Triangle mesh to return when condition is False"
                }),
            },
            "optional": {
                "trimesh_true": ("TRIMESH", {
                    "tooltip": "Triangle mesh to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("TRIMESH", "BOOLEAN")
    RETURN_NAMES = ("trimesh_output", "boolean")
    FUNCTION = "trimesh_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two triangle mesh inputs based on boolean condition"

    def trimesh_switch(self, boolean_value: bool, trimesh_false: Any, trimesh_true: Any = None) -> Tuple[Any, bool]:
        """Select triangle mesh input based on boolean condition"""
        if trimesh_true is not None and boolean_value:
            return (trimesh_true, boolean_value)
        else:
            return (trimesh_false, boolean_value)

class CR_OrbitPoseInputSwitch_JK:
    """Switch between two orbit camera pose inputs based on boolean condition"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Condition to select between inputs (True=orbit_camposes_true, False=orbit_camposes_false)"
                }),
                "orbit_camposes_false": ("ORBIT_CAMPOSES", {
                    "tooltip": "Orbit camera poses to return when condition is False"
                }),
            },
            "optional": {
                "orbit_camposes_true": ("ORBIT_CAMPOSES", {
                    "tooltip": "Orbit camera poses to return when condition is True (optional)"
                }),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES", "BOOLEAN")
    RETURN_NAMES = ("orbit_camposes_output", "boolean")
    FUNCTION = "orbit_switch"
    CATEGORY = icons.get("JK/Switch")
    DESCRIPTION = "Switch between two orbit camera pose inputs based on boolean condition"

    def orbit_switch(self, boolean_value: bool, orbit_camposes_false: Any, orbit_camposes_true: Any = None) -> Tuple[Any, bool]:
        """Select orbit camera pose input based on boolean condition"""
        if orbit_camposes_true is not None and boolean_value:
            return (orbit_camposes_true, boolean_value)
        else:
            return (orbit_camposes_false, boolean_value)

#---------------------------------------------------------------------------------------------------------------------#
# Pipe Switch Nodes
#---------------------------------------------------------------------------------------------------------------------#

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
