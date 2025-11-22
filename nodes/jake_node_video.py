#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Video Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import math
from typing import Tuple, List
from ..categories import icons

class CreateLoopScheduleList:
    """Create loop schedule list for animation."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "loop_count": ("INT", {
                "default": 5, 
                "min": 2, 
                "max": 1000, 
                "step": 1, 
                "tooltip": "Number of loops to schedule for animation sequence"
            }),
            }
        }
    
    RETURN_TYPES = ("ITEM_LIST", )
    RETURN_NAMES = ("int_list",)
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Generate a sequential integer list for animation loop scheduling."
    
    def process(self, loop_count: int) -> Tuple[list]:
        """创建循环调度列表"""
        step_list = [1] * loop_count
        
        for i in range(0, loop_count):
            step_list[i] = i + 1
            
        return (step_list,)

class WanFrameCount_JK:
    """Calculate WAN frame count."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_count": ("INT",{
                    "default": 81,
                    "min": 1,
                    "max": 16385,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Input frame count to calculate WAN-compatible frame count"
                }),
            },
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("wan_frame_count",)
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Calculate WAN-compatible frame count by rounding up to nearest multiple of 4 plus 1."
    OUTPUT_NODE = False

    def process(self, frame_count: int) -> Tuple[int]:
        """计算WAN帧数"""
        wan_frame_count = int(math.ceil(max(0, (frame_count - 1)) / 4) * 4 + 1)
        return (wan_frame_count,)

class Wan22cfgSchedulerList_JK:
    """WAN 2.2 CFG scheduler list generator."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_cfg": ("FLOAT", {
                    "default": 3.5, 
                    "min": 0.0, 
                    "max": 30.0, 
                    "step": 0.01,
                    "tooltip": "Initial CFG value for first steps"
                }),
                "cfg": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 30.0, 
                    "step": 0.01,
                    "tooltip": "CFG value to switch to after initial steps"
                }),
                "steps": ("INT", {
                    "default": 20, 
                    "min": 2, 
                    "max": 1000, 
                    "step": 1,
                    "tooltip": "Total number of steps in the schedule"
                }),
                "first_switch_at_step": ("INT", {
                    "default": 2, 
                    "min": 1, 
                    "max": 1000, 
                    "step": 1,
                    "tooltip": "Step number to switch from first_cfg to cfg"
                }),
            },
        }
    
    RETURN_TYPES = ("FLOAT", )
    RETURN_NAMES = ("cfg_list",)
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Generate CFG scheduler list with initial and subsequent values for WAN 2.2."
    OUTPUT_NODE = False
    
    def get_value(self, first_cfg: float, cfg: float, steps: int, first_switch_at_step: int) -> Tuple[float]:
        """生成CFG调度列表"""
        actual_switch_step = min(first_switch_at_step, steps)
        cfg_list = [first_cfg] * actual_switch_step + [cfg] * (steps - actual_switch_step)
        return (cfg_list,)

# WanWrapper scheduler list
WANWRAPPER_SCHEDULER_LIST = [
    "unipc", "unipc/beta",
    "dpm++", "dpm++/beta",
    "dpm++_sde", "dpm++_sde/beta",
    "euler", "euler/beta",
    "longcat_distill_euler", "deis",
    "lcm", "lcm/beta",
    "res_multistep",
    "flowmatch_causvid",
    "flowmatch_distill",
    "flowmatch_pusa",
    "multitalk",
    "sa_ode_stable", "rcm"
]

class WanWrapperSamplerDefault_JK:
    """WAN wrapper sampler defaults."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scheduler": (WANWRAPPER_SCHEDULER_LIST, {
                    "default": "unipc",
                    "tooltip": "Select scheduler type for WAN wrapper"
                }),
            },
        }
    
    RETURN_TYPES = (WANWRAPPER_SCHEDULER_LIST, "STRING")
    RETURN_NAMES = ("scheduler", "rope_function")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Provide default sampler settings for WAN wrapper including scheduler and rope function."
    OUTPUT_NODE = False
    
    def get_value(self, scheduler: str) -> Tuple[str, str]:
        """获取WAN包装器采样器默认值"""
        return (scheduler, "comfy")