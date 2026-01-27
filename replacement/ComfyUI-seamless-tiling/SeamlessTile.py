from typing import Optional

import PIL
import torch
from torch import Tensor
from torch.nn import Conv2d
from torch.nn import functional as F
from torch.nn.modules.utils import _pair


class SeamlessTile:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "tiling": (["enable", "x_only", "y_only", "disable"],),
                "copy_model": (["Modify in place"],),
            },
        }

    CATEGORY = "conditioning"

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "run"

    def run(self, model, copy_model, tiling):
        # 直接修改原始模型，不复制
        if tiling == "enable":
            make_circular_asymm(model.model, True, True)
        elif tiling == "x_only":
            make_circular_asymm(model.model, True, False)
        elif tiling == "y_only":
            make_circular_asymm(model.model, False, True)
        else:
            make_circular_asymm(model.model, False, False)
        return (model,)


# asymmetric tiling from https://github.com/tjm35/asymmetric-tiling-sd-webui/blob/main/scripts/asymmetric_tiling.py
def make_circular_asymm(model, tileX: bool, tileY: bool):
    # 记录已经修改过的层，避免重复修改
    modified_layers = set()
    
    for layer in model.modules():
        if isinstance(layer, torch.nn.Conv2d) and id(layer) not in modified_layers:
            # 标记为已修改
            modified_layers.add(id(layer))
            
            # 保存原始状态（如果需要恢复）
            if not hasattr(layer, '_original_padding_mode'):
                layer._original_padding_mode = layer.padding_mode
            
            # 设置新的padding模式
            layer.padding_modeX = 'circular' if tileX else 'constant'
            layer.padding_modeY = 'circular' if tileY else 'constant'
            
            # 获取padding值
            # 注意：_reversed_padding_repeated_twice是(左, 右, 上, 下)
            padding = layer._reversed_padding_repeated_twice
            layer.paddingX = (padding[0], padding[1], 0, 0)
            layer.paddingY = (0, 0, padding[2], padding[3])
            
            # 保存原始_conv_forward
            if not hasattr(layer, '_original_conv_forward'):
                layer._original_conv_forward = layer._conv_forward
            
            # 替换_conv_forward
            layer._conv_forward = __replacementConv2DConvForward.__get__(layer, Conv2d)
    
    return model


def __replacementConv2DConvForward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
    # 应用X方向填充
    working = F.pad(input, self.paddingX, mode=self.padding_modeX)
    # 应用Y方向填充
    working = F.pad(working, self.paddingY, mode=self.padding_modeY)
    # 执行卷积（padding设为0，因为我们已经手动应用了填充）
    return F.conv2d(working, weight, bias, self.stride, _pair(0), self.dilation, self.groups)


class CircularVAEDecode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "samples": ("LATENT",),
                "vae": ("VAE",),
                "tiling": (["enable", "x_only", "y_only", "disable"],),
                "copy_vae": (["Modify in place"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"

    CATEGORY = "latent"

    def decode(self, samples, vae, tiling, copy_vae):
        # 保存原始状态
        original_states = {}
        
        # 收集原始状态
        for name, module in vae.first_stage_model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                state = {}
                # 保存原始属性
                for attr in ['padding_modeX', 'padding_modeY', 'paddingX', 'paddingY', '_conv_forward']:
                    if hasattr(module, attr):
                        state[attr] = getattr(module, attr)
                original_states[name] = state
        
        try:
            # 临时修改VAE
            if tiling == "enable":
                make_circular_asymm(vae.first_stage_model, True, True)
            elif tiling == "x_only":
                make_circular_asymm(vae.first_stage_model, True, False)
            elif tiling == "y_only":
                make_circular_asymm(vae.first_stage_model, False, True)
            else:
                make_circular_asymm(vae.first_stage_model, False, False)
            
            # 解码
            result = vae.decode(samples["samples"])
        finally:
            # 恢复原始状态
            for name, module in vae.first_stage_model.named_modules():
                if name in original_states:
                    state = original_states[name]
                    for attr, value in state.items():
                        setattr(module, attr, value)
        
        return (result,)


class MakeCircularVAE:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "vae": ("VAE",),
                "tiling": (["enable", "x_only", "y_only", "disable"],),
                "copy_vae": (["Modify in place"],),
            }
        }

    RETURN_TYPES = ("VAE",)
    FUNCTION = "run"
    CATEGORY = "latent"

    def run(self, vae, tiling, copy_vae):
        # 直接修改原始VAE
        if tiling == "enable":
            make_circular_asymm(vae.first_stage_model, True, True)
        elif tiling == "x_only":
            make_circular_asymm(vae.first_stage_model, True, False)
        elif tiling == "y_only":
            make_circular_asymm(vae.first_stage_model, False, True)
        else:
            make_circular_asymm(vae.first_stage_model, False, False)
        
        return (vae,)


class OffsetImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pixels": ("IMAGE",),
                "x_percent": (
                    "FLOAT",
                    {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1},
                ),
                "y_percent": (
                    "FLOAT",
                    {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "image"

    def run(self, pixels, x_percent, y_percent):
        n, y, x, c = pixels.size()
        y = round(y * y_percent / 100)
        x = round(x * x_percent / 100)
        return (pixels.roll((y, x), (1, 2)),)