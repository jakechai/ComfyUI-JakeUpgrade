"""
SAM3D Mesh Sequence Generator Nodes
处理视频、mhr_params和NPZ文件，生成二进制Mesh序列 (.bin)
"""

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

# 获取当前文件所在目录
CURRENT_FILE_DIR = Path(__file__).parent.absolute()

# =============================================================================
# 检查 SAM3D 依赖是否可用
# =============================================================================

def check_sam3d_dependencies():
    """
    检查 SAM3D 依赖是否可用
    返回: (bool, str) - (是否可用, 错误信息)
    """
    # 尝试多种可能的SAM3D节点路径
    possible_paths = [
        # 1. 尝试从当前文件向上回溯查找
        CURRENT_FILE_DIR.parent.parent.parent / "ComfyUI_Motion" / "custom_nodes" / "ComfyUI-SAM3DBody",
        CURRENT_FILE_DIR.parent.parent.parent.parent / "ComfyUI_Motion" / "ComfyUI" / "custom_nodes" / "ComfyUI-SAM3DBody",
        
        # 2. 尝试ComfyUI根目录的相对路径
        CURRENT_FILE_DIR.parent.parent.parent / "ComfyUI-SAM3DBody",
        
        # 3. 尝试从环境变量获取
        os.environ.get("SAM3D_NODE_PATH", ""),
        
        # 4. 绝对路径备选
        Path(r"I:\ComfyUI_Motion\ComfyUI\custom_nodes\ComfyUI-SAM3DBody"),
    ]
    
    sam3d_node_path = None
    for path_str in possible_paths:
        if not path_str:
            continue
            
        path = Path(path_str) if isinstance(path_str, str) else path_str
        if path.exists():
            sam3d_node_path = path
            print(f"[SAM3D Check] Found SAM3D node at: {sam3d_node_path}")
            break
    
    if sam3d_node_path is None:
        return False, "未找到SAM3D节点路径，请确保已安装ComfyUI-SAM3DBody节点"
    
    # 检查虚拟环境路径
    sam3d_env_path = sam3d_node_path / "_env_sam3dbody"
    if not sam3d_env_path.exists():
        print(f"[SAM3D Check] Warning: SAM3D虚拟环境路径不存在: {sam3d_env_path}")
        # 虚拟环境不是必需的，可以继续
    
    # 尝试导入 sam_3d_body
    try:
        # 将 SAM3D 节点路径添加到 sys.path
        if str(sam3d_node_path) not in sys.path:
            sys.path.insert(0, str(sam3d_node_path))
        
        # 尝试导入
        from sam_3d_body import load_sam_3d_body, SAM3DBodyEstimator
        
        print(f"[SAM3D Check] SAM3D依赖检查通过")
        return True, "SAM3D依赖检查通过"
    except ImportError as e:
        return False, f"无法导入SAM3D模块: {str(e)}"
    except Exception as e:
        return False, f"SAM3D依赖检查失败: {str(e)}"

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

# =============================================================================
# 共享函数
# =============================================================================

# 模块级缓存，复用 SAM3DBodyProcess 中的模型
_MODEL_CACHE_PROCESS = {}

def _load_sam3d_model_process(model_config: dict):
    """
    加载 SAM 3D Body 模型（与 process.py 中的函数相同）
    """
    cache_key = model_config["ckpt_path"]

    if cache_key in _MODEL_CACHE_PROCESS:
        return _MODEL_CACHE_PROCESS[cache_key]

    # 检查依赖是否可用
    available, error_msg = check_sam3d_dependencies()
    if not available:
        raise ImportError(f"SAM3D依赖不可用: {error_msg}")

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
    """
    对顶点序列应用坐标变换
    
    参数:
        vertices_sequence: (num_frames, num_verts, 3) 的顶点序列
        transform_type: 变换类型
            - "rotate_z_180": 绕Z轴旋转180度 (X,Y取反)
            - "rotate_y_180": 绕Y轴旋转180度 (X,Z取反)
            - "rotate_x_180": 绕X轴旋转180度 (Y,Z取反)
            - "rotate_z_90": 绕Z轴旋转90度
            - "none": 不应用变换
    
    返回:
        变换后的顶点序列
    """
    if transform_type == "none" or vertices_sequence is None:
        return vertices_sequence
    
    num_frames, num_verts, _ = vertices_sequence.shape
    transformed_sequence = vertices_sequence.copy()
    
    if transform_type == "rotate_z_180":
        # 绕Z轴旋转180度: (x, y, z) -> (-x, -y, z)
        print(f"[CoordinateTransform] Rotate 180 degrees around Z axis: {num_frames}frames, {num_verts}vertices")
        transformed_sequence[:, :, 0] = -vertices_sequence[:, :, 0]  # X取反
        transformed_sequence[:, :, 1] = -vertices_sequence[:, :, 1]  # Y取反
        # Z保持不变
    elif transform_type == "rotate_y_180":
        # 绕Y轴旋转180度: (x, y, z) -> (-x, y, -z)
        print(f"[CoordinateTransform] Rotate 180 degrees around Y axis: {num_frames}frames, {num_verts}vertices")
        transformed_sequence[:, :, 0] = -vertices_sequence[:, :, 0]  # X取反
        transformed_sequence[:, :, 2] = -vertices_sequence[:, :, 2]  # Z取反
        # Y保持不变
    elif transform_type == "rotate_x_180":
        # 绕X轴旋转180度: (x, y, z) -> (x, -y, -z)
        print(f"[CoordinateTransform] Rotate 180 degrees around X axis: {num_frames}frames, {num_verts}vertices")
        transformed_sequence[:, :, 1] = -vertices_sequence[:, :, 1]  # Y取反
        transformed_sequence[:, :, 2] = -vertices_sequence[:, :, 2]  # Z取反
        # X保持不变
    elif transform_type == "rotate_z_90":
        # 绕Z轴旋转90度: (x, y, z) -> (-y, x, z)
        print(f"[CoordinateTransform] Rotate 90 degrees around Z axis: {num_frames}frames, {num_verts}vertices")
        x_original = vertices_sequence[:, :, 0].copy()
        y_original = vertices_sequence[:, :, 1].copy()
        transformed_sequence[:, :, 0] = -y_original  # X = -Y
        transformed_sequence[:, :, 1] = x_original   # Y = X
        # Z保持不变
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


# =============================================================================
# 视频处理节点
# =============================================================================

class SAM3DMeshSequenceFromVideo_JK:
    """
    从视频文件生成 Mesh 序列，使用与 SAM3DBodyProcess 相同的输入格式
    
    注意: 此节点需要 SAM3DBody 节点的依赖
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 检查依赖是否可用
        available, error_msg = check_sam3d_dependencies()
        if not available:
            print(f"警告: SAM3D依赖不可用，节点可能无法正常工作: {error_msg}")
        
        return {
            "required": {
                "model": ("SAM3D_MODEL", {
                    "tooltip": "SAM3D 模型配置"
                }),
                "image": ("IMAGE", {
                    "tooltip": "视频帧序列（批处理的图像）"
                }),
                "output_filename": ("STRING", {
                    "default": "mesh_sequence.bin",
                    "multiline": False,
                    "placeholder": "输出文件名 (会自动添加时间戳)",
                    "tooltip": "输出二进制文件名，会保存在 Adv3DViewer_JK_tmp 目录"
                }),
            },
            "optional": {
                "bbox_threshold": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "人体检测阈值"
                }),
                "inference_type": (["full", "body", "hand"], {
                    "default": "full",
                    "tooltip": "推理类型"
                }),
                "mask": ("MASK", {
                    "tooltip": "可选的分割掩码序列"
                }),
                "coordinate_transform": (["none", "rotate_z_180", "rotate_y_180", "rotate_x_180", "rotate_z_90"], {
                    "default": "rotate_z_180",
                    "tooltip": "坐标变换类型。通常使用rotate_z_180修正朝向问题"
                }),
                "smoothing_sigma": ("FLOAT", {
                    "default": 3.0,
                    "min": 0.5,
                    "max": 10.0,
                    "step": 0.5,
                    "tooltip": "高斯平滑核宽度（越高越平滑）"
                }),
                "smoothing_method": (["gaussian", "moving_average"], {
                    "default": "gaussian",
                    "tooltip": "平滑算法"
                }),
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
            print(f"警告: SAM3D依赖不可用，节点可能无法正常工作: {error_msg}")
        
        import folder_paths
        self.output_dir = folder_paths.get_output_directory()
        self.tmp_output_dir_name = "Adv3DViewer_JK_tmp"
        
        # 只在需要时创建目录
        tmp_output_dir = Path(self.output_dir) / self.tmp_output_dir_name
        tmp_output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[SAM3DMeshSequence] Output directory: {tmp_output_dir}")
    
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
                                  smoothing_sigma=3.0, smoothing_method="gaussian"):
        """
        从图像序列（视频帧）生成 Mesh 序列
        """
        
        import time
        start_time_total = time.time()
        
        # 检查依赖是否可用
        available, error_msg = check_sam3d_dependencies()
        if not available:
            return (f"错误: SAM3D依赖不可用 - {error_msg}",)
        
        # 1. 检查输入图像
        if image is None or len(image) == 0:
            return (f"错误: 没有输入图像",)
        
        num_frames = len(image)
        print(f"[VideoFramesToMesh] Input image sequence: {num_frames}frames")
        print(f"[VideoFramesToMesh] Coordinate transformation: {coordinate_transform}")
        print(f"[VideoFramesToMesh] Temporal smoothing: enabled, method: {smoothing_method}, sigma: {smoothing_sigma}")
        
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
            return (f"错误: 无法加载SAM3D模型 - {str(e)}",)
        
        print(f"[VideoFramesToMesh] Model loaded, time: {time.time() - model_start_time:.2f}seconds")
        
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
            return (f"错误: 无法获取面数据",)
        
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
        
        print(f"[VideoFramesToMesh] Output file: {output_path}")
        
        # 5. 处理图像序列 - 收集顶点信息
        vertices_sequence = []
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
                        
                        # 添加空白帧
                        num_verts = faces.shape[0]
                        blank_vertices = np.zeros((num_verts, 3))
                        vertices_sequence.append(blank_vertices)
                        
                        processed_frames += 1
                        continue
                    
                    # 取第一个检测到的人体
                    output = outputs[0]
                    
                    # 提取顶点
                    pred_vertices = output.get("pred_vertices")
                    if pred_vertices is None:
                        print(f"[VideoFramesToMesh] Warning: Frame {frame_idx} no vertex output, using blank frame")
                        num_verts = faces.shape[0]
                        blank_vertices = np.zeros((num_verts, 3))
                        vertices_sequence.append(blank_vertices)
                    else:
                        # 转换为 numpy 数组
                        if torch.is_tensor(pred_vertices):
                            vertices = pred_vertices.detach().cpu().numpy()
                        else:
                            vertices = pred_vertices
                        
                        vertices_sequence.append(vertices)
                    
                    processed_frames += 1
                    
                except Exception as e:
                    print(f"[VideoFramesToMesh] Error: Processing frame {frame_idx} failed - {e}")
                    failed_frames += 1
                    
                    # 添加空白帧
                    num_verts = faces.shape[0]
                    blank_vertices = np.zeros((num_verts, 3))
                    vertices_sequence.append(blank_vertices)
                    
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
        
        # 6. 转换为 numpy 数组
        vertices_sequence_np = np.stack(vertices_sequence, axis=0)
        
        # 7. 总是应用时间平滑（如果有多于1帧）
        if processed_frames > 1:
            print(f"[VideoFramesToMesh] Applying temporal smoothing (method: {smoothing_method}, sigma: {smoothing_sigma})")
            
            vertices_sequence_np = self.smooth_sequence(
                vertices_sequence_np, 
                sigma=smoothing_sigma, 
                method=smoothing_method
            )
            
            print(f"[VideoFramesToMesh] Temporal smoothing completed")
        
        # 8. 应用坐标变换
        if coordinate_transform != "none":
            print(f"[CoordinateTransform] Applying coordinate transformation: {coordinate_transform}")
            
            # 变换顶点序列
            vertices_sequence_np = apply_coordinate_transform(vertices_sequence_np, coordinate_transform)
        
        # 9. 总是保存为 SMPL 兼容格式
        MeshSequenceBinaryFormat.save_smpl_compatible(
            vertices_sequence=vertices_sequence_np,
            faces=faces,
            output_path=output_path,
            fps=DEFAULT_FPS,
            coordinate_transform="none"  # 已经在前面应用了变换
        )
        
        print(f"[VideoFramesToMesh] SMPL compatible format generation completed! Total time: {time.time() - start_time_total:.2f}seconds")
        print(f"[VideoFramesToMesh] Successfully processed: {processed_frames - failed_frames}frames, Failed: {failed_frames}frames")
        print(f"[VideoFramesToMesh] Coordinate transformation: {coordinate_transform}")
        print(f"[VideoFramesToMesh] Temporal smoothing: enabled ({smoothing_method}, sigma={smoothing_sigma})")
        print(f"[VideoFramesToMesh] Output file: {output_path}")
        
        # 只返回完整路径
        return (str(output_path),)
