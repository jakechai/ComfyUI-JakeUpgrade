import configparser
import os
import re
import folder_paths
import sys
import nodes
from typing import Dict, Type, Any

# WEB directory settings
WEB_DIR_NAME = "ComfyUI-JakeUpgrade"
WEB_JS_DIR = 'web/js'
nodes.EXTENSION_WEB_DIRS[WEB_DIR_NAME] = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 
    WEB_JS_DIR
)

# Path settings
jakeupgrade_path = os.path.dirname(__file__)
jakeupgrade_nodes_path = os.path.join(jakeupgrade_path, "nodes")

# 直接修改 sys.path 来支持相对导入
sys.path.insert(0, jakeupgrade_path)

print(f"--------------------- Jake Upgrade Nodes ---------------------")

def get_version_from_pyproject():
    """从 pyproject.toml 读取版本信息"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pyproject_path = os.path.join(current_dir, 'pyproject.toml')
        
        # 读取 pyproject.toml 文件
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配版本号
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            return version_match.group(1)
        else:
            print("⚠️ Version info not found")
            return "unknown"
            
    except Exception as e:
        print(f"❌ Failed to read version: {e}")
        return "unknown"

__version__ = get_version_from_pyproject()
print(f"🔶 Version {__version__}")

def load_config():
    """从 config.ini 加载配置 / Load configuration from config.ini"""
    config = configparser.ConfigParser()
    
    # 获取配置文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')
    
    # 如果配置文件存在，读取它
    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
            print("🔶 Config file loaded successfully")
        except Exception as e:
            print(f"❌ Config file read error: {e}")
            # 使用默认值创建新的配置文件
            create_default_config(config_path)
    else:
        # 创建默认配置文件
        create_default_config(config_path)
    
    # 获取配置值
    try:
        load_deprecated = config.getboolean('JakeUpgrade', 'LOAD_DEPRECATED_NODES', fallback=False)
        enabled_modules_str = config.get('JakeUpgrade', 'ENABLED_MODULES', fallback='')
        random_prompter_abc = config.getboolean('JakeUpgrade', 'RANDOM_PROMPTER_ABC', fallback=False)
    except Exception as e:
        print(f"❌ Config parsing error: {e}")
        load_deprecated = False
        enabled_modules_str = ''
        random_prompter_abc = False
    
    # 处理启用的模块列表
    if enabled_modules_str.strip().lower() == 'all':
        # 如果设置为 'all'，启用所有模块
        enabled_modules = []
    elif enabled_modules_str.strip():
        # 否则按逗号分割
        enabled_modules = [m.strip().lower() for m in enabled_modules_str.split(',') if m.strip()]
    else:
        # 如果为空，也启用所有模块
        enabled_modules = []
    
    return load_deprecated, enabled_modules, random_prompter_abc

def create_default_config(config_path):
    """创建默认配置文件 / Create default config file"""
    try:
        config_content = """; JakeUpgrade 配置文件 / JakeUpgrade Configuration File
; 注意: 修改配置后需要重启 ComfyUI / Note: Restart ComfyUI after modifying config

[JakeUpgrade]
; 设置为 True 来加载已弃用的节点，False不加载。
; Set to True to load deprecated nodes, False to unload.
LOAD_DEPRECATED_NODES = False

; 启用模块列表 (留空或填写all表示全读取，指定读取模块用逗号分隔)
; Enabled modules list (Leave it blank or fill in "all" to load all modules, and specify the modules separated by commas.)
; 3d,audio,controlnet,lora,experimental,image,latent,mask,math,misc,prompt,switch,video
ENABLED_MODULES = all

; True表示使用ABC Stratagy架构的RandomPrompter节点，False不使用。
; Should we use the ABC Stratagy architecture's RandomPrompter node? True indicates use, False indicates not use.
RANDOM_PROMPTER_ABC = false

[RandomPrompterConfig]
; 提示词数据目录
; Prompt data directory
PROMPT_DATA_DIR = prompt_data

; 目录映射配置 (格式: 内部名称:目录名称)
; Directory mapping configuration (format: internal name: directory name)
DIRECTORY_MAPPING_scene = scenes
DIRECTORY_MAPPING_motion = motions
DIRECTORY_MAPPING_facial_action = facial_actions
DIRECTORY_MAPPING_exp_str = exp_strs
DIRECTORY_MAPPING_expression = expressions
DIRECTORY_MAPPING_lighting = lightings
DIRECTORY_MAPPING_camera = cameras
DIRECTORY_MAPPING_style = styles
DIRECTORY_MAPPING_style_artist = 1-artists
DIRECTORY_MAPPING_style_form = 2-forms
DIRECTORY_MAPPING_description = descriptions

; 概率参数配置
; Probability parameter configuration
RANDOM_EMPTY_PROB = 0.10
CUSTOM_FIELD_PROB = 0.05
EXP_STR_RANDOM_PROB = 0.80
STRUCTURED_SELECT_PROB = 0.50

; 参考图像数量 (QWen)
; Number of reference images (QWen)
REF_IMAGE_COUNT = 3

; 随机计算时排除的文件记号 (900 表示文件开头字符数字 >=900 的所有文件)
; File identifiers excluded during randomization (900 indicates all files whose first digits are >= 900).
EXCLUSION_MARK = 900
"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"🔶 Default config file created: {config_path}")
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")

# 获取配置
LOAD_DEPRECATED_NODES, ENABLED_MODULES, RANDOM_PROMPTER_ABC = load_config()

# 根据配置选择提示词节点文件
if RANDOM_PROMPTER_ABC:
    PROMPT_NODE_FILE = "jake_node_prompt_ABC"
    print("🔶 Using ABC Strategy version of RandomPrompter")
else:
    PROMPT_NODE_FILE = "jake_node_prompt"
    print("🔶 Using standard version of RandomPrompter")

# Main node mappings
NODE_CLASS_MAPPINGS: Dict[str, Type[Any]] = {}
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {}

# 模块映射定义
MODULE_MAPPING = {
    '3d': ('jake_node_3d', '3D Nodes'),
    'audio': ('jake_node_audio', 'Audio Nodes'),
    'controlnet': ('jake_node_controlnet', 'ControlNet Nodes'),
    'lora': ('jake_node_lora', 'LoRA Nodes'),
    'experimental': ('jake_node_experimental', 'Experimental Nodes'),
    'image': ('jake_node_image', 'Image Nodes'),
    'latent': ('jake_node_latent', 'Latent Nodes'),
    'mask': ('jake_node_mask', 'Mask Nodes'),
    'math': ('jake_node_math', 'Math Nodes'),
    'misc': ('jake_node_misc', 'Misc Nodes'),
    'prompt': (PROMPT_NODE_FILE, 'Prompt Nodes'),
    'switch': ('jake_node_switch', 'Switch Nodes'),
    'video': ('jake_node_video', 'Video Nodes')
}

def load_modules():
    """根据配置动态加载模块"""
    loaded_modules = []
    
    # 构建导入命令字符串
    import_commands = []
    
    # 如果没有指定模块，默认加载所有
    if not ENABLED_MODULES:
        # print("🔶 Loading all main modules.")
        for module_key, (module_file, module_name) in MODULE_MAPPING.items():
            import_commands.append(f"from .nodes.{module_file} import *")
            loaded_modules.append(module_key)
    else:
        # 加载指定的模块
        # print("🔶 Loading specified main modules.")
        for module_key in ENABLED_MODULES:
            if module_key in MODULE_MAPPING:
                module_file, module_name = MODULE_MAPPING[module_key]
                # print(f"🔶 Attempting to import: {module_file}") 
                import_commands.append(f"from .nodes.{module_file} import *")
                loaded_modules.append(module_key)
            else:
                print(f"⚠️ Unknown module: {module_key}")
    
    # 一次性执行所有导入命令
    if import_commands:
        try:
            import_statement = "\n".join(import_commands)
            exec(import_statement, globals())
            if not ENABLED_MODULES:
                print("🔶 All main modules loaded")
            else:
                print(f"🔶 Loaded modules: {', '.join(loaded_modules) if loaded_modules else 'None'}")
        except ImportError as e:
            print(f"❌ Failed to load modules: {e}")
    
    return loaded_modules

# 加载模块
loaded_modules = load_modules()

if LOAD_DEPRECATED_NODES:
    try:
        from .nodes.jake_node_deprecated import *
        print("🔶 All deprecated nodes loaded")
    except ImportError as e:
        print(f"❌ Failed to load deprecated nodes: {e}")
else:
    print("🔶 No deprecated nodes loaded")

# 根据实际加载的模块动态创建节点映射
def create_node_mappings() -> Dict[str, Type[Any]]:
    """创建节点映射字典"""
    node_mappings = {}
    
    # 使用全局符号表来检查已导入的类
    global_symbols = globals()
    
    # 使用lambda函数延迟求值
    module_mappings = {    
        ### 3D Nodes
        '3d': lambda: {
            "Orbit Poses JK": lambda: global_symbols.get("OrbitPoses_JK"),
            "OrbitLists to OrbitPoses JK": lambda: global_symbols.get("OrbitLists_to_OrbitPoses_JK"),
            "OrbitPoses to OrbitLists JK": lambda: global_symbols.get("OrbitPoses_to_OrbitLists_JK"),
            "Get OrbitPoses From List JK": lambda: global_symbols.get("Get_OrbitPoses_From_List_JK"),
        },
        ### Audio Nodes
        'audio': lambda: {
            "Scene Cuts JK": lambda: global_symbols.get("SceneCuts_JK"),
            "Cut Audio JK": lambda: global_symbols.get("CutAudio_JK"),
            "Cut Audio Index JK": lambda: global_symbols.get("CutAudioIndex_JK"),
            "Cut Audio Cuts JK": lambda: global_symbols.get("CutAudioCuts_JK"),
            "Cut Audio Loop JK": lambda: global_symbols.get("CutAudioLoop_JK"),
        },
        ### ControlNet Nodes
        'controlnet': lambda: {
            "CR ControlNet Loader JK": lambda: global_symbols.get("CR_ControlNetLoader_JK"),
            "CR Multi-ControlNet Param Stack JK": lambda: global_symbols.get("CR_ControlNetParamStack_JK"),
            "CR Apply ControlNet JK": lambda: global_symbols.get("CR_ApplyControlNet_JK"),
            "CR Apply Multi-ControlNet Adv JK": lambda: global_symbols.get("CR_ApplyControlNetStackAdv_JK"),
        },
        ### LoRA Nodes
        'lora': lambda: {
            "CR LoRA Stack JK": lambda: global_symbols.get("CR_LoRAStack_JK"),
            "CR Apply LoRA Stack JK": lambda: global_symbols.get("CR_ApplyLoRAStack_JK"),
            "CR LoRA Stack Model Only JK": lambda: global_symbols.get("CR_LoRAStack_ModelOnly_JK"),
            "CR Apply LoRA Stack Model Only JK": lambda: global_symbols.get("CR_ApplyLoRAStack_ModelOnly_JK"),
        },
        ### Experimental Nodes
        'experimental': lambda: {
            "Random Beats JK": lambda: global_symbols.get("RandomBeats_JK"),
        },
        ### Image Nodes
        'image': lambda: {
            "Rough Outline JK": lambda: global_symbols.get("RoughOutline_JK"),
            "OpenDWPose_JK": lambda: global_symbols.get("OpenDWPose_JK"),
            "Make Image Grid JK": lambda: global_symbols.get("MakeImageGrid_JK"),
            "Split Image Grid JK": lambda: global_symbols.get("SplitImageGrid_JK"),
            "Image Remove Alpha JK": lambda: global_symbols.get("ImageRemoveAlpha_JK"),
            "Color Grading JK": lambda: global_symbols.get("ColorGrading_JK"),
            "Get Size JK": lambda: global_symbols.get("GetSize_JK"),
            "Image Crop By Mask Resolution Grp JK": lambda: global_symbols.get("ImageCropByMaskResolutionGrp_JK"),
            "Image Crop by Mask Params JK": lambda: global_symbols.get("ImageCropByMaskParams_JK"),
            "Scale To Resolution JK": lambda: global_symbols.get("ScaleToResolution_JK"),
            "HintImageEnchance JK": lambda: global_symbols.get("HintImageEnchance_JK"),
        },
        ### Latent Nodes
        'latent': lambda: {
            "Empty Latent Color JK": lambda: global_symbols.get("EmptyLatentColor_JK"),
            "Latent Crop Offset JK": lambda: global_symbols.get("LatentCropOffset_JK"),
        },
        ### Mask Nodes
        'mask': lambda: {
            "Is Mask Empty JK": lambda: global_symbols.get("IsMaskEmpty_JK"),
        },
        ### Math Nodes
        'math': lambda: {
            "CM_BoolToInt JK": lambda: global_symbols.get("BoolToInt_JK"),
            "CM_IntToBool JK": lambda: global_symbols.get("IntToBool_JK"),
            "CM_BoolUnaryOperation JK": lambda: global_symbols.get("BoolUnaryOperation_JK"),
            "CM_BoolBinaryOperation JK": lambda: global_symbols.get("BoolBinaryOperation_JK"),
            "Bool Binary And JK": lambda: global_symbols.get("BoolBinaryAnd_JK"),
            "Bool Binary OR JK": lambda: global_symbols.get("BoolBinaryOR_JK"),
            "CM_StringBinaryCondition_JK": lambda: global_symbols.get("StringBinaryCondition_JK"),
            "CM_FloatUnaryCondition JK": lambda: global_symbols.get("FloatUnaryCondition_JK"),
            "CM_FloatBinaryCondition JK": lambda: global_symbols.get("FloatBinaryCondition_JK"),
            "CM_IntUnaryCondition JK": lambda: global_symbols.get("IntUnaryCondition_JK"),
            "CM_IntBinaryCondition JK": lambda: global_symbols.get("IntBinaryCondition_JK"),
            "CM_FloatToInt JK": lambda: global_symbols.get("FloatToInt_JK"),
            "CM_IntToFloat JK": lambda: global_symbols.get("IntToFloat_JK"),
            "CM_FloatUnaryOperation JK": lambda: global_symbols.get("FloatUnaryOperation_JK"),
            "CM_FloatBinaryOperation JK": lambda: global_symbols.get("FloatBinaryOperation_JK"),
            "CM_IntUnaryOperation JK": lambda: global_symbols.get("IntUnaryOperation_JK"),
            "CM_IntBinaryOperation JK": lambda: global_symbols.get("IntBinaryOperation_JK"),
            "Int Sub Operation JK": lambda: global_symbols.get("IntSubOperation_JK"),
            "Evaluate Ints JK": lambda: global_symbols.get("EvaluateInts_JK"),
            "Evaluate Floats JK": lambda: global_symbols.get("EvaluateFloats_JK"),
            "Evaluate Strings JK": lambda: global_symbols.get("EvaluateStrs_JK"),
            "Evaluate Examples JK": lambda: global_symbols.get("EvalExamples_JK"),
        },
        ### Misc Nodes
        'misc': lambda: {
            "Project Setting JK": lambda: global_symbols.get("ProjectSetting_JK"),
            "Ksampler Parameters Default JK": lambda: global_symbols.get("KsamplerParametersDefault_JK"),
            "Ksampler Adv Parameters Default JK": lambda: global_symbols.get("KsamplerAdvParametersDefault_JK"),
            "Base Model Parameters SD3API JK": lambda: global_symbols.get("BaseModelParametersSD3API_JK"),
            "Inject Noise Params JK": lambda: global_symbols.get("Inject_Noise_Params_JK"),
            "SD3 Prompts Switch JK": lambda: global_symbols.get("SD3_Prompts_Switch_JK"),
            "SDXL Target Res JK": lambda: global_symbols.get("SDXL_TargetRes_JK"),
            "Guidance Default JK": lambda: global_symbols.get("GuidanceDefault_JK"),
            "Image Resize Mode JK": lambda: global_symbols.get("ImageResizeMode_JK"),
            "Sampler Loader JK": lambda: global_symbols.get("SamplerLoader_JK"),
            "Upscale Method JK": lambda: global_symbols.get("UpscaleMethod_JK"),
            "CR Aspect Ratio JK": lambda: global_symbols.get("CR_AspectRatio_JK"),
            "String To Combo JK": lambda: global_symbols.get("StringToCombo_JK"),
            "Get Nth String JK": lambda: global_symbols.get("GetNthString_JK"),
            "Save String List To JSON JK": lambda: global_symbols.get("SaveStringListToJSON_JK"),
            "Load String List From JSON JK": lambda: global_symbols.get("LoadStringListFromJSON_JK"),
            "Tiling Mode JK": lambda: global_symbols.get("TilingMode_JK"),
            "Remove Input JK": lambda: global_symbols.get("RemoveInput_JK"),
        },
        ### Prompt Nodes
        'prompt': lambda: {
            "RandomPrompter_JK": lambda: global_symbols.get("RandomPrompter_JK"),
            "RandomPrompterGeek_JK": lambda: global_symbols.get("RandomPrompterGeek_JK"),
            "CM_PromptCombine_JK": lambda: global_symbols.get("PromptCombine_JK"),
            "SystemPrompter_JK": lambda: global_symbols.get("SystemPrompter_JK"),
            "ShotScriptExtractor_JK": lambda: global_symbols.get("ShotScriptExtractor_JK"),
            "ShotScriptCombiner_JK": lambda: global_symbols.get("ShotScriptCombiner_JK"),
        },
        ### Switch Nodes
        'switch': lambda: {
            "CR Boolean JK": lambda: global_symbols.get("CR_Boolean_JK"),
            "CR Int Input Switch JK": lambda: global_symbols.get("CR_IntInputSwitch_JK"),
            "CR Float Input Switch JK": lambda: global_symbols.get("CR_FloatInputSwitch_JK"),
            "CR Image Input Switch JK": lambda: global_symbols.get("CR_ImageInputSwitch_JK"),
            "CR Mask Input Switch JK": lambda: global_symbols.get("CR_MaskInputSwitch_JK"),
            "CR Latent Input Switch JK": lambda: global_symbols.get("CR_LatentInputSwitch_JK"),
            "CR Conditioning Input Switch JK": lambda: global_symbols.get("CR_ConditioningInputSwitch_JK"),
            "CR Clip Input Switch JK": lambda: global_symbols.get("CR_ClipInputSwitch_JK"),
            "CR Model Input Switch JK": lambda: global_symbols.get("CR_ModelInputSwitch_JK"),
            "CR ControlNet Input Switch JK": lambda: global_symbols.get("CR_ControlNetInputSwitch_JK"),
            "CR ControlNet Stack Input Switch JK": lambda: global_symbols.get("CR_ControlNetStackInputSwitch_JK"),
            "CR Text Input Switch JK": lambda: global_symbols.get("CR_TextInputSwitch_JK"),
            "CR VAE Input Switch JK": lambda: global_symbols.get("CR_VAEInputSwitch_JK"),
            "CR Noise Input Switch JK": lambda: global_symbols.get("CR_NoiseInputSwitch_JK"),
            "CR Guider Input Switch JK": lambda: global_symbols.get("CR_GuiderInputSwitch_JK"),
            "CR Sampler Input Switch JK": lambda: global_symbols.get("CR_SamplerInputSwitch_JK"),
            "CR Sigmas Input Switch JK": lambda: global_symbols.get("CR_SigmasInputSwitch_JK"),
            "CR Mesh Input Switch JK": lambda: global_symbols.get("CR_MeshInputSwitch_JK"),
            "CR Ply Input Switch JK": lambda: global_symbols.get("CR_PlyInputSwitch_JK"),
            "CR Orbit Pose Input Switch JK": lambda: global_symbols.get("CR_OrbitPoseInputSwitch_JK"),
            "CR TriMesh Input Switch JK": lambda: global_symbols.get("CR_TriMeshInputSwitch_JK"),
            "CR Impact Pipe Input Switch JK": lambda: global_symbols.get("CR_ImpactPipeInputSwitch_JK"),
        },
        ### Video Nodes
        'video': lambda: {
            "Create Loop Schedule List": lambda: global_symbols.get("CreateLoopScheduleList"),
            "Wan Frame Count JK": lambda: global_symbols.get("WanFrameCount_JK"),
            "Wan22 cfg Scheduler List JK": lambda: global_symbols.get("Wan22cfgSchedulerList_JK"),
            "Wan Wrapper Sampler Default JK": lambda: global_symbols.get("WanWrapperSamplerDefault_JK"),
        }
    }
    
    # 高效处理：根据是否指定模块选择不同策略
    if not ENABLED_MODULES:
        # 加载所有模块
        for module_key, node_dict_func in module_mappings.items():
            node_dict = node_dict_func()  # 调用lambda函数获取字典
            for display_name, class_func in node_dict.items():
                node_class = class_func()  # 调用lambda函数获取类
                if node_class is not None and isinstance(node_class, type):
                    node_mappings[display_name] = node_class
                    # print(f"✅ Found node: {display_name}")
                else:
                    print(f"⚠️ Node class not found: {display_name}")
    else:
        # 只加载指定模块
        for module_key in ENABLED_MODULES:
            if module_key in module_mappings:
                node_dict_func = module_mappings[module_key]
                node_dict = node_dict_func()  # 调用lambda函数获取字典
                for display_name, class_func in node_dict.items():
                    node_class = class_func()  # 调用lambda函数获取类
                    if node_class is not None and isinstance(node_class, type):
                        node_mappings[display_name] = node_class
                        # print(f"✅ Found node: {display_name}")
                    else:
                        print(f"⚠️ Node class not found: {display_name}")
    
    return node_mappings

def create_deprecated_node_mappings() -> Dict[str, Type[Any]]:
    """创建已弃用节点映射字典"""
    return {
        ### 3D Nodes [Deprecated]
        "Hy3D Cam Config 20to21 JK": Hy3DCamConfig20to21_JK,
        ### Animation Nodes [Deprecated]
        "Animation Prompt JK": AnimPrompt_JK,
        "Animation Value JK": AnimValue_JK,
        ### ControlNet Nodes [Deprecated]
        "CR Multi-ControlNet Stack JK": CR_ControlNetStack_JK,
        "CR Apply Multi-ControlNet JK": CR_ApplyControlNetStack_JK,
        ### Embedding Nodes [Deprecated]
        "Embedding Picker JK": EmbeddingPicker_JK,
        "Embedding Picker Multi JK": EmbeddingPicker_Multi_JK,
        ### Image Nodes [Deprecated]
        "Image Crop by Mask Resolution JK": ImageCropByMaskResolution_JK,
        ### Loader Nodes [Deprecated]
        "Ckpt Loader JK": CkptLoader_JK,
        "Vae Loader JK": VaeLoader_JK,
        "Upscale Model Loader JK": UpscaleModelLoader_JK,
        ### LoRA Nodes [Deprecated]
        "CR Load LoRA JK": CR_LoraLoader_JK,
        ### Math Nodes [Deprecated]
        "CM_NumberUnaryCondition JK": NumberUnaryCondition_JK,
        "CM_NumberBinaryCondition JK": NumberBinaryCondition_JK,
        "CM_Vec2UnaryCondition JK": Vec2UnaryCondition_JK,
        "CM_Vec2BinaryCondition JK": Vec2BinaryCondition_JK,
        "CM_Vec2ToFloatUnaryOperation JK": Vec2ToFloatUnaryOperation_JK,
        "CM_Vec2ToFloatBinaryOperation JK": Vec2ToFloatBinaryOperation_JK,
        "CM_Vec2FloatOperation_JK": Vec2FloatOperation_JK,
        "CM_Vec3UnaryCondition JK": Vec3UnaryCondition_JK,
        "CM_Vec3BinaryCondition JK": Vec3BinaryCondition_JK,
        "CM_Vec3ToFloatUnaryOperation JK": Vec3ToFloatUnaryOperation_JK,
        "CM_Vec3ToFloatBinaryOperation JK": Vec3ToFloatBinaryOperation_JK,
        "CM_Vec3FloatOperation_JK": Vec3FloatOperation_JK,
        "CM_Vec4UnaryCondition JK": Vec4UnaryCondition_JK,
        "CM_Vec4BinaryCondition JK": Vec4BinaryCondition_JK,
        "CM_Vec4ToFloatUnaryOperation JK": Vec4ToFloatUnaryOperation_JK,
        "CM_Vec4ToFloatBinaryOperation JK": Vec4ToFloatBinaryOperation_JK,
        "CM_Vec4FloatOperation_JK": Vec4FloatOperation_JK,
        "CM_IntToNumber JK": IntToNumber_JK,
        "CM_NumberToInt JK": NumberToInt_JK,
        "CM_FloatToNumber JK": FloatToNumber_JK,
        "CM_NumberToFloat JK": NumberToFloat_JK,
        "CM_NumberUnaryOperation JK": NumberUnaryOperation_JK,
        "CM_NumberBinaryOperation JK": NumberBinaryOperation_JK,
        "CM_ComposeVec2 JK": ComposeVec2_JK,
        "CM_ComposeVec3 JK": ComposeVec3_JK,
        "CM_ComposeVec4 JK": ComposeVec4_JK,
        "CM_BreakoutVec2 JK": BreakoutVec2_JK,
        "CM_BreakoutVec3 JK": BreakoutVec3_JK,
        "CM_BreakoutVec4 JK": BreakoutVec4_JK,
        "CM_FillVec2 JK": FillVec2_JK,
        "CM_FillVec3 JK": FillVec3_JK,
        "CM_FillVec4 JK": FillVec4_JK,
        "CM_Vec2UnaryOperation JK": Vec2UnaryOperation_JK,
        "CM_Vec2BinaryOperation JK": Vec2BinaryOperation_JK,
        "CM_Vec3UnaryOperation JK": Vec3UnaryOperation_JK,
        "CM_Vec3BinaryOperation JK": Vec3BinaryOperation_JK,
        "CM_Vec4UnaryOperation JK": Vec4UnaryOperation_JK,
        "CM_Vec4BinaryOperation JK": Vec4BinaryOperation_JK,
        ### Misc Nodes [Deprecated]
        "CR SD1.5 Aspect Ratio JK": CR_AspectRatioSD15_JK,
        "CR SDXL Aspect Ratio JK": CR_AspectRatioSDXL_JK,
        "CR SD3 Aspect Ratio JK": CR_AspectRatioSD3_JK,
        ### Pipe Nodes [Deprecated]
        "Pipe End JK": PipeEnd_JK,
        "NodesState JK": NodesState_JK,
        "Ksampler Parameters JK": KsamplerParameters_JK,
        "Base Model Parameters JK": BaseModelParameters_JK,
        "Base Model Parameters Extract JK": BaseModelParametersExtract_JK,
        "Base Image Parameters Extract JK": BaseImageParametersExtract_JK,
        "Base Model Pipe JK": BaseModelPipe_JK,
        "Base Model Pipe Extract JK": BaseModelPipeExtract_JK,
        "Noise Injection Parameters JK": NoiseInjectionParameters_JK,
        "Noise Injection Pipe Extract JK": NoiseInjectionPipeExtract_JK,
        "Refine Model Parameters JK": RefineModelParameters_JK,
        "Refine 1 Parameters Extract JK": Refine1ParametersExtract_JK,
        "Refine 2 Parameters Extract JK": Refine2ParametersExtract_JK,
        "Refine Pipe JK": RefinePipe_JK,
        "Refine Pipe Extract JK": RefinePipeExtract_JK,
        "Upscale Model Parameters JK": UpscaleModelParameters_JK,
        "Image Upscale Parameters Extract JK": ImageUpscaleParametersExtract_JK,
        "Latent Upscale Parameters Extract JK": LatentUpscaleParametersExtract_JK,
        "Upscale Model Parameters Extract JK": UpscaleModelParametersExtract_JK,
        "Detailer Parameters JK": DetailerParameters_JK,
        "Metadata Pipe JK": MetadataPipe_JK,
        "Metadata Pipe Extract JK": MetadataPipeExtract_JK,
        "Save Image with Metadata JK": ImageSaveWithMetadata_JK,
        "Save Image with Metadata Flow JK": ImageSaveWithMetadata_Flow_JK,
        "Load Image With Metadata JK": LoadImageWithMetadata_JK,
        "Load Image With Alpha JK": LoadImageWithAlpha_JK,
        ### Reroute Nodes [Deprecated]
        "Reroute List JK": RerouteList_JK,
        "Reroute Ckpt JK": RerouteCkpt_JK,
        "Reroute Vae JK": RerouteVae_JK,
        "Reroute Sampler JK": RerouteSampler_JK,
        "Reroute Upscale JK": RerouteUpscale_JK,
        "Reroute Resize JK": RerouteResize_JK,
        "Reroute String JK": RerouteString_JK,
        ### Switch Nodes [Deprecated]
        "CR Pipe Input Switch JK": CR_PipeInputSwitch_JK,
    }

def filter_valid_mappings(mappings: Dict[str, Type[Any]]) -> Dict[str, Type[Any]]:
    """过滤掉None值（未成功导入的类）"""
    return {k: v for k, v in mappings.items() if v is not None}

def add_dragon_emoji(name: str) -> str:
    """为节点名称添加龙表情符号"""
    # 使用正则表达式移除 CR 或 CM_ 前缀
    name = re.sub(r'^(CR |CM_)', '', name)
    # 将下划线替换为空格
    name = name.replace('_', ' ')
    # 在符合"小写英文字母+大写英文字母+小写英文字母"模式的大写字母前添加空格
    name = re.sub(r'(?<=[a-z])([A-Z])(?=[a-z])', r' \1', name)
    return f"{name}🐉"

# 构建主节点映射
node_mappings = create_node_mappings()
valid_node_mappings = filter_valid_mappings(node_mappings)

NODE_CLASS_MAPPINGS.update(valid_node_mappings)
NODE_DISPLAY_NAME_MAPPINGS.update({k: add_dragon_emoji(k) for k in NODE_CLASS_MAPPINGS.keys()})

# 处理已弃用节点
if LOAD_DEPRECATED_NODES:
    deprecated_node_mappings = create_deprecated_node_mappings()
    valid_deprecated_node_mappings = filter_valid_mappings(deprecated_node_mappings)
    
    NODE_CLASS_MAPPINGS.update(valid_deprecated_node_mappings)
    NODE_DISPLAY_NAME_MAPPINGS.update({k: add_dragon_emoji(k) for k in valid_deprecated_node_mappings.keys()})

# 导出配置
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 加载统计
active_nodes_count = len(NODE_CLASS_MAPPINGS)

print(f"🔶 Total nodes: {active_nodes_count}")
print("--------------------------------------------------------------")
