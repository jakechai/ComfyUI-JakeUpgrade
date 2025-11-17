import json
import os
import re
from typing import List, Dict, Any, Tuple
from .jake_node_prompt_shared import PromptConfig, DataCleaner, PromptUtils, ShotScriptUtils
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# System Prompter (same)
#---------------------------------------------------------------------------------------------------------------------#

class SysPromptBuilder:
    """Build prompts based on user input and preset templates"""
    
    # Language mapping for <特定语种> replacement
    LANGUAGE_MAPPING = {
        "Chinese": "中文",
        "English": "英文", 
        "Spanish": "西班牙文",
        "France": "法文",
        "German": "德文",
        "Japanese": "日文",
        "Korean": "韩文",
        "Russian": "俄文",
        "Arabic": "阿拉伯文",
        "Italian": "意大利文",
        "Portuguese": "葡萄牙文"
    }
    
    def __init__(self):
        self.preset_data = self._load_preset_data()
    
    def _load_preset_data(self):
        """Load preset data from JSON file"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), PromptConfig.PROMPT_DATA_DIR, PromptConfig.PRESET_FILE)
            
            if not os.path.exists(file_path):
                print(f"Error: File does not exist: {file_path}")
                return {}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preset data: {e}")
            return {}
    
    def _get_language_key(self, language: str) -> str:
        """Convert language to preset key"""
        return "cn" if language == "Chinese" else "en"
    
    def _replace_variables(self, text: str, output_language: str, shot_count: int, json_detail_format: bool) -> str:
        """Replace variables in text with actual values"""
        if not text:
            return text
            
        # Replace <specified_language>
        text = text.replace("<specified_language>", output_language)
        
        # Replace <特定语种>
        chinese_lang = self.LANGUAGE_MAPPING.get(output_language, "英文")
        text = text.replace("<特定语种>", chinese_lang)
        
        # Replace <shot_count>
        text = text.replace("<shot_count>", str(shot_count))
        
        # Replace <json_detail_format>
        json_detail_format_str = self.preset_data.get("json_detail", {}).get("format", "{}")
        text = text.replace("<json_detail_format>", json_detail_format_str)
        
        return text
    
    def _get_preset_value(self, path: list, system_language: str) -> str:
        """Get value from preset data using path"""
        try:
            current = self.preset_data
            
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return ""
            
            # Handle the final value
            if isinstance(current, dict):
                lang_key = self._get_language_key(system_language)
                return current.get(lang_key, "")
            else:
                return str(current) if current else ""
                
        except Exception as e:
            return ""
    
    def _build_common_parts(self, model_type: str, mode: str, detail: str, json_detail_format: bool, 
                           input_as_1st_shot: bool) -> list:
        """Build common template parts for both LLM and VLM"""
        json_key = "json_detail" if json_detail_format else "no_json_detail"
        
        if mode == "single image":
            if json_detail_format:
                return [
                    [model_type, "single", "part_01"],
                    ["detail_preset", detail],
                    [model_type, "single", "part_02"],
                    ["add_json_detail", "single", json_key],
                    ["json_detail", "description"]
                ]
            else:
                return [
                    [model_type, "single", "part_01"],
                    ["detail_preset", detail],
                    [model_type, "single", "part_02"],
                    ["add_json_detail", "single", json_key]
                ]
        else:  # shot script
            if json_detail_format:
                return [
                    [model_type, "script", "part_01"],
                    ["detail_preset", detail],
                    (["first_shot_01"] if input_as_1st_shot else []),
                    [model_type, "script", "part_02"],
                    ["split_shots"],
                    [model_type, "script", "part_03"],
                    (["first_shot_02"] if input_as_1st_shot else []),
                    ["detail_preset", detail],
                    [model_type, "script", "part_04"],
                    (["first_shot_03"] if input_as_1st_shot else []),
                    ["add_json_detail", "script", json_key],
                    ["json_detail", "description"],
                    [model_type, "script", "part_05"],
                    ["combine_shots"]
                ]
            else:
                return [
                    [model_type, "script", "part_01"],
                    ["detail_preset", detail],
                    (["first_shot_01"] if input_as_1st_shot else []),
                    [model_type, "script", "part_02"],
                    ["split_shots"],
                    [model_type, "script", "part_03"],
                    (["first_shot_02"] if input_as_1st_shot else []),
                    ["detail_preset", detail],
                    [model_type, "script", "part_04"],
                    (["first_shot_03"] if input_as_1st_shot else []),
                    ["add_json_detail", "script", json_key],
                    [model_type, "script", "part_05"],
                    ["combine_shots"]
                ]
    
    def build_prompt(self, model: str, mode: str, detail: str, json_detail_format: bool, 
                    shot_count: int, input_as_1st_shot: bool, system_language: str, output_language: str) -> str:
        """Build prompt based on input parameters"""
        
        # Determine model type for template paths
        model_type = model.lower()
        
        # Build template parts based on model and mode
        template_parts = self._build_common_parts(model_type, mode, detail, json_detail_format, input_as_1st_shot)
        
        # Add final part for LLM
        if model == "Text":
            template_parts.append(["text", "part_final"])
        
        # Build the prompt by concatenating all parts
        prompt_parts = []
        
        for part_path in template_parts:
            part_text = self._get_preset_value(part_path, system_language)
            if part_text:
                prompt_parts.append(part_text)
        
        # Combine all parts and replace variables
        full_prompt = "".join(prompt_parts)
        full_prompt = self._replace_variables(full_prompt, output_language, shot_count, json_detail_format)
        
        return full_prompt

class SystemPrompter_JK:
    """ComfyUI Node for building prompts based on preset templates"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (["Text", "Image"], {
                    "default": "Text",
                    "tooltip": "Select model type. Text: generate prompt from user text; Image: generate prompt from ref image."
                }),
                "mode": (["single image", "shot script"], {
                    "default": "single image", 
                    "tooltip": "Select mode: single image or shot script."
                }),
                "detail": (["simple", "detailed", "extreme_detailed"], {
                    "default": "detailed",
                    "tooltip": "Select detail level for prompt generation."
                }),
                "json_detail_format": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Only available for QWen3-VL for now. Whether to output in JSON format with detailed breakdown."
                }),
                "shot_count": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 20,
                    "step": 1,
                    "tooltip": "Number of shots for script mode. Total count +1 if input_as_1st_shot is True."
                }),
                "input_as_1st_shot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Whether to use the custom prompt or reference image as the first shot"
                }),
                "system_language": (["Chinese", "English"], {
                    "default": "English",
                    "tooltip": "System language for LLM/VLM."
                }),
                "output_language": (["Chinese", "English", "Spanish", "France", "German", 
                                   "Japanese", "Korean", "Russian", "Arabic", "Italian", 
                                   "Portuguese"], {
                    "default": "English",
                    "tooltip": "Output language for the generated prompt."
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build_prompt"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Build single image | shot script system prompt for LLM/VLM based on preset templates and user configuration. Supports JSON format and multi-language output request."
    
    def __init__(self):
        self.builder = SysPromptBuilder()
    
    def build_prompt(self, model: str, mode: str, detail: str, json_detail_format: bool, 
                    shot_count: int, input_as_1st_shot: bool, system_language: str, output_language: str) -> Tuple[str]:
        """Build and return the prompt string"""
        
        prompt = self.builder.build_prompt(
            model=model,
            mode=mode,
            detail=detail,
            json_detail_format=json_detail_format,
            shot_count=shot_count,
            input_as_1st_shot=input_as_1st_shot,
            system_language=system_language,
            output_language=output_language
        )
        
        return (prompt,)

#---------------------------------------------------------------------------------------------------------------------#
# Shot Script Nodes (same)
#---------------------------------------------------------------------------------------------------------------------#

class ShotScriptCombiner_JK:
    """Combine shot scripts into string list output"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shot_scripts": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "JSON string containing shot prompts or single description"
                }),
                "max_shots": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 50,
                    "step": 1,
                    "tooltip": "Maximum number of shots to extract"
                }),
                "merge_json_details": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Merge JSON detail fields into coherent paragraphs"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("script_list",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "combine_shots"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Combine shot scripts into string list output."
    
    def combine_shots(self, shot_scripts: str, max_shots: int, merge_json_details: bool) -> Tuple[List[str], str]:
        """Combine shot scripts into string list output"""
        
        if not shot_scripts.strip():
            return ([""],)
        
        # 检测输入格式并处理
        result_list = self._process_to_list(shot_scripts, max_shots, merge_json_details)
        
        return (result_list,)
    
    def _process_to_list(self, shot_scripts: str, max_shots: int, merge_json_details: bool) -> List[str]:
        """处理输入为字符串列表"""
        
        # 检测输入格式
        input_format = ShotScriptUtils.detect_format(shot_scripts)
        
        if input_format == "dict":
            # JSON字典格式：按顶级key拆分
            return self._process_dict(shot_scripts, max_shots, merge_json_details)
        elif input_format == "list":
            # JSON列表格式：直接转换
            return self._process_list(shot_scripts, merge_json_details)
        else:
            # 字符串格式：按行分割
            return self._process_string(shot_scripts, max_shots)
    
    def _process_dict(self, shot_scripts: str, max_shots: int, merge_json_details: bool) -> List[str]:
        """处理字典格式输入"""
        try:
            data = json.loads(shot_scripts)
            result = []
            
            # 检查是否是特殊JSON格式（包含subject, background等字段）
            is_special_format = ShotScriptUtils.is_special_json_detail_format(data)
            
            # 如果是特殊格式且没有shot键，直接作为单个shot处理
            if is_special_format and not ShotScriptUtils.has_shot_keys(data, max_shots):
                if merge_json_details:
                    merged = ShotScriptUtils.merge_json_details(shot_scripts)
                    result.append(merged)
                else:
                    result.append(ShotScriptUtils.preserve_format(data))
                return result
            
            # 处理镜头键（按数字顺序）
            for i in range(1, max_shots + 1):
                found = False
                for key_format in [f"shot{i:02d}", f"shot{i}", f"frame{i:02d}", f"frame{i}", str(i)]:
                    if key_format in data:
                        value = data[key_format]
                        if merge_json_details and isinstance(value, dict):
                            # 合并JSON详情
                            merged = ShotScriptUtils.merge_json_details(json.dumps(value))
                            result.append(merged)
                        else:
                            # 保持原有格式
                            result.append(ShotScriptUtils.preserve_format(value))
                        found = True
                        break
                
                # 如果没有找到当前索引的键，停止查找
                if not found:
                    break
            
            # 如果是特殊格式且有shot键，但没找到任何shot，则处理整个字典
            if is_special_format and len(result) == 0:
                if merge_json_details:
                    merged = ShotScriptUtils.merge_json_details(shot_scripts)
                    result.append(merged)
                else:
                    result.append(ShotScriptUtils.preserve_format(data))
            
            # 添加其他非镜头键（只有在不是特殊格式的情况下）
            if not is_special_format:
                for key, value in data.items():
                    # 跳过已经处理的镜头键
                    if any(re.match(r'^(shot|frame)\d+', str(key), re.IGNORECASE) for pattern in 
                          [r'^(shot|frame)\d+', r'^\d+$'] if re.match(pattern, str(key), re.IGNORECASE)):
                        continue
                    
                    if merge_json_details and isinstance(value, dict):
                        merged = ShotScriptUtils.merge_json_details(json.dumps(value))
                        result.append(merged)
                    else:
                        result.append(ShotScriptUtils.preserve_format(value))
            
            return result
            
        except json.JSONDecodeError:
            return [shot_scripts]
    
    def _process_list(self, shot_scripts: str, merge_json_details: bool) -> List[str]:
        """处理列表格式输入"""
        try:
            data = json.loads(shot_scripts)
            result = []
            for item in data:
                if merge_json_details and isinstance(item, dict):
                    merged = ShotScriptUtils.merge_json_details(json.dumps(item))
                    result.append(merged)
                else:
                    result.append(ShotScriptUtils.preserve_format(item))
            return result
            
        except json.JSONDecodeError:
            return [shot_scripts]
    
    def _process_string(self, text: str, max_shots: int) -> List[str]:
        """处理字符串格式输入"""
        return ShotScriptUtils.split_string_into_lines(text, max_shots)

class ShotScriptExtractor_JK:
    """Extract specific shot prompt from shot script JSON or string list"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_inputs": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Shot script JSON or string list to extract from"
                }),
                "key_or_index": ("STRING", {
                    "default": "1",
                    "tooltip": "Key name for dict_string, index for other types (supports negative indexing)"
                }),
                "input_type": (["string_list", "dict_string", "array_string", "multilines"], {
                    "default": "string_list",
                    "tooltip": "Input type: string_list, dict_string, array_string, or multilines"
                }),
            }
        }
    
    # 两个输入都是列表
    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("element", "element_counts", "status")
    FUNCTION = "extract_element"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Extract specific element from string list, dictionary stirng, array string or multiline string based on index or key value."
    
    def extract_element(self, string_inputs, key_or_index, input_type):
        """Extract specific element from shot script or string list based on key or index"""
        
        if not string_inputs:
            return ("", 0, "Empty input")
        
        # 获取key_or_index值
        key_or_index_str = key_or_index[0] if key_or_index else "1"
        
        # 获取输入类型
        input_type = input_type[0] if input_type else "string_list"
        
        if input_type == "dict_string":
            # 使用字典键提取逻辑
            return self._extract_from_dict_string(string_inputs[0], key_or_index_str)
        elif input_type == "array_string":
            # 使用数组字符串提取逻辑
            return self._extract_from_array_string(string_inputs[0], key_or_index_str)
        elif input_type == "multilines":
            # 使用多行文本提取逻辑
            return self._extract_from_multilines(string_inputs[0], key_or_index_str)
        else:
            # 使用字符串列表提取逻辑
            return self._extract_from_string_list(string_inputs, key_or_index_str)
    
    def _extract_from_dict_string(self, dict_string: str, key: str) -> Tuple[str, int, str]:
        """从字典字符串中根据键名提取元素"""
        if not dict_string.strip():
            return ("", 0, "Empty dict string")
        
        try:
            # 解析JSON为字典
            data = json.loads(dict_string)
            
            if not isinstance(data, dict):
                return ("", 0, "Input is not a dictionary")
            
            # 获取所有可用键
            available_keys = ShotScriptUtils.get_available_keys(data)
            shot_counts = len(available_keys)
            
            # 根据键名提取值
            result_script, matched_key = ShotScriptUtils.extract_from_dict_by_key(data, key)
            
            if result_script:
                status = f"Key '{matched_key}' found"
            else:
                status = f"Key '{key}' not found. Available keys: {', '.join(available_keys)}"
            
            return (result_script, shot_counts, status)
            
        except json.JSONDecodeError as e:
            return ("", 0, f"Invalid JSON: {str(e)}")
        except Exception as e:
            return ("", 0, f"Error: {str(e)}")
    
    def _extract_from_array_string(self, array_string: str, index_str: str) -> Tuple[str, int, str]:
        """从数组字符串中提取元素"""
        if not array_string.strip():
            return ("", 0, "Empty array string")
        
        try:
            # 解析JSON数组
            data = json.loads(array_string)
            
            if not isinstance(data, list):
                return ("", 0, "Input is not an array")
            
            shot_counts = len(data)
            
            # 将索引字符串转换为整数
            try:
                index = int(index_str)
            except ValueError:
                return ("", shot_counts, f"Invalid index: {index_str}")
            
            # 处理负索引
            if index < 0:
                index = shot_counts + index + 1
            
            # 检查索引是否有效
            if 1 <= index <= shot_counts:
                result_script = ShotScriptUtils.preserve_format(data[index-1])
                status = f"Element {index} of {shot_counts}"
            else:
                result_script = ""
                status = f"Index out of range (1-{shot_counts})"
            
            return (result_script, shot_counts, status)
            
        except json.JSONDecodeError as e:
            return ("", 0, f"Invalid JSON: {str(e)}")
        except Exception as e:
            return ("", 0, f"Error: {str(e)}")
    
    def _extract_from_multilines(self, text: str, index_str: str) -> Tuple[str, int, str]:
        """从多行文本中提取元素"""
        if not text.strip():
            return ("", 0, "Empty text")
        
        # 分割文本为行
        lines = ShotScriptUtils.split_string_into_lines(text)
        shot_counts = len(lines)
        
        # 将索引字符串转换为整数
        try:
            index = int(index_str)
        except ValueError:
            return ("", shot_counts, f"Invalid index: {index_str}")
        
        # 处理负索引
        if index < 0:
            index = shot_counts + index + 1
        
        # 检查索引是否有效
        if 1 <= index <= shot_counts:
            result_script = lines[index-1]
            status = f"Line {index} of {shot_counts}"
        else:
            result_script = ""
            status = f"Index out of range (1-{shot_counts})"
        
        return (result_script, shot_counts, status)
    
    def _extract_from_string_list(self, string_list: List[str], index_str: str) -> Tuple[str, int, str]:
        """从字符串列表中提取元素"""
        if not string_list:
            return ("", 0, "Empty list")
        
        shot_counts = len(string_list)
        
        # 将索引字符串转换为整数
        try:
            index = int(index_str)
        except ValueError:
            return ("", shot_counts, f"Invalid index: {index_str}")
        
        # 处理负索引（从末尾开始计数）
        if index < 0:
            index = shot_counts + index + 1
        
        # 检查索引是否有效
        if index < 1 or index > shot_counts:
            # 索引超出范围，返回最后一个元素
            result_script = string_list[-1]
            status = f"Index out of range, returning last element ({shot_counts} of {shot_counts})"
        else:
            # 提取元素
            result_script = string_list[index - 1]
            status = f"Element {index} of {shot_counts}"
        
        return (result_script, shot_counts, status)

class PromptCombine_JK:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"default": '', "multiline": True}),
                "prompt_2": ("STRING", {"default": '', "multiline": True}),
                "preserve_format": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Preserve original format of prompts (including line breaks)"
                }),
                "remove_prompt_emphasis": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Remove emphasis symbols and weight markers from custom_subject (e.g., (word:1.5) -> word, [A:B:0.5] -> A-B)"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Prompt",)
    FUNCTION = "combine"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Merge the two strings into one and clean up the result."
    
    def combine(self, prompt_1=None, prompt_2=None, preserve_format=True, remove_prompt_emphasis=True):
        # 根据 preserve_format 参数选择处理方式
        if preserve_format:
            # 保持原始格式，使用换行符作为分隔符
            processed_1 = ShotScriptUtils.preserve_format(prompt_1) if prompt_1 else ""
            processed_2 = ShotScriptUtils.preserve_format(prompt_2) if prompt_2 else ""
            if remove_prompt_emphasis:
                processed_1 = PromptUtils.remove_prompt_emphasis(processed_1)
                processed_2 = PromptUtils.remove_prompt_emphasis(processed_2)
            
            # 使用换行符连接两个字符串
            elements = []
            if processed_1:
                elements.append(processed_1)
            if processed_2:
                elements.append(processed_2)
            
            prompt_output = "\n".join(elements)
        else:
            # 清理两个输入字符串
            processed_1 = DataCleaner.clean_prompt_string(prompt_1) if prompt_1 else ""
            processed_2 = DataCleaner.clean_prompt_string(prompt_2) if prompt_2 else ""
            if remove_prompt_emphasis:
                processed_1 = PromptUtils.remove_prompt_emphasis(processed_1)
                processed_2 = PromptUtils.remove_prompt_emphasis(processed_2)
            
            # 检查 processed_1 的结尾是否有标点符号
            ends_with_punctuation = False
            if processed_1:
                # 去除末尾空白字符后检查最后一个字符
                trimmed_1 = processed_1.rstrip()
                if trimmed_1:
                    last_char = trimmed_1[-1]
                    # 检查是否为中英文标点符号
                    punctuation_chars = ['.', '。', ',', '，', '!', '！', '?', '？', ':', '：', ';', '；']
                    if last_char in punctuation_chars:
                        ends_with_punctuation = True
            
            # 根据条件选择分隔符
            separator = " " if ends_with_punctuation else ". "
            
            # 使用 smart_join 合并两个字符串
            elements = []
            if processed_1:
                elements.append(processed_1)
            if processed_2:
                elements.append(processed_2)
            
            prompt_output = PromptUtils.smart_join(elements, separator=separator)
        
        return (prompt_output,)
