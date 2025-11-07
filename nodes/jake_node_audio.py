#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Audio Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
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
                "segment_frame_count": ("INT", {
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
                    "tooltip": "Sometimes Wan Wapper needs several frames to warm up before normal output, especially for ref2v."
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
                    "label_off": "context"
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
            },
            "optional": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("INT", "SCENECUTS", "STRING", "STRING", "STRING", "STRING", "STRING", "FLOAT", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = ("scene_count", "scene_cuts", "select_cuts", "cut_frame_counts", "loop_frame_counts", "total_duration", "total_frame_count", "fps", "seg_frame_count", "overlap_frame_count", "long_vid_method")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Create scene cuts based on multiple cut point times or durations and an optional audio duration."
    OUTPUT_NODE = False
    
    def process(self, segments: str, mode: bool, fps: int, segment_frame_count: int, warmup_frame_count: int, long_vid_method: bool, overlap_frame_count: int, 
                min_loop_frame_count: bool, select_cuts: str, audio: Dict[str, Any] = None) -> Tuple[int, Dict, str, str, str, str, str, float, int, int, bool]:
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
        
        # Adjust segment frame count for WAN compatibility
        segment_frame_count = self._adjust_segment_frame_count(segment_frame_count)
        
        # Process selected cuts
        selected_scene_cuts, selected_indices = self._process_selected_cuts(
            scene_cuts, select_cuts, fps, segment_frame_count, overlap_frame_count, long_vid_method, warmup_frame_count
        )
        
        # Generate output strings
        output_strings = self._generate_output_strings(
            selected_scene_cuts, selected_indices, total_duration, fps
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
            segment_frame_count,
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
    
    def _adjust_segment_frame_count(self, segment_frame_count: int) -> int:
        """Adjust segment frame count for WAN compatibility."""
        return int(math.ceil(max(0, (segment_frame_count - 1)) / 4) * 4 + 1)
    
    def _process_selected_cuts(self, scene_cuts: List[List[float]], select_cuts: str, fps: int, 
                              segment_frame_count: int, overlap_frame_count: int, long_vid_method: bool, 
                              warmup_frame_count: int) -> Tuple[List[List[float]], List[int]]:
        """Process and filter selected cuts."""
        selected_indices = parse_select_cuts(select_cuts, len(scene_cuts))
        selected_scene_cuts = []
        
        for idx in selected_indices:
            if idx < len(scene_cuts):
                selected_scene_cuts.append(scene_cuts[idx])
        
        return selected_scene_cuts, selected_indices
    
    def _generate_output_strings(self, scene_cuts: List[List[float]], selected_indices: List[int], 
                                total_duration: float, fps: int) -> Dict[str, str]:
        """Generate output summary strings."""
        cut_frame_counts = []
        loop_frame_counts = []
        total_gen_frames = 0
        
        for start, end in scene_cuts:
            duration = end - start
            cut_frames = max(0, int(round(duration * fps)))
            loop_frames = calculate_loop_frame_count(duration, fps, 81, 10, False)  # Using defaults
            
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

#---------------------------------------------------------------------------------------------------------------------#
# Audio Cutting Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CutAudio_JK:
    """Cut audio file based on start and end time."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "start_time": ("FLOAT", {
                    "default": 0.0,
                    "min": -10000.0,
                    "max": 10000.0,
                    "step": 0.001,
                    "display": "number"
                }),
                "end_time": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.1,
                    "max": 10000.0,
                    "step": 0.001,
                    "display": "number"
                }),
                "add_start_mute": ("BOOLEAN", {
                    "default": False,
                    "label_on": "enabled",
                    "label_off": "disabled",
                    "tooltip": "Add mute when time < 0.0."
                }),
                "add_end_mute": ("BOOLEAN", {
                    "default": False,
                    "label_on": "enabled",
                    "label_off": "disabled",
                    "tooltip": "Add mute when time > audio duration."
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "duration")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Cut an audio file based on start and end time."
    OUTPUT_NODE = False

    def process(self, audio: Dict[str, Any], start_time: float, end_time: float, 
                add_start_mute: bool, add_end_mute: bool) -> Tuple[Dict[str, Any], float]:
        """Cut audio based on time range."""
        if start_time >= end_time:
            raise ValueError("The start time must be less than the end time.")
        
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        total_duration = waveform.shape[-1] / sample_rate
        
        # Calculate sample indices
        start_sample = int(max(0.0, min(start_time, total_duration)) * sample_rate)
        end_sample = int(max(start_time, min(end_time, total_duration)) * sample_rate)
        
        start_sample = min(start_sample, waveform.shape[-1])
        end_sample = min(end_sample, waveform.shape[-1])
        
        # Extract audio segment
        cut_waveform = waveform[..., start_sample:end_sample]
        
        # Add silence if needed
        if add_start_mute and start_time < 0:
            cut_waveform = self._add_start_silence(cut_waveform, start_time, sample_rate)
        
        if add_end_mute and end_time > total_duration:
            cut_waveform = self._add_end_silence(cut_waveform, end_time, total_duration, sample_rate)
        
        result_audio = {
            "waveform": cut_waveform,
            "sample_rate": sample_rate
        }
        
        return (result_audio, cut_waveform.shape[-1] / sample_rate)
    
    def _add_start_silence(self, waveform: torch.Tensor, start_time: float, sample_rate: int) -> torch.Tensor:
        """Add silence to the start of waveform."""
        silence_duration = abs(start_time)
        silence_samples = int(silence_duration * sample_rate)
        
        silence_shape = list(waveform.shape)
        silence_shape[-1] = silence_samples
        silence = torch.zeros(silence_shape, dtype=waveform.dtype, device=waveform.device)
        
        return torch.cat([silence, waveform], dim=-1)
    
    def _add_end_silence(self, waveform: torch.Tensor, end_time: float, total_duration: float, sample_rate: int) -> torch.Tensor:
        """Add silence to the end of waveform."""
        silence_duration = abs(end_time - total_duration)
        silence_samples = int(silence_duration * sample_rate)
        
        silence_shape = list(waveform.shape)
        silence_shape[-1] = silence_samples
        silence = torch.zeros(silence_shape, dtype=waveform.dtype, device=waveform.device)
        
        return torch.cat([waveform, silence], dim=-1)

class CutAudioIndex_JK:
    """Cut audio based on scene cuts metadata and index."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "scene_cuts": ("SCENECUTS",),
                "index": ("INT", {
                    "default": 0,
                    "min": -1,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Cut an audio file based on scene cuts metadata and cut index."
    OUTPUT_NODE = False

    def process(self, audio: Dict[str, Any], scene_cuts: Dict[str, Any], index: int) -> Tuple[Dict[str, Any]]:
        """Cut audio using scene cuts and index."""
        # Handle negative indexing
        if index < 0:
            index = scene_cuts["count"] + index
        
        if index < 0 or index >= scene_cuts["count"]:
            raise ValueError(f"Index {index} out of range (0-{scene_cuts['count']-1})")
        
        # Get time range from scene cuts
        start_time, end_time = scene_cuts["cuts"][index]
        
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        # Calculate sample indices
        start_sample = int(max(0, start_time) * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        start_sample = min(start_sample, waveform.shape[-1])
        end_sample = min(end_sample, waveform.shape[-1])
        
        # Extract audio segment
        cut_waveform = waveform[..., start_sample:end_sample]
        
        # Add silence if start time is negative
        if start_time < 0:
            cut_waveform = self._add_start_silence(cut_waveform, start_time, sample_rate)
        
        result_audio = {
            "waveform": cut_waveform,
            "sample_rate": sample_rate
        }
        
        return (result_audio,)
    
    def _add_start_silence(self, waveform: torch.Tensor, start_time: float, sample_rate: int) -> torch.Tensor:
        """Add silence to the start of waveform."""
        silence_duration = abs(start_time)
        silence_samples = int(silence_duration * sample_rate)
        
        silence_shape = list(waveform.shape)
        silence_shape[-1] = silence_samples
        silence = torch.zeros(silence_shape, dtype=waveform.dtype, device=waveform.device)
        
        return torch.cat([silence, waveform], dim=-1)

class CutAudioCuts_JK:
    """Merge all cuts from scene_cuts into a single audio file."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "scene_cuts": ("SCENECUTS",),
            },
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Merge all cuts from scene_cuts into a single audio file in chronological order."
    OUTPUT_NODE = False

    def process(self, audio: Dict[str, Any], scene_cuts: Dict[str, Any]) -> Tuple[Dict[str, Any]]:
        """Merge all audio cuts into single audio file."""
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        cuts = scene_cuts["cuts"]
        count = scene_cuts["count"]
        warmup = scene_cuts["warmup"]
        
        if count == 0:
            raise ValueError("No cuts available in scene_cuts")
        
        # Sort cuts by start time
        sorted_cuts = sorted(cuts, key=lambda x: x[0])
        
        audio_segments = []
        
        for start_time, end_time in sorted_cuts:
            # Adjust start time to remove warmup
            start_time = max(0, start_time + warmup)
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            
            start_sample = min(start_sample, waveform.shape[-1])
            end_sample = min(end_sample, waveform.shape[-1])
            
            cut_waveform = waveform[..., start_sample:end_sample]
            audio_segments.append(cut_waveform)
        
        # Merge all segments
        if audio_segments:
            merged_waveform = torch.cat(audio_segments, dim=-1)
        else:
            # Create empty audio if no valid segments
            merged_waveform = torch.zeros_like(waveform[..., :0])
        
        result_audio = {
            "waveform": merged_waveform,
            "sample_rate": sample_rate
        }
        
        return (result_audio,)

class CutAudioLoop_JK:
    """Cut audio for loop-based video generation."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "fps": ("INT", {
                    "default": 16,
                    "min": 1,
                    "max": 120,
                    "step": 1,
                    "display": "number"
                }),
                "segment_frame_count": ("INT", {
                    "default": 81,
                    "min": 1,
                    "max": 1000,
                    "step": 1,
                    "display": "number"
                }),
                "overlap_frame_count": ("INT", {
                    "default": 10,
                    "min": 4,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Overlap frames for Context Window or for-loop long-vid generation."
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("audio", "duration", "start", "end")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Cut an audio file based on loop metadata and cut index."
    OUTPUT_NODE = False

    def process(self, audio: Dict[str, Any], fps: int, segment_frame_count: int, 
                overlap_frame_count: int, index: int) -> Tuple[Dict[str, Any], float, float, float]:
        """Cut audio for specific loop segment."""
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        total_duration = waveform.shape[-1] / sample_rate
        
        # Calculate time parameters
        loop_duration = segment_frame_count / fps
        overlap_duration = overlap_frame_count / fps
        
        # Calculate start time based on index
        if index == 0:
            start_time = 0
        else:
            start_time = max(0, ((loop_duration - overlap_duration) * index))
        
        if start_time >= total_duration:
            raise ValueError(f"Index {index} out of range (0 - {total_duration} second).")
        
        end_time = start_time + loop_duration
        
        # Extract audio segment
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        start_sample = min(start_sample, waveform.shape[-1])
        end_sample = min(end_sample, waveform.shape[-1])
        
        cut_waveform = waveform[..., start_sample:end_sample]
        
        # Add silence if end time exceeds audio duration
        if end_time > total_duration:
            cut_waveform = self._add_end_silence(cut_waveform, end_time, total_duration, sample_rate)
        
        result_audio = {
            "waveform": cut_waveform,
            "sample_rate": sample_rate
        }
        
        actual_duration = cut_waveform.shape[-1] / sample_rate
        
        return (result_audio, actual_duration, start_time, end_time)
    
    def _add_end_silence(self, waveform: torch.Tensor, end_time: float, total_duration: float, sample_rate: int) -> torch.Tensor:
        """Add silence to the end of waveform."""
        silence_duration = abs(end_time - total_duration)
        silence_samples = int(silence_duration * sample_rate)
        
        silence_shape = list(waveform.shape)
        silence_shape[-1] = silence_samples
        silence = torch.zeros(silence_shape, dtype=waveform.dtype, device=waveform.device)
        
        return torch.cat([waveform, silence], dim=-1)