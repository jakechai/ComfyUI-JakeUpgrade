#-----------------------------------------------------------------------------#
# Jake Upgrade SAM3D Mesh Sequence Generator Node for JK Custom Workflow of ComfyUI
#-----------------------------------------------------------------------------#
import os
import sys
import time
import struct
import json
import tempfile
import torch
import torch.nn.functional as F
from einops import rearrange
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import torch
import numpy as np
import cv2

# =============================================================================
# 配置常量
# =============================================================================

DEFAULT_FPS = 30.0  # 默认帧率
BINARY_MAGIC = b"MESH"  # 魔数标识
BINARY_VERSION = 2  # 版本号

# =============================================================================
# SAM3D 模型顶点和关节索引定义（仅备案未使用）
# =============================================================================

# 脚部顶点索引 
LEFT_FOOT_VERTICES = list(range(12223, 12234)) + list(range(12237, 13266))  # 12223-12233, 12237-13265
RIGHT_FOOT_VERTICES = list(range(17396, 17407)) + list(range(17410, 18439))  # 17396-17406, 17410-18438
FOOT_VERTICES = LEFT_FOOT_VERTICES + RIGHT_FOOT_VERTICES

# 手部顶点索引
LEFT_HAND_VERTICES = list(range(8883, 11234))  # 8883-11233
RIGHT_HAND_VERTICES = list(range(14053, 14059)) + list(range(14063, 16407))  # 14053-14059, 14063-16406

# 脚踝关节索引
LEFT_ANKLE_JOINT = 4   # joint_004
RIGHT_ANKLE_JOINT = 20  # joint_020
FOOT_JOINTS = [LEFT_ANKLE_JOINT, RIGHT_ANKLE_JOINT]

# MHR127关节索引
MHR127_JOINT_INDICES = {
    "root": 0,              # joint_000
    "pelvis": 1,            # joint_001
    "spine1": 34,           # joint_034
    "spine2": 35,           # joint_035
    "spine3": 36,           # joint_036
    "spine4": 37,           # joint_037
    "neck": 110,            # joint_110
    "head": 113,            # joint_113
    "left_hip": 2,          # joint_002
    "left_knee": 3,         # joint_003
    "left_ankle": 4,        # joint_004
    "left_heel": 6,         # joint_006
    "left_foot": 7,         # joint_007
    "left_toe": 8,          # joint_008
    "right_hip": 18,        # joint_018
    "right_knee": 19,       # joint_019
    "right_ankle": 20,      # joint_020
    "right_heel": 22,       # joint_022
    "right_foot": 23,       # joint_023
    "right_toe": 24,        # joint_024
    "left_collar": 74,      # joint_074
    "left_shoulder": 75,    # joint_075
    "left_elbow": 76,       # joint_076
    "left_wrist": 77,       # joint_077
    "left_hand": 78,        # joint_078
    "right_collar": 38,     # joint_038
    "right_shoulder": 39,   # joint_039
    "right_elbow": 40,      # joint_040
    "right_wrist": 41,      # joint_041
    "right_hand": 42,       # joint_042
}

# =============================================================================
# 检查 SAM3D 依赖是否可用
# =============================================================================

def check_sam3d_dependencies():
    """
    检查 SAM3D 依赖是否可用
    返回: (bool, str) - (是否可用, 错误信息)
    """
    # 尝试多种可能的SAM3D节点路径
    custom_nodes_dir = Path(__file__).absolute().parent.parent.parent
    sam3d_node_path = custom_nodes_dir / "ComfyUI-SAM3DBody"
    
    # 检查路径是否存在
    if not sam3d_node_path.exists():
        return False, "[SAM3D Check] SAM3D node path not found. Please ensure that the ComfyUI-SAM3DBody node is installed."
    
    print(f"[SAM3D Check] ComfyUI-SAM3DBody path: {sam3d_node_path}")
    
    # 检查虚拟环境路径
    sam3d_env_path = sam3d_node_path / "_env_sam3dbody"
    if not sam3d_env_path.exists():
        print(f"[SAM3D Check] Warning: The SAM3D virtual environment path does not exist: {sam3d_env_path}")
        # 虚拟环境不是必需的，可以继续
    
    # 尝试导入 sam_3d_body
    try:
        # 将 SAM3D 节点路径添加到 sys.path
        if str(sam3d_node_path) not in sys.path:
            sys.path.insert(0, str(sam3d_node_path))
        
        # 尝试导入
        from sam_3d_body import load_sam_3d_body, SAM3DBodyEstimator
        
        print(f"[SAM3D Check] SAM3D dependency check passed")
        return True, "[SAM3D Check] SAM3D dependency check passed"
    except ImportError as e:
        return False, f"[SAM3D Check] Unable to import SAM3D module: {str(e)}"
    except Exception as e:
        return False, f"[SAM3D Check] SAM3D dependency check failed: {str(e)}"

# =============================================================================
# 二进制格式定义
# =============================================================================

class MeshSequenceBinaryFormat:
    """
    Binary Mesh sequence format V2
    
    Header structure (28 bytes):
    - magic: b"MESH" (4 bytes)
    - version: uint32 (4 bytes)  # Format version
    - num_frames: uint32 (4 bytes)
    - num_verts: uint32 (4 bytes)
    - num_faces: uint32 (4 bytes)
    - fps: float32 (4 bytes)
    - flags: uint32 (4 bytes)     # Flags
    - metadata_size: uint32 (4 bytes)  # Metadata size (bytes)
    
    Data section:
    - Vertex sequence: num_frames * num_verts * 3 * float32
    - Face data: num_faces * 3 * uint32
    - Metadata: metadata_size bytes of UTF-8 JSON string
    """
    
    @staticmethod
    def save_smpl_compatible(vertices_sequence: np.ndarray, faces: np.ndarray,
                             output_path: Path, fps: float = DEFAULT_FPS,
                             coordinate_transform: str = "rotate_z_180") -> Dict:
        """
        保存为 SMPL 兼容格式（用于 CompareSMPLtoBVH 查看器）
        
        头部结构 (20字节):
        - magic: b"SMPL" (4字节)
        - num_frames: uint32 (4字节)
        - num_verts: uint32 (4字节)
        - num_faces: uint32 (4字节)
        - fps: float32 (4字节)
        
        数据部分:
        - 顶点序列: num_frames * num_verts * 3 * float32
        - 面数据: num_faces * 3 * uint32
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        num_frames = vertices_sequence.shape[0]
        num_verts = vertices_sequence.shape[1]
        num_faces = faces.shape[0]
        
        print(f"[MeshSequence] Saving SMPL compatible sequence: {num_frames}frames, {num_verts}vertices, {num_faces}faces, {fps}FPS")
        
        # 应用坐标变换
        if coordinate_transform != "none":
            vertices_sequence = apply_coordinate_transform(vertices_sequence, coordinate_transform)
        
        with open(output_path, 'wb') as f:
            # 写入头部 - SMPL格式
            magic = b"SMPL"
            f.write(magic)                                  # 4 bytes
            f.write(struct.pack('I', num_frames))           # 4 bytes
            f.write(struct.pack('I', num_verts))            # 4 bytes
            f.write(struct.pack('I', num_faces))            # 4 bytes
            f.write(struct.pack('f', fps))                  # 4 bytes
            
            # 写入顶点序列 (float32)
            # 确保顶点数据是C连续的
            vertices_flat = np.ascontiguousarray(vertices_sequence, dtype=np.float32).reshape(-1)
            f.write(vertices_flat.tobytes())
            
            # 写入面数据 (uint32)
            # 确保面数据是C连续的
            faces_flat = np.ascontiguousarray(faces, dtype=np.uint32).reshape(-1)
            f.write(faces_flat.tobytes())
        
        file_size = output_path.stat().st_size
        print(f"[MeshSequence] SMPL compatible file saved: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return {
            'path': str(output_path),
            'num_frames': num_frames,
            'num_verts': num_verts,
            'num_faces': num_faces,
            'fps': fps,
            'coordinate_transform': coordinate_transform,
            'file_size_mb': file_size / 1024 / 1024
        }

# 模块级缓存，复用 SAM3DBodyProcess 中的模型
_MODEL_CACHE_PROCESS = {}

def _load_sam3d_model_process(model_config: dict):
    """
    加载 SAM 3D Body 模型
    """
    cache_key = model_config["ckpt_path"]

    if cache_key in _MODEL_CACHE_PROCESS:
        return _MODEL_CACHE_PROCESS[cache_key]

    # 检查依赖是否可用
    available, error_msg = check_sam3d_dependencies()
    if not available:
        raise ImportError(f"[SAM3D Check] SAM3D dependency unavailable: {error_msg}")

    # 导入依赖
    from sam_3d_body import load_sam_3d_body

    ckpt_path = model_config["ckpt_path"]
    device = model_config["device"]
    mhr_path = model_config.get("mhr_path", "")

    print(f"[MeshSequence] Loading model: {ckpt_path}")
    sam_3d_model, model_cfg, _ = load_sam_3d_body(
        checkpoint_path=ckpt_path,
        device=device,
        mhr_path=mhr_path,
    )

    print(f"[MeshSequence] Model loaded, device: {device}")

    # 缓存结果
    result = {
        "model": sam_3d_model,
        "model_cfg": model_cfg,
        "device": device,
        "mhr_path": mhr_path,
    }
    _MODEL_CACHE_PROCESS[cache_key] = result

    return result

def apply_coordinate_transform(vertices_sequence: np.ndarray, transform_type: str = "rotate_z_180") -> np.ndarray:

    if transform_type == "none" or vertices_sequence is None:
        return vertices_sequence
    
    num_frames, num_verts, _ = vertices_sequence.shape
    transformed_sequence = vertices_sequence.copy()
    
    if transform_type == "rotate_z_180":
        # 绕Z轴旋转180度: (x, y, z) -> (-x, -y, z)
        transformed_sequence[:, :, 0] = -vertices_sequence[:, :, 0]  # X取反
        transformed_sequence[:, :, 1] = -vertices_sequence[:, :, 1]  # Y取反
        # Z保持不变
    elif transform_type == "rotate_y_180":
        # 绕Y轴旋转180度: (x, y, z) -> (-x, y, -z)
        transformed_sequence[:, :, 0] = -vertices_sequence[:, :, 0]  # X取反
        transformed_sequence[:, :, 2] = -vertices_sequence[:, :, 2]  # Z取反
        # Y保持不变
    elif transform_type == "rotate_x_180":
        # 绕X轴旋转180度: (x, y, z) -> (x, -y, -z)
        transformed_sequence[:, :, 1] = -vertices_sequence[:, :, 1]  # Y取反
        transformed_sequence[:, :, 2] = -vertices_sequence[:, :, 2]  # Z取反
        # X保持不变
    else:
        print(f"[CoordinateTransform] Unknown transformation type: {transform_type}, no transformation applied")
    
    return transformed_sequence

def _gaussian_kernel1d(sigma, order=0, radius=None):
    """生成1D高斯核"""
    if radius is None:
        radius = int(4 * sigma + 0.5)
    
    x = torch.arange(-radius, radius + 1, dtype=torch.float32)
    x = x / sigma
    
    kernel = torch.exp(-0.5 * x ** 2)
    kernel = kernel / kernel.sum()
    
    return kernel.numpy()

def gaussian_smooth_numpy(x_np, sigma=3, dim=0):
    """
    NumPy版本的高斯平滑函数，基于附件代码实现
    """
    # 转换为PyTorch张量以便使用相同的卷积逻辑
    if isinstance(x_np, np.ndarray):
        x_tensor = torch.from_numpy(x_np).float()
    else:
        x_tensor = x_np
    
    # 生成高斯核
    kernel_smooth = _gaussian_kernel1d(sigma=sigma, order=0, radius=int(4 * sigma + 0.5))
    kernel_smooth = torch.from_numpy(kernel_smooth).float()[None, None]  # (1, 1, K)
    rad = kernel_smooth.size(-1) // 2
    
    # 确保张量在CPU上
    x_tensor = x_tensor.cpu()
    kernel_smooth = kernel_smooth.cpu()
    
    # 获取原始形状并准备卷积
    x = x_tensor.transpose(dim, -1)
    x_shape = x.shape[:-1]
    x = rearrange(x, "... f -> (...) 1 f")  # (NB, 1, f)
    
    # 使用replicate模式进行填充
    x = F.pad(x[None], (rad, rad, 0, 0), mode="replicate")[0]
    
    # 执行卷积
    x = F.conv1d(x, kernel_smooth)
    
    # 恢复原始形状
    x = x.squeeze(1).reshape(*x_shape, -1)  # (..., f)
    x = x.transpose(-1, dim)
    
    # 转换回NumPy
    if isinstance(x_np, np.ndarray):
        return x.numpy()
    else:
        return x

def moving_average_smooth_numpy(x_np, window_size=5, dim=0):
    """
    NumPy版本的移动平均平滑函数
    """
    # 转换为PyTorch张量
    if isinstance(x_np, np.ndarray):
        x_tensor = torch.from_numpy(x_np).float()
    else:
        x_tensor = x_np
    
    # 生成平均核
    kernel_smooth = torch.ones(window_size).float() / window_size
    kernel_smooth = kernel_smooth[None, None]  # (1, 1, window_size)
    rad = kernel_smooth.size(-1) // 2
    
    # 确保张量在CPU上
    x_tensor = x_tensor.cpu()
    kernel_smooth = kernel_smooth.cpu()
    
    # 获取原始形状并准备卷积
    x = x_tensor.transpose(dim, -1)
    x_shape = x.shape[:-1]
    x = rearrange(x, "... f -> (...) 1 f")  # (NB, 1, f)
    
    # 使用replicate模式进行填充
    x = F.pad(x[None], (rad, rad, 0, 0), mode="replicate")[0]
    
    # 执行卷积
    x = F.conv1d(x, kernel_smooth)
    
    # 恢复原始形状
    x = x.squeeze(1).reshape(*x_shape, -1)  # (..., f)
    x = x.transpose(-1, dim)
    
    # 转换回NumPy
    if isinstance(x_np, np.ndarray):
        return x.numpy()
    else:
        return x

def align_models_to_fixed_camera(frames_data, faces, reference_frame=0):
    """
    将所有模型对齐到固定相机（参考帧的相机）
    
    参数：
    - frames_data: 每帧的数据列表，包含vertices, cam_t, focal_length
    - faces: 面数据
    - reference_frame: 参考帧索引（通常为0）
    
    返回：
    - aligned_vertices: 对齐后的顶点序列
    - valid_frames: 有效帧的索引列表
    - reference_cam_params: 参考帧的相机参数
    """
    
    # 找到第一个有效帧作为参考帧（如果指定参考帧无效）
    valid_indices = [i for i, d in enumerate(frames_data) if d["success"]]
    if not valid_indices:
        raise ValueError("[Alignment] No valid frames found")
    
    # 如果指定的参考帧无效，使用第一个有效帧
    if not frames_data[reference_frame]["success"]:
        reference_frame = valid_indices[0]
        print(f"[Alignment] Reference frame changed to first valid frame: {reference_frame}")
    
    # 获取参考帧数据
    ref_data = frames_data[reference_frame]
    ref_vertices = ref_data["vertices"]
    ref_cam_t = ref_data["cam_t"]
    ref_focal_length = ref_data["focal_length"]
    
    if ref_vertices is None or ref_cam_t is None:
        raise ValueError(f"[Alignment] Reference frame {reference_frame} has invalid data")
    
    print(f"[Alignment] Reference frame: {reference_frame}")
    print(f"[Alignment] Reference camera: cam_t={ref_cam_t}, focal={ref_focal_length}")
    
    # 准备输出序列
    num_frames = len(frames_data)
    num_verts = ref_vertices.shape[0]
    aligned_vertices = np.zeros((num_frames, num_verts, 3))
    valid_frames = []
    
    # 处理每一帧
    for i in range(num_frames):
        frame_data = frames_data[i]
        
        if not frame_data["success"]:
            # 无效帧：复制参考帧的顶点（或保持为0）
            aligned_vertices[i] = ref_vertices.copy()
            continue
        
        vertices = frame_data["vertices"]
        cam_t = frame_data["cam_t"]
        focal_length = frame_data["focal_length"]
        
        if vertices is None or cam_t is None:
            # 数据不完整
            aligned_vertices[i] = ref_vertices.copy()
            continue
        
        # 检查形状一致性
        if vertices.shape[0] != num_verts:
            print(f"[Alignment] Warning: Frame {i} has {vertices.shape[0]} vertices, expected {num_verts}")
            aligned_vertices[i] = ref_vertices.copy()
            continue
        
        # 应用对齐变换：V_i' = V_i + C_i - C_ref
        # 注意：这里假设焦距相同，如果需要处理变焦，需要额外的缩放
        if focal_length is not None and ref_focal_length is not None and focal_length != ref_focal_length:
            # 如果需要处理焦距变化
            scale = ref_focal_length / focal_length
            aligned_vertices[i] = (vertices + cam_t) * scale - ref_cam_t
            if i < 3:  # 打印前几帧的调试信息
                print(f"[Alignment] Frame {i}: scaled by {scale:.3f} (focal: {focal_length:.1f} -> {ref_focal_length:.1f})")
        else:
            # 简单的相机位置对齐
            aligned_vertices[i] = vertices + cam_t - ref_cam_t
        
        valid_frames.append(i)
        
        # 调试信息
        if i < 3:  # 只打印前3帧的详细信息
            print(f"[Alignment] Frame {i}: cam_t={cam_t.flatten()}, aligned offset={-cam_t.flatten() + ref_cam_t.flatten()}")
    
    print(f"[Alignment] Completed: {len(valid_frames)} valid frames aligned to reference camera")
    
    # 计算对齐后的统计信息
    if valid_frames:
        # 计算有效帧的顶点变化范围
        valid_vertices = aligned_vertices[valid_frames]
        min_pos = valid_vertices.min(axis=(0, 1))
        max_pos = valid_vertices.max(axis=(0, 1))
        range_pos = max_pos - min_pos
        
        print(f"[Alignment] Vertex position range after alignment:")
        print(f"  X: {min_pos[0]:.3f} to {max_pos[0]:.3f} (range: {range_pos[0]:.3f})")
        print(f"  Y: {min_pos[1]:.3f} to {max_pos[1]:.3f} (range: {range_pos[1]:.3f})")
        print(f"  Z: {min_pos[2]:.3f} to {max_pos[2]:.3f} (range: {range_pos[2]:.3f})")
    
    return aligned_vertices, valid_frames, {
        "cam_t": ref_cam_t,
        "focal_length": ref_focal_length,
        "reference_frame": reference_frame
    }

# =============================================================================
# 视频处理节点
# =============================================================================

class SAM3DMeshSequenceFromVideo_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        # 检查依赖是否可用
        available, error_msg = check_sam3d_dependencies()
        if not available:
            print(f"Warning: ComfyUI-SAM3DBody dependency is unavailable; nodes may not function correctly: {error_msg}")
        
        return {
            "required": {
                "model": ("SAM3D_MODEL", {
                    "tooltip": "SAM3D Model"
                }),
                "image": ("IMAGE", {
                    "tooltip": "Image Batch"
                }),
                "output_filename": ("STRING", {
                    "default": "mesh_sequence",
                    "multiline": False,
                    "tooltip": "The output binary filename will be saved in the Adv3DViewer_JK_tmp directory of the output folder."
                }),
            },
            "optional": {
                "bbox_threshold": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Human body detection threshold"
                }),
                "inference_type": (["full", "body", "hand"], {
                    "default": "full",
                    "tooltip": "Inference type"
                }),
                "mask": ("MASK", {
                    "tooltip": "Optional Mask"
                }),
                # "coordinate_transform": (["none", "rotate_z_180", "rotate_y_180", "rotate_x_180"], {
                    # "default": "rotate_z_180",
                    # "tooltip": "Coordinate transformation type. Rotate_z_180 is typically used to correct SAM3D Body orientation issues."
                # }),
                "smoothing_method": (["gaussian", "moving_average"], {
                    "default": "gaussian",
                    "tooltip": "Smoothing Method"
                }),
                "smoothing_sigma": ("FLOAT", {
                    "default": 3.0,
                    "min": 0.5,
                    "max": 10.0,
                    "step": 0.5,
                    "tooltip": "Gaussian smoothing kernel width (the higher the width, the smoother the surface)"
                }),
                # "align_to_reference_camera": ("BOOLEAN", {
                    # "default": True,
                    # "label_on": "Enabled",
                    # "label_off": "Disabled",
                    # "tooltip": "Align all models to the camera (fixed camera) of the reference frame to ensure perfect alignment with the video."
                # }),
                # "reference_frame": ("INT", {
                    # "default": 0,
                    # "min": 0,
                    # "max": 1000,
                    # "step": 1,
                    # "tooltip": "Reference frame index (used for camera alignment)"
                # }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("bin_file_path",)
    FUNCTION = "generate_from_video_frames"
    CATEGORY = "🐉 JK/🕒 3D"
    OUTPUT_NODE = True
    
    def __init__(self):
        """初始化输出目录，参考jake_node_3d_viewer.py"""
        # 检查依赖是否可用
        available, error_msg = check_sam3d_dependencies()
        if not available:
            print(f"[SAM3D Check] ComfyUI-SAM3DBody dependency is unavailable; nodes may not function correctly: {error_msg}")
        
        import folder_paths
        self.output_dir = folder_paths.get_output_directory()
        self.tmp_output_dir_name = "Adv3DViewer_JK_tmp"
        
        # 只在需要时创建目录
        tmp_output_dir = Path(self.output_dir) / self.tmp_output_dir_name
        tmp_output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_tmp_output_dir(self):
        """获取临时输出目录的 Path 对象"""
        return Path(self.output_dir) / self.tmp_output_dir_name
    
    def clean_file_path(self, file_path: str) -> str:
        """清理文件路径，去除可能的引号（参考jake_node_3d_viewer.py）"""
        if not file_path:
            return ""
        
        # 去除首尾的引号（单引号和双引号）
        file_path = file_path.strip()
        if (file_path.startswith('"') and file_path.endswith('"')) or \
           (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1]
        
        return file_path.strip()
    
    def smooth_sequence(self, sequence: np.ndarray, sigma: float = 3.0, method: str = "gaussian") -> np.ndarray:
        """
        应用时间平滑到序列上
        """
        if sequence.shape[0] <= 1 or sigma <= 0:
            return sequence
        
        if method == "gaussian":
            smoothed = gaussian_smooth_numpy(sequence, sigma=sigma, dim=0)
        else:  # moving_average
            window_size = int(sigma * 2 + 1)
            smoothed = moving_average_smooth_numpy(sequence, window_size=window_size, dim=0)
        
        return smoothed
    
    def generate_from_video_frames(self, model, image, output_filename,
                                  bbox_threshold=0.8, inference_type="full", mask=None,
                                  coordinate_transform="rotate_z_180",
                                  smoothing_sigma=3.0, smoothing_method="gaussian",
                                  align_to_reference_camera=True, reference_frame=0):
        
        start_time_total = time.time()
        
        # 检查依赖是否可用
        available, error_msg = check_sam3d_dependencies()
        if not available:
            return (f"[SAM3D Check] SAM3D dependency unavailable: {error_msg}",)
        
        # 1. 检查输入图像
        if image is None or len(image) == 0:
            return (f"[VideoFramesToMesh] Error: No input image",)
        
        num_frames = len(image)
        
        # 2. 加载模型
        model_start_time = time.time()
        
        device = model.get("device", "cuda")
        if not torch.cuda.is_available():
            device = "cpu"
        
        model_config = model.copy()
        model_config["device"] = device
        
        try:
            loaded = _load_sam3d_model_process(model_config)
        except ImportError as e:
            return (f"[SAM3D Check] SAM3D dependency unavailable: {str(e)}",)
        
        # 3. 获取面数据
        from sam_3d_body import SAM3DBodyEstimator
        
        estimator = SAM3DBodyEstimator(
            sam_3d_body_model=loaded["model"],
            model_cfg=loaded["model_cfg"],
            human_detector=None,
            human_segmentor=None,
            fov_estimator=None,
        )
        
        faces = estimator.faces
        if faces is None:
            try:
                if hasattr(loaded["model"], 'faces'):
                    faces = loaded["model"].faces
                elif hasattr(loaded["model_cfg"], 'faces'):
                    faces = loaded["model_cfg"].faces
            except:
                pass
        
        if faces is None:
            return (f"[VideoFramesToMesh] Error: Unable to retrieve face data",)
        
        # 4. 准备输出路径
        # 清理文件名
        output_filename = self.clean_file_path(output_filename)
        
        # 生成唯一的文件名
        timestamp = int(time.time() * 1000)
        
        # 确保文件名以.bin结尾
        if not output_filename.lower().endswith('.bin'):
            output_filename += '.bin'
        
        # 添加时间戳以确保唯一性
        base_name = Path(output_filename).stem
        extension = Path(output_filename).suffix
        unique_filename = f"{base_name}_{timestamp}{extension}"
        
        # 使用 get_tmp_output_dir 方法获取 Path 对象
        tmp_output_dir = self.get_tmp_output_dir()
        output_path = tmp_output_dir / unique_filename
        
        # 5. 处理图像序列 - 收集顶点信息
        frames_data = []  # 存储每帧的完整数据
        processed_frames = 0
        failed_frames = 0
        
        print(f"[VideoFramesToMesh] Start processing {num_frames} frames...")
        
        # 临时目录用于保存帧图像
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # 逐帧处理
            for frame_idx in range(num_frames):
                try:
                    # 转换 ComfyUI 图像为 numpy
                    img_tensor = image[frame_idx]
                    if len(img_tensor.shape) == 4:  # [B, H, W, C]
                        img_np = img_tensor[0].cpu().numpy()
                    else:  # [H, W, C]
                        img_np = img_tensor.cpu().numpy()
                    
                    # 转换为 BGR 和 uint8
                    img_np = (img_np * 255).astype(np.uint8)
                    img_bgr = img_np[..., ::-1].copy()  # RGB -> BGR
                    
                    # 保存到临时文件
                    frame_path = temp_dir_path / f"frame_{frame_idx:06d}.jpg"
                    cv2.imwrite(str(frame_path), img_bgr)
                    
                    # 准备掩码（如果有）
                    mask_np = None
                    if mask is not None and len(mask) > frame_idx:
                        mask_tensor = mask[frame_idx]
                        if len(mask_tensor.shape) == 3:  # [B, H, W]
                            mask_np = mask_tensor[0].cpu().numpy()
                        else:  # [H, W]
                            mask_np = mask_tensor.cpu().numpy()
                    
                    # 计算边界框（如果有掩码）
                    bboxes = None
                    if mask_np is not None:
                        rows = np.any(mask_np > 0.5, axis=1)
                        cols = np.any(mask_np > 0.5, axis=0)
                        
                        if rows.any() and cols.any():
                            rmin, rmax = np.where(rows)[0][[0, -1]]
                            cmin, cmax = np.where(cols)[0][[0, -1]]
                            bboxes = np.array([[cmin, rmin, cmax, rmax]], dtype=np.float32)
                    
                    # 处理单帧图像
                    outputs = estimator.process_one_image(
                        str(frame_path),
                        bboxes=bboxes,
                        masks=mask_np,
                        bbox_thr=bbox_threshold,
                        use_mask=(mask_np is not None),
                        inference_type=inference_type,
                    )
                    
                    if not outputs or len(outputs) == 0:
                        print(f"[VideoFramesToMesh] Warning: Frame {frame_idx} no human detected")
                        failed_frames += 1
                        
                        # 添加空白帧数据
                        frames_data.append({
                            "vertices": None,
                            "cam_t": None,
                            "focal_length": None,
                            "success": False
                        })
                        processed_frames += 1
                        continue
                    
                    # 取第一个检测到的人体
                    output = outputs[0]
                    
                    # 提取顶点
                    pred_vertices = output.get("pred_vertices")
                    
                    # 提取相机参数
                    pred_cam_t = output.get("pred_cam_t")
                    focal_length = output.get("focal_length")
                    
                    if pred_vertices is None:
                        print(f"[VideoFramesToMesh] Warning: Frame {frame_idx} no vertex output, using blank frame")
                        frames_data.append({
                            "vertices": None,
                            "cam_t": None,
                            "focal_length": None,
                            "success": False
                        })
                    else:
                        # 转换为 numpy 数组
                        if torch.is_tensor(pred_vertices):
                            vertices = pred_vertices.detach().cpu().numpy()
                        else:
                            vertices = pred_vertices
                        
                        # 处理相机参数
                        if torch.is_tensor(pred_cam_t):
                            cam_t = pred_cam_t.detach().cpu().numpy()
                        else:
                            cam_t = pred_cam_t
                        
                        if focal_length is not None:
                            if hasattr(focal_length, 'item'):
                                focal_length = focal_length.item()
                            focal_length = float(focal_length)
                        
                        # 保存帧数据
                        frames_data.append({
                            "vertices": vertices,
                            "cam_t": cam_t,
                            "focal_length": focal_length,
                            "success": True
                        })
                    
                    processed_frames += 1
                    
                except Exception as e:
                    print(f"[VideoFramesToMesh] Error: Processing frame {frame_idx} failed - {e}")
                    failed_frames += 1
                    
                    frames_data.append({
                        "vertices": None,
                        "cam_t": None,
                        "focal_length": None,
                        "success": False
                    })
                    
                    processed_frames += 1
                
                # 每处理10帧显示一次进度
                if (frame_idx + 1) % 10 == 0 or (frame_idx + 1) == num_frames:
                    elapsed = time.time() - start_time_total
                    fps_rate = processed_frames / elapsed if elapsed > 0 else 0
                    print(f"[VideoFramesToMesh] Progress: {frame_idx + 1}/{num_frames} frames, "
                          f"Success: {processed_frames - failed_frames}, Failed: {failed_frames}, "
                          f"Speed: {fps_rate:.1f} FPS")
        
        if processed_frames == 0:
            return (f"错误: 没有成功处理任何帧",)
        
        # 6. 根据参数决定是否应用模型对齐
        if align_to_reference_camera:
            print(f"[VideoFramesToMesh] Aligning models to fixed camera (reference frame: {reference_frame})...")
            try:
                aligned_vertices, valid_frames, ref_cam_params = align_models_to_fixed_camera(
                    frames_data,
                    faces,
                    reference_frame=reference_frame
                )
                
                print(f"[Alignment] Reference camera parameters:")
                print(f"  cam_t: {ref_cam_params['cam_t'].flatten()}")
                print(f"  focal_length: {ref_cam_params['focal_length']}")
                
            except Exception as e:
                print(f"[Alignment] Error during alignment: {e}")
                print(f"[Alignment] Falling back to original vertices")
                
                # 回退：使用原始顶点（不应用对齐）
                aligned_vertices = np.stack([d["vertices"] if d["success"] else np.zeros((faces.shape[0], 3))
                                            for d in frames_data], axis=0)
                valid_frames = [i for i, d in enumerate(frames_data) if d["success"]]
        else:
            print(f"[VideoFramesToMesh] Skipping model alignment (align_to_reference_camera=False)")
            # 使用原始顶点
            aligned_vertices = np.stack([d["vertices"] if d["success"] else np.zeros((faces.shape[0], 3))
                                        for d in frames_data], axis=0)
            valid_frames = [i for i, d in enumerate(frames_data) if d["success"]]
        
        # 7. 总是应用时间平滑（如果有多于1帧）
        if len(valid_frames) > 1:
            print(f"[VideoFramesToMesh] Applying temporal smoothing (method: {smoothing_method}, sigma: {smoothing_sigma})")
            
            # 只对有效帧应用平滑
            valid_vertices = aligned_vertices[valid_frames]
            smoothed_vertices = self.smooth_sequence(
                valid_vertices, 
                sigma=smoothing_sigma, 
                method=smoothing_method
            )
            aligned_vertices[valid_frames] = smoothed_vertices
            
            print(f"[VideoFramesToMesh] Temporal smoothing completed")
        
        # 8. 应用坐标变换
        if coordinate_transform != "none":
            print(f"[CoordinateTransform] Applying coordinate transformation: {coordinate_transform}")
            
            # 变换顶点序列
            aligned_vertices = apply_coordinate_transform(aligned_vertices, coordinate_transform)
        
        # 9. 总是保存为 SMPL 兼容格式
        MeshSequenceBinaryFormat.save_smpl_compatible(
            vertices_sequence=aligned_vertices,
            faces=faces,
            output_path=output_path,
            fps=DEFAULT_FPS,
            coordinate_transform="none"  # 已经在前面应用了变换
        )
        
        print(f"[VideoFramesToMesh] Model alignment and generation completed!")
        print(f"[VideoFramesToMesh] Successfully processed: {processed_frames - failed_frames} frames, Failed: {failed_frames} frames")
        print(f"[VideoFramesToMesh] Model alignment: enabled (reference frame: {ref_cam_params.get('reference_frame', 0)})")
        print(f"[VideoFramesToMesh] Coordinate transformation: {coordinate_transform}")
        print(f"[VideoFramesToMesh] Temporal smoothing: enabled ({smoothing_method}, sigma={smoothing_sigma})")
        print(f"[VideoFramesToMesh] Output file: {output_path}")
        
        # 只返回完整路径
        return (str(output_path),)
