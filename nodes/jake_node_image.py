#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Image Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
import cv2
import numpy
import math
from PIL import ImageEnhance
from typing import Any, Tuple, List, Dict
from .jake_tools import tensor2pil, pil2tensor
from .jake_utils import (
    torch_imgs_to_pils, pils_to_torch_imgs,
    pil_split_image, pil_make_image_grid,
    image_gray_offset, RGB2RGBA,
    image_channel_merge
)
from nodes import MAX_RESOLUTION
from ..categories import icons

class RoughOutline_JK:
    """Extract rough outlines from images using Canny edge detection and contour processing"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "blur_size": ("INT", {"default": 5, "min": 0, "max": 30, "step": 2}),
                "canny_low": ("INT", {"default": 50, "min": 1, "max": 255, "step": 1}),
                "canny_high": ("INT", {"default": 150, "min": 1, "max": 255, "step": 1}),
                "simplify_mode": (["dynamic", "fixed"], {"default": "dynamic"}),
                "simplify_tolerance": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 20.0, "step": 0.1}),
                "morph_kernel": ("INT", {"default": 9, "min": 0, "max": 20, "step": 2}),
                "thickness": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
            },
        }
        
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("outline_image", "overlay_image", "canny_image")
    FUNCTION = "rough_outline"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Extract rough outlines from images using Canny edge detection and contour processing"
    
    def rough_outline(self, images, blur_size, canny_low, canny_high, simplify_mode, simplify_tolerance, morph_kernel, thickness):
        """
        Extract outlines from input images using Canny edge detection and contour processing
        Returns outline image, overlay image, and canny edges
        """
        batch_size = images.shape[0]
        np_images = images.cpu().numpy() * 255.0
        np_images = np_images.astype(numpy.uint8)
        
        overlay_list = []
        contour_list = []
        edges_list = []
        
        for i in range(batch_size):
            img = np_images[i]
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            if blur_size > 0:
                blur_size_adj = blur_size + 1 if blur_size % 2 == 0 else blur_size
                gray = cv2.GaussianBlur(gray, (blur_size_adj, blur_size_adj), 0)
            
            # Canny edge detection
            edges = cv2.Canny(gray, canny_low, canny_high)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
            # Morphological closing operation
            if morph_kernel > 0:
                kernel = numpy.ones((morph_kernel, morph_kernel), numpy.uint8)
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find and process contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            valid_contours = []
            for contour in contours:
                arc_len = cv2.arcLength(contour, True)
                
                # Dynamic simplification strategy
                if simplify_mode == "dynamic":
                    epsilon = max(1.0, (arc_len * 0.01) * simplify_tolerance)
                else:
                    epsilon = simplify_tolerance
                
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) >= 2:
                    approx = self.connect_breakpoints(approx, max_gap=5)
                    valid_contours.append(approx)
            
            # Create output images
            overlay_img = img_bgr.copy()
            white_bg = numpy.ones_like(img_bgr) * 255
            
            if valid_contours:
                # Draw red contours (BGR format)
                cv2.drawContours(overlay_img, valid_contours, -1, (0, 0, 255), thickness)
                cv2.drawContours(white_bg, valid_contours, -1, (0, 0, 0), thickness)
            
            # Convert and normalize
            overlay_rgb = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB) / 255.0
            contour_rgb = cv2.cvtColor(white_bg, cv2.COLOR_BGR2RGB) / 255.0
            edges_rgb = edges_rgb / 255.0
            
            overlay_list.append(torch.from_numpy(overlay_rgb))
            contour_list.append(torch.from_numpy(contour_rgb))
            edges_list.append(torch.from_numpy(edges_rgb))
        
        return (
            torch.stack(contour_list),
            torch.stack(overlay_list),
            torch.stack(edges_list)
        )

    def connect_breakpoints(self, contour, max_gap=5):
        """Connect breakpoints in contours to maintain shape consistency"""
        new_contour = []
        if len(contour) == 0:
            return contour
        
        # Ensure correct initial point shape
        last_point = numpy.array(contour[0], dtype=numpy.int32).reshape(1,1,2)
        new_contour.append(last_point)
        
        for point in contour[1:]:
            current_point = numpy.array(point, dtype=numpy.int32).reshape(1,1,2)
            distance = numpy.linalg.norm(current_point - last_point)
            
            if distance > max_gap:
                # Generate intermediate points and maintain 3D shape (N,1,2)
                num_intermediate = int(distance // max_gap) + 1
                intermediate = numpy.linspace(
                    last_point[0,0], 
                    current_point[0,0], 
                    num=num_intermediate+2,
                    dtype=numpy.int32
                )
                # Reshape to (N,1,2) format
                intermediate = intermediate.reshape(-1,1,2)
                
                # Skip first and last points (already included)
                for p in intermediate[1:-1]:
                    new_contour.append(p.reshape(1,1,2))
            
            new_contour.append(current_point)
            last_point = current_point
        
        # Concatenate after unifying shapes
        return numpy.concatenate(new_contour, axis=0)

class OpenDWPose_JK:
    """Combine DWPose and OpenPose images by removing and reserving specific colors"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "DWPose": ("IMAGE",),
                "OpenPose": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("pose_image",)
    FUNCTION = "add_images"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Combine DWPose and OpenPose images by removing and reserving specific colors"

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip("#")
        return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]

    def remove_color(self, image, hex_color="#000099"):
        """Remove specific color from image"""
        target_rgb = self.hex_to_rgb(hex_color)

        # Convert PyTorch tensor to NumPy array
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()

        # Convert target color to same scale as image
        target_rgb_normalized = [c / 255.0 for c in target_rgb]

        # Apply color removal with tolerance for small differences
        tolerance = 0.01
        mask = numpy.all(numpy.abs(image - target_rgb_normalized) < tolerance, axis=-1)
        image[mask] = 0

        # Convert back to PyTorch tensor
        image = torch.from_numpy(image)

        return image

    def reserve_color(self, image, reserved_colors=["#000099", "#00FF00"]):
        """Reserve only specified colors in image"""
        # Convert PyTorch tensor to NumPy array
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()

        # Convert reserved colors to same scale as image
        reserved_colors_normalized = []
        for each in reserved_colors:
            target_rgb = self.hex_to_rgb(each)
            reserved_colors_normalized.append([c / 255.0 for c in target_rgb])

        # Create mask to reserve specified colors
        mask = None
        for color_normalized in reserved_colors_normalized:
            color_mask = numpy.all(numpy.abs(image - color_normalized) < 0.01, axis=-1)
            if mask is None:
                mask = color_mask
            else:
                mask |= color_mask

        # Set non-reserved colors to zero
        image[~mask] = 0

        # Convert back to PyTorch tensor
        image = torch.from_numpy(image)

        return image

    def add_images(self, DWPose, OpenPose):
        """Combine DWPose and OpenPose images"""
        print("type(DWPose)", type(DWPose))
        print("DWPose shape", DWPose.shape)
        
        # Remove specific colors from DWPose
        dwpose_color_to_remove = ['#000099', '#990066', '#990099',  # Three lines
                                  '#aa00ff', '#ff0000', '#ff00aa', '#ff00ff', '#ff0055',
                                  '#660099', '#330099']
        for each in dwpose_color_to_remove:
            DWPose = self.remove_color(DWPose, hex_color=each)

        # Reserve only specified colors in OpenPose
        OpenPose = self.reserve_color(OpenPose, reserved_colors=['#ff0055', '#ff00aa',
                                                                 '#ffffff',
                                                                 '#000099','#660099','#330099','#990099','#990066'
                                                                 '#ff00aa','#ff0000','#ff0055'])

        # Add the numpy arrays of input images
        result_image = numpy.add(DWPose, OpenPose)
        return (result_image,)

class MakeImageGrid_JK:
    """Create image grid from multiple images"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "grid_side": ("BOOLEAN", {"default": True, "label_on": "rows", "label_off": "columns"},),
                "grid_side_num": ("INT", {"default": 1, "min": 1, "max": 8192}),
            },
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_grid",)
    FUNCTION = "make_image_grid"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Create image grid from multiple images with specified rows or columns"

    def make_image_grid(self, images, grid_side_num, grid_side):
        """Create image grid from batch of images"""
        try:
            import torchvision.transforms.functional as TF
        except ImportError:
            raise ImportError("torchvision is required for MakeImageGrid_JK")
            
        pil_image_list = torch_imgs_to_pils(images)

        if grid_side:
            rows = grid_side_num
            cols = None
        else:
            cols = grid_side_num
            rows = None

        image_grid = pil_make_image_grid(pil_image_list, rows, cols)

        image_grid = TF.to_tensor(image_grid).permute(1, 2, 0).unsqueeze(0)  # [1, H, W, 3]

        return (image_grid,)

class SplitImageGrid_JK:
    """Split image grid into individual images"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "grid_side": ("BOOLEAN", {"default": True, "label_on": "rows", "label_off": "columns"}),
                "grid_side_num": ("INT", {"default": 1, "min": 1, "max": 8192}),
                "crop_excess": ("BOOLEAN", {"default": True, "label_on": "crop", "label_off": "error"}),
            },
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "split_image_grid"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Split image grid into individual images based on rows or columns"

    def split_image_grid(self, image, grid_side_num, grid_side, crop_excess=True):
        """Split image grid into multiple images"""
        images = []
        for image_pil in torch_imgs_to_pils(image):
            if grid_side:
                rows = grid_side_num
                cols = None
            else:
                cols = grid_side_num
                rows = None

            try:
                image_pils = pil_split_image(image_pil, rows, cols, crop_excess)
                if image_pils:  # Only process if we have images
                    torch_imgs = pils_to_torch_imgs(image_pils, image.dtype, image.device)
                    images.append(torch_imgs)
            except Exception as e:
                if not crop_excess:
                    raise e
                # In crop mode, try to handle the error more gracefully
                print(f"Warning: {e}. Using fallback splitting.")
                # Fallback: use single image
                images.append(image)
        
        if not images:
            # If no images were created, return the original
            return (image,)
            
        images = torch.cat(images, dim=0)
        return (images,)

class ImageRemoveAlpha_JK:
    """Remove alpha channel from RGBA images"""
    
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "RGBA_image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("RGB_image",)
    FUNCTION = "image_remove_alpha"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Remove alpha channel from RGBA images and convert to RGB"

    def image_remove_alpha(self, RGBA_image):
        """Convert RGBA images to RGB by removing alpha channel"""
        ret_images = []

        for index, img in enumerate(RGBA_image):
            _image = tensor2pil(img)
            ret_images.append(pil2tensor(tensor2pil(img).convert('RGB')))
        
        return (torch.cat(ret_images, dim=0),)

class ColorGrading_JK:
    """Apply color grading with brightness, contrast, saturation and RGB adjustments"""
    
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "brightness": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "contrast": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "saturation": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "R": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
                "G": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
                "B": ("INT", {"default": 0, "min": -255, "max": 255, "step": 1}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "color_grading"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Apply color grading with brightness, contrast, saturation and RGB channel adjustments"

    def color_grading(self, image, brightness, contrast, saturation, R, G, B):
        """Apply color grading adjustments to images"""
        ret_images = []

        for i in image:
            i = torch.unsqueeze(i,0)
            original_image = tensor2pil(i)
            ret_image = original_image.convert('RGB')
            
            # Apply brightness adjustment
            if brightness != 1:
                brightness_image = ImageEnhance.Brightness(ret_image)
                ret_image = brightness_image.enhance(factor=brightness)
            
            # Apply contrast adjustment
            if contrast != 1:
                contrast_image = ImageEnhance.Contrast(ret_image)
                ret_image = contrast_image.enhance(factor=contrast)
            
            # Apply saturation adjustment
            if saturation != 1:
                color_image = ImageEnhance.Color(ret_image)
                ret_image = color_image.enhance(factor=saturation)
            
            # Apply RGB channel adjustments
            if R != 0 or G != 0 or B != 0:
                red_channel, green_channel, blue_channel = ret_image.split()
                if R != 0:
                    red_channel = image_gray_offset(red_channel, R)
                if G != 0:
                    green_channel = image_gray_offset(green_channel, G)
                if B != 0:
                    blue_channel = image_gray_offset(blue_channel, B)
                ret_image = image_channel_merge((red_channel, green_channel, blue_channel), 'RGB')
            
            # Preserve alpha channel if original image has it
            if original_image.mode == 'RGBA':
                ret_image = RGB2RGBA(ret_image, original_image.split()[-1])
            
            ret_images.append(pil2tensor(ret_image))
        
        return (torch.cat(ret_images, dim=0),)

class GetSize_JK:
    """Get dimensions from image, latent, or mask"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE",),
                "latent": ("LATENT",),
                "mask": ("MASK",),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Get width and height dimensions from image, latent, or mask input"

    def get_value(self, image: torch.Tensor = None, latent: Dict = None, mask: torch.Tensor = None) -> Tuple[int, int]:
        """Get dimensions from input (image, latent, or mask)"""
        if image is not None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent is not None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        elif mask is not None:
            image_width = mask.shape[2]
            image_height = mask.shape[1]
        else:
            image_width = 0
            image_height = 0
        
        return (image_width, image_height)

# Helper functions for image cropping operations
def get_bounding_box(mask):
    """Calculate bounding box from mask"""
    # Implementation depends on jake_utils
    # Placeholder implementation
    if mask.dim() == 4:
        mask = mask[0]  # Take first batch
    if mask.dim() == 3:
        mask = mask[0]  # Take first channel
    
    non_zero_indices = torch.nonzero(mask)
    if non_zero_indices.numel() == 0:
        return 0, 0, mask.shape[1], mask.shape[0]
    
    y_min = non_zero_indices[:, 0].min().item()
    y_max = non_zero_indices[:, 0].max().item()
    x_min = non_zero_indices[:, 1].min().item()
    x_max = non_zero_indices[:, 1].max().item()
    
    return x_min, y_min, x_max - x_min, y_max - y_min

def calculate_crop_dimensions(bbox, image_width, image_height, padding):
    """Calculate crop dimensions from bounding box"""
    x, y, w, h = bbox
    
    # Apply padding
    x_start = max(0, x - padding)
    y_start = max(0, y - padding)
    x_end = min(image_width, x + w + padding)
    y_end = min(image_height, y + h + padding)
    
    crop_width = x_end - x_start
    crop_height = y_end - y_start
    offset_x = x_start
    offset_y = y_start
    
    return crop_width, crop_height, offset_x, offset_y, x_start, y_start

def multiple_of_int(value, multiple):
    """Round value to nearest multiple"""
    return int(value) // multiple * multiple

def calculate_scale_factor(target_mega_pixel, width, height):
    """Calculate scale factor for target megapixel"""
    current_pixels = width * height
    target_pixels = target_mega_pixel * 1000000  # Convert to pixels
    return math.sqrt(target_pixels / current_pixels)

class ImageCropByMaskResolutionGrp_JK:
    """Calculate crop parameters based on mask for image processing"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE",),
                "latent": ("LATENT",),
            },
            "required": {
                "mask": ("MASK",),
                "padding": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "use_image_res": ("BOOLEAN", {"default": False}),
                "use_target_res": ("BOOLEAN", {"default": False}),
                "target_res": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False}),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("crop_width", "crop_height", "offset_x", "offset_y", "target_width", "target_height")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Calculate crop parameters based on mask with various resolution options"

    def get_value(self, mask: torch.Tensor, padding: int, use_image_res: bool, use_target_mega_pixel: bool, 
                  target_mega_pixel: float, use_target_res: bool, target_res: int, 
                  image: torch.Tensor = None, latent: Dict = None) -> Tuple[int, int, int, int, int, int]:
        """Calculate crop parameters from mask with resolution options"""
        # Get image dimensions
        if image is not None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent is not None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        else:
            image_width = 1024
            image_height = 1024
        
        # Get bounding box from mask
        bbox = get_bounding_box(mask)
        crop_width, crop_height, offset_x, offset_y, _, _ = calculate_crop_dimensions(
            bbox, image_width, image_height, padding
        )
        
        # Calculate base resolution
        if use_image_res:
            base_res = multiple_of_int(
                max(image_width, image_height) if crop_width >= crop_height else min(image_width, image_height), 
                8
            )
        elif use_target_res:
            base_res = multiple_of_int(target_res, 8)
        elif use_target_mega_pixel:
            scale_factor = calculate_scale_factor(target_mega_pixel, crop_width, crop_height)
            base_dim = crop_width if crop_width >= crop_height else crop_height
            base_res = multiple_of_int(base_dim * scale_factor, 8)
        else:
            base_dim = crop_width if crop_width >= crop_height else crop_height
            base_res = multiple_of_int(base_dim, 8)
        
        # Calculate target dimensions
        if crop_width >= crop_height:
            target_width = multiple_of_int(base_res, 8)
            target_height = multiple_of_int(target_width * (crop_height / crop_width), 8)
        else:
            target_height = multiple_of_int(base_res, 8)
            target_width = multiple_of_int(target_height * (crop_width / crop_height), 8)
        
        return (crop_width, crop_height, offset_x, offset_y, target_width, target_height)

class ImageCropByMaskParams_JK:
    """Provide crop parameters for mask-based image cropping"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "inpaint_crop_and_stitch": ("BOOLEAN", {"default": False}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "use_image_res": ("BOOLEAN", {"default": False}),
                "use_target_res": ("BOOLEAN", {"default": False}),
                "target_res": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False}),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("BOOLEAN", "INT", "BOOLEAN", "BOOLEAN", "INT", "BOOLEAN", "FLOAT")
    RETURN_NAMES = ("inpaint_crop_and_stitch", "padding", "use_image_res", "use_target_res", "target_res", "use_target_mega_pixel", "target_mega_pixel")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Provide crop parameters for mask-based image cropping operations"

    def get_value(self, inpaint_crop_and_stitch, padding, use_image_res, use_target_res, target_res, use_target_mega_pixel, target_mega_pixel):
        """Pass through crop parameters"""
        return (inpaint_crop_and_stitch, padding, use_image_res, use_target_res, target_res, use_target_mega_pixel, target_mega_pixel)


class ScaleToResolution_JK:
    """Scale image to target resolution based on width, height or megapixels"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE",),
                "latent": ("LATENT",),
            },
            "required": {
                "direction": ("BOOLEAN", {"default": False, "label_on": "height", "label_off": "width"}),
                "target_resolution": ("INT", {"default": 512, "min": 8, "max": 16384, "step": 8}),
                "use_target_mega_pixel": ("BOOLEAN", {"default": False}),
                "target_mega_pixel": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 16.0, "step": 0.01}),
                "multiple_of": ("INT", {"default": 8, "min": 0, "max": 16, "step": 8}),
            },
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("target_width", "target_height")
    FUNCTION = "get_value"
    CATEGORY = icons.get("JK/Image")
    DESCRIPTION = "Scale image to target resolution based on width, height or megapixel constraints"

    def get_value(self, direction, target_resolution, use_target_mega_pixel, target_mega_pixel, multiple_of, image=None, latent=None):
        """Calculate target dimensions for scaling"""
        if image is not None:
            image_width = image.shape[2]
            image_height = image.shape[1]
        elif latent is not None:
            image_width = latent['samples'].shape[-1] * 8
            image_height = latent['samples'].shape[-2] * 8
        else:
            image_width = 1024
            image_height = 1024
        
        multiple_of = 1 if multiple_of == 0 else multiple_of
        
        if use_target_mega_pixel:
            # Calculate scale factor based on target megapixels
            scale_factor = math.sqrt(target_mega_pixel * 1000000 / (image_width * image_height))
            width = math.ceil((image_width * scale_factor) / multiple_of) * multiple_of
            height = math.ceil((image_height * scale_factor) / multiple_of) * multiple_of
            return (width, height)
        
        elif direction:  # Scale based on height
            height = math.ceil(target_resolution / multiple_of) * multiple_of
            width = math.ceil((image_width / image_height * target_resolution) / multiple_of) * multiple_of
            return (width, height)
        
        else:  # Scale based on width
            width = math.ceil(target_resolution / multiple_of) * multiple_of
            height = math.ceil((image_height / image_width * target_resolution) / multiple_of) * multiple_of
            return (width, height)

#---------------------------------------------------------------------------------------------------------------------#
# Image Resize from ControlNet AUX
# High Quality Edge Thinning using Pure Python
# Written by Lvmin Zhang
# 2023 April
# Stanford University
#---------------------------------------------------------------------------------------------------------------------#
RESIZE_MODES = ["Just Resize", "Crop and Resize", "Resize and Fill"]

# Edge thinning kernels for high quality image processing
lvmin_kernels_raw = [
    numpy.array([
        [-1, -1, -1],
        [0, 1, 0],
        [1, 1, 1]
    ], dtype=numpy.int32),
    numpy.array([
        [0, -1, -1],
        [1, 1, -1],
        [0, 1, 0]
    ], dtype=numpy.int32)
]

lvmin_kernels = []
lvmin_kernels += [numpy.rot90(x, k=0, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=1, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=2, axes=(0, 1)) for x in lvmin_kernels_raw]
lvmin_kernels += [numpy.rot90(x, k=3, axes=(0, 1)) for x in lvmin_kernels_raw]

lvmin_prunings_raw = [
    numpy.array([
        [-1, -1, -1],
        [-1, 1, -1],
        [0, 0, -1]
    ], dtype=numpy.int32),
    numpy.array([
        [-1, -1, -1],
        [-1, 1, -1],
        [-1, 0, 0]
    ], dtype=numpy.int32)
]

lvmin_prunings = []
lvmin_prunings += [numpy.rot90(x, k=0, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=1, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=2, axes=(0, 1)) for x in lvmin_prunings_raw]
lvmin_prunings += [numpy.rot90(x, k=3, axes=(0, 1)) for x in lvmin_prunings_raw]


def remove_pattern(x, kernel):
    """Remove specific patterns from image using morphological hit-miss transform"""
    objects = cv2.morphologyEx(x, cv2.MORPH_HITMISS, kernel)
    objects = numpy.where(objects > 127)
    x[objects] = 0
    return x, objects[0].shape[0] > 0


def thin_one_time(x, kernels):
    """Apply one iteration of thinning using multiple kernels"""
    y = x
    is_done = True
    for k in kernels:
        y, has_update = remove_pattern(y, k)
        if has_update:
            is_done = False
    return y, is_done


def lvmin_thin(x, prunings=True):
    """Apply Lvmin thinning algorithm for high quality edge processing"""
    y = x
    for i in range(32):
        y, is_done = thin_one_time(y, lvmin_kernels)
        if is_done:
            break
    if prunings:
        y, _ = thin_one_time(y, lvmin_prunings)
    return y


def nake_nms(x):
    """Non-maximum suppression for edge thinning"""
    f1 = numpy.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]], dtype=numpy.uint8)
    f2 = numpy.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=numpy.uint8)
    f3 = numpy.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=numpy.uint8)
    f4 = numpy.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]], dtype=numpy.uint8)
    y = numpy.zeros_like(x)
    for f in [f1, f2, f3, f4]:
        numpy.putmask(y, cv2.dilate(x, kernel=f) == x, x)
    return y


def safe_numpy(x):
    """Safe numpy array conversion for Apple/Mac compatibility"""
    # A very safe method to make sure that Apple/Mac works
    y = x

    # below is very boring but do not change these. If you change these Apple or Mac may fail.
    y = y.copy()
    y = numpy.ascontiguousarray(y)
    y = y.copy()
    return y


def get_unique_axis0(data):
    """Get unique rows from 2D array"""
    arr = numpy.asanyarray(data)
    idxs = numpy.lexsort(arr.T)
    arr = arr[idxs]
    unique_idxs = numpy.empty(len(arr), dtype=numpy.bool_)
    unique_idxs[:1] = True
    unique_idxs[1:] = numpy.any(arr[:-1, :] != arr[1:, :], axis=-1)
    return arr[unique_idxs]


class HintImageEnchance_JK:
    """Enhance hint images with high quality resizing and edge processing"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hint_image": ("IMAGE",),
                "image_gen_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "image_gen_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "resize_mode": (RESIZE_MODES, {"default": "Just Resize"})
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("IMAGE", "METADATA", "MODE")
    FUNCTION = "execute"
    CATEGORY = "🐉 JK/🛩️ Image"
    DESCRIPTION = "Enhance hint images with high quality resizing, edge processing and multiple resize modes"

    def execute(self, hint_image, image_gen_width, image_gen_height, resize_mode):
        """Process hint images with high quality enhancement"""
        outs = []
        for single_hint_image in hint_image:
            np_hint_image = numpy.asarray(single_hint_image * 255., dtype=numpy.uint8)

            if resize_mode == "Just Resize":
                np_hint_image = self.execute_resize(np_hint_image, image_gen_width, image_gen_height)
                metadata = "Resize Mode: Just Resize"
            elif resize_mode == "Resize and Fill":
                np_hint_image = self.execute_outer_fit(np_hint_image, image_gen_width, image_gen_height)
                metadata = "Resize Mode: Resize and Fill"
            else:
                np_hint_image = self.execute_inner_fit(np_hint_image, image_gen_width, image_gen_height)
                metadata = "Resize Mode: Crop and Resize"
            
            outs.append(torch.from_numpy(np_hint_image.astype(numpy.float32) / 255.0))
        
        return (torch.stack(outs, dim=0), metadata, resize_mode)
    
    def execute_resize(self, detected_map, w, h):
        """Resize image to target dimensions"""
        detected_map = self.high_quality_resize(detected_map, (w, h))
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def execute_outer_fit(self, detected_map, w, h):
        """Resize image to fit within target dimensions while preserving aspect ratio"""
        old_h, old_w, _ = detected_map.shape
        old_w = float(old_w)
        old_h = float(old_h)
        k0 = float(h) / old_h
        k1 = float(w) / old_w
        safeint = lambda x: int(numpy.round(x))
        k = min(k0, k1)
        
        # Calculate border color for filling
        borders = numpy.concatenate([detected_map[0, :, :], detected_map[-1, :, :], detected_map[:, 0, :], detected_map[:, -1, :]], axis=0)
        high_quality_border_color = numpy.median(borders, axis=0).astype(detected_map.dtype)
        if len(high_quality_border_color) == 4:
            # Inpaint hijack
            high_quality_border_color[3] = 255
        high_quality_background = numpy.tile(high_quality_border_color[None, None], [h, w, 1])
        detected_map = self.high_quality_resize(detected_map, (safeint(old_w * k), safeint(old_h * k)))
        new_h, new_w, _ = detected_map.shape
        pad_h = max(0, (h - new_h) // 2)
        pad_w = max(0, (w - new_w) // 2)
        high_quality_background[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = detected_map
        detected_map = high_quality_background
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def execute_inner_fit(self, detected_map, w, h):
        """Crop and resize image to fit target dimensions"""
        old_h, old_w, _ = detected_map.shape
        old_w = float(old_w)
        old_h = float(old_h)
        k0 = float(h) / old_h
        k1 = float(w) / old_w
        safeint = lambda x: int(numpy.round(x))
        k = max(k0, k1)

        detected_map = self.high_quality_resize(detected_map, (safeint(old_w * k), safeint(old_h * k)))
        new_h, new_w, _ = detected_map.shape
        pad_h = max(0, (new_h - h) // 2)
        pad_w = max(0, (new_w - w) // 2)
        detected_map = detected_map[pad_h:pad_h+h, pad_w:pad_w+w]
        detected_map = safe_numpy(detected_map)
        return detected_map
    
    def high_quality_resize(self, x, size):
        """
        Super high-quality control map up-scaling
        Considering binary, seg, and one-pixel edges
        Written by lvmin
        """
        inpaint_mask = None
        if x.ndim == 3 and x.shape[2] == 4:
            inpaint_mask = x[:, :, 3]
            x = x[:, :, 0:3]

        if x.shape[0] != size[1] or x.shape[1] != size[0]:
            new_size_is_smaller = (size[0] * size[1]) < (x.shape[0] * x.shape[1])
            new_size_is_bigger = (size[0] * size[1]) > (x.shape[0] * x.shape[1])
            unique_color_count = len(get_unique_axis0(x.reshape(-1, x.shape[2])))
            is_one_pixel_edge = False
            is_binary = False
            
            if unique_color_count == 2:
                is_binary = numpy.min(x) < 16 and numpy.max(x) > 240
                if is_binary:
                    xc = x
                    xc = cv2.erode(xc, numpy.ones(shape=(3, 3), dtype=numpy.uint8), iterations=1)
                    xc = cv2.dilate(xc, numpy.ones(shape=(3, 3), dtype=numpy.uint8), iterations=1)
                    one_pixel_edge_count = numpy.where(xc < x)[0].shape[0]
                    all_edge_count = numpy.where(x > 127)[0].shape[0]
                    is_one_pixel_edge = one_pixel_edge_count * 2 > all_edge_count

            # Choose interpolation method based on image characteristics
            if 2 < unique_color_count < 200:
                interpolation = cv2.INTER_NEAREST
            elif new_size_is_smaller:
                interpolation = cv2.INTER_AREA
            else:
                interpolation = cv2.INTER_CUBIC  # Must be CUBIC because we now use nms. NEVER CHANGE THIS

            y = cv2.resize(x, size, interpolation=interpolation)
            if inpaint_mask is not None:
                inpaint_mask = cv2.resize(inpaint_mask, size, interpolation=interpolation)

            # Handle binary images with edge processing
            if is_binary:
                y = numpy.mean(y.astype(numpy.float32), axis=2).clip(0, 255).astype(numpy.uint8)
                if is_one_pixel_edge:
                    y = nake_nms(y)
                    _, y = cv2.threshold(y, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    y = lvmin_thin(y, prunings=new_size_is_bigger)
                else:
                    _, y = cv2.threshold(y, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                y = numpy.stack([y] * 3, axis=2)
        else:
            y = x

        # Restore inpaint mask if exists
        if inpaint_mask is not None:
            inpaint_mask = (inpaint_mask > 127).astype(numpy.float32) * 255.0
            inpaint_mask = inpaint_mask[:, :, None].clip(0, 255).astype(numpy.uint8)
            y = numpy.concatenate([y, inpaint_mask], axis=2)

        return y
