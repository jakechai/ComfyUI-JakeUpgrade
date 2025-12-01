#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Experimental Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import random
from typing import Tuple
from ..categories import icons

#---------------------------------------------------------------------------------------------------------------------#
# Experimental Nodes
#---------------------------------------------------------------------------------------------------------------------#

class RandomBeats_JK:
    """
    Generate random beat patterns for experimental animation sequences
    
    This node creates randomized coordinate patterns in X_Y_Z format that can be used
    for generating musical beats, animation timing, or procedural content generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {
                    "default": 1, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Number of beat groups to generate"
                }),
                "X_start": ("INT", {
                    "default": 1, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Minimum value for X coordinate"
                }),
                "X_end": ("INT", {
                    "default": 4, 
                    "min": 1, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Maximum value for X coordinate"
                }),
                "Y_start": ("INT", {
                    "default": 1, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Minimum value for Y coordinate"
                }),
                "Y_end": ("INT", {
                    "default": 4, 
                    "min": 1, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Maximum value for Y coordinate"
                }),
                "Z_start": ("INT", {
                    "default": 1, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Minimum value for Z coordinate"
                }),
                "Z_end": ("INT", {
                    "default": 23, 
                    "min": 1, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Maximum value for Z coordinate"
                }),
                "max_items_per_count": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "Maximum number of items per beat group"
                }),
                "max_items_odds": ("INT", {
                    "default": 5, 
                    "min": 0, 
                    "max": 10,
                    "tooltip": "Probability (0-10) of generating multiple items per beat"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("BEATSTEXT",)
    FUNCTION = "gen_beats"
    CATEGORY = icons.get("JK/Experiment")
    DESCRIPTION = "Generate random beat patterns for experimental animation and timing sequences"
    EXPERIMENTAL = True

    def gen_beats(self, count: int, X_start: int, X_end: int, Y_start: int, Y_end: int, 
                  Z_start: int, Z_end: int, max_items_per_count: int, max_items_odds: int) -> Tuple[str]:
        """
        生成随机节奏模式
        
        Args:
            count: 节奏组数量
            X_start: X坐标最小值
            X_end: X坐标最大值  
            Y_start: Y坐标最小值
            Y_end: Y坐标最大值
            Z_start: Z坐标最小值
            Z_end: Z坐标最大值
            max_items_per_count: 每个节奏组最大项目数
            max_items_odds: 生成多个项目的概率
            
        Returns:
            格式化的节奏文本字符串
        """
        
        # 验证输入范围
        if X_start > X_end:
            raise ValueError("X_start must be less than or equal to X_end")
        if Y_start > Y_end:
            raise ValueError("Y_start must be less than or equal to Y_end")
        if Z_start > Z_end:
            raise ValueError("Z_start must be less than or equal to Z_end")
        if max_items_odds < 0 or max_items_odds > 10:
            raise ValueError("max_items_odds must be between 0 and 10")
        
        beatstext = ""
        
        # 生成指定数量的节奏组
        for i in range(count):
            
            # 确定当前组中的项目数量
            if max_items_per_count == 1 or max_items_odds == 0:
                randomItem = 1
            else:
                # 根据概率决定是否生成多个项目
                randomItemOdds = random.randint(1, 10)
                randomItem = random.randint(1, max_items_per_count if randomItemOdds <= max_items_odds else 1)
            
            # 生成当前组中的所有项目
            for j in range(randomItem):
                # 生成随机坐标
                randomX = random.randint(X_start, X_end)
                randomY = random.randint(Y_start, Y_end)
                randomZ = random.randint(Z_start, Z_end)
                
                # 格式化输出文本
                pretext = "  - mTextVal: " if j == 0 else ""
                endtext = "\n" if j == (randomItem - 1) else ""
                beatstext = f"{beatstext}{pretext}{randomX}_{randomY}_{randomZ},{endtext}"
        
        # 输出调试信息
        print(f"Generated beats text with {count} groups")
        return (beatstext,)
