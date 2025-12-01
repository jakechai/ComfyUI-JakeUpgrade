#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade ControlNet Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
import folder_paths
import comfy.controlnet
import comfy.sd
import comfy.utils
from nodes import ControlNetApplyAdvanced
from typing import Any, Tuple, List, Dict
from .jake_tools import UNION_CONTROLNET_TYPES
from ..categories import icons

class CR_ControlNetLoader_JK:
    """Load ControlNet models with union type support for advanced control"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "control_net_name": (["None"] + folder_paths.get_filename_list("controlnet"), {
                    "tooltip": "Select ControlNet model to load"
                }),
                "union_type": (["None"] + ["auto"] + list(UNION_CONTROLNET_TYPES.keys()), {
                    "tooltip": "Select union type for ControlNet compatibility"
                })
            }
        }

    RETURN_TYPES = ("CONTROL_NET",)
    FUNCTION = "load_controlnet"
    CATEGORY = icons.get("JK/ControlNet")
    DESCRIPTION = "Load ControlNet models with configurable union types."
    
    def load_controlnet(self, control_net_name, union_type):
        """加载ControlNet模型，支持union类型配置"""
        
        if control_net_name == "None":
            return ("",)
        
        else:
            # 加载ControlNet模型
            controlnet_path = folder_paths.get_full_path_or_raise("controlnet", control_net_name)
            controlnet_load = comfy.controlnet.load_controlnet(controlnet_path)
            
            # 获取union类型编号
            type_number = UNION_CONTROLNET_TYPES.get(union_type, -2)
                        
            if type_number >= -1:
                controlnet_load = controlnet_load.copy()
            
                if type_number >= 0:
                    # 设置控制类型
                    controlnet_load.set_extra_arg("control_type", [type_number])
                else:
                    controlnet_load.set_extra_arg("control_type", [])

            return (controlnet_load,)

class CR_ControlNetParamStack_JK:
    """Stack multiple ControlNet parameters for advanced multi-ControlNet setups"""
    
    @classmethod
    def INPUT_TYPES(cls):
        
        inputs = {
            "optional": {
                "controlnet_0": ("CONTROL_NET", {"tooltip": "First ControlNet input"}),
                "image_0": ("IMAGE", {"tooltip": "First control image input"}),
                "controlnet_1": ("CONTROL_NET", {"tooltip": "Second ControlNet input"}),
                "image_1": ("IMAGE", {"tooltip": "Second control image input"}),
                "controlnet_2": ("CONTROL_NET", {"tooltip": "Third ControlNet input"}),
                "image_2": ("IMAGE", {"tooltip": "Third control image input"}),
                "controlnet_3": ("CONTROL_NET", {"tooltip": "Fourth ControlNet input"}),
                "image_3": ("IMAGE", {"tooltip": "Fourth control image input"}),
                "controlnet_4": ("CONTROL_NET", {"tooltip": "Fifth ControlNet input"}),
                "image_4": ("IMAGE", {"tooltip": "Fifth control image input"}),
                "controlnet_5": ("CONTROL_NET", {"tooltip": "Sixth ControlNet input"}),
                "image_5": ("IMAGE", {"tooltip": "Sixth control image input"}),
            },
            "required": {
                "control_switch": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable/disable ControlNet stacking"
                }),
            },
        }
        
        # 动态添加6个ControlNet单元的参数
        for i in range(0, 6):
            inputs["required"][f"ControlNet_Unit_{i}"] = ("BOOLEAN", {
                "default": False,
                "tooltip": f"Enable/disable ControlNet unit {i}"
            })
            inputs["required"][f"controlnet_strength_{i}"] = ("FLOAT", {
                "default": 1.0, 
                "min": -10.0, 
                "max": 10.0, 
                "step": 0.01,
                "tooltip": f"Control strength for unit {i}"
            })
            inputs["required"][f"start_percent_{i}"] = ("FLOAT", {
                "default": 0.0, 
                "min": 0.0, 
                "max": 1.0, 
                "step": 0.001,
                "tooltip": f"Start percentage for unit {i}"
            })
            inputs["required"][f"end_percent_{i}"] = ("FLOAT", {
                "default": 1.0, 
                "min": 0.0, 
                "max": 1.0, 
                "step": 0.001,
                "tooltip": f"End percentage for unit {i}"
            })

        return inputs

    RETURN_TYPES = ("CONTROL_NET_STACK", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("CONTROLNET_STACK", "ContrlNet_Switch", "ContrlNet0_Switch", "ContrlNet1_Switch", "ContrlNet2_Switch", "ContrlNet3_Switch", "ContrlNet4_Switch", "ContrlNet5_Switch")
    FUNCTION = "controlnet_stacker"
    CATEGORY = icons.get("JK/ControlNet")
    DESCRIPTION = "Stack multiple ControlNet parameters for complex control scenarios."
    
    def controlnet_stacker(self, control_switch, **kwargs):
        """堆叠多个ControlNet参数，支持复杂的多ControlNet配置"""

        # 初始化列表
        controlnet_list = []
        
        if control_switch == True:
            for i in range(0, 6):
                # 检查ControlNet单元是否启用且有有效输入
                if (kwargs.get(f"controlnet_{i}") is not None and 
                    kwargs.get(f"controlnet_{i}") != "" and 
                    kwargs.get(f"ControlNet_Unit_{i}") == True and 
                    kwargs.get(f"image_{i}") is not None):
                    
                    # 添加到堆栈
                    controlnet_list.extend([
                        (kwargs.get(f"controlnet_{i}"), 
                         kwargs.get(f"image_{i}"), 
                         kwargs.get(f"controlnet_strength_{i}"), 
                         kwargs.get(f"start_percent_{i}"), 
                         kwargs.get(f"end_percent_{i}"))
                    ])
        
        # 返回ControlNet堆栈和各单元开关状态
        return (controlnet_list, control_switch, 
                control_switch and kwargs.get(f"ControlNet_Unit_0"), 
                control_switch and kwargs.get(f"ControlNet_Unit_1"), 
                control_switch and kwargs.get(f"ControlNet_Unit_2"), 
                control_switch and kwargs.get(f"ControlNet_Unit_3"), 
                control_switch and kwargs.get(f"ControlNet_Unit_4"), 
                control_switch and kwargs.get(f"ControlNet_Unit_5"))

class CR_ApplyControlNet_JK:
    """Apply single ControlNet to conditioning with mask support"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_positive": ("CONDITIONING", {"tooltip": "Positive conditioning input"}),
                "base_negative": ("CONDITIONING", {"tooltip": "Negative conditioning input"}),
                "effective_mask": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Apply mask to ControlNet effect"
                }),
                "strength": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.01,
                    "tooltip": "ControlNet strength multiplier"
                }),
                "start_percent": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.001,
                    "tooltip": "Start percentage of denoising process"
                }),
                "end_percent": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.001,
                    "tooltip": "End percentage of denoising process"
                }),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Control image input"}),
                "mask": ("MASK", {"tooltip": "Mask for selective application"}),
                "vae": ("VAE", {"tooltip": "VAE for image encoding"}),
                "control_net": ("CONTROL_NET", {"tooltip": "ControlNet model to apply"}),
             }
        }
    
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING",)
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet"
    CATEGORY = icons.get("JK/ControlNet")
    DESCRIPTION = "Apply single ControlNet to conditioning with mask support."

    def apply_controlnet(self, base_positive, base_negative, effective_mask, strength, start_percent, end_percent, 
                        image=None, vae=None, mask=None, control_net=None):
        """应用单个ControlNet到条件输入，支持遮罩控制"""
        
        if image is not None and control_net is not None and control_net != "" and strength != 0.0:
            
            from comfy_extras.nodes_compositing import SplitImageWithAlpha
            
            # 加载ControlNet模型
            if type(control_net) == str:
                controlnet_path = folder_paths.get_full_path("controlnet", control_net)
                controlnet = comfy.sd.load_controlnet(controlnet_path)
            else:
                controlnet = control_net
            
            # 分离图像和alpha通道
            image, mask_from_image = SplitImageWithAlpha().execute(image)
            
            # 确定使用的遮罩
            if mask is None or torch.all(mask_from_image == 0).int().item() == 0:
                mask_cal = mask_from_image
            else:
                mask_cal = mask
            
            extra_concat = []
            if control_net.concat_mask:
                # 处理遮罩连接
                mask_cal = 1.0 - mask_cal.reshape((-1, 1, mask_cal.shape[-2], mask_cal.shape[-1]))
                mask_apply = comfy.utils.common_upscale(mask_cal, image.shape[2], image.shape[1], "bilinear", "center").round()
                image = image * mask_apply.movedim(1, -1).repeat(1, 1, 1, image.shape[3])
                extra_concat = [mask_cal]
                
            # 应用ControlNet
            controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(
                base_positive, base_negative, controlnet, image, strength, start_percent, end_percent, 
                vae=vae, extra_concat=extra_concat
            )
            
            # 处理有效遮罩
            if effective_mask and torch.all(mask_cal == 0).int().item() == 0:
                from node_helpers import conditioning_set_values
                base_positive = conditioning_set_values(controlnet_conditioning[0], {
                    "mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                }) + conditioning_set_values(base_positive, {
                    "mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                })
                base_negative = conditioning_set_values(controlnet_conditioning[1], {
                    "mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                }) + conditioning_set_values(base_negative, {
                    "mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                })
            else:
                base_positive, base_negative = controlnet_conditioning[0], controlnet_conditioning[1]
        
        return (base_positive, base_negative, )

class CR_ApplyControlNetStackAdv_JK:
    """Apply stacked ControlNets to conditioning with advanced masking"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_positive": ("CONDITIONING", {"tooltip": "Positive conditioning input"}),
                "base_negative": ("CONDITIONING", {"tooltip": "Negative conditioning input"}),
                "effective_mask": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Apply mask to ControlNet effects"
                }),
            },
             "optional": {
                "mask": ("MASK", {"tooltip": "Mask for selective application"}),
                "vae": ("VAE", {"tooltip": "VAE for image encoding"}),
                "controlnet_stack": ("CONTROL_NET_STACK", {"tooltip": "Stack of ControlNet parameters"}),
             }
        }                    
    
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("base_pos", "base_neg", )
    FUNCTION = "apply_controlnet_stack"
    CATEGORY = icons.get("JK/ControlNet")
    DESCRIPTION = "Apply multiple ControlNets from stack to conditioning."

    def apply_controlnet_stack(self, base_positive, base_negative, effective_mask, vae=None, mask=None, controlnet_stack=None):
        """应用堆叠的多个ControlNet到条件输入"""
        
        from comfy_extras.nodes_compositing import SplitImageWithAlpha
        
        if controlnet_stack is not None and len(controlnet_stack) != 0:
            for controlnet_tuple in controlnet_stack:
                controlnet_name, image, strength, start_percent, end_percent = controlnet_tuple
                
                # 加载ControlNet模型
                if type(controlnet_name) == str:
                    controlnet_path = folder_paths.get_full_path("controlnet", controlnet_name)
                    controlnet = comfy.sd.load_controlnet(controlnet_path)
                else:
                    controlnet = controlnet_name
                
                # 分离图像和alpha通道
                image, mask_from_image = SplitImageWithAlpha().execute(image)
                
                # 确定使用的遮罩
                if mask is None or torch.all(mask_from_image == 0).int().item() == 0:
                    mask_cal = mask_from_image
                else:
                    mask_cal = mask
                
                extra_concat = []
                if controlnet.concat_mask:
                    # 处理遮罩连接
                    mask_cal = 1.0 - mask_cal.reshape((-1, 1, mask_cal.shape[-2], mask_cal.shape[-1]))
                    mask_apply = comfy.utils.common_upscale(mask_cal, image.shape[2], image.shape[1], "bilinear", "center").round()
                    image = image * mask_apply.movedim(1, -1).repeat(1, 1, 1, image.shape[3])
                    extra_concat = [mask_cal]
                
                # 应用ControlNet
                controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(
                    base_positive, base_negative, controlnet, image, strength, start_percent, end_percent, 
                    vae=vae, extra_concat=extra_concat
                )
                
                # 处理有效遮罩
                if effective_mask and torch.all(mask_cal == 0).int().item() == 0:
                    from node_helpers import conditioning_set_values
                    base_positive = conditioning_set_values(controlnet_conditioning[0], {
                        "mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                    }) + conditioning_set_values(base_positive, {
                        "mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                    })
                    base_negative = conditioning_set_values(controlnet_conditioning[1], {
                        "mask": mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                    }) + conditioning_set_values(base_negative, {
                        "mask": 1.0 - mask_cal, "set_area_to_bounds": False, "mask_strength": 1.0
                    })
                else:
                    base_positive, base_negative = controlnet_conditioning[0], controlnet_conditioning[1]
                
        return (base_positive, base_negative, )
