import random
import json
import os
import re
import configparser
from functools import lru_cache
from typing import List, Dict, Any, Tuple

#---------------------------------------------------------------------------------------------------------------------#
# 配置类 (same)
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
        "audio": "audios",
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
        DIRECTORY_MAPPING["audio"], 
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
    
    # Sys Prompter的预设文件名
    PRESET_FILE = "sys_prompt_preset.json"

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
    def clean_prompt_string(text: str, language: str = "english") -> str:
        """清理提示词字符串，根据语言处理标点"""
        if not text:
            return ""
        
        # 判断是否使用中文标点规则
        use_chinese = language in ["chinese", "japanese", "korean"]
        comma = "，" if use_chinese else ", "
        period = "。" if use_chinese else ". "
        semicolon = "；" if use_chinese else "; "
        question_mark = "？" if use_chinese else "? "
        exclamation_mark = "！" if use_chinese else "! "
        
        # 标准化空白
        text = re.sub(r'\s+', ' ', text)
        
        # 使用循环处理连续标点，直到没有变化为止
        max_iterations = 5
        for i in range(max_iterations):
            old_text = text
            
            # 一次性处理所有标点类型
            patterns = [
                (r'[,，]\s*[。，；？！.,;?!]', comma),
                (r'[.。]\s*[。，；？！.,;?!]', period),
                (r'[;；]\s*[。，；？！.,;?!]', semicolon),
                (r'[?？]\s*[。，；？！.,;?!]', question_mark),
                (r'[!！]\s*[。，；？！.,;?!]', exclamation_mark)
            ]
            
            for pattern, replacement in patterns:
                text = re.sub(pattern, replacement, text)
            
            # 如果没有变化，提前退出
            if text == old_text:
                break
        
        # 标准化标点周围空格
        if use_chinese:
            # 中文：移除标点周围的所有空格
            text = re.sub(r'\s*，\s*', comma, text)
            text = re.sub(r'\s*。\s*', period, text)
            text = re.sub(r'\s*；\s*', semicolon, text)
            text = re.sub(r'\s*？\s*', question_mark, text)
            text = re.sub(r'\s*！\s*', exclamation_mark, text)
        else:
            # 英文：确保标点后有空格
            text = re.sub(r'\s*,\s*', comma, text)
            text = re.sub(r'\s*\.\s*', period, text)
            text = re.sub(r'\s*;\s*', semicolon, text)
            text = re.sub(r'\s*\?\s*', question_mark, text)
            text = re.sub(r'\s*!\s*', exclamation_mark, text)
            # 确保单词间只有一个空格
            text = re.sub(r' +', ' ', text)
        
        # 扩展边界清理，包含所有标点
        all_punctuation = ',.，。;；?？!！'
        text = text.strip(all_punctuation + ' ')
        
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
                    
                    new_prefix = f"{current_prefix}{os.path.sep}{subdir_name}" if current_prefix else subdir_name
                    _process_directory(entry_path, new_prefix, should_add_prefix or len(entries) > 1)
                    
                elif any(entry.endswith(ext) for ext in PromptConfig.SUPPORTED_FORMATS.keys()):
                    # 处理支持的文件格式
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
                    
                    # 使用相对于base_dir的路径
                    file_relative_path = os.path.relpath(entry_path, base_dir)
                    # 确保使用正确的路径分隔符（Windows使用\）
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
        'AUDIO_OPTIONS': DataManager.load_category_options(PromptConfig.DIRECTORY_MAPPING["audio"]),
        'AUDIO_STRUCTURED_OPTIONS': DataManager.load_structured_category_options(PromptConfig.DIRECTORY_MAPPING["audio"], PromptConfig.EXCLUSION_MARK),
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
        'AUDIO_CATEGORIES': DataManager.load_geek_category_options(PromptConfig.DIRECTORY_MAPPING["audio"], is_primary=True),
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
# 工具类 (same)
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

    @staticmethod
    def remove_prompt_emphasis(text):
        """
        移除提示词中的强调符号和权重标记
        """
        if not text:
            return text
        
        # 1. [a:b:weight] → a-b
        text = re.sub(r'\[([^:]+):([^:]+):[^]]*\]', r'\1-\2', text)

        # 2. (a:weight) → a
        text = re.sub(
            r'\(([^)]+?)\s*:\s*\d+(?:\.\s*\d+)?\)', 
            r'\1', 
            text
        )
        
        return text

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

class ShotScriptUtils:
    """工具类，包含ShotScript节点的共用方法"""
    
    @staticmethod
    def detect_format(script: str) -> str:
        """检测输入格式：dict, list, 或 string"""
        if not script.strip():
            return "string"
            
        try:
            script_data = json.loads(script)
            
            if isinstance(script_data, dict):
                return "dict"
            elif isinstance(script_data, list):
                return "list"
            else:
                return "string"
                
        except json.JSONDecodeError:
            return "string"
    
    @staticmethod  
    def preserve_format(value) -> str:
        """保持值的原始格式，包括换行符"""
        if isinstance(value, (dict, list)):
            # 对于字典或列表，使用JSON格式保持结构
            return json.dumps(value, ensure_ascii=False, indent=2)
        else:
            # 对于其他类型，直接转为字符串，保留原始格式
            return str(value)
    
    @staticmethod
    def split_string_into_lines(text: str, max_lines: int = 0) -> List[str]:
        """将字符串分割为行并过滤空行"""
        if not text.strip():
            return []
            
        lines = text.split('\n')
        # 过滤空行并去除前后空格
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        # 限制最大行数
        if max_lines > 0:
            return cleaned_lines[:max_lines]
        return cleaned_lines
    
    @staticmethod
    def detect_language(text: str) -> str:
        """检测文本语言类型"""
        if not text.strip():
            return "english"  # 默认英文
            
        # 检查是否包含中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        if chinese_pattern.search(text):
            return "chinese"
        
        # 检查是否包含日文字符
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')  # 平假名和片假名
        if japanese_pattern.search(text):
            return "japanese"
        
        # 检查是否包含韩文字符
        korean_pattern = re.compile(r'[\uac00-\ud7af]')  # 韩文字母
        if korean_pattern.search(text):
            return "korean"
        
        # 默认返回英文
        return "english"
    
    @staticmethod
    def get_punctuation_for_language(language: str) -> tuple:
        """根据语言获取适当的分隔符和结束标点"""
        # 东亚文字使用中文标点
        if language in ["chinese", "japanese", "korean"]:
            return "。", "。"
        # 其他语言使用英文标点
        else:
            return ". ", "."
    
    @staticmethod
    def merge_json_details(script: str) -> str:
        """合并JSON详情格式为连贯段落"""
        if not script.strip():
            return ""
            
        try:
            script_data = json.loads(script)
            
            # 处理单描述（非字典）
            if not isinstance(script_data, dict):
                # 先检测语言
                language = ShotScriptUtils.detect_language(str(script_data))
                return DataCleaner.clean_prompt_string(str(script_data), language)
            
            # 提取详情字段
            detail_fields = [
                'subject', 'background', 'atmosphere', 'lighting', 
                'shot type', 'movement', 'motion', 'expression', 'style'
            ]
            
            parts = []
            for field in detail_fields:
                if field in script_data and script_data[field]:
                    value = script_data[field].strip()
                    if value:
                        parts.append(value)
            
            if parts:
                # 检测语言并选择适当的分隔符和结束标点
                language = ShotScriptUtils.detect_language(" ".join(parts))
                separator, end_punctuation = ShotScriptUtils.get_punctuation_for_language(language)
                
                # 使用智能连接
                result = PromptUtils.smart_join(parts, separator)
                # 使用DataCleaner清理结果字符串，并传递语言参数
                result = DataCleaner.clean_prompt_string(result, language)
                # 添加结束标点（如果缺失）
                if not result.endswith(('.', '!', '?', '。', '！', '？')):
                    result += end_punctuation
                return result
            else:
                # 先检测语言
                language = ShotScriptUtils.detect_language(str(script_data))
                return DataCleaner.clean_prompt_string(str(script_data), language)
                
        except json.JSONDecodeError:
            # 如果不是JSON，清理后返回
            # 先检测语言
            language = ShotScriptUtils.detect_language(script)
            return DataCleaner.clean_prompt_string(script, language)

    @staticmethod
    def get_shot_keys(max_shots: int) -> List[List[str]]:
        """获取可能的镜头键格式"""
        keys = []
        for i in range(1, max_shots + 1):
            keys.append([
                f"shot{i:02d}", f"shot{i}", 
                f"frame{i:02d}", f"frame{i}", 
                f"shot_{i:02d}", f"shot_{i}",
                str(i)
            ])
        return keys
    
    @staticmethod
    def count_shots_in_dict(data: dict) -> int:
        """计算字典中的镜头数量"""
        shot_count = 0
        for key in data.keys():
            if re.match(r'^(shot|frame)\d+', str(key), re.IGNORECASE) or re.match(r'^\d+$', str(key)):
                shot_count += 1
        return shot_count
    
    @staticmethod
    def extract_from_dict(data: dict, shot_index: int) -> Tuple[str, str]:
        """从字典中提取指定索引的镜头"""
        possible_keys = [
            f"shot{shot_index:02d}", f"shot{shot_index}",
            f"frame{shot_index:02d}", f"frame{shot_index}",
            f"shot_{shot_index:02d}", f"shot_{shot_index}",
            str(shot_index)
        ]
        
        # 查找匹配的键
        for key in possible_keys:
            if key in data:
                return ShotScriptUtils.preserve_format(data[key]), key
        
        # 如果未找到，尝试查找包含索引的键
        index_str = str(shot_index)
        for key, value in data.items():
            if index_str in key:
                return ShotScriptUtils.preserve_format(value), key
        
        return "", ""
    
    @staticmethod
    def extract_from_dict_by_key(data: dict, key: str) -> Tuple[str, str]:
        """从字典中根据键名提取值"""
        # 精确匹配
        if key in data:
            return ShotScriptUtils.preserve_format(data[key]), key
        
        # 如果没有精确匹配，尝试大小写不敏感匹配
        key_lower = key.lower()
        for dict_key, value in data.items():
            if str(dict_key).lower() == key_lower:
                return ShotScriptUtils.preserve_format(value), dict_key
        
        # 如果没有找到，尝试将key转换为数字作为回退
        try:
            index = int(key)
            return ShotScriptUtils.extract_from_dict(data, index)
        except (ValueError, TypeError):
            pass
        
        return "", ""
    
    @staticmethod
    def get_available_keys(data: dict) -> List[str]:
        """获取字典中所有可用的键"""
        return [str(key) for key in data.keys()]
    
    @staticmethod
    def is_special_json_detail_format(data: dict) -> bool:
        """检查是否是特殊JSON格式（包含subject, background等字段）"""
        special_fields = [
            'subject', 'background', 'atmosphere', 'lighting', 
            'shot type', 'movement', 'motion', 'expression', 'style'
        ]
        
        # 检查是否包含特殊字段
        has_special_fields = any(field in data for field in special_fields)
        
        # 检查是否不包含明显的shot键
        has_shot_keys = any(re.match(r'^(shot|frame)\d+', str(key), re.IGNORECASE) for key in data.keys())
        has_numeric_keys = any(re.match(r'^\d+$', str(key)) for key in data.keys())
        
        return has_special_fields and not (has_shot_keys or has_numeric_keys)
    
    @staticmethod
    def has_shot_keys(data: dict, max_shots: int = 10) -> bool:
        """检查字典中是否有shot键"""
        for i in range(1, max_shots + 1):
            for key_format in [f"shot{i:02d}", f"shot{i}", f"frame{i:02d}", f"frame{i}", str(i)]:
                if key_format in data:
                    return True
        return False
