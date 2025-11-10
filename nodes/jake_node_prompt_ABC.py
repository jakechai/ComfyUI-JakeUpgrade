import random
import json
import os
import re
import configparser
from functools import lru_cache
from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# 配置类
#---------------------------------------------------------------------------------------------------------------------#
def load_random_prompter_config():
    """从 config.ini 加载 RandomPrompter 配置"""
    config = configparser.ConfigParser()
    
    # 获取配置文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config.ini')
    
    # 默认配置
    default_config = {
        'PROMPT_DATA_DIR': "prompt_data",
        'RANDOM_EMPTY_PROB': 0.10,
        'CUSTOM_FIELD_PROB': 0.05,
        'EXP_STR_RANDOM_PROB': 0.80,
        'STRUCTURED_SELECT_PROB': 0.50,
        'REF_IMAGE_COUNT': 3,
        'EXCLUSION_MARK': 900
    }
    
    # 默认目录映射
    default_directory_mapping = {
        "scene": "scenes",
        "motion": "motions",
        "facial_action": "facial_actions",
        "exp_str": "exp_strs",
        "expression": "expressions",
        "lighting": "lightings",
        "camera": "cameras",
        "style": "styles",
        "style_artist": "1-artists",
        "style_form": "2-forms",
        "description": "descriptions"
    }
    
    # 如果配置文件存在，读取它
    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
            
            # 读取基本配置
            for key in default_config:
                if key in config['RandomPrompterConfig']:
                    value = config['RandomPrompterConfig'][key]
                    if key in ['RANDOM_EMPTY_PROB', 'CUSTOM_FIELD_PROB', 'EXP_STR_RANDOM_PROB', 'STRUCTURED_SELECT_PROB']:
                        default_config[key] = float(value)
                    elif key in ['REF_IMAGE_COUNT', 'EXCLUSION_MARK']:
                        default_config[key] = int(value)
                    else:
                        default_config[key] = value
            
            # 读取目录映射配置
            directory_mapping = {}
            for internal_name in default_directory_mapping:
                config_key = f"DIRECTORY_MAPPING_{internal_name}"
                if config_key in config['RandomPrompterConfig']:
                    directory_mapping[internal_name] = config['RandomPrompterConfig'][config_key]
                else:
                    directory_mapping[internal_name] = default_directory_mapping[internal_name]
                    
        except Exception as e:
            print(f"❌ RandomPrompter config read error: {e}")
            directory_mapping = default_directory_mapping
    else:
        print("⚠️ RandomPrompter config file not found, using defaults")
        directory_mapping = default_directory_mapping
    
    return default_config, directory_mapping

# 加载配置
prompter_config, directory_mapping = load_random_prompter_config()

class PromptConfig:
    """配置管理类"""
    PROMPT_DATA_DIR = prompter_config['PROMPT_DATA_DIR']
    
    DIRECTORY_MAPPING = directory_mapping
    
    # 概率参数配置
    RANDOM_EMPTY_PROB = prompter_config['RANDOM_EMPTY_PROB']
    CUSTOM_FIELD_PROB = prompter_config['CUSTOM_FIELD_PROB']
    EXP_STR_RANDOM_PROB = prompter_config['EXP_STR_RANDOM_PROB']
    STRUCTURED_SELECT_PROB = prompter_config['STRUCTURED_SELECT_PROB']
    
    # 参考图像参数
    REF_IMAGE_COUNT = prompter_config['REF_IMAGE_COUNT']
    
    # 随机计算时排除的文件记号
    EXCLUSION_MARK = prompter_config['EXCLUSION_MARK']
    
    # 图像类型映射
    IMAGE_TYPE_MAPPING = {
        "scene": "scene",
        "motion": "character pose", 
        "facial_action": "character face action",
        "expression": "character face expression",
        "lighting": "lighting",
        "camera": "view angle",
        "style": "style"
    }
    
    # Geek 版本专用配置
    GEEK_SELECT_OPTION = "select"
    GEEK_CATEGORY_FORMAT = "[{category_name}]"
    
    # 一级菜单选项
    PRIMARY_CATEGORIES = [
        DIRECTORY_MAPPING["scene"], 
        DIRECTORY_MAPPING["motion"], 
        DIRECTORY_MAPPING["facial_action"], 
        DIRECTORY_MAPPING["expression"], 
        DIRECTORY_MAPPING["lighting"], 
        DIRECTORY_MAPPING["camera"], 
        DIRECTORY_MAPPING["style"], 
        DIRECTORY_MAPPING["description"]
    ]
    
    # 二级菜单选项（style 的子分类）- 使用实际的目录名称
    STYLE_SUBCATEGORIES = [
        DIRECTORY_MAPPING["style_artist"], 
        DIRECTORY_MAPPING["style_form"]
    ]
    
    # 支持的文件格式
    SUPPORTED_FORMATS = {
        '.txt': 'Text', 
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.csv': 'CSV'
    }
    
    # 格式优先级
    PREFERRED_FORMATS = ['.txt', '.json', '.yaml', '.yml', '.toml', '.csv']

class DependencyManager:
    """依赖管理类"""
    
    @staticmethod
    def check_dependencies():
        """检查可选依赖的可用性"""
        dependencies = {
            'yaml': False,
            'toml': False,
            'csv': True  # csv是标准库
        }
        
        try:
            import yaml
            dependencies['yaml'] = True
        except ImportError:
            print("Warning: PyYAML not available, YAML files will be skipped")
        
        try:
            import toml
            dependencies['toml'] = True
        except ImportError:
            print("Warning: TOML library not available, TOML files will be skipped")
        
        return dependencies
    
    @staticmethod
    def get_available_formats():
        """获取可用的文件格式"""
        deps = DependencyManager.check_dependencies()
        available_formats = ['.json', '.txt', '.csv']  # 始终可用的格式
        
        if deps['yaml']:
            available_formats.extend(['.yaml', '.yml'])
        if deps['toml']:
            available_formats.append('.toml')
        
        return {
            'available': available_formats,
            'dependencies': deps
        }

class DataCleaner:
    """数据清理工具类"""
    
    @staticmethod
    def clean_and_deduplicate(data_list: List[Any]) -> List[str]:
        """统一的清理和去重逻辑"""
        if not data_list:
            return []
        
        # 确保所有元素为字符串并去除前后空格
        cleaned = [str(item).strip() for item in data_list if str(item).strip()]
        # 去重但保持顺序
        return list(dict.fromkeys(cleaned))
    
    @staticmethod
    def clean_prompt_string(text: str) -> str:
        """清理提示词字符串"""
        if not text:
            return ""
        
        # 合并处理连续逗号
        text = re.sub(r',(\s*,)+', ',', text)
        
        # 标准化空白和逗号格式
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*,\s*', ', ', text)
        
        # 清理边界
        text = text.strip(', .')
        
        return text.strip()
    
    @staticmethod
    def remove_category_prefix(value: str) -> str:
        """移除类别前缀，返回原始值"""
        if not value or value in ["enable", "disable", "random"]:
            return value
        
        # 查找最后一个路径分隔符，取后面的内容
        last_separator = value.rfind(os.path.sep)
        if last_separator != -1:
            return value[last_separator + 1:]
        
        # 同时检查反斜杠（兼容旧数据）
        last_backslash = value.rfind('\\')
        if last_backslash != -1:
            return value[last_backslash + 1:]
        
        return value

class FileLoader:
    """文件加载器"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def load_data_file(file_path: str) -> List[str]:
        """统一的数据文件加载器，支持多种格式（带缓存）"""
        full_path = os.path.join(os.path.dirname(__file__), PromptConfig.PROMPT_DATA_DIR, file_path)
        
        # 添加调试信息
        # print(f"Debug: Trying to load file from {full_path}")
        # print(f"Debug: File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            print(f"Warning: File not found at {full_path}")
            return []
        
        ext = os.path.splitext(full_path)[1].lower()
        
        try:
            if ext == '.json':
                result = FileLoader._load_json(full_path)
            elif ext == '.txt':
                result = FileLoader._load_txt(full_path)
            elif ext == '.csv':
                result = FileLoader._load_csv(full_path)
            elif ext in ['.yaml', '.yml']:
                result = FileLoader._load_yaml(full_path)
            elif ext == '.toml':
                result = FileLoader._load_toml(full_path)
            else:
                print(f"Warning: Unsupported file format {ext}, trying as text file")
                result = FileLoader._load_txt(full_path)
            
            return result
                
        except Exception as e:
            print(f"Error loading {full_path}: {e}")
            return []
    
    @staticmethod
    def _load_txt(file_path: str) -> List[str]:
        """加载TXT文件"""
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                lines = []
                for line in f:
                    stripped = line.strip()
                    # 跳过空行和注释行
                    if stripped and not stripped.startswith('#'):
                        lines.append(stripped)
                return DataCleaner.clean_and_deduplicate(lines)
        except Exception as e:
            print(f"Error reading TXT file {file_path}: {e}")
            return []
    
    @staticmethod
    def _load_json(file_path: str) -> List[str]:
        """加载JSON文件"""
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                
            # 确保返回列表格式
            if isinstance(data, list):
                return DataCleaner.clean_and_deduplicate(data)
            elif isinstance(data, dict):
                # 如果是字典，提取所有值
                all_values = []
                for value in data.values():
                    if isinstance(value, list):
                        all_values.extend(value)
                    else:
                        all_values.append(value)
                return DataCleaner.clean_and_deduplicate(all_values)
            else:
                print(f"Warning: JSON file {file_path} has unsupported structure")
                return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Error reading JSON file {file_path}: {e}")
            return []
    
    @staticmethod
    def _load_yaml(file_path: str) -> List[str]:
        """加载YAML文件"""
        try:
            import yaml
        except ImportError:
            print("Warning: PyYAML not installed, cannot load YAML files")
            return []
            
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if isinstance(data, list):
                    all_values = [str(item).strip() for item in data if str(item).strip()]
                    return DataCleaner.clean_and_deduplicate(all_values)
                elif isinstance(data, dict):
                    # 处理YAML字典格式
                    all_values = []
                    for value in data.values():
                        if isinstance(value, list):
                            all_values.extend(value)
                        else:
                            all_values.append(value)
                    return DataCleaner.clean_and_deduplicate(all_values)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    # 如果不是标准的YAML结构，按文本文件处理
                    return [line.strip() for line in content.split('\n') if line.strip()]
        except Exception as e:
            print(f"Error reading YAML file {file_path}: {e}")
            return []
    
    @staticmethod
    def _load_toml(file_path: str) -> List[str]:
        """加载TOML文件"""
        try:
            import toml
        except ImportError:
            print("Warning: TOML library not installed, cannot load TOML files")
            return []
            
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = toml.load(f)
                
                # TOML通常以字典形式组织
                all_values = []
                for value in data.values():
                    if isinstance(value, list):
                        all_values.extend(value)
                    else:
                        all_values.append(value)
                
                return DataCleaner.clean_and_deduplicate(all_values)
        except Exception as e:
            print(f"Error reading TOML file {file_path}: {e}")
            return []
    
    @staticmethod
    def _load_csv(file_path: str) -> List[str]:
        """加载CSV文件"""
        try:
            import csv
            lines = []
            with open(file_path, "r", encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # 跳过空行
                        # 取第一列非空值
                        first_col = row[0].strip() if row[0].strip() else None
                        if first_col and not first_col.startswith('#'):  # 跳过注释
                            lines.append(first_col)
            return DataCleaner.clean_and_deduplicate(lines)
        except ImportError:
            print("Warning: CSV module not available, falling back to text parsing")
            return FileLoader._load_txt(file_path)
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {e}")
            return []

class DirectoryWalker:
    """目录遍历器"""
    
    @staticmethod
    def _walk_category_directory(category_dir: str, exclusion: any = "") -> List[Tuple[str, str, bool]]:
        """
        公共目录遍历函数 - 修复文件路径问题
        """
        base_dir = os.path.join(os.path.dirname(__file__), PromptConfig.PROMPT_DATA_DIR)
        dir_path = os.path.join(base_dir, category_dir)
        
        if not os.path.exists(dir_path):
            print(f"Warning: Directory not found at {dir_path}")
            return []
        
        entries_list = []
        
        def _process_directory(current_dir: str, current_prefix: str = "", parent_has_multiple: bool = False):
            """递归处理目录"""
            # 获取目录下所有条目
            entries = []
            for entry in os.listdir(current_dir):
                if entry.startswith('.'):
                    continue
                
                # 排除逻辑
                skip_entry = False
                if exclusion:
                    if isinstance(exclusion, int) and exclusion > 0:
                        match = re.match(r'^(\d+)-', entry)
                        if match:
                            entry_number = int(match.group(1))
                            if entry_number >= exclusion:
                                skip_entry = True
                    elif isinstance(exclusion, str) and exclusion:
                        if entry.startswith(exclusion):
                            skip_entry = True
                
                if not skip_entry:
                    entries.append(entry)
            
            # 按数字前缀排序
            entries.sort(key=lambda x: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', x)])
            
            # 统计当前目录下的文件和子目录数量
            file_count = 0
            subdir_count = 0
            
            for entry in entries:
                entry_path = os.path.join(current_dir, entry)
                if os.path.isdir(entry_path):
                    subdir_count += 1
                elif any(entry.endswith(ext) for ext in PromptConfig.SUPPORTED_FORMATS.keys()):
                    file_count += 1
            
            # 判断当前目录是否需要添加前缀
            should_add_prefix = (subdir_count > 0 or file_count > 1 or parent_has_multiple)
            
            for entry in entries:
                entry_path = os.path.join(current_dir, entry)
                
                if os.path.isdir(entry_path):
                    # 处理子目录
                    subdir_name = os.path.splitext(entry)[0]
                    # 移除数字前缀
                    if '-' in subdir_name:
                        subdir_name = subdir_name.split('-', 1)[1]
                    
                    new_prefix = f"{current_prefix}{os.path.sep}{subdir_name}" if current_prefix else subdir_name
                    _process_directory(entry_path, new_prefix, should_add_prefix or len(entries) > 1)
                    
                elif any(entry.endswith(ext) for ext in PromptConfig.SUPPORTED_FORMATS.keys()):
                    # 处理支持的文件格式 - 修复：构建正确的文件路径
                    category_name = os.path.splitext(entry)[0]
                    # 移除数字前缀
                    if '-' in category_name:
                        category_name = category_name.split('-', 1)[1]
                    
                    # 构建完整前缀
                    if current_prefix and should_add_prefix:
                        full_prefix = f"{current_prefix}{os.path.sep}{category_name}"
                    elif should_add_prefix:
                        full_prefix = category_name
                    else:
                        full_prefix = ""  # 不需要前缀
                    
                    # 修复：构建相对于 base_dir 的正确路径
                    file_relative_path = os.path.relpath(entry_path, base_dir)
                    # 确保使用正确的路径分隔符
                    file_relative_path = os.path.normpath(file_relative_path)
                    
                    entries_list.append((file_relative_path, full_prefix, should_add_prefix))
        
        # 开始处理目录
        _process_directory(dir_path)
        
        return entries_list

class DataManager:
    """数据管理器"""
    
    @staticmethod
    def load_category_options(category_dir: str) -> List[str]:
        """扁平化版本 - 使用公共遍历函数"""
        all_options = []
        entries = DirectoryWalker._walk_category_directory(category_dir)
        
        for file_relative_path, prefix, should_add_prefix in entries:
            options = FileLoader.load_data_file(file_relative_path)
            
            # 根据是否需要添加前缀来处理选项
            if should_add_prefix and prefix:
                # 需要添加前缀
                prefixed_options = [f"{prefix}{os.path.sep}{option}" for option in options]
                all_options.extend(prefixed_options)
            else:
                # 不需要添加前缀，直接使用原始选项
                all_options.extend(options)
        
        return all_options
    
    @staticmethod
    def load_structured_category_options(category_dir: str, exclusion: any = "") -> List[Dict[str, Any]]:
        """结构化版本 - 使用公共遍历函数"""
        
        structured_options = []
        entries = DirectoryWalker._walk_category_directory(category_dir, exclusion)
        
        for file_relative_path, prefix, should_add_prefix in entries:
            options = FileLoader.load_data_file(file_relative_path)
            
            structured_option = {
                'file': os.path.basename(file_relative_path),
                'file_relative_path': file_relative_path,  # 存储完整相对路径
                'category': prefix,
                'should_add_prefix': should_add_prefix,
                'options': options
            }
            structured_options.append(structured_option)
            
        return structured_options
    
    @staticmethod
    def load_geek_category_options(category_dir: str, is_primary: bool = False) -> List[str]:
        """为 Geek 版本生成分类选项 - 统一版本"""
        options = [PromptConfig.GEEK_SELECT_OPTION]
        
        # 获取分类条目
        entries = DirectoryWalker._walk_category_directory(category_dir, PromptConfig.EXCLUSION_MARK)
        
        # 收集所有分类名称并按照数字顺序排序
        category_entries = []
        for file_relative_path, prefix, should_add_prefix in entries:
            if should_add_prefix and prefix:
                # 对于需要前缀的情况，使用前缀作为分类名
                category_name = prefix
            else:
                # 不需要前缀，使用文件名作为分类名
                file_name = os.path.splitext(os.path.basename(file_relative_path))[0]
                # 移除数字前缀
                if '-' in file_name:
                    file_name = file_name.split('-', 1)[1]
                category_name = file_name
            
            # 获取原始文件名用于排序
            original_file_name = os.path.splitext(os.path.basename(file_relative_path))[0]
            category_entries.append((original_file_name, category_name))
        
        # 按照数字前缀排序
        def extract_number(name):
            if '-' in name:
                try:
                    return int(name.split('-')[0])
                except ValueError:
                    return 9999
            return 9999
        
        category_entries.sort(key=lambda x: extract_number(x[0]))
        
        # 添加排序后的分类到选项
        for original_name, category_name in category_entries:
            options.append(category_name)
        
        # 如果是主要分类，添加"all + 分类名"作为选项
        if is_primary:
            # 获取分类显示名称
            category_name = os.path.basename(category_dir)
            # 清理分类名称（移除数字前缀）
            if '-' in category_name:
                category_name = category_name.split('-', 1)[1]
            # 添加 "all " 前缀
            options.append(f"all {category_name}")
        
        return options
    
    @staticmethod
    def load_geek_style_options() -> List[str]:
        """为 Geek 版本生成样式选项（包含子分类）- 统一使用目录名方式"""
        # 获取 style 目录名
        style_dir = PromptConfig.DIRECTORY_MAPPING["style"]
        
        # 使用统一的 load_geek_category_options 方法获取基础选项
        options = DataManager.load_geek_category_options(style_dir, is_primary=True)
        
        # 添加 style 子分类的 "all" 选项
        for subcategory in PromptConfig.STYLE_SUBCATEGORIES:
            # 获取子分类的显示名称
            subcategory_display_name = subcategory
            if '-' in subcategory_display_name:
                subcategory_display_name = subcategory_display_name.split('-', 1)[1]
            
            # 添加 "all artist" 和 "all vision"
            all_subcategory_option = f"all {subcategory_display_name}"
            if all_subcategory_option not in options:
                options.append(all_subcategory_option)
        
        return options

    @staticmethod
    def build_category_mapping() -> Dict[str, List[str]]:
        """构建分类名称到文件路径的映射表 - 确保与选项生成逻辑一致"""
        mapping = {}
        
        # 处理所有主要分类
        for category_dir in PromptConfig.PRIMARY_CATEGORIES:
            entries = DirectoryWalker._walk_category_directory(category_dir, PromptConfig.EXCLUSION_MARK)
            
            # 获取显示名称（与 load_geek_category_options 保持一致）
            category_name = os.path.basename(category_dir)
            # 清理分类名称（移除数字前缀）
            if '-' in category_name:
                category_name = category_name.split('-', 1)[1]
            
            # 为 "all + 分类名" 添加映射
            mapping_key = f"all {category_name}"
            mapping[mapping_key] = []
            
            for file_relative_path, prefix, should_add_prefix in entries:
                mapping[mapping_key].append(file_relative_path)
                
                # 确定具体分类名称（与 load_geek_category_options 保持一致）
                if should_add_prefix and prefix:
                    # 清理前缀中的数字和路径分隔符
                    clean_prefix = prefix
                    if os.path.sep in clean_prefix:
                        parts = clean_prefix.split(os.path.sep)
                        cleaned_parts = []
                        for part in parts:
                            if '-' in part:
                                cleaned_parts.append(part.split('-', 1)[1])
                            else:
                                cleaned_parts.append(part)
                        clean_prefix = os.path.sep.join(cleaned_parts)
                    elif '-' in clean_prefix:
                        clean_prefix = clean_prefix.split('-', 1)[1]
                    
                    category_name_for_mapping = clean_prefix
                else:
                    file_name = os.path.splitext(os.path.basename(file_relative_path))[0]
                    if '-' in file_name:
                        file_name = file_name.split('-', 1)[1]
                    category_name_for_mapping = file_name
                
                # 添加到映射表
                if category_name_for_mapping not in mapping:
                    mapping[category_name_for_mapping] = []
                mapping[category_name_for_mapping].append(file_relative_path)
        
        # 处理 style 子分类的特殊映射（保持不变）
        for subcategory in PromptConfig.STYLE_SUBCATEGORIES:
            subcategory_path = os.path.join(PromptConfig.DIRECTORY_MAPPING["style"], subcategory)
            entries = DirectoryWalker._walk_category_directory(subcategory_path, PromptConfig.EXCLUSION_MARK)
            
            # 清理子分类显示名称
            subcategory_display_name = subcategory
            if '-' in subcategory_display_name:
                subcategory_display_name = subcategory_display_name.split('-', 1)[1]
            
            # 为 "all artist" 和 "all vision" 添加映射
            mapping[f"all {subcategory_display_name}"] = []
            
            for file_relative_path, prefix, should_add_prefix in entries:
                mapping[f"all {subcategory_display_name}"].append(file_relative_path)
                
                if should_add_prefix and prefix:
                    clean_prefix = prefix
                    if '-' in clean_prefix:
                        clean_prefix = clean_prefix.split('-', 1)[1]
                    
                    # 为子分类创建映射键
                    geek_category_name = f"{subcategory_display_name}{os.path.sep}{clean_prefix}"
                    
                    if geek_category_name not in mapping:
                        mapping[geek_category_name] = []
                    mapping[geek_category_name].append(file_relative_path)
                else:
                    file_name = os.path.splitext(os.path.basename(file_relative_path))[0]
                    if '-' in file_name:
                        file_name = file_name.split('-', 1)[1]
                    
                    geek_category_name = f"{subcategory_display_name}{os.path.sep}{file_name}"
                    
                    if geek_category_name not in mapping:
                        mapping[geek_category_name] = []
                    mapping[geek_category_name].append(file_relative_path)
        
        # 添加 expression strength 映射
        exp_str_files = DirectoryWalker._walk_category_directory(
            PromptConfig.DIRECTORY_MAPPING["exp_str"], PromptConfig.EXCLUSION_MARK
        )
        if exp_str_files:
            mapping["expression strength"] = [entry[0] for entry in exp_str_files]
        
        return mapping

# 预加载分类数据（使用缓存）
@lru_cache(maxsize=1)
def load_all_data():
    """预加载所有数据"""
    
    data = {
        # RandomPrompter_JK的数据
        'SCENE_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["scene"]),
        'SCENE_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["scene"], PromptConfig.EXCLUSION_MARK),
        'MOTION_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["motion"]),
        'MOTION_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["motion"], PromptConfig.EXCLUSION_MARK),
        'FACIAL_ACTION_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["facial_action"]),
        'FACIAL_ACTION_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["facial_action"], PromptConfig.EXCLUSION_MARK),
        'EXPRESSION_STR': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["exp_str"]),
        'EXPRESSION_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["expression"]),
        'EXPRESSION_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["expression"], PromptConfig.EXCLUSION_MARK),
        'LIGHTING_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["lighting"]),
        'LIGHTING_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["lighting"], PromptConfig.EXCLUSION_MARK),
        'CAMERA_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["camera"]),
        'CAMERA_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["camera"], PromptConfig.EXCLUSION_MARK),
        'STYLE_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["style"]),
        'STYLE_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["style"], PromptConfig.EXCLUSION_MARK),
        'DESCRIPTION_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["description"]),
        'DESCRIPTION_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["description"], PromptConfig.EXCLUSION_MARK),
        
        # Geek 版本新增数据 - 为每个主要分类添加 is_primary=True
        'SCENE_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["scene"], is_primary=True),
        'MOTION_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["motion"], is_primary=True),
        'FACIAL_ACTION_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["facial_action"], is_primary=True),
        'EXPRESSION_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["expression"], is_primary=True),
        'LIGHTING_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["lighting"], is_primary=True),
        'CAMERA_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["camera"], is_primary=True),
        'STYLE_CATEGORIES': DataManager.load_geek_style_options(),
        'DESCRIPTION_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["description"], is_primary=True),
        
        # 用于运行时替换的映射表
        'CATEGORY_MAPPING': DataManager.build_category_mapping()
    }
    
    return data

# 全局数据缓存
_DATA_CACHE = None

def get_data_cache():
    """获取数据缓存"""
    global _DATA_CACHE
    if _DATA_CACHE is None:
        _DATA_CACHE = load_all_data()
    return _DATA_CACHE

#---------------------------------------------------------------------------------------------------------------------#
# 工具类
#---------------------------------------------------------------------------------------------------------------------#
class PromptUtils:
    """提示词工具类"""
    
    @staticmethod
    def smart_join(elements: List[str], separator: str = ", ") -> str:
        """智能连接元素"""
        return separator.join(filter(None, elements))
    
    @staticmethod
    def generate_image_based_options(ref_count: int) -> List[str]:
        """生成图像选项"""
        base_options = ["enable", "disable", "random"]
        image_options = [f"use image {i+1}" for i in range(ref_count)]
        return base_options + image_options

class ExpressionUtils:
    """Expression 组合工具类 - 纯逻辑，无状态"""
    
    @staticmethod
    def combine_expression(
        exp_str_value: str, 
        expression_value: str,
        rng: random.Random,
        exp_str_options: List[str] = None,
        exp_str_prob: float = PromptConfig.EXP_STR_RANDOM_PROB
    ) -> str:
        """
        统一的 expression 组合逻辑
        可以被任何策略或生成器使用
        
        Args:
            exp_str_value: 指定的 exp_str 值
            expression_value: expression 内容
            rng: 随机数生成器
            exp_str_options: exp_str 选项列表（用于随机选择）
            exp_str_prob: 使用 exp_str 的概率
            
        Returns:
            组合后的 expression 字符串
        """
        # 如果 expression 为空，直接返回空
        if not expression_value or not expression_value.strip():
            return ""
        
        # 清理 expression 值
        cleaned_expression = DataCleaner.clean_prompt_string(expression_value)
        if not cleaned_expression:
            return ""
        
        # 处理 exp_str
        final_exp_str = ""
        
        # 如果有指定的 exp_str_value，使用它
        if exp_str_value and exp_str_value.strip():
            final_exp_str = DataCleaner.clean_prompt_string(exp_str_value)
        # 否则根据概率随机选择
        elif exp_str_options and rng.random() < exp_str_prob:
            final_exp_str = rng.choice(exp_str_options)
            final_exp_str = DataCleaner.clean_prompt_string(final_exp_str)
        
        # 组合结果
        if final_exp_str and cleaned_expression:
            return f"{final_exp_str} {cleaned_expression}"
        else:
            return cleaned_expression
    
    @staticmethod
    def should_include_exp_str(rng: random.Random, prob: float = PromptConfig.EXP_STR_RANDOM_PROB) -> bool:
        """判断是否应该包含 exp_str"""
        return rng.random() < prob
    
    @staticmethod
    def select_random_exp_str(exp_str_options: List[str], rng: random.Random) -> str:
        """随机选择 exp_str"""
        if not exp_str_options:
            return ""
        selected = rng.choice(exp_str_options)
        return DataCleaner.clean_prompt_string(selected)
    
    @staticmethod
    def process_expression_option(
        choice: str, 
        custom_value: str, 
        rng: random.Random,
        exp_str_options: List[str] = None,
        generate_func = None
    ) -> str:
        """
        处理 expression 选项的通用逻辑
        
        Args:
            choice: 用户选择的选项（disable/random/具体选项）
            custom_value: 自定义值
            rng: 随机数生成器
            exp_str_options: exp_str 选项列表
            generate_func: 生成 expression 的函数
            
        Returns:
            处理后的 expression 字符串
        """
        if choice.lower() == "disable":
            return ""
        
        elif choice.lower() == "random":
            # 几率使用 custom_value 的内容
            if custom_value and custom_value.strip() and rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
                return DataCleaner.clean_prompt_string(custom_value)
            
            # 使用随机组合
            exp_str_value = ""
            if ExpressionUtils.should_include_exp_str(rng):
                exp_str_value = ExpressionUtils.select_random_exp_str(exp_str_options, rng)
            
            # 生成随机 expression
            random_expression = generate_func("") if generate_func else ""
            
            return ExpressionUtils.combine_expression(
                exp_str_value, random_expression, rng, exp_str_options
            )
        
        else:
            # 具体选项，使用 custom_value
            if custom_value and custom_value.strip():
                return DataCleaner.clean_prompt_string(custom_value)
            return ""

#---------------------------------------------------------------------------------------------------------------------#
# 策略类
#---------------------------------------------------------------------------------------------------------------------#
class PromptGenerationStrategy(ABC):
    """提示词生成策略抽象基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    def generate(self, context: Dict[str, Any]) -> str:
        """生成提示词组件"""
        pass
    
    @abstractmethod
    def get_strategy_type(self) -> str:
        """返回策略类型标识"""
        pass
    
    def _should_generate_empty(self, rng: random.Random) -> bool:
        """判断是否应该生成空内容"""
        return rng.random() < self.config.get("random_empty_prob", PromptConfig.RANDOM_EMPTY_PROB)
    
    def _should_use_custom_value(self, custom_value: str, rng: random.Random) -> bool:
        """判断是否应该使用自定义值"""
        return (custom_value and custom_value.strip() and 
                rng.random() < self.config.get("custom_field_prob", PromptConfig.CUSTOM_FIELD_PROB))

class SingleFileRandomStrategy(PromptGenerationStrategy):
    """单文件随机策略 - 用于 motion, lighting, style 等"""
    
    def generate(self, context: Dict[str, Any]) -> str:
        rng = context.get('rng')
        file_paths = context.get('file_paths', [])
        custom_value = context.get('custom_value', '')
        category_name = context.get('category_name', '')
        
        # 几率为空
        if self._should_generate_empty(rng):
            return ""
        
        # 几率使用自定义值
        if self._should_use_custom_value(custom_value, rng):
            return DataCleaner.clean_prompt_string(custom_value)
        
        if not file_paths:
            return ""
        
        # 随机选择一个文件
        selected_file = rng.choice(file_paths)
        options = FileLoader.load_data_file(selected_file)
        
        if not options:
            return ""
        
        # 从选中的文件中随机选择一条
        choice = rng.choice(options)
        clean_choice = DataCleaner.remove_category_prefix(choice)
        
        return DataCleaner.clean_prompt_string(clean_choice)
    
    def get_strategy_type(self) -> str:
        return "single_file_random"

class MultipleFilesRandomStrategy(PromptGenerationStrategy):
    """多文件随机策略 - 用于 scene, facial_action, camera 等"""
    
    def generate(self, context: Dict[str, Any]) -> str:
        rng = context.get('rng')
        file_paths = context.get('file_paths', [])
        custom_value = context.get('custom_value', '')
        category_name = context.get('category_name', '')
        
        # 几率为空
        if self._should_generate_empty(rng):
            return ""
        
        # 几率使用自定义值
        if self._should_use_custom_value(custom_value, rng):
            return DataCleaner.clean_prompt_string(custom_value)
        
        if not file_paths:
            return ""
        
        parts = []
        structured_select_prob = self.config.get("structured_select_prob", PromptConfig.STRUCTURED_SELECT_PROB)
        
        # 所有文件几率选择，选择上的文件随机挑选一条，并按顺序组合
        for file_path in file_paths:
            options = FileLoader.load_data_file(file_path)
            if options and rng.random() < structured_select_prob:
                choice = rng.choice(options)
                clean_choice = DataCleaner.remove_category_prefix(choice)
                parts.append(clean_choice)
        
        # 清理每个部分，避免多余的分隔符
        cleaned_parts = [DataCleaner.clean_prompt_string(part) for part in parts]
        
        return PromptUtils.smart_join(cleaned_parts)
    
    def get_strategy_type(self) -> str:
        return "multiple_files_random"

class ExpressionCombinationStrategy(PromptGenerationStrategy):
    """表达式组合策略 - 专门处理 expression + exp_str 的组合"""
    
    def generate(self, context: Dict[str, Any]) -> str:
        rng = context.get('rng')
        file_paths = context.get('file_paths', [])
        custom_value = context.get('custom_value', '')
        data_cache = context.get('data_cache', {})
        
        # 几率为空
        if self._should_generate_empty(rng):
            return ""
        
        # 获取 exp_str 选项
        exp_str_options = data_cache.get('EXPRESSION_STR', [])
        
        # 几率使用自定义值
        if self._should_use_custom_value(custom_value, rng):
            # 对于自定义值，也应用 exp_str 组合
            exp_str_value = ""
            if ExpressionUtils.should_include_exp_str(rng):
                exp_str_value = ExpressionUtils.select_random_exp_str(exp_str_options, rng)
            
            return ExpressionUtils.combine_expression(
                exp_str_value, custom_value, rng, exp_str_options
            )
        
        if not file_paths:
            return ""
        
        # 构建结构化选项格式（模拟 PromptComponentGenerator 的输入）
        structured_options = []
        for file_path in file_paths:
            options = FileLoader.load_data_file(file_path)
            if options:
                structured_option = {
                    'file': os.path.basename(file_path),
                    'category': PromptConfig.DIRECTORY_MAPPING["expression"],
                    'should_add_prefix': True,
                    'options': options
                }
                structured_options.append(structured_option)
        
        # 生成随机 expression（使用单文件策略）
        expression_value = ""
        if structured_options:
            selected_category = rng.choice(structured_options)
            if selected_category['options']:
                choice = rng.choice(selected_category['options'])
                expression_value = DataCleaner.remove_category_prefix(choice)
        
        if not expression_value:
            return ""
        
        # 使用 ExpressionUtils 进行组合
        exp_str_value = ""
        if ExpressionUtils.should_include_exp_str(rng):
            exp_str_value = ExpressionUtils.select_random_exp_str(exp_str_options, rng)
        
        return ExpressionUtils.combine_expression(
            exp_str_value, expression_value, rng, exp_str_options
        )
    
    def get_strategy_type(self) -> str:
        return "expression_combination"

class TagReplacementStrategy(PromptGenerationStrategy):
    """标记替换策略 - 用于 Geek 版本的 [category_name] 替换"""
    
    def generate(self, context: Dict[str, Any]) -> str:
        """
        替换模板中的分类标记为随机内容
        
        Args:
            context: 包含以下键的字典：
                - prompt_template: 包含标记的模板字符串
                - category_mapping: 分类名称到文件路径的映射
                - rng: 随机数生成器
                - data_cache: 数据缓存
                
        Returns:
            替换后的提示词字符串
        """
        prompt_template = context.get('prompt_template', '')
        category_mapping = context.get('category_mapping', {})
        rng = context.get('rng')
        data_cache = context.get('data_cache', {})
        
        if not prompt_template:
            return ""
        
        # 正则表达式匹配 [category_name] 格式的标记
        pattern = r'\[([^\[\]]+)\]'
        
        def replace_match(match):
            category_name = match.group(1)
            return self._replace_single_tag(category_name, category_mapping, rng, data_cache)
        
        # 替换所有匹配的标记
        result = re.sub(pattern, replace_match, prompt_template)
        
        return DataCleaner.clean_prompt_string(result)
    
    def _replace_single_tag(self, category_name: str, category_mapping: Dict[str, List[str]], 
                           rng: random.Random, data_cache: Dict[str, Any]) -> str:
        """替换单个分类标记"""
        # 检查是否是有效的分类名称
        if category_name not in category_mapping:
            print(f"Warning: Category '{category_name}' not found in mapping")
            # 尝试在映射键中查找相似键（调试用）
            similar_keys = [k for k in category_mapping.keys() if category_name in k]
            if similar_keys:
                print(f"  Similar keys: {similar_keys[:5]}")
            return f"[{category_name}]"  # 返回原标记
        
        # 从分类对应的文件中获取文件路径
        file_paths = category_mapping[category_name]
        if not file_paths:
            print(f"Warning: No files found for category '{category_name}'")
            return f"[{category_name}]"
        
        # 处理 "all xxx" 选项 - 使用对应的随机策略
        if category_name.startswith("all "):
            return self._generate_for_all_category(category_name, file_paths, rng, data_cache)
        else:
            # 对于具体分类，检查是否为expression相关分类
            if self._is_expression_category(category_name, file_paths):
                return self._generate_expression_content(file_paths, rng, data_cache)
            else:
                # 对于非expression分类，使用默认的随机选择逻辑
                return self._generate_for_specific_category(category_name, file_paths, rng)
    
    def _is_expression_category(self, category_name: str, file_paths: List[str]) -> bool:
        """判断是否为expression相关分类"""
        expression_dir = PromptConfig.DIRECTORY_MAPPING["expression"]
        
        # 通过分类名称判断
        if expression_dir in category_name.lower():
            return True
        
        # 通过文件路径判断
        for file_path in file_paths:
            if expression_dir in file_path.lower():
                return True
        
        return False
    
    def _generate_expression_content(self, file_paths: List[str], rng: random.Random, 
                                   data_cache: Dict[str, Any]) -> str:
        """为所有expression分类生成内容，包含exp_str"""
        # 随机选择一个文件
        selected_file = rng.choice(file_paths)
        
        # 加载文件内容
        options = FileLoader.load_data_file(selected_file)
        if not options:
            print(f"Warning: No content found in file '{selected_file}' for expression category")
            return ""
        
        # 随机选择一条expression内容
        selected_expression = rng.choice(options)
        cleaned_expression = DataCleaner.remove_category_prefix(selected_expression)
        
        # 获取exp_str选项
        exp_str_options = data_cache.get('EXPRESSION_STR', [])
        
        # 使用ExpressionUtils进行组合
        exp_str_value = ""
        if ExpressionUtils.should_include_exp_str(rng):
            exp_str_value = ExpressionUtils.select_random_exp_str(exp_str_options, rng)
        
        return ExpressionUtils.combine_expression(
            exp_str_value, cleaned_expression, rng, exp_str_options
        )
    
    def _generate_for_all_category(self, category_name: str, file_paths: List[str], 
                                 rng: random.Random, data_cache: Dict[str, Any]) -> str:
        """为 'all xxx' 分类生成内容"""
        # 移除 "all " 前缀获取基础分类名
        base_category = category_name[4:]
        
        # 根据分类类型使用不同的策略
        if base_category == PromptConfig.DIRECTORY_MAPPING["expression"]:
            # 特殊处理 expression：需要包含 exp_str
            return self._generate_all_expression(file_paths, rng, data_cache)
        else:
            # 直接使用策略，避免创建新的上下文
            strategy_type = PromptStrategyFactory.get_strategy_for_category(base_category)
            strategy = PromptStrategyFactory.create_strategy(strategy_type)
            
            context_data = {
                'rng': rng,
                'file_paths': file_paths,
                'data_cache': data_cache,
                'custom_value': "",  # all 选项不使用自定义值
            }
            
            return strategy.generate(context_data)
    
    def _generate_for_specific_category(self, category_name: str, file_paths: List[str], 
                                      rng: random.Random) -> str:
        """为具体分类生成内容"""
        # 随机选择一个文件
        selected_file = rng.choice(file_paths)
        
        # 加载文件内容
        options = FileLoader.load_data_file(selected_file)
        if not options:
            print(f"Warning: No content found in file '{selected_file}' for category '{category_name}'")
            return f"[{category_name}]"
        
        # 随机选择一条内容
        selected_option = rng.choice(options)
        
        # 清理内容中的子分类前缀
        cleaned_option = DataCleaner.remove_category_prefix(selected_option)
        
        return DataCleaner.clean_prompt_string(cleaned_option)
    
    def _generate_all_expression(self, file_paths: List[str], rng: random.Random, 
                               data_cache: Dict[str, Any]) -> str:
        """特殊处理 all expression：包含 exp_str 前缀"""
        # 创建表达式组合策略
        expression_strategy = ExpressionCombinationStrategy()
        
        context_data = {
            'rng': rng,
            'file_paths': file_paths,
            'data_cache': data_cache,
            'custom_value': ""
        }
        
        return expression_strategy.generate(context_data)
    
    def get_strategy_type(self) -> str:
        return "tag_replacement"

class PromptStrategyFactory:
    """提示词策略工厂"""
    
    # 策略类型映射 - 更新以包含 TagReplacementStrategy
    STRATEGY_MAP = {
        "single_file_random": SingleFileRandomStrategy,
        "multiple_files_random": MultipleFilesRandomStrategy,
        "expression_combination": ExpressionCombinationStrategy,
        "tag_replacement": TagReplacementStrategy,
    }
    
    # 分类到策略的映射 - 保持不变
    CATEGORY_STRATEGY_MAP = {
        "scene": "multiple_files_random",
        "motion": "single_file_random", 
        "facial_action": "multiple_files_random",
        "expression": "expression_combination",
        "lighting": "single_file_random",
        "camera": "multiple_files_random",
        "style": "single_file_random",
        "artist": "single_file_random",  # style 子分类
        "vision": "single_file_random",  # style 子分类
    }
    
    @staticmethod
    def create_strategy(strategy_type: str, config: Dict[str, Any] = None) -> PromptGenerationStrategy:
        """根据类型创建策略实例"""
        strategy_class = PromptStrategyFactory.STRATEGY_MAP.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"未知的策略类型: {strategy_type}")
        
        return strategy_class(config) if config else strategy_class()
    
    @staticmethod
    def get_strategy_for_category(category_name: str, is_all_option: bool = False) -> str:
        """根据分类名称和选项类型返回推荐的策略类型"""
        # 移除 "all " 前缀（如果存在）
        base_category = category_name[4:] if category_name.startswith("all ") else category_name
        
        return PromptStrategyFactory.CATEGORY_STRATEGY_MAP.get(
            base_category, "single_file_random"
        )

#---------------------------------------------------------------------------------------------------------------------#
# 上下文类
#---------------------------------------------------------------------------------------------------------------------#
class PromptGenerationContext:
    """提示词生成上下文 - 统一管理生成参数和策略"""
    
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
        self.data_cache = get_data_cache()
        self.strategies: Dict[str, PromptGenerationStrategy] = {}
        
        # 配置参数
        self.config = {
            "random_empty_prob": PromptConfig.RANDOM_EMPTY_PROB,
            "custom_field_prob": PromptConfig.CUSTOM_FIELD_PROB,
            "structured_select_prob": PromptConfig.STRUCTURED_SELECT_PROB,
            "exp_str_random_prob": PromptConfig.EXP_STR_RANDOM_PROB,
        }
    
    def set_strategy(self, strategy_type: str, strategy: PromptGenerationStrategy):
        """设置策略"""
        self.strategies[strategy_type] = strategy
    
    def get_strategy(self, strategy_type: str) -> PromptGenerationStrategy:
        """获取策略，如果不存在则创建"""
        if strategy_type not in self.strategies:
            strategy = PromptStrategyFactory.create_strategy(strategy_type, self.config)
            self.set_strategy(strategy_type, strategy)
        return self.strategies[strategy_type]
    
    def generate_with_strategy(self, strategy_type: str, context_data: Dict[str, Any]) -> str:
        """使用指定策略生成内容"""
        strategy = self.get_strategy(strategy_type)
        
        # 注入公共上下文
        context_data.update({
            "rng": self.rng,
            "data_cache": self.data_cache,
            "config": self.config
        })
        
        return strategy.generate(context_data)
    
    def generate_for_category(self, category_name: str, file_paths: List[str], 
                            custom_value: str = "") -> str:
        """为指定分类生成内容"""
        strategy_type = PromptStrategyFactory.get_strategy_for_category(category_name)
        
        context_data = {
            "category_name": category_name,
            "file_paths": file_paths,
            "custom_value": custom_value,
        }
        
        return self.generate_with_strategy(strategy_type, context_data)
    
    def generate_for_all_category(self, category_name: str, file_paths: List[str]) -> str:
        """为 'all xxx' 分类生成内容"""
        # 移除 "all " 前缀获取基础分类名
        base_category = category_name[4:] if category_name.startswith("all ") else category_name
        strategy_type = PromptStrategyFactory.get_strategy_for_category(base_category)
        
        context_data = {
            "category_name": base_category,
            "file_paths": file_paths,
            "custom_value": "",  # all 选项不使用自定义值
        }
        
        return self.generate_with_strategy(strategy_type, context_data)

#---------------------------------------------------------------------------------------------------------------------#
# 生成器类
#---------------------------------------------------------------------------------------------------------------------#
class PromptComponentGenerator:
    """提示词组件生成器"""
    
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.data_cache = get_data_cache()
    
    def _generate_from_multiple_files(self, structured_options: List[Dict], custom_value: str, category_name: str = "") -> str:
        """
        通用函数1：从多个文件中按概率选择，每个选中的文件随机挑选一条，并按顺序组合
        适用于：scene, facial_action, camera
        """
        # 几率为空
        if self.rng.random() < PromptConfig.RANDOM_EMPTY_PROB:
            return ""
        
        # 几率使用custom_value的内容
        if custom_value and custom_value.strip() and self.rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
            return DataCleaner.clean_prompt_string(custom_value)
        
        if not structured_options:
            return ""
        
        parts = []
        
        # 所有文件几率选择，选择上的文件随机挑选一条，并按顺序组合
        for category in structured_options:
            if category['options'] and self.rng.random() < PromptConfig.STRUCTURED_SELECT_PROB:
                choice = self.rng.choice(category['options'])
                # 如果该类别不需要添加前缀，那么choice已经是原始值
                if category.get('should_add_prefix', True):
                    clean_choice = DataCleaner.remove_category_prefix(choice)
                else:
                    clean_choice = choice
                parts.append(clean_choice)
        
        # 清理每个部分，避免多余的分隔符
        cleaned_parts = [DataCleaner.clean_prompt_string(part) for part in parts]
        
        return PromptUtils.smart_join(cleaned_parts)
    
    def _generate_from_single_file(self, structured_options: List[Dict], custom_value: str, category_name: str = "") -> str:
        """
        通用函数2：从所有文件中只选一个文件，再从这个文件中随机挑选一条
        适用于：motion, expression, lighting, style
        """
        
        # 几率为空
        if self.rng.random() < PromptConfig.RANDOM_EMPTY_PROB:
            return ""
        
        # 几率使用custom_value的内容
        if custom_value and custom_value.strip() and self.rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
            return DataCleaner.clean_prompt_string(custom_value)
        
        if not structured_options:
            return ""
        
        # 修复：确保有可用的选项
        available_categories = [cat for cat in structured_options if cat.get('options')]
        if not available_categories:
            print(f"Warning: No available {category_name} categories with options")
            return ""
        
        # 随机选择一个文件
        selected_category = self.rng.choice(available_categories)
        
        if selected_category['options']:
            # 从选中的文件中随机选择一条
            choice = self.rng.choice(selected_category['options'])
            # 如果该类别不需要添加前缀，那么choice已经是原始值
            if selected_category.get('should_add_prefix', True):
                clean_choice = DataCleaner.remove_category_prefix(choice)
            else:
                clean_choice = choice
            
            result = DataCleaner.clean_prompt_string(clean_choice)
            
            if not result and category_name == "style":
                print(f"Warning: Empty result for style selection from {selected_category.get('file', 'unknown')}")
            
            return result
        
        return ""
    
    def generate_scene(self, custom_scene_value: str) -> str:
        """生成随机scene内容"""
        return self._generate_from_multiple_files(
            self.data_cache['SCENE_STRUCTURED_OPTIONS'], custom_scene_value, PromptConfig.DIRECTORY_MAPPING["scene"]
        )
    
    def generate_motion(self, custom_motion_value: str) -> str:
        """生成随机motion内容"""
        return self._generate_from_single_file(
            self.data_cache['MOTION_STRUCTURED_OPTIONS'], custom_motion_value, PromptConfig.DIRECTORY_MAPPING["motion"]
        )
    
    def generate_facial_action(self, custom_facial_action_value: str) -> str:
        """生成随机facial_action内容"""
        return self._generate_from_multiple_files(
            self.data_cache['FACIAL_ACTION_STRUCTURED_OPTIONS'], custom_facial_action_value, PromptConfig.DIRECTORY_MAPPING["facial_action"]
        )
    
    def generate_expression(self, custom_expression_value: str) -> str:
        """生成随机expression内容"""
        return self._generate_from_single_file(
            self.data_cache['EXPRESSION_STRUCTURED_OPTIONS'], custom_expression_value, PromptConfig.DIRECTORY_MAPPING["expression"]
        )
    
    def generate_lighting(self, custom_lighting_value: str) -> str:
        """生成随机lighting内容"""
        return self._generate_from_single_file(
            self.data_cache['LIGHTING_STRUCTURED_OPTIONS'], custom_lighting_value, PromptConfig.DIRECTORY_MAPPING["lighting"]
        )
    
    def generate_camera(self, custom_camera_value: str) -> str:
        """生成随机camera内容"""
        return self._generate_from_multiple_files(
            self.data_cache['CAMERA_STRUCTURED_OPTIONS'], custom_camera_value, PromptConfig.DIRECTORY_MAPPING["camera"]
        )
    
    def generate_style(self, custom_style_value: str) -> str:
        """生成随机style内容"""
        return self._generate_from_single_file(
            self.data_cache['STYLE_STRUCTURED_OPTIONS'], custom_style_value, "style"
        )
    
    def generate_exp_str(self) -> str:
        """生成随机exp_str内容"""
        if not self.data_cache['EXPRESSION_STR']:
            return ""
        
        # 几率选择exp_str
        if self.rng.random() < PromptConfig.EXP_STR_RANDOM_PROB:
            # 随机选择一条
            choice = self.rng.choice(self.data_cache['EXPRESSION_STR'])
            return DataCleaner.remove_category_prefix(choice)
        
        return ""
    
    def generate_description(self, custom_description_value: str) -> str:
        """生成随机description内容"""
        # 几率为空
        if self.rng.random() < PromptConfig.RANDOM_EMPTY_PROB:
            return ""
        
        # 几率使用custom_description的内容
        if custom_description_value and custom_description_value.strip() and self.rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
            return DataCleaner.clean_prompt_string(custom_description_value)
        
        if not self.data_cache['DESCRIPTION_STRUCTURED_OPTIONS']:
            return ""
        
        # 按子类别分组
        description_parts = {
            'sensory': [],
            'detail': [], 
            'quality': [],
            'composition': [],
            'color': [],
            'creativity': []
        }
        
        # 将选项按子类别分组
        for category in self.data_cache['DESCRIPTION_STRUCTURED_OPTIONS']:
            category_name = category['category']
            if category_name in description_parts:
                for option in category['options']:
                    # 如果该类别不需要添加前缀，那么option已经是原始值
                    if category.get('should_add_prefix', True):
                        clean_value = DataCleaner.remove_category_prefix(option)
                    else:
                        clean_value = option
                    description_parts[category_name].append(clean_value)
        
        # 从每个子类别中随机选择一条
        selected_parts = {}
        for category, options in description_parts.items():
            if options:
                selected_parts[category] = self.rng.choice(options)
        
        # 按规定的格式组合
        sensory = selected_parts.get('sensory', 'masterpiece')
        detail = selected_parts.get('detail', 'insane detail')
        quality = selected_parts.get('quality', 'best quality')
        composition = selected_parts.get('composition', 'masterfully balanced composition')
        color = selected_parts.get('color', 'harmonious colors')
        creativity = selected_parts.get('creativity', 'groundbreaking concept')
        
        return f"A {sensory} of work with {detail} and {quality}, featuring a {composition} and {color}, presenting a {creativity}"

class PromptGenerator:
    """主提示词生成器 - 使用策略模式重构"""
    
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.context_manager = PromptGenerationContext(seed)
        self.data_cache = get_data_cache()
        
        # 保留原有的组件生成器用于兼容性
        self.component_generator = PromptComponentGenerator(self.rng)
    
    def _process_category_with_strategy(self, choice: str, custom_value: str, category_name: str, 
                                      file_paths: List[str], strategy_type: str) -> str:
        """使用策略处理分类选项 - 修复版本"""
        if choice.lower() == "disable":
            return ""
        elif choice.lower() == "enable":
            if custom_value and custom_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_value)
                if cleaned_value:
                    return cleaned_value
        elif choice.lower() == "random":
            # 修复：使用传入的 file_paths（来自 category_mapping）
            if file_paths:
                return self.context_manager.generate_with_strategy(
                    strategy_type, 
                    {
                        "category_name": category_name,
                        "file_paths": file_paths,
                        "custom_value": custom_value,
                    }
                )
            
            # 回退到组件生成器
            return getattr(self.component_generator, f'generate_{category_name}')(custom_value)
            
        elif choice.lower().startswith("use image "):
            if custom_value and custom_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_value)
                if cleaned_value:
                    return cleaned_value
            else:
                image_ref = self._get_image_ref_string(choice, category_name)
                if image_ref:
                    return image_ref
        elif choice.lower() not in ["disable", "random", "enable"]:
            if custom_value and custom_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_value)
                if cleaned_value:
                    return cleaned_value
            else:
                clean_value = DataCleaner.remove_category_prefix(choice)
                if clean_value:
                    return clean_value
        
        return ""
    
    def _get_expression_combination(self, exp_str_value: str, expression_value: str, custom_expression_value: str) -> str:
        """使用 ExpressionUtils 处理 exp_str 和 expression 的组合"""
        # 如果 expression 是 disable，不使用任何表情
        if expression_value.lower() == "disable":
            return ""
        
        # 获取 exp_str 选项
        exp_str_options = self.data_cache['EXPRESSION_STR']
        
        # 如果 expression 是 random，随机生成 expression 和 exp_str 的组合
        if expression_value.lower() == "random":
            # 几率使用 custom_expression 的内容
            if custom_expression_value and custom_expression_value.strip() and self.rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
                return ExpressionUtils.combine_expression(
                    "", custom_expression_value, self.rng, exp_str_options
                )
            
            # 使用 ExpressionUtils 进行组合
            exp_str_selected = ""
            if ExpressionUtils.should_include_exp_str(self.rng):
                exp_str_selected = ExpressionUtils.select_random_exp_str(exp_str_options, self.rng)
            
            # 生成随机 expression
            random_expression = self.component_generator.generate_expression("")
            
            return ExpressionUtils.combine_expression(
                exp_str_selected, random_expression, self.rng, exp_str_options
            )
        
        # 如果 expression 是具体选项，使用 custom_expression
        else:
            if custom_expression_value and custom_expression_value.strip():
                return ExpressionUtils.combine_expression(
                    exp_str_value, custom_expression_value, self.rng, exp_str_options
                )
            return ""
    
    def _get_image_ref_string(self, choice: str, category: str) -> str:
        """根据选择生成图像引用字符串"""
        match = re.match(r"use image (\d+)", choice.lower())
        if match:
            image_num = match.group(1)
            image_type = PromptConfig.IMAGE_TYPE_MAPPING.get(category, category)
            return f"use image {image_num} {image_type}"
        return ""
    
    def _arrange_components_by_priority(self, components_dict: Dict[str, str], priority: str) -> List[str]:
        """根据优先级设置安排组件顺序"""
        priority_orders = {
            "subject + scene": [
                "subject", "scene", "motion", "facial_action", "expression", 
                "lighting", "camera", "style", "description"
            ],
            "description + style": [
                "description", "style", "subject", "scene", "motion", 
                "facial_action", "expression", "lighting", "camera"
            ],
            "description + style + lighting + camera": [
                "description", "style", "lighting", "camera", "subject", 
                "scene", "motion", "facial_action", "expression"
            ],
            "lighting + camera": [
                "lighting", "camera", "subject", "scene", "motion", 
                "facial_action", "expression", "style", "description"
            ]
        }
        
        # 获取对应的顺序，如果找不到则使用默认顺序
        order = priority_orders.get(priority, priority_orders["subject + scene"])
        
        # 按照顺序提取组件，只保留有值的组件
        arranged_components = []
        for key in order:
            if key in components_dict and components_dict[key]:
                arranged_components.append(components_dict[key])
        
        return arranged_components
    
    def generate_prompt(self, **kwargs) -> str:
        """生成提示词 - 使用策略模式重构"""
        prompt_priority = kwargs.get("prompt_priority", "subject + scene")
        
        # 收集所有组件
        components_dict = {}
        
        # custom_subject - 总是使用
        custom_subject = kwargs.get("custom_subject", "")
        if custom_subject:
            cleaned_value = DataCleaner.clean_prompt_string(custom_subject)
            if cleaned_value:
                components_dict["subject"] = cleaned_value
        
        # 处理各个分类 - 使用策略模式
        categories_config = [
            ("scene", "custom_scene", "multiple_files_random"),
            ("motion", "custom_motion", "single_file_random"),
            ("facial_action", "custom_facial_action", "multiple_files_random"),
            ("lighting", "custom_lighting", "single_file_random"),
            ("camera", "custom_camera", "multiple_files_random"),
            ("style", "custom_style", "single_file_random"),
        ]
        
        for category_name, custom_field, strategy_type in categories_config:
            choice = kwargs.get(category_name, "disable")
            custom_value = kwargs.get(custom_field, "")
            
            # 修复：直接从数据缓存的结构化选项中获取文件路径
            data_cache = get_data_cache()
            structured_options_key = f"{category_name.upper()}_STRUCTURED_OPTIONS"
            
            file_paths = []
            if structured_options_key in data_cache:
                structured_options = data_cache[structured_options_key]
                # 直接使用存储的完整相对路径
                for category_data in structured_options:
                    file_relative_path = category_data.get('file_relative_path', '')
                    if file_relative_path:
                        file_paths.append(file_relative_path)
            
            result = self._process_category_with_strategy(
                choice, custom_value, category_name, file_paths, strategy_type
            )
            if result:
                components_dict[category_name] = result
        
        # 特殊处理 expression（使用 ExpressionUtils）
        expression_choice = kwargs.get("expression", "disable")
        custom_expression_value = kwargs.get("custom_expression", "")
        exp_str_value = kwargs.get("exp_str", "quite")
        
        expression_result = self._get_expression_combination(
            exp_str_value, expression_choice, custom_expression_value
        )
        if expression_result:
            components_dict["expression"] = expression_result
        
        # 特殊处理 description（保持原有逻辑）
        description_choice = kwargs.get("description", "disable")
        custom_description_value = kwargs.get("custom_description", "")
        
        if description_choice.lower() == "disable":
            pass
        elif description_choice.lower() == "enable":
            if custom_description_value and custom_description_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_description_value)
                if cleaned_value:
                    components_dict["description"] = cleaned_value
        elif description_choice.lower() == "random":
            random_description = self.component_generator.generate_description("")
            if random_description:
                components_dict["description"] = random_description
        else:
            if custom_description_value and custom_description_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_description_value)
                if cleaned_value:
                    components_dict["description"] = cleaned_value
            else:
                clean_value = DataCleaner.remove_category_prefix(description_choice)
                if clean_value:
                    components_dict["description"] = clean_value
        
        # 根据优先级设置组合组件
        components = self._arrange_components_by_priority(components_dict, prompt_priority)
        full_prompt_string = PromptUtils.smart_join(components, separator=", ")
        
        return full_prompt_string

class PromptGeneratorGeek:
    """Geek 版本提示词生成器 - 使用重构后的生成器"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self.context_manager = PromptGenerationContext(seed)
        self.data_cache = get_data_cache()
    
    def generate_prompt(self, custom_prompt: str, custom_subject: str) -> str:
        """生成 Geek 版本的提示词"""
        # 处理主题
        cleaned_subject = DataCleaner.clean_prompt_string(custom_subject) if custom_subject else ""
        
        # 使用 TagReplacementStrategy 替换分类标记
        final_prompt = self._replace_category_tags_with_strategy(custom_prompt)
        
        # 修复：使用 smart_join 组合主题和提示词，避免多余的逗号
        elements = []
        if cleaned_subject:
            elements.append(cleaned_subject)
        if final_prompt:
            elements.append(final_prompt)
        
        full_prompt = PromptUtils.smart_join(elements, separator=", ")
        
        return full_prompt
    
    def _replace_category_tags_with_strategy(self, prompt: str) -> str:
        """使用 TagReplacementStrategy 替换分类标记"""
        if not prompt:
            return ""
        
        # 创建标记替换策略
        tag_replacement_strategy = PromptStrategyFactory.create_strategy("tag_replacement")
        
        # 准备上下文数据
        context_data = {
            'prompt_template': prompt,
            'category_mapping': self.data_cache['CATEGORY_MAPPING'],
            'rng': self.context_manager.rng,
            'data_cache': self.data_cache
        }
        
        # 使用策略生成替换后的内容
        return tag_replacement_strategy.generate(context_data)

class UnifiedPromptGenerator:
    """统一提示词生成器 - 同时支持标准模式和 Geek 模式"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self.context_manager = PromptGenerationContext(seed)
        self.data_cache = get_data_cache()
        
        # 创建标准生成器
        self.standard_generator = PromptGenerator(seed)
        
        # 创建 Geek 生成器
        self.geek_generator = PromptGeneratorGeek(seed)
    
    def generate_standard_prompt(self, **kwargs) -> str:
        """生成标准模式提示词"""
        return self.standard_generator.generate_prompt(**kwargs)
    
    def generate_geek_prompt(self, custom_prompt: str, custom_subject: str = "") -> str:
        """生成 Geek 模式提示词"""
        return self.geek_generator.generate_prompt(custom_prompt, custom_subject)
    
    def generate_for_category(self, category_name: str, file_paths: List[str], 
                            custom_value: str = "") -> str:
        """为指定分类生成内容（通用方法）"""
        return self.context_manager.generate_for_category(category_name, file_paths, custom_value)
    
    def generate_for_all_category(self, category_name: str, file_paths: List[str]) -> str:
        """为 'all xxx' 分类生成内容"""
        return self.context_manager.generate_for_all_category(category_name, file_paths)
    
    def replace_category_tags(self, prompt_template: str) -> str:
        """替换模板中的分类标记"""
        tag_replacement_strategy = PromptStrategyFactory.create_strategy("tag_replacement")
        
        context_data = {
            'prompt_template': prompt_template,
            'category_mapping': self.data_cache['CATEGORY_MAPPING'],
            'rng': self.context_manager.rng,
            'data_cache': self.data_cache
        }
        
        return tag_replacement_strategy.generate(context_data)

#---------------------------------------------------------------------------------------------------------------------#
# 节点类
#---------------------------------------------------------------------------------------------------------------------#
class RandomPrompter_JK:
    """ComfyUI 节点类 - 使用重构后的 PromptGenerator"""
    
    # 使用动态生成的图像选项
    IMAGE_BASED_OPTIONS = PromptUtils.generate_image_based_options(PromptConfig.REF_IMAGE_COUNT)
    
    @classmethod
    def INPUT_TYPES(cls):
        # 优先级选项
        priority_options = [
            "subject + scene", 
            "description + style", 
            "description + style + lighting + camera", 
            "lighting + camera"
        ]
        
        # 获取数据缓存
        data_cache = get_data_cache()
        
        required_inputs = {
            "seed": ("INT", {
                "default": 0, 
                "min": 0, 
                "max": 0xffffffffffffffff, 
                "step": 1,
                "tooltip": "Random seed for prompt generation. Use 0 for random seed each time."
            }),
            "auto_fill": ("BOOLEAN", {
                "default": True,
                "tooltip": "Automatically fill custom fields when menu selections change."
            }),
            "prompt_priority": (priority_options, {
                "default": "subject + scene",
                "tooltip": "Determine the order of components in the generated prompt."
            }),
            "custom_subject": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Main subject description. You can obtain the subject's auto-prompt from LLM/VLM or custom nodes, such as Portrait Master."
            }),
            
            "scene": (cls.IMAGE_BASED_OPTIONS + data_cache['SCENE_OPTIONS'], {
                "default": "disable",
                "tooltip": "Scene setting and background options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific scene options."
            }),
            "custom_scene": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom scene description. Used when scene is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "motion": (cls.IMAGE_BASED_OPTIONS + data_cache['MOTION_OPTIONS'], {
                "default": "disable",
                "tooltip": "Character motion and pose options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific motion options."
            }),
            "custom_motion": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom motion description. Used when motion is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "facial_action": (cls.IMAGE_BASED_OPTIONS + data_cache['FACIAL_ACTION_OPTIONS'], {
                "default": "disable",
                "tooltip": "Facial action details. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific facial action options."
            }),
            "custom_facial_action": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom facial action description. Used when facial_action is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "exp_str": (data_cache['EXPRESSION_STR'], {
                "default": "quite",
                "tooltip": "Expression intensity modifier. Combined with expression selection to create nuanced emotional descriptions."
            }),
            "expression": (cls.IMAGE_BASED_OPTIONS + data_cache['EXPRESSION_OPTIONS'], {
                "default": "disable",
                "tooltip": "Character expression options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific expression options."
            }),
            "custom_expression": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom expression description. Used when expression is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options. Combines with exp_str when applicable."
            }),
            
            "lighting": (cls.IMAGE_BASED_OPTIONS + data_cache['LIGHTING_OPTIONS'], {
                "default": "disable",
                "tooltip": "Lighting options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific lighting options."
            }),
            "custom_lighting": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom lighting description. Used when lighting is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "camera": (cls.IMAGE_BASED_OPTIONS + data_cache['CAMERA_OPTIONS'], {
                "default": "disable",
                "tooltip": "Camera angle and shot composition options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific camera options."
            }),
            "custom_camera": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom camera description. Used when camera is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "style": (cls.IMAGE_BASED_OPTIONS + data_cache['STYLE_OPTIONS'], {
                "default": "disable",
                "tooltip": "Artistic style and visual treatment options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific style options."
            }),
            "custom_style": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Custom style description. Used when style is set to 'enable' or specific options are selected, or is set to 'random' and is one of the possible options."
            }),
            
            "description": (["enable", "disable", "random"] + data_cache['DESCRIPTION_OPTIONS'], {
                "default": "disable",
                "tooltip": "Overall description template options. Choose 'disable' to exclude, 'enable' to use custom value, 'random' for random selection, or specific description templates."
            }),
            "custom_description": ("STRING", {
                "multiline": True, 
                "default": "A masterpiece of work with insane detail and best quality, featuring a masterfully balanced composition and harmonious colors, presenting a groundbreaking concept",
                "tooltip": "Custom description template. Used when description is set to 'enable' or specific templates are selected. Follows the format: 'A [sensory] of work with [detail] and [quality], featuring a [composition] and [color], presenting a [creativity]'"
            }),
        }
        
        return {"required": required_inputs}
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Random prompt generator with categorized options for scene, motion, facial actions, expressions, lighting, camera, style, and description. Supports manual selection, random generation, and image reference integration for comprehensive prompt creation."
    
    def execute(self, **kwargs):
        """执行提示词生成"""
        seed = kwargs.get('seed', 0)
        # 改为使用 UnifiedPromptGenerator
        unified_generator = UnifiedPromptGenerator(seed)
        prompt = unified_generator.generate_standard_prompt(**kwargs)
        return (prompt,)

class RandomPrompterGeek_JK:
    """ComfyUI Geek 版本节点类 - 使用重构后的生成器"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取数据缓存
        data_cache = get_data_cache()
        
        required_inputs = {
            "seed": ("INT", {
                "default": 0, 
                "min": 0, 
                "max": 0xffffffffffffffff, 
                "step": 1,
                "tooltip": "Random seed for prompt generation. Use 0 for random seed each time."
            }),
            "auto_fill": ("BOOLEAN", {
                "default": True,
                "tooltip": "Automatically fill custom_prompt when category selections change."
            }),
            
            "custom_subject": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Main subject description. This will be combined with category tags in custom_prompt."
            }),
            
            "scene": (data_cache['SCENE_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Scene category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "motion": (data_cache['MOTION_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Motion category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "facial_action": (data_cache['FACIAL_ACTION_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Facial action category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "expression": (data_cache['EXPRESSION_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Expression category selection. Includes expression strength options."
            }),
            
            "lighting": (data_cache['LIGHTING_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Lighting category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "camera": (data_cache['CAMERA_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Camera category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "style": (data_cache['STYLE_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Style category selection. Includes artist and vision subcategories."
            }),
            
            "description": (data_cache['DESCRIPTION_CATEGORIES'], {
                "default": PromptConfig.GEEK_SELECT_OPTION,
                "tooltip": "Description category selection. Choose a category to add its tag to custom_prompt."
            }),
            
            "custom_prompt": ("STRING", {
                "multiline": True, 
                "default": "",
                "tooltip": "Build your prompt using category tags like [category_name]. These will be replaced with random content from the corresponding files at runtime."
            }),
        }
        
        return {"required": required_inputs}
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Geek version: Build prompts using category tags that are replaced with random content at runtime. Supports manual category selection and automatic tag insertion."
    
    def execute(self, **kwargs):
        """执行提示词生成"""
        seed = kwargs.get('seed', 0)
        # 改为使用 UnifiedPromptGenerator
        unified_generator = UnifiedPromptGenerator(seed)
        prompt = unified_generator.generate_geek_prompt(
            kwargs.get('custom_prompt', ''),
            kwargs.get('custom_subject', '')
        )
        return (prompt,)

class PromptCombine_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"default": '', "multiline": True}),
                "prompt_2": ("STRING", {"default": '', "multiline": True}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Prompt",)
    FUNCTION = "combine"
    CATEGORY = icons.get("JK/Prompt")
    
    def combine(self, prompt_1=None, prompt_2=None):
        # 清理两个输入字符串
        cleaned_1 = DataCleaner.clean_prompt_string(prompt_1) if prompt_1 else ""
        cleaned_2 = DataCleaner.clean_prompt_string(prompt_2) if prompt_2 else ""
        
        # 使用 smart_join 合并两个字符串
        elements = []
        if cleaned_1:
            elements.append(cleaned_1)
        if cleaned_2:
            elements.append(cleaned_2)
        
        prompt_output = PromptUtils.smart_join(elements, separator=", ")
        
        return (prompt_output,)
