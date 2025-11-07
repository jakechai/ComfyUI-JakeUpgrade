#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Lora Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import folder_paths
import comfy.sd
import comfy.utils
from pathlib import Path
from .jake_tools import calculate_sha256
from ..categories import icons

class CR_LoRAStack_JK:
    """Stack multiple LoRA models with prompt and metadata generation"""
    
    @classmethod
    def INPUT_TYPES(cls):
    
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        inputs = {
            "required": {
                "input_mode": (['model_only', 'advanced'], {
                    "default": 'model_only',
                    "tooltip": "LoRA application mode: model_only or advanced"
                }),
            },
            "optional": {
                "lora_stack": ("LORA_STACK", {"tooltip": "Existing LoRA stack to extend"}),
                "lora_prompt": ("STRING", {
                    "default": '',
                    "tooltip": "Existing LoRA prompt to extend"
                }),
                "lora_metadata": ("STRING", {
                    "default": '',
                    "tooltip": "Existing LoRA metadata to extend"
                }),
            },
        }
        
        # 动态添加6个LoRA插槽
        for i in range(1, 7):
            inputs["required"][f"lora_{i}"] = ("BOOLEAN", {
                "default": False,
                "tooltip": f"Enable/disable LoRA {i}"
            })
            inputs["required"][f"lora_name_{i}"] = (loras, {
                "tooltip": f"Select LoRA model {i}"
            })
            inputs["required"][f"model_weight_{i}"] = ("FLOAT", {
                "default": 1.0, 
                "min": -10.0, 
                "max": 10.0, 
                "step": 0.01,
                "tooltip": f"Model weight for LoRA {i}"
            })
            inputs["required"][f"clip_weight_{i}"] = ("FLOAT", {
                "default": 1.0, 
                "min": -10.0, 
                "max": 10.0, 
                "step": 0.01,
                "tooltip": f"CLIP weight for LoRA {i}"
            })
        
        inputs["required"][f"save_hash"] = ("BOOLEAN", {
            "default": False,
            "tooltip": "Include hash in LoRA metadata"
        })
        
        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING",)
    RETURN_NAMES = ("LORA_STACK", "LORA_PROMPT", "LORA_MetaData",)
    FUNCTION = "lora_stacker"
    CATEGORY = icons.get("JK/LoRA")
    DESCRIPTION = "Stack multiple LoRA models with prompt and metadata generation."

    def lora_stacker(self, input_mode, save_hash, lora_stack=None, lora_prompt=None, lora_metadata=None, **kwargs):
        """堆叠多个LoRA模型，生成提示词和元数据"""
        
        # 初始化列表
        lora_list = list()
        lora_enable_check = False
        lorapromptout = ""
        lorametaout = ""
        
        # 添加现有的LoRA堆栈
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])
        
        j = 0
        
        for i in range(1, 7):
            
            # 根据模式检查LoRA是否启用
            if input_mode == "model_only":
                if (kwargs.get(f"lora_{i}") == True and 
                    kwargs.get(f"lora_name_{i}") != "None" and 
                    kwargs.get(f"model_weight_{i}") != 0):
                    lora_enable_check = True
                else:
                    lora_enable_check = False
            elif input_mode == "advanced": 
                if (kwargs.get(f"lora_{i}") == True and 
                    kwargs.get(f"lora_name_{i}") != "None" and 
                    kwargs.get(f"model_weight_{i}") != 0 and 
                    kwargs.get(f"clip_weight_{i}") != 0):
                    lora_enable_check = True
                else:
                    lora_enable_check = False
            
            if lora_enable_check:
                
                # 添加到LoRA堆栈
                if input_mode == "model_only":
                    lora_list.extend([(kwargs.get(f"lora_name_{i}"), kwargs.get(f"model_weight_{i}"), 0.0)])
                elif input_mode == "advanced":
                    lora_list.extend([(kwargs.get(f"lora_name_{i}"), kwargs.get(f"model_weight_{i}"), kwargs.get(f"clip_weight_{i}"))])
                
                # 生成LoRA提示词
                lora_name = Path(kwargs.get(f"lora_name_{i}")).stem
                loraprompt = f"lora:{lora_name}"
                loraweight = f"{kwargs.get(f'model_weight_{i}'):.3f}"
                loraprompt = f"<{loraprompt}:{loraweight}>"
                
                # 构建提示词输出
                if (lora_prompt is None or lora_prompt == "") and j == 0:
                    lorapromptout = f"{loraprompt}"
                elif lora_prompt is not None and lora_prompt != "" and j == 0:
                    lorapromptout = f"{lora_prompt},{loraprompt}"
                else:
                    lorapromptout = f"{lorapromptout},{loraprompt}"
                
                # 生成元数据（可选包含哈希值）
                lora_path = folder_paths.get_full_path("loras", kwargs.get(f"lora_name_{i}"))
                lora_hash = f": [{calculate_sha256(lora_path)[:12]}]" if save_hash == True else ""
                lora_meta = f"{lora_name}{lora_hash}"
                
                # 构建元数据输出
                if (lora_metadata is None or lora_metadata == "") and j == 0:
                    lorametaout = f"{lora_meta}"
                elif lora_metadata is not None and lora_metadata != "" and j == 0:
                    lorametaout = f"{lora_metadata}, {lora_meta}"
                else:
                    lorametaout = f"{lorametaout}, {lora_meta}"
                
                j += 1
                
        return (lora_list, lorapromptout, lorametaout,)

class CR_ApplyLoRAStack_JK:
    """Apply stacked LoRA models to both model and CLIP"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "Model to apply LoRAs to"}),
                "clip": ("CLIP", {"tooltip": "CLIP model to apply LoRAs to"}),
                "lora_stack": ("LORA_STACK", {"tooltip": "Stack of LoRA parameters to apply"}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP",)
    RETURN_NAMES = ("MODEL", "CLIP",)
    FUNCTION = "apply_lora_stack"
    CATEGORY = icons.get("JK/LoRA")
    DESCRIPTION = "Apply multiple LoRA models from stack to both model and CLIP."

    def apply_lora_stack(self, model, clip, lora_stack=None):
        """应用堆叠的LoRA模型到模型和CLIP"""
        
        lora_params = list()
 
        if lora_stack:
            lora_params.extend(lora_stack)
        else:
            return (model, clip,)

        model_lora = model
        clip_lora = clip

        # 依次应用每个LoRA
        for tup in lora_params:
            lora_name, strength_model, strength_clip = tup
            
            lora_path = folder_paths.get_full_path("loras", lora_name)
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            
            model_lora, clip_lora = comfy.sd.load_lora_for_models(
                model_lora, clip_lora, lora, strength_model, strength_clip
            )

        return (model_lora, clip_lora,)

class CR_LoRAStack_ModelOnly_JK:
    """Stack LoRA models for model-only application (no CLIP)"""
    
    @classmethod
    def INPUT_TYPES(cls):
    
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        inputs = {
            "required": {},
            "optional": {
                "lora_stack": ("LORA_STACK", {"tooltip": "Existing LoRA stack to extend"}),
            },
        }
        
        # 动态添加6个LoRA插槽（仅模型权重）
        for i in range(1, 7):
            inputs["required"][f"lora_{i}"] = ("BOOLEAN", {
                "default": False,
                "tooltip": f"Enable/disable LoRA {i}"
            })
            inputs["required"][f"lora_name_{i}"] = (loras, {
                "tooltip": f"Select LoRA model {i}"
            })
            inputs["required"][f"model_weight_{i}"] = ("FLOAT", {
                "default": 1.0, 
                "min": -10.0, 
                "max": 10.0, 
                "step": 0.01,
                "tooltip": f"Model weight for LoRA {i}"
            })
        
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "lora_stacker"
    CATEGORY = icons.get("JK/LoRA")
    DESCRIPTION = "Stack LoRA models for model-only application."

    def lora_stacker(self, lora_stack=None, **kwargs):
        """堆叠LoRA模型，仅用于模型应用（不包含CLIP）"""
        
        # 初始化列表
        lora_list = list()
        lora_enable_check = False
        
        # 添加现有的LoRA堆栈
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])
        
        for i in range(1, 7):
            
            # 检查LoRA是否启用
            if (kwargs.get(f"lora_{i}") == True and 
                kwargs.get(f"lora_name_{i}") != "None" and 
                kwargs.get(f"model_weight_{i}") != 0):
                lora_enable_check = True
            else:
                lora_enable_check = False
            
            if lora_enable_check:
                # 添加到LoRA堆栈（CLIP权重设为0）
                lora_list.extend([(kwargs.get(f"lora_name_{i}"), kwargs.get(f"model_weight_{i}"), 0.0)])
                
        return (lora_list,)

class CR_ApplyLoRAStack_ModelOnly_JK:
    """Apply stacked LoRA models to model only (CLIP unchanged)"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "Model to apply LoRAs to"}),
                "lora_stack": ("LORA_STACK", {"tooltip": "Stack of LoRA parameters to apply"}),
            }
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("MODEL",)
    FUNCTION = "apply_lora_stack"
    CATEGORY = icons.get("JK/LoRA")
    DESCRIPTION = "Apply multiple LoRA models from stack to model only."

    def apply_lora_stack(self, model, lora_stack=None):
        """应用堆叠的LoRA模型到模型（CLIP保持不变）"""
        
        lora_params = list()
 
        if lora_stack:
            lora_params.extend(lora_stack)
        else:
            return (model,)

        model_lora = model
        
        # 依次应用每个LoRA（仅影响模型）
        for tup in lora_params:
            lora_name, strength_model, strength_clip = tup
            lora_path = folder_paths.get_full_path("loras", lora_name)
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            model_lora = comfy.sd.load_lora_for_models(model_lora, None, lora, strength_model, 0)[0]
        
        return (model_lora,)