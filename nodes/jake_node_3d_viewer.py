#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade 3D Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import sys
import os
import shutil
import folder_paths
from pathlib import Path
from typing import Dict, Tuple, Optional
import time
from ..categories import icons

class Adv3DViewer_JK:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Optional: Full path to 3D file (glb, fbx, smpl bin, obj, ply, etc.)"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "view_file"
    OUTPUT_NODE = True
    CATEGORY = icons.get("JK/3D")
    DESCRIPTION = "Advanced 3D Viewer, supports GLB, FBX, SMPL bin, OBJ, PLY, OBJ Zip, and FBX Zip formats with/without camera animation, and with custom camera animation and exported as GLB.."

    def __init__(self):
        """初始化输出目录"""
        self.output_dir = Path(folder_paths.get_output_directory())
        self.tmp_output_dir = self.output_dir / "Adv3DViewer_JK_tmp"
        self.tmp_output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[Adv3DViewer_JK] Output directory: {self.tmp_output_dir}")

    def clean_file_path(self, file_path: str) -> str:
        """清理文件路径，去除可能的引号"""
        if not file_path:
            return ""
        
        # 去除首尾的引号（单引号和双引号）
        file_path = file_path.strip()
        if (file_path.startswith('"') and file_path.endswith('"')) or \
           (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1]
        
        return file_path.strip()

    def view_file(
        self,
        file_path: str = "",
    ) -> Tuple[str]:
        
        try:
            print("[Adv3DViewer_JK] Preparing 3D file for viewing...")

            # 清理文件路径（去除可能的引号）
            cleaned_file_path = self.clean_file_path(file_path)
            
            # 检查文件路径是否存在
            if not cleaned_file_path:
                error_msg = "No file path provided"
                print(error_msg)
                return {
                    "ui": {
                        "file_path": [""]
                    },
                    "result": (error_msg,)
                }
            
            input_file = Path(cleaned_file_path)
            if not input_file.exists():
                error_msg = f"File not found: {cleaned_file_path}"
                print(error_msg)
                return {
                    "ui": {
                        "file_path": [""]
                    },
                    "result": (error_msg,)
                }
            
            print(f"[Adv3DViewer_JK] Using file: {cleaned_file_path}")
            
            # 生成唯一的文件名
            timestamp = int(time.time() * 1000)
            original_ext = input_file.suffix.lower()
            mesh_filename = f"view_mesh_{timestamp}{original_ext}"
            mesh_filepath = self.tmp_output_dir / mesh_filename
            
            # 复制文件
            shutil.copy2(input_file, mesh_filepath)
            
            print(f"[Adv3DViewer_JK] File copied to: {mesh_filepath}")
            
            # 返回相对路径，使用新的路由
            relative_path = f"Adv3DViewer_JK_tmp/{mesh_filename}"
            
            return {
                "ui": {
                    "file_path": [relative_path],
                },
                "result": (f"Loaded file: {input_file.name}",)
            }

        except Exception as e:
            error_msg = f"Adv3DViewer_JK failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                "ui": {
                    "file_path": [""]
                },
                "result": (error_msg,)
            }

# ==================== 路由注册部分 ====================

from aiohttp import web
import json

def setup_adv3dviewer_routes():
    """设置 Adv3DViewer_JK 的路由"""
    try:
        from server import PromptServer
        
        # 获取 PromptServer 实例
        server = PromptServer.instance
        
        @server.routes.get("/adv3dviewer_jk")
        async def get_adv3dviewer_file(request):
            """获取 Adv3DViewer_JK 文件的处理器"""
            try:
                # 获取查询参数中的文件名
                filename = request.rel_url.query.get("filename", "")
                if not filename:
                    return web.Response(status=400, text="Missing filename parameter")
                
                # 构建文件路径 - 使用 ComfyUI 的输出目录
                import folder_paths
                output_dir = Path(folder_paths.get_output_directory())
                
                # 支持子目录路径（如 "Adv3DViewer_JK_tmp/filename.glb"）
                file_path = output_dir / filename
                
                # 防止目录遍历攻击，确保文件在输出目录内
                try:
                    file_path.resolve().relative_to(output_dir.resolve())
                except ValueError:
                    return web.Response(status=403, text="Access denied")
                
                # 检查文件是否存在
                if file_path.exists():
                    return web.FileResponse(file_path)
                else:
                    return web.Response(
                        status=404, 
                        text=f"File not found: {filename}"
                    )
                    
            except Exception as e:
                print(f"[Adv3DViewer_JK] Route error: {e}")
                return web.Response(status=500, text=f"Internal server error: {str(e)}")
        
        # print("🔶 [Adv3DViewer_JK] Route registered: /adv3dviewer_jk")
        return True
        
    except ImportError as e:
        print(f"🔶 [Adv3DViewer_JK] Cannot import PromptServer: {e}")
        return False
    except Exception as e:
        print(f"🔶 [Adv3DViewer_JK] Failed to register route: {e}")
        return False

# 尝试注册路由
try:
    setup_adv3dviewer_routes()
except Exception as e:
    print(f"🔶 [Adv3DViewer_JK] Error during route registration: {e}")