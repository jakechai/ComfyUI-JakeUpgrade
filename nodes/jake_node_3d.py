#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade 3D Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
from typing import Any, Tuple, List, Dict
from ..categories import icons

ORBITPOSE_PRESET = ["Custom", "CRM(6)", "Zero123Plus(6)", "Wonder3D(6)", "Era3D(6)", "MVDream(4)", "Unique3D(4)", "CharacterGen(4)"]

# 完整的预设数据配置
OrbitPosesList = {
    "Custom":           [[-90.0, 0.0, 180.0, 90.0, 0.0, 0.0], [0.0, 90.0, 0.0, 0.0, -90.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "CRM(6)":           [[-90.0, 0.0, 180.0, 90.0, 0.0, 0.0], [0.0, 90.0, 0.0, 0.0, -90.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Wonder3D(6)":      [[0.0, 45.0, 90.0, 180.0, -90.0, -45.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Zero123Plus(6)":   [[30.0, 90.0, 150.0, -150.0, -90.0, -30.0], [-20.0, 10.0, -20.0, 10.0, -20.0, 10.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Era3D(6)":         [[0.0, 45.0, 90.0, 180.0, -90.0, -45.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "Hunyuan3D(6)":     [[0.0, 60.0, 120.0, 180.0, -120.0, -60.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    "MVDream(4)":       [[0.0, 90.0, 180.0, -90.0], [0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
    "Unique3D(4)":      [[0.0, 90.0, 180.0, -90.0], [0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
    "CharacterGen(4)":  [[-90.0, 180.0, 90.0, 0.0], [0.0, 0.0, 0.0, 0.0], [4.0, 4.0, 4.0, 4.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
}

class OrbitPoseUtils:
    """工具类，提供相机位姿转换的通用方法"""
    
    @staticmethod
    def validate_and_parse_float_list(input_str: str, field_name: str = "") -> List[float]:
        """
        验证并解析浮点数列表
        
        Args:
            input_str: 输入的逗号分隔字符串
            field_name: 字段名称，用于错误提示
            
        Returns:
            解析后的浮点数列表
            
        Raises:
            ValueError: 当输入格式无效时
        """
        try:
            values = [float(item.strip()) for item in input_str.split(",")]
            return values
        except ValueError as e:
            raise ValueError(f"Invalid {field_name} format: {input_str}. Please use comma-separated floating point numbers.")
    
    @staticmethod
    def lists_to_camposes(orbit_lists: List[List[float]]) -> List[List[float]]:
        """
        将列表格式转换为相机位姿格式
        
        Args:
            orbit_lists: [方位角, 仰角, 半径, 中心X, 中心Y, 中心Z] 的列表
            
        Returns:
            相机位姿列表: [[半径, 仰角, 方位角, 中心X, 中心Y, 中心Z], ...]
        """
        orbit_camposes = []
        for i in range(len(orbit_lists[0])):
            orbit_camposes.append([
                orbit_lists[2][i],  # radius
                orbit_lists[1][i],  # elevation
                orbit_lists[0][i],  # azimuth
                orbit_lists[3][i],  # center_x
                orbit_lists[4][i],  # center_y
                orbit_lists[5][i]   # center_z
            ])
        return orbit_camposes
    
    @staticmethod
    def camposes_to_lists(orbit_camposes: List[List[float]]) -> List[List[float]]:
        """
        将相机位姿格式转换为列表格式
        
        Args:
            orbit_camposes: [[半径, 仰角, 方位角, 中心X, 中心Y, 中心Z], ...]
            
        Returns:
            列表格式: [方位角, 仰角, 半径, 中心X, 中心Y, 中心Z]
        """
        azimuths, elevations, radius, centers_x, centers_y, centers_z = [], [], [], [], [], []
        
        for pose in orbit_camposes:
            radius.append(pose[0])
            elevations.append(pose[1])
            azimuths.append(pose[2])
            centers_x.append(pose[3])
            centers_y.append(pose[4])
            centers_z.append(pose[5])
        
        return [azimuths, elevations, radius, centers_x, centers_y, centers_z]

class OrbitPoses_JK:
    """
    生成轨道相机位姿配置的节点
    
    支持多种3D生成模型的预设相机轨迹，包括CRM、Wonder3D、Zero123Plus等，
    也支持完全自定义的相机参数配置。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbitpose_preset": (ORBITPOSE_PRESET, {
                    "default": "Custom",
                    "tooltip": "Select a preset camera track configuration, or select Custom to customize it."
                }),
                "azimuths": ("STRING", {
                    "default": "-90.0, 0.0, 180.0, 90.0, 0.0, 0.0",
                    "tooltip": "A comma-separated list of azimuth angles (degrees). Controls the camera's horizontal rotation angle."
                }),
                "elevations": ("STRING", {
                    "default": "0.0, 90.0, 0.0, 0.0, -90.0, 0.0", 
                    "tooltip": "Elevation angle list (degrees), comma separated. Controls the vertical tilt angle of the camera."
                }),
                "radius": ("STRING", {
                    "default": "4.0, 4.0, 4.0, 4.0, 4.0, 4.0",
                    "tooltip": "A comma-separated list of radius that controls the distance between the camera and the target."
                }),
                "center": ("STRING", {
                    "default": "0.0, 0.0, 0.0, 0.0, 0.0, 0.0",
                    "tooltip": "A comma-separated list of center point coordinates. The XYZ coordinates of the center of the control track."
                }),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES", "ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_lists", "orbit_camposes",)
    FUNCTION = "get_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    DESCRIPTION = "Generate 3D camera track pose configurations, supporting multiple preset and custom parameters."
    
    def get_orbit_poses(self, orbitpose_preset: str, azimuths: str, elevations: str, radius: str, center: str) -> Tuple[List, List]:
        """
        获取轨道相机位姿配置
        
        Args:
            orbitpose_preset: 预设名称
            azimuths: 方位角字符串
            elevations: 仰角字符串  
            radius: 半径字符串
            center: 中心点字符串
            
        Returns:
            tuple: (orbit_lists, orbit_camposes)
        """
        # 获取预设配置
        orbit_lists = OrbitPosesList.get(orbitpose_preset)
        
        if orbit_lists is None:
            raise ValueError(f"Unsupported presets: {orbitpose_preset}")
        
        # 自定义配置处理
        if orbitpose_preset == "Custom":
            try:
                azimuths_list = OrbitPoseUtils.validate_and_parse_float_list(azimuths, "azimuths")
                elevations_list = OrbitPoseUtils.validate_and_parse_float_list(elevations, "elevations")
                radius_list = OrbitPoseUtils.validate_and_parse_float_list(radius, "radius")
                center_list = OrbitPoseUtils.validate_and_parse_float_list(center, "center")
                
                # 验证所有列表长度一致
                list_lengths = [len(azimuths_list), len(elevations_list), len(radius_list), len(center_list)]
                if len(set(list_lengths)) != 1:
                    raise ValueError("All parameter lists must be the same length.")
                
                orbit_lists = [azimuths_list, elevations_list, radius_list, center_list, center_list, center_list]
                
            except Exception as e:
                raise ValueError(f"Custom configuration parsing error: {str(e)}")
        
        # 转换为相机位姿格式
        orbit_camposes = OrbitPoseUtils.lists_to_camposes(orbit_lists)
        
        return (orbit_lists, orbit_camposes)

class OrbitLists_to_OrbitPoses_JK:
    """
    将轨道列表格式转换为相机位姿格式
    
    将[方位角,仰角,半径,中心X,中心Y,中心Z]的列表格式转换为
    [半径,仰角,方位角,中心X,中心Y,中心Z]的相机位姿格式。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbit_lists": ("ORBIT_CAMPOSES", {
                    "tooltip": "Input track list format: [azimuth, elevation, radius, center X, center Y, center Z]."
                }),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_camposes",)
    FUNCTION = "convert_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    DESCRIPTION = "Convert track list format to camera pose format."
    
    def convert_orbit_poses(self, orbit_lists: List[List[float]]) -> Tuple[List[List[float]]]:
        """
        转换轨道列表为相机位姿
        
        Args:
            orbit_lists: 轨道列表格式
            
        Returns:
            tuple: 相机位姿列表
        """
        orbit_camposes = OrbitPoseUtils.lists_to_camposes(orbit_lists)
        return (orbit_camposes,)

class OrbitPoses_to_OrbitLists_JK:
    """
    将相机位姿格式转换为轨道列表格式
    
    将[半径,仰角,方位角,中心X,中心Y,中心Z]的相机位姿格式转换为
    [方位角,仰角,半径,中心X,中心Y,中心Z]的列表格式。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "orbit_camposes": ("ORBIT_CAMPOSES", {
                    "tooltip": "Input camera pose format: [radius, elevation, azimuth, center X, center Y, center Z]."
                }),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    RETURN_NAMES = ("orbit_lists",)
    FUNCTION = "convert_orbit_poses"
    CATEGORY = icons.get("JK/3D")
    DESCRIPTION = "Convert camera pose format to track list format."
    
    def convert_orbit_poses(self, orbit_camposes: List[List[float]]) -> Tuple[List[List[float]]]:
        """
        转换相机位姿为轨道列表
        
        Args:
            orbit_camposes: 相机位姿列表
            
        Returns:
            tuple: 轨道列表格式
        """
        orbit_lists = OrbitPoseUtils.camposes_to_lists(orbit_camposes)
        return (orbit_lists,)

class Get_OrbitPoses_From_List_JK:
    """
    从相机位姿列表中按索引选择特定位姿
    
    通过指定索引列表，从输入的相机位姿序列中选择特定的相机位姿，
    用于生成特定角度的视图或减少渲染数量。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_orbit_camera_poses": ("ORBIT_CAMPOSES", {
                    "tooltip": "The original camera pose list, in the format of [radius, elevation, azimuth, center X, center Y, center Z]."
                }),
                "indexes": ("STRING", {
                    "default": "0, 1, 2", 
                    "multiline": True,
                    "tooltip": "The pose index to be selected, separated by commas. For example: 0,2,5 selects the 1st, 3rd, and 6th poses."
                }),
            },
        }
    
    RETURN_TYPES = ("ORBIT_CAMPOSES",)
    FUNCTION = "get_indexed_camposes"
    CATEGORY = icons.get("JK/3D")
    DESCRIPTION = "Select a specific pose by index from a list of camera poses."
    
    def get_indexed_camposes(self, original_orbit_camera_poses: List[List[float]], indexes: str) -> Tuple[List[List[float]]]:
        """
        获取指定索引的相机位姿
        
        Args:
            original_orbit_camera_poses: 原始相机位姿列表
            indexes: 索引字符串
            
        Returns:
            tuple: 选择的相机位姿列表
        """
        try:
            # 解析索引字符串
            index_list = [int(index.strip()) for index in indexes.split(',')]
            
            # 验证索引范围
            max_index = len(original_orbit_camera_poses) - 1
            for idx in index_list:
                if idx < 0 or idx > max_index:
                    raise ValueError(f"Index {idx} is out of range. Valid range: 0-{max_index}")
            
            # 选择指定索引的位姿
            orbit_camera_poses = []
            for i in index_list:
                orbit_camera_poses.append(original_orbit_camera_poses[i])
            
            return (orbit_camera_poses,)
            
        except ValueError as e:
            raise ValueError(f"Index parse error: {str(e)}. Please use comma-separated integer indices.")
        except Exception as e:
            raise ValueError(f"An error occurred while selecting the camera pose.: {str(e)}")