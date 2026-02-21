#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Video Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import math
from typing import Any, Tuple, List, Dict
from .jake_utils import parse_select_cuts, calculate_loop_frame_count
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Scene Cutting Nodes
#---------------------------------------------------------------------------------------------------------------------#

class SceneCuts_JK:
    """Create scene cuts based on timing or duration with audio support."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fps": ("INT", {
                    "default": 16,
                    "min": 1,
                    "max": 120,
                    "step": 1,
                    "display": "number"
                }),
                "loop_frame_count": ("INT", {
                    "default": 81,
                    "min": 1,
                    "max": 1000,
                    "step": 1,
                    "display": "number"
                }),
                "warmup_frame_count": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Only for WAN. Sometimes Wan Wapper needs several frames to warm up before normal output, especially for ref2v."
                }),
                "overlap_frame_count": ("INT", {
                    "default": 10,
                    "min": 4,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Overlap frames for Context Window or for-loop long-vid generation."
                }),
                "min_loop_frame_count": ("BOOLEAN", {
                    "default": False,
                    "label_on": "segment",
                    "label_off": "duration",
                    "tooltip": "Deactivated."
                }),
                "long_vid_method": ("BOOLEAN", {
                    "default": False,
                    "label_on": "for-loop",
                    "label_off": "context",
                    "tooltip": "Only for WAN."
                }),
                "mode": ("BOOLEAN", {
                    "default": True,
                    "label_on": "duration",
                    "label_off": "cut point"
                }),
                "select_cuts": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Select specific cuts to output (e.g., '0' for first cut, '0-2' for cuts 0 to 2, '0,2,4' for specific cuts)"
                }),
                "segments": ("STRING", {
                    "default": "3.0, 6.2\n9.875",
                    "multiline": True,
                    "tooltip": "Enter the duration or cut points in 'second.millisecond' format, separated by commas or '\n'(e.g., 3.0, 6.2, 9.875)"
                }),
                "compatibility": ("BOOLEAN", {
                    "default": False,
                    "label_on": "LTXV2",
                    "label_off": "WAN"
                }),
            },
            "optional": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("INT", "SCENECUTS", "STRING", "STRING", "STRING", "STRING", "STRING", "FLOAT", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = ("scene_count", "scene_cuts", "select_cuts", "cut_frame_counts", "loop_frame_counts", "total_duration", "total_frame_count", "fps", "seg_frame_count", "overlap_frame_count", "long_vid_method")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Create scene cuts based on multiple cut point times or durations and an optional audio duration."
    OUTPUT_NODE = False
    
    def process(self, segments: str, mode: bool, fps: int, loop_frame_count: int, warmup_frame_count: int, long_vid_method: bool, overlap_frame_count: int, 
                min_loop_frame_count: bool, select_cuts: str, compatibility: bool, audio: Dict[str, Any] = None) -> Tuple[int, Dict, str, str, str, str, str, float, int, int, bool]:
        """Process scene cuts from timing data and optional audio."""
        # Parse segment values
        float_values = self._parse_segment_values(segments)
        if not float_values:
            raise ValueError("At least one cut point or duration must be provided.")
        
        # Get audio duration if available
        audio_duration = self._get_audio_duration(audio)
        
        # Create scene cuts based on mode
        if mode:
            scene_cuts = self._create_duration_cuts(float_values, audio_duration, warmup_frame_count, fps)
            total_duration = audio_duration if audio_duration is not None else scene_cuts[-1][1] if scene_cuts else 0
        else:
            scene_cuts, total_duration = self._create_cut_point_cuts(float_values, audio_duration, warmup_frame_count, fps)
        
        # Adjust segment frame count for WAN|LTXV2 compatibility
        loop_frame_count = self._adjust_segment_frame_count(loop_frame_count, compatibility)
        overlap_frame_count = self._adjust_segment_frame_count(overlap_frame_count, compatibility) if compatibility else overlap_frame_count
        
        # Process selected cuts
        selected_scene_cuts, selected_indices = self._process_selected_cuts(
            scene_cuts, select_cuts, fps, loop_frame_count, overlap_frame_count, long_vid_method, warmup_frame_count
        )
        
        # Generate output strings
        output_strings = self._generate_output_strings(
            selected_scene_cuts, selected_indices, total_duration, fps, compatibility
        )
        
        return (
            len(selected_scene_cuts),
            {"cuts": selected_scene_cuts, "count": len(selected_scene_cuts), "warmup": (warmup_frame_count / fps)},
            output_strings["select_cuts"],
            output_strings["cut_frame_counts"], 
            output_strings["loop_frame_counts"],
            output_strings["total_duration"],
            output_strings["total_frame_count"],
            float(fps),
            loop_frame_count,
            overlap_frame_count,
            long_vid_method
        )
    
    def _parse_segment_values(self, segments: str) -> List[float]:
        """Parse segment string into float values."""
        from .jake_utils import parse_string_list
        
        values = parse_string_list(segments)
        float_values = []
        
        for value in values:
            try:
                float_values.append(float(value))
            except ValueError:
                continue
        
        return float_values
    
    def _get_audio_duration(self, audio: Dict[str, Any]) -> float:
        """Get duration from audio data."""
        if audio is not None:
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            return waveform.shape[-1] / sample_rate
        return None
    
    def _create_duration_cuts(self, durations: List[float], audio_duration: float, warmup_frames: int, fps: float) -> List[List[float]]:
        """Create scene cuts from duration values."""
        scene_cuts = []
        current_time = 0.0
        
        for i, duration in enumerate(durations):
            end_time = current_time + duration
            
            if audio_duration is not None:
                if current_time >= audio_duration:
                    break
                
                if end_time > audio_duration:
                    end_time = audio_duration
            
            start_time = current_time - warmup_frames / fps
            scene_cuts.append([start_time, end_time])
            current_time = end_time
        
            if audio_duration is not None and current_time >= audio_duration:
                break
        
        return scene_cuts
    
    def _create_cut_point_cuts(self, cut_points: List[float], audio_duration: float, warmup_frames: int, fps: float) -> Tuple[List[List[float]], float]:
        """Create scene cuts from cut point values."""
        if audio_duration is None:
            total_duration = max(cut_points) if cut_points else 0
        else:
            total_duration = audio_duration
        
        valid_cut_points = [point for point in cut_points if 0 < point < total_duration]
        all_points = [0.0] + sorted(valid_cut_points) + [total_duration]
        
        scene_cuts = []
        for i in range(len(all_points) - 1):
            start_time = all_points[i] - warmup_frames / fps
            scene_cuts.append([start_time, all_points[i + 1]])
        
        return scene_cuts, total_duration
    
    def _adjust_segment_frame_count(self, loop_frame_count: int, compatibility: bool) -> int:
        """Adjust segment frame count for WAN|LTXV2 compatibility."""
        frame_seg = 8 if compatibility else 4
        return int(math.ceil(max(0, (loop_frame_count - 1)) / frame_seg) * frame_seg + 1)
    
    def _process_selected_cuts(self, scene_cuts: List[List[float]], select_cuts: str, fps: int, 
                              loop_frame_count: int, overlap_frame_count: int, long_vid_method: bool, 
                              warmup_frame_count: int) -> Tuple[List[List[float]], List[int]]:
        """Process and filter selected cuts."""
        selected_indices = parse_select_cuts(select_cuts, len(scene_cuts))
        selected_scene_cuts = []
        
        for idx in selected_indices:
            if idx < len(scene_cuts):
                selected_scene_cuts.append(scene_cuts[idx])
        
        return selected_scene_cuts, selected_indices
    
    def _generate_output_strings(self, scene_cuts: List[List[float]], selected_indices: List[int], 
                                total_duration: float, fps: int, compatibility: bool) -> Dict[str, str]:
        """Generate output summary strings."""
        cut_frame_counts = []
        loop_frame_counts = []
        total_gen_frames = 0
        
        for start, end in scene_cuts:
            duration = end - start
            cut_frames = max(0, int(round(duration * fps)))
            loop_frames = calculate_loop_frame_count(duration, fps, 81, 10, False, compatibility)  # Using defaults
            
            cut_frame_counts.append(str(cut_frames))
            loop_frame_counts.append(str(loop_frames))
            total_gen_frames += loop_frames
        
        return {
            "select_cuts": ", ".join(str(i) for i in selected_indices),
            "cut_frame_counts": ", ".join(cut_frame_counts),
            "loop_frame_counts": ", ".join(loop_frame_counts),
            "total_duration": f"{round(total_duration, 3)} (scene) | {round(total_gen_frames / fps, 3)} (gen)",
            "total_frame_count": f"{int(round(total_duration * fps))} (scene) | {total_gen_frames} (gen)"
        }

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

class LtxV2FrameCount_JK:
    """Calculate LTXV2 frame count."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_count": ("INT",{
                    "default": 241,
                    "min": 1,
                    "max": 16385,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Input frame count to calculate LTXV2-compatible frame count"
                }),
            },
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("ltxv2_frame_count",)
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Video")
    DESCRIPTION = "Calculate LTXV2-compatible frame count by rounding up to nearest multiple of 8 plus 1."
    OUTPUT_NODE = False

    def process(self, frame_count: int) -> Tuple[int]:
        """计算WAN帧数"""
        ltxv2_frame_count = int(math.ceil(max(0, (frame_count - 1)) / 8) * 8 + 1)
        return (ltxv2_frame_count,)

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