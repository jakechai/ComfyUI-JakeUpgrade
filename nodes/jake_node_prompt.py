import random
import json
import os
import re
import configparser
from functools import lru_cache
from typing import List, Dict, Any, Tuple
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
        
        # 查找最后一个反斜杠，取后面的内容
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
        公共目录遍历函数
        支持两种排除方式：
        - 字符串：排除以该字符串开头的条目
        - 整数：排除编号大于等于该数字的条目
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
                        # 数字排除：排除编号大于等于指定数字的条目
                        match = re.match(r'^(\d+)-', entry)
                        if match:
                            entry_number = int(match.group(1))
                            if entry_number >= exclusion:
                                skip_entry = True
                    elif isinstance(exclusion, str) and exclusion:
                        # 字符串排除：排除以指定字符串开头的条目
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
            
            # 判断当前目录是否需要添加前缀：
            # 1. 如果当前目录有子目录，则需要前缀
            # 2. 如果当前目录有多个文件，则需要前缀
            # 3. 如果父目录有多个条目，则需要前缀
            should_add_prefix = (subdir_count > 0 or file_count > 1 or parent_has_multiple)
            
            for entry in entries:
                entry_path = os.path.join(current_dir, entry)
                
                if os.path.isdir(entry_path):
                    # 处理子目录
                    subdir_name = os.path.splitext(entry)[0]
                    # 移除数字前缀
                    if '-' in subdir_name:
                        subdir_name = subdir_name.split('-', 1)[1]
                    
                    new_prefix = f"{current_prefix}\\{subdir_name}" if current_prefix else subdir_name
                    _process_directory(entry_path, new_prefix, should_add_prefix or len(entries) > 1)
                    
                elif any(entry.endswith(ext) for ext in PromptConfig.SUPPORTED_FORMATS.keys()):
                    # 处理支持的文件格式
                    category_name = os.path.splitext(entry)[0]
                    # 移除数字前缀
                    if '-' in category_name:
                        category_name = category_name.split('-', 1)[1]
                    
                    # 构建完整前缀
                    if current_prefix and should_add_prefix:
                        full_prefix = f"{current_prefix}\\{category_name}"
                    elif should_add_prefix:
                        full_prefix = category_name
                    else:
                        full_prefix = ""  # 不需要前缀
                    
                    # 使用相对于base_dir的路径
                    file_relative_path = os.path.relpath(entry_path, base_dir)
                    # 确保使用正确的路径分隔符（Windows使用\）
                    file_relative_path = file_relative_path.replace('/', '\\')
                    
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
                prefixed_options = [f"{prefix}\\{option}" for option in options]
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
            structured_options.append({
                'file': os.path.basename(file_relative_path),
                'category': prefix,
                'should_add_prefix': should_add_prefix,
                'options': options
            })
        
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
                    if '\\' in clean_prefix:
                        parts = clean_prefix.split('\\')
                        cleaned_parts = []
                        for part in parts:
                            if '-' in part:
                                cleaned_parts.append(part.split('-', 1)[1])
                            else:
                                cleaned_parts.append(part)
                        clean_prefix = '\\'.join(cleaned_parts)
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
                    geek_category_name = f"{subcategory_display_name}\\{clean_prefix}"
                    
                    if geek_category_name not in mapping:
                        mapping[geek_category_name] = []
                    mapping[geek_category_name].append(file_relative_path)
                else:
                    file_name = os.path.splitext(os.path.basename(file_relative_path))[0]
                    if '-' in file_name:
                        file_name = file_name.split('-', 1)[1]
                    
                    geek_category_name = f"{subcategory_display_name}\\{file_name}"
                    
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
        
        # 随机选择一个文件
        selected_category = self.rng.choice(structured_options)
        if selected_category['options']:
            # 从选中的文件中随机选择一条
            choice = self.rng.choice(selected_category['options'])
            # 如果该类别不需要添加前缀，那么choice已经是原始值
            if selected_category.get('should_add_prefix', True):
                return DataCleaner.remove_category_prefix(choice)
            else:
                return choice
        
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
            self.data_cache['STYLE_STRUCTURED_OPTIONS'], custom_style_value, PromptConfig.DIRECTORY_MAPPING["style"]
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
    """主提示词生成器"""
    
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.component_generator = PromptComponentGenerator(self.rng)
        # 添加数据缓存访问
        self.data_cache = get_data_cache()
    
    def _get_expression_combination(self, exp_str_value: str, expression_value: str, custom_expression_value: str) -> str:
        """使用ExpressionUtils处理exp_str和expression的组合"""
        # 获取exp_str选项
        exp_str_options = self.data_cache['EXPRESSION_STR']
        
        # 如果expression是disable，不使用任何表情
        if expression_value.lower() == "disable":
            return ""
        
        # 如果expression是random，随机生成expression和exp_str的组合
        elif expression_value.lower() == "random":
            # 几率使用custom_expression的内容
            if custom_expression_value and custom_expression_value.strip() and self.rng.random() < PromptConfig.CUSTOM_FIELD_PROB:
                return ExpressionUtils.combine_expression(
                    exp_str_value="",  # 不使用指定的exp_str_value，因为这里我们随机
                    expression_value=custom_expression_value,
                    rng=self.rng,
                    exp_str_options=exp_str_options,
                    exp_str_prob=PromptConfig.EXP_STR_RANDOM_PROB
                )
            
            # 使用随机组合
            exp_str_selected = ""
            if ExpressionUtils.should_include_exp_str(self.rng):
                exp_str_selected = ExpressionUtils.select_random_exp_str(exp_str_options, self.rng)
            
            # 生成随机expression
            random_expression = self.component_generator.generate_expression("")
            
            # 如果expression为空，则返回空，不管exp_str的值
            if not random_expression:
                return ""
            
            # 使用ExpressionUtils组合
            return ExpressionUtils.combine_expression(
                exp_str_value=exp_str_selected,
                expression_value=random_expression,
                rng=self.rng,
                exp_str_options=exp_str_options,
                exp_str_prob=PromptConfig.EXP_STR_RANDOM_PROB
            )
        
        # 如果expression是具体选项，使用custom_expression
        else:
            if custom_expression_value and custom_expression_value.strip():
                return ExpressionUtils.combine_expression(
                    exp_str_value=exp_str_value,
                    expression_value=custom_expression_value,
                    rng=self.rng,
                    exp_str_options=exp_str_options,
                    exp_str_prob=PromptConfig.EXP_STR_RANDOM_PROB
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
    
    def _process_category(self, choice: str, custom_value: str, category_name: str, 
                         generate_func=None, exp_mode: bool = False, exp_str_value: str = "") -> str:
        """处理分类选项"""
        if choice.lower() == "disable":
            return ""
        elif choice.lower() == "enable":
            if custom_value and custom_value.strip():
                cleaned_value = DataCleaner.clean_prompt_string(custom_value)
                if cleaned_value:
                    return cleaned_value
        elif choice.lower() == "random":
            if generate_func:
                if not exp_mode:
                    random_value = generate_func(custom_value)
                else:
                    random_value = generate_func(exp_str_value, choice, custom_value)
                if random_value:
                    return random_value
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
            elif not exp_mode:
                clean_value = DataCleaner.remove_category_prefix(choice)
                if clean_value:
                    return clean_value
            else:
                exp_str_clean = DataCleaner.remove_category_prefix(exp_str_value) if exp_str_value else ""
                expression_clean = DataCleaner.remove_category_prefix(choice)
                
                if not expression_clean:
                    return ""
                
                if exp_str_clean and expression_clean:
                    return f"{exp_str_clean} {expression_clean}"
                else:
                    return expression_clean
        
        return ""
    
    def generate_prompt(self, **kwargs) -> str:
        """生成提示词"""
        prompt_priority = kwargs.get("prompt_priority", "subject + scene")
        
        # 收集所有组件
        components_dict = {}
        
        # custom_subject - 总是使用
        custom_subject = kwargs.get("custom_subject", "")
        if custom_subject:
            cleaned_value = DataCleaner.clean_prompt_string(custom_subject)
            if cleaned_value:
                components_dict["subject"] = cleaned_value
        
        # 处理各个分类
        categories = [
            ("scene", "custom_scene", self.component_generator.generate_scene, False),
            ("motion", "custom_motion", self.component_generator.generate_motion, False),
            ("facial_action", "custom_facial_action", self.component_generator.generate_facial_action, False),
            ("expression", "custom_expression", self._get_expression_combination, True),
            ("lighting", "custom_lighting", self.component_generator.generate_lighting, False),
            ("camera", "custom_camera", self.component_generator.generate_camera, False),
            ("style", "custom_style", self.component_generator.generate_style, False),
            ("description", "custom_description", self.component_generator.generate_description, False)
        ]
        
        for category_name, custom_field, generate_func, exp_mode in categories:
            choice = kwargs.get(category_name, "disable")
            custom_value = kwargs.get(custom_field, "")
            exp_str_value = kwargs.get("exp_str", "quite") if exp_mode else ""
            
            result = self._process_category(choice, custom_value, category_name, generate_func, exp_mode, exp_str_value)
            if result:
                components_dict[category_name] = result
        
        # 根据优先级设置组合组件
        components = self._arrange_components_by_priority(components_dict, prompt_priority)
        full_prompt_string = PromptUtils.smart_join(components, separator=", ")
        
        return full_prompt_string

class PromptGeneratorGeek:
    """Geek 版本提示词生成器"""
    
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.prompt_generator = PromptGenerator(seed)
        self.component_generator = self.prompt_generator.component_generator
        self.data_cache = get_data_cache()
    
    def generate_prompt(self, custom_prompt: str, custom_subject: str) -> str:
        """生成 Geek 版本的提示词"""
        # 处理主题
        cleaned_subject = DataCleaner.clean_prompt_string(custom_subject) if custom_subject else ""
        
        # 替换分类标记
        final_prompt = self._replace_category_tags(custom_prompt)
        
        # 组合主题和提示词
        if cleaned_subject and final_prompt:
            full_prompt = f"{cleaned_subject}, {final_prompt}"
        elif cleaned_subject:
            full_prompt = cleaned_subject
        else:
            full_prompt = final_prompt
        
        return full_prompt
    
    def _replace_category_tags(self, prompt: str) -> str:
        """替换分类标记为随机内容 - 使用ExpressionUtils"""
        if not prompt:
            return ""
        
        category_mapping = self.data_cache['CATEGORY_MAPPING']
        
        # 正则表达式匹配 [category_name] 格式的标记
        pattern = r'\[([^\[\]]+)\]'
        
        def replace_match(match):
            category_name = match.group(1)
            
            # 检查是否是有效的分类名称
            if category_name not in category_mapping:
                print(f"Warning: Category '{category_name}' not found in mapping")
                similar_keys = [k for k in category_mapping.keys() if category_name in k]
                if similar_keys:
                    print(f"  Similar keys: {similar_keys[:5]}")
                return match.group(0)
            
            # 从分类对应的文件中获取文件路径
            file_paths = category_mapping[category_name]
            if not file_paths:
                print(f"Warning: No files found for category '{category_name}'")
                return match.group(0)
            
            # 处理expression相关标签 - 使用ExpressionUtils
            if category_name == "all expression" or category_name in self._get_expression_category_names():
                return self._generate_all_expression_with_utils(file_paths)
            
            # 处理 "all xxx" 选项 - 使用 RandomPrompter_JK 的随机策略
            if category_name.startswith("all "):
                base_category = category_name[4:]  # 移除 "all " 前缀
                
                if base_category in [PromptConfig.DIRECTORY_MAPPING["scene"], PromptConfig.DIRECTORY_MAPPING["facial_action"], PromptConfig.DIRECTORY_MAPPING["camera"]]:
                    return self._generate_all_multiple_files(file_paths, base_category)
                elif base_category in [PromptConfig.DIRECTORY_MAPPING["motion"], PromptConfig.DIRECTORY_MAPPING["lighting"], PromptConfig.DIRECTORY_MAPPING["style"]]:
                    return self._generate_all_single_file(file_paths, base_category)
                elif base_category in ["artist", "vision"]:
                    return self._generate_all_single_file(file_paths, base_category)
                else:
                    return self._generate_all_single_file(file_paths, base_category)
            else:
                # 原有逻辑：对于具体分类，通常只有一个文件
                selected_file = self.component_generator.rng.choice(file_paths)
                
                # 加载文件内容
                options = FileLoader.load_data_file(selected_file)
                if not options:
                    print(f"Warning: No content found in file '{selected_file}' for category '{category_name}'")
                    return match.group(0)
                
                # 随机选择一条内容
                selected_option = self.component_generator.rng.choice(options)
                
                # 清理内容中的子分类前缀
                cleaned_option = DataCleaner.remove_category_prefix(selected_option)
                
                return DataCleaner.clean_prompt_string(cleaned_option)
        
        # 替换所有匹配的标记
        result = re.sub(pattern, replace_match, prompt)
        
        return DataCleaner.clean_prompt_string(result)

    def _generate_all_expression_with_utils(self, file_paths: List[str]) -> str:
        """使用ExpressionUtils为所有expression分类生成内容"""
        return self._generate_all_expression(file_paths)

    def _get_expression_category_names(self) -> List[str]:
        """获取所有 expression 分类名称"""
        expression_categories = []
        
        # 从映射表中获取所有以 "expression" 开头的键
        for key in self.data_cache['CATEGORY_MAPPING'].keys():
            if key.startswith(PromptConfig.DIRECTORY_MAPPING["expression"]+"\\") or (key in self.data_cache['EXPRESSION_CATEGORIES'] and key != "select" and key != "all expression"):
                expression_categories.append(key)
        
        return expression_categories
    
    def _generate_all_multiple_files(self, file_paths: List[str], category_name: str) -> str:
        """使用 PromptComponentGenerator._generate_from_multiple_files 策略"""
        # 构建结构化选项格式
        structured_options = []
        for file_path in file_paths:
            options = FileLoader.load_data_file(file_path)
            if options:
                # 模拟结构化选项的格式
                structured_option = {
                    'file': os.path.basename(file_path),
                    'category': category_name,
                    'should_add_prefix': True,
                    'options': options
                }
                structured_options.append(structured_option)
        
        # 使用 PromptComponentGenerator 的方法
        return self.component_generator._generate_from_multiple_files(
            structured_options, "", category_name
        )
    
    def _generate_all_single_file(self, file_paths: List[str], category_name: str) -> str:
        """使用 PromptComponentGenerator._generate_from_single_file 策略"""
        # 构建结构化选项格式
        structured_options = []
        for file_path in file_paths:
            options = FileLoader.load_data_file(file_path)
            if options:
                # 模拟结构化选项的格式
                structured_option = {
                    'file': os.path.basename(file_path),
                    'category': category_name,
                    'should_add_prefix': True,
                    'options': options
                }
                structured_options.append(structured_option)
        
        # 使用 PromptComponentGenerator 的方法
        return self.component_generator._generate_from_single_file(
            structured_options, "", category_name
        )
    
    def _generate_all_expression(self, file_paths: List[str]) -> str:
        """使用ExpressionUtils处理所有expression分类的生成"""
        # 获取exp_str选项
        exp_str_options = self.data_cache['EXPRESSION_STR']
        
        # 随机选择一个exp_str
        exp_str_value = ""
        if ExpressionUtils.should_include_exp_str(self.component_generator.rng):
            exp_str_value = ExpressionUtils.select_random_exp_str(exp_str_options, self.component_generator.rng)
        
        # 根据文件数量决定使用哪种策略
        if len(file_paths) == 1:
            # 单个文件 - 从该文件中随机选择
            selected_file = file_paths[0]
            options = FileLoader.load_data_file(selected_file)
            if options:
                expression_value = self.component_generator.rng.choice(options)
            else:
                expression_value = ""
        else:
            # 多个文件 - 使用单文件策略从所有文件中随机选择
            structured_options = []
            for file_path in file_paths:
                options = FileLoader.load_data_file(file_path)
                if options:
                    # 模拟结构化选项的格式
                    structured_option = {
                        'file': os.path.basename(file_path),
                        'category': PromptConfig.DIRECTORY_MAPPING["expression"],
                        'should_add_prefix': True,
                        'options': options
                    }
                    structured_options.append(structured_option)
            
            # 随机生成一个expression（使用单文件策略）
            expression_value = self.component_generator._generate_from_single_file(
                structured_options, "", PromptConfig.DIRECTORY_MAPPING["expression"]
            )
        
        # 使用ExpressionUtils组合expression
        return ExpressionUtils.combine_expression(
            exp_str_value=exp_str_value,
            expression_value=expression_value,
            rng=self.component_generator.rng,
            exp_str_options=exp_str_options,
            exp_str_prob=PromptConfig.EXP_STR_RANDOM_PROB
        )

#---------------------------------------------------------------------------------------------------------------------#
# 节点类
#---------------------------------------------------------------------------------------------------------------------#
class RandomPrompter_JK:
    """ComfyUI 节点类"""
    
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
    
    @classmethod
    # def IS_CHANGED(cls, **kwargs):
        # return float("NaN")
    
    def execute(self, **kwargs):
        seed = kwargs.get('seed', 0)
        prompt_generator = PromptGenerator(seed)
        prompt = prompt_generator.generate_prompt(**kwargs)
        return (prompt,)

class RandomPrompterGeek_JK:
    """ComfyUI Geek 版本节点类 - 分类级别随机提示词生成器"""
    
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
    DESCRIPTION = "Random Prompter Geek version: Build prompts using category tags that are replaced with random content at runtime. Supports manual category selection and automatic tag insertion."
    
    def execute(self, **kwargs):
        """执行提示词生成"""
        seed = kwargs.get('seed', 0)
        custom_prompt = kwargs.get('custom_prompt', '')
        custom_subject = kwargs.get('custom_subject', '')
        
        # 创建 Geek 版本提示词生成器
        prompt_generator_geek = PromptGeneratorGeek(seed)
        
        # 生成提示词
        prompt = prompt_generator_geek.generate_prompt(custom_prompt, custom_subject)
        
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
    DESCRIPTION = "Merge the two strings into one and clean up the result."
    
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
