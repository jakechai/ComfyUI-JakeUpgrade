import random
import json
import os
import re
from typing import List, Dict, Any, Tuple
from .jake_node_prompt_shared import PromptConfig, DataCleaner, FileLoader, get_data_cache, PromptUtils, ExpressionUtils, ShotScriptUtils
from ..categories import icons

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
        
        return f"a {sensory} of work with {detail} and {quality}, featuring a {composition} and {color}, presenting a {creativity}"

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
            if key.startswith(PromptConfig.DIRECTORY_MAPPING["expression"] + os.path.sep) or (key in self.data_cache['EXPRESSION_CATEGORIES'] and key != "select" and key != "all expression"):
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
                "default": "a masterpiece of work with insane detail and best quality, featuring a masterfully balanced composition and harmonious colors, presenting a groundbreaking concept",
                "tooltip": "Custom description template. Used when description is set to 'enable' or specific templates are selected. Follows the format: 'a [sensory] of work with [detail] and [quality], featuring a [composition] and [color], presenting a [creativity]'"
            }),
            "remove_prompt_emphasis": ("BOOLEAN", {
                "default": True,
                "tooltip": "Remove emphasis symbols and weight markers from custom_subject (e.g., (word:1.5) -> word, [A:B:0.5] -> A-B)"
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
        remove_prompt_emphasis = kwargs.get('remove_prompt_emphasis', True)
        prompt_generator = PromptGenerator(seed)
        prompt = prompt_generator.generate_prompt(**kwargs)
        if remove_prompt_emphasis:
            prompt = PromptUtils.remove_prompt_emphasis(prompt)
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
            "remove_prompt_emphasis": ("BOOLEAN", {
                "default": True,
                "tooltip": "Remove emphasis symbols and weight markers from custom_subject (e.g., (word:1.5) -> word, [A:B:0.5] -> A-B)"
            }),
        }
        
        return {"required": required_inputs}
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "sys_prompt")
    FUNCTION = "execute"
    CATEGORY = icons.get("JK/Prompt")
    DESCRIPTION = "Build prompts using category tags that are replaced with random content at runtime. Supports manual category selection and automatic tag insertion."
    
    def execute(self, **kwargs):
        """执行提示词生成"""
        seed = kwargs.get('seed', 0)
        custom_prompt = kwargs.get('custom_prompt', '')
        custom_subject = kwargs.get('custom_subject', '')
        remove_prompt_emphasis = kwargs.get('remove_prompt_emphasis', True)
        
        # 创建 Geek 版本提示词生成器
        prompt_generator_geek = PromptGeneratorGeek(seed)
        
        # 生成提示词
        prompt = prompt_generator_geek.generate_prompt(custom_prompt, custom_subject)
        if remove_prompt_emphasis:
            prompt = PromptUtils.remove_prompt_emphasis(prompt)
        
        config_file_path = os.path.join(
            os.path.dirname(__file__), 
            PromptConfig.PROMPT_DATA_DIR, 
            'sys_prompt_random_mapping.json'
        )
        
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                mapping_config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_file_path}")
            # 如果文件不存在，使用默认配置
            mapping_config = {
                "use_llm": {},
                "replace_01": {},
                "replace_02": {}
            }
        except Exception as e:
            print(f"Error loading config file: {e}")
            mapping_config = {
                "use_llm": {},
                "replace_01": {},
                "replace_02": {}
            }
        
        # 初始化 sys_prompt
        sys_prompt = custom_prompt
        
        # 步骤1: 根据 use_llm 决定是否执行替换
        use_llm = mapping_config.get("use_llm", {})
        replace_01 = mapping_config.get("replace_01", {})
        replace_02 = mapping_config.get("replace_02", {})
        
        # 步骤2: 执行 replace_01 替换
        for original, replacement in replace_01.items():
            # 检查是否需要替换（use_llm 中对应项为 True）
            # 注意：配置文件中 use_llm 的键可能包含方括号，需要匹配
            use_llm_key = original  # 直接使用原键，因为配置文件中就是带方括号的
            if use_llm.get(use_llm_key, True):
                sys_prompt = sys_prompt.replace(original, replacement)
        
        # 步骤3: 字符去重处理
        def keep_first_tag(text, tag):
            first_match = re.search(re.escape(tag), text)
            if first_match:
                return text[:first_match.end()] + re.sub(re.escape(tag), '', text[first_match.end():])
            return text
        
        # 去重处理特定标签
        duplicate_tags = [
            '[all scenes]', '[season]', '[weather]', '[color]', 
            '[all facial_actions]', '[composition]', '[all styles]', 
            '[all artists]', '[all forms]'
        ]
        
        for tag in duplicate_tags:
            sys_prompt = keep_first_tag(sys_prompt, tag)
        
        # 步骤4: 执行 replace_02 替换
        for original, replacement in replace_02.items():
            # 检查是否需要替换（use_llm 中对应项为 True）
            use_llm_key = original  # 直接使用原键
            if use_llm.get(use_llm_key, True):
                if isinstance(replacement, list):
                    # 如果是列表，随机选择一个
                    chosen_replacement = random.choice(replacement)
                    sys_prompt = sys_prompt.replace(original, chosen_replacement)
                else:
                    # 如果是字符串，直接替换
                    sys_prompt = sys_prompt.replace(original, replacement)
        
        # 步骤5: 执行最终的 generate_prompt 方法
        sys_prompt = prompt_generator_geek.generate_prompt(sys_prompt, custom_subject)
        if remove_prompt_emphasis:
            sys_prompt = PromptUtils.remove_prompt_emphasis(sys_prompt)
        
        return (prompt, sys_prompt)
