#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Audio Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
import math
from typing import Any, Tuple, Dict, Optional
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Audio Cutting Nodes
#---------------------------------------------------------------------------------------------------------------------#

class CutAudio_JK:
    """Cut audio file based on start and end time. If no audio is provided, a silent audio is generated."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
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
            "optional": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "duration")
    FUNCTION = "process"
    CATEGORY = icons.get("JK/Audio")
    DESCRIPTION = "Cut an audio file based on start and end time."
    OUTPUT_NODE = False

    def process(self, start_time: float, end_time: float, add_start_mute: bool, add_end_mute: bool, 
                audio: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], float]:
        """Cut audio based on time range. If audio is None, generate silent audio."""
        if start_time >= end_time:
            raise ValueError("The start time must be less than the end time.")
        
        # Case 1: Audio is provided → perform actual cutting
        if audio is not None:
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
    
        # Case 2: No audio provided → generate silent audio
        else:
            # Determine effective start based on add_start_mute
            if add_start_mute:
                effective_start = start_time
            else:
                effective_start = max(0.0, start_time)
            
            effective_end = end_time  # No upper bound when generating silence
            
            if effective_start >= effective_end:
                raise ValueError(f"Effective start ({effective_start}) must be less than end ({effective_end}).")
            
            # Use a default sample rate (44.1 kHz is common)
            sample_rate = 44100
            duration = effective_end - effective_start
            samples = int(duration * sample_rate)
            
            # Create silent waveform: shape (batch=1, channels=1, samples)
            waveform = torch.zeros((1, 1, samples), dtype=torch.float32)
            
            result_audio = {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            return (result_audio, duration)
    
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