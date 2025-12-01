#---------------------------------------------------------------------------------------------------------------------#
# Jake Upgrade Utilities for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import torch
import numpy
import math
import torchvision.transforms.functional as TF
from PIL import Image
from typing import Tuple, Union, List
from .jake_tools import tensor2pil

#---------------------------------------------------------------------------------------------------------------------#
# Math Utilities
#---------------------------------------------------------------------------------------------------------------------#

def multiple_of_int(original_int: int, multiple_of: int, mode: bool = True) -> int:
    """
    Round integer to nearest multiple.
    
    Args:
        original_int: Input integer
        multiple_of: Multiple to round to
        mode: True for ceil, False for floor
    
    Returns:
        Rounded integer
    """
    if multiple_of == 0:
        return original_int
    
    if mode:
        return math.ceil(original_int / multiple_of) * multiple_of
    else:
        return math.floor(original_int / multiple_of) * multiple_of

def calculate_scale_factor(target_megapixel: float, width: int, height: int) -> float:
    """
    Calculate scale factor for target megapixel.
    
    Args:
        target_megapixel: Target megapixel value
        width: Original width
        height: Original height
    
    Returns:
        Scale factor
    """
    if width <= 0 or height <= 0:
        return 1.0
    
    current_pixels = width * height
    target_pixels = target_megapixel * 1000000
    
    if current_pixels <= 0:
        return 1.0
    
    return math.sqrt(target_pixels / current_pixels)

#---------------------------------------------------------------------------------------------------------------------#
# Image Processing Utilities
#---------------------------------------------------------------------------------------------------------------------#

def get_bounding_box(mask: torch.Tensor) -> Tuple[int, int, int, int]:
    """
    Get bounding box coordinates from mask tensor.
    
    Args:
        mask: Mask tensor
    
    Returns:
        Tuple of (min_x, min_y, max_x, max_y)
    """
    _mask = tensor2pil(mask)
    non_zero_indices = numpy.nonzero(numpy.array(_mask))

    if len(non_zero_indices[0]) == 0:
        return (0, 0, 0, 0)
    
    min_x, max_x = numpy.min(non_zero_indices[1]).astype(int), numpy.max(non_zero_indices[1]).astype(int)
    min_y, max_y = numpy.min(non_zero_indices[0]).astype(int), numpy.max(non_zero_indices[0]).astype(int)
    
    return (int(min_x), int(min_y), int(max_x), int(max_y))

def calculate_crop_dimensions(
    mask_bbox: Tuple[int, int, int, int], 
    image_width: int, 
    image_height: int,
    padding: int = 0,
    min_crop_size: int = 128
) -> Tuple[int, int, int, int, int, int]:
    """
    Calculate crop dimensions from mask bounding box.
    
    Args:
        mask_bbox: Mask bounding box (min_x, min_y, max_x, max_y)
        image_width: Image width
        image_height: Image height
        padding: Padding around crop
        min_crop_size: Minimum crop size
    
    Returns:
        Tuple of (crop_width, crop_height, offset_x, offset_y, actual_min_x, actual_min_y)
    """
    min_x, min_y, max_x, max_y = mask_bbox
    
    # Calculate initial crop dimensions
    crop_width = max((max_x - min_x), min_crop_size)
    crop_height = max((max_y - min_y), min_crop_size)
    
    # Adjust for minimum size
    if (max_x - min_x) < min_crop_size:
        offset = (min_crop_size - (max_x - min_x)) // 2
        if min_x <= offset:
            min_x = 0
            max_x = min_x + crop_width
        else:
            max_x = image_width
            min_x = max_x - crop_width
    
    if (max_y - min_y) < min_crop_size:
        offset = (min_crop_size - (max_y - min_y)) // 2
        if min_y <= offset:
            min_y = 0
            max_y = min_y + crop_height
        else:
            max_y = image_height
            min_y = max_y - crop_height
    
    # Apply padding
    if padding > 0:
        min_x = max(0, min_x - min(min_x, padding))
        max_x = min(image_width, max_x + min((image_width - max_x), padding))
        min_y = max(0, min_y - min(min_y, padding))
        max_y = min(image_height, max_y + min((image_height - max_y), padding))
        
        crop_width = max_x - min_x
        crop_height = max_y - min_y
    
    return crop_width, crop_height, min_x, min_y, min_x, min_y

#---------------------------------------------------------------------------------------------------------------------#
# String Processing Utilities
#---------------------------------------------------------------------------------------------------------------------#

def parse_string_list(string_input: str) -> List[str]:
    """
    Parse string input into list of items.
    
    Args:
        string_input: Input string with items separated by commas or newlines
    
    Returns:
        List of parsed items
    """
    lines = string_input.split('\n')
    items = []
    
    for line in lines:
        if ',' in line:
            items.extend([item.strip() for item in line.split(',') if item.strip()])
        elif line.strip():
            items.append(line.strip())
    
    return items

def parse_select_cuts(select_cuts: str, max_cuts: int) -> List[int]:
    """
    Parse select cuts string into list of indices.
    
    Args:
        select_cuts: String with cut selection (e.g., "0", "0-2", "0,2,4")
        max_cuts: Maximum number of cuts available
    
    Returns:
        List of selected indices
    """
    if not select_cuts.strip():
        return list(range(max_cuts))
    
    selected_indices = set()
    parts = select_cuts.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:  # Range format (e.g., "1-3")
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range format: '{part}'. Expected format like '1-3'.")
            
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
            except ValueError:
                raise ValueError(f"Invalid range values: '{part}'. Expected integers.")
            
            if start < 0 or end < 0:
                raise ValueError(f"Range values cannot be negative: '{part}'.")
            
            if start > end:
                raise ValueError(f"Range start cannot be greater than end: '{part}'.")
            
            start = min(start, max_cuts - 1)
            end = min(end, max_cuts - 1)
            
            for i in range(start, end + 1):
                selected_indices.add(i)
        
        else:  # Single index
            try:
                index = int(part)
            except ValueError:
                raise ValueError(f"Invalid cut index: '{part}'. Expected integer.")
            
            if index < 0:
                raise ValueError(f"Cut index cannot be negative: '{index}'.")
            
            if index >= max_cuts:
                continue
            
            selected_indices.add(index)
    
    return sorted(list(selected_indices))

#---------------------------------------------------------------------------------------------------------------------#
# Audio Processing Utilities  
#---------------------------------------------------------------------------------------------------------------------#

def calculate_loop_frame_count(
    duration: float, 
    fps: int, 
    segment_frame_count: int, 
    overlap_frame_count: int,
    long_vid_method: bool
) -> int:
    """
    Calculate loop frame count for video generation.
    
    Args:
        duration: Scene duration in seconds
        fps: Frames per second
        segment_frame_count: Base segment frame count
        overlap_frame_count: Overlap frames between segments
        long_vid_method: Whether to use long video method
    
    Returns:
        Calculated loop frame count
    """
    total_frames = duration * fps
    
    if not long_vid_method:
        return multiple_of_int(max(0, total_frames - 1), 4) + 1
    else:
        if (total_frames - segment_frame_count) > 0:
            segment_step = segment_frame_count - overlap_frame_count
            full_segments = (total_frames - segment_frame_count) // segment_step
            remaining_frames = (total_frames - segment_frame_count) % segment_step
            
            loop_frame_count = (
                segment_frame_count + 
                full_segments * segment_step + 
                multiple_of_int(max(0, remaining_frames - 1), 4) + 1
            )
        else:
            loop_frame_count = multiple_of_int(max(0, total_frames - 1), 4) + 1
        
        return int(loop_frame_count)

#---------------------------------------------------------------------------------------------------------------------#
# Image Utilities copied and modified from 3D Pack
#---------------------------------------------------------------------------------------------------------------------#
def torch_imgs_to_pils(images, masks=None, alpha_min=0.1):
    """
        images (torch): [N, H, W, C] or [H, W, C]
        masks (torch): [N, H, W] or [H, W]
    """
    if len(images.shape) == 3:
        images = images.unsqueeze(0)

    if masks is not None:
        masks = masks.to(dtype=images.dtype, device=images.device)
        
        if len(masks.shape) == 2:
            masks = masks.unsqueeze(0)

        inv_mask_index = masks < alpha_min
        images[inv_mask_index] = 0.
        
        masks = masks.unsqueeze(3)
        images = torch.cat((images, masks), dim=3)
        mode="RGBA"
    else:
        mode="RGB"

    pil_image_list = [Image.fromarray((images[i].detach().cpu().numpy() * 255).astype(numpy.uint8), mode=mode) for i in range(images.shape[0])]

    return pil_image_list

def pils_to_torch_imgs(pils: Union[Image.Image, List[Image.Image]], dtype=torch.float16, device="cuda", force_rgb=True):
    if isinstance(pils, Image.Image):
        pils = [pils]
    
    images = []
    for pil in pils:
        if pil.mode == "RGBA" and force_rgb:
            pil = pil.convert('RGB')

        images.append(TF.to_tensor(pil).permute(1, 2, 0))

    images = torch.stack(images, dim=0).to(dtype=dtype, device=device)

    return images

def pil_split_image(image, rows=None, cols=None, crop_excess=True):
    """
    Split image into grid with proper error handling and validation
    
    Args:
        image: PIL Image to split
        rows: Number of rows (None for auto)
        cols: Number of columns (None for auto)  
        crop_excess: Whether to crop excess pixels or raise error
    """
    original_width, original_height = image.size
    
    # Validate input parameters
    if rows is not None and rows <= 0:
        raise ValueError(f"Rows must be positive, got {rows}")
    if cols is not None and cols <= 0:
        raise ValueError(f"Columns must be positive, got {cols}")
    
    # Case 1: Both rows and cols specified
    if rows is not None and cols is not None:
        subimg_width = original_width // cols
        subimg_height = original_height // rows
        
        # Validate if splitting is possible
        if subimg_width <= 0 or subimg_height <= 0:
            raise ValueError(f"Cannot split image {original_width}x{original_height} into {cols}x{rows} grid - subimage size would be {subimg_width}x{subimg_height}")
        
        if crop_excess:
            # Crop to make divisible
            new_width = subimg_width * cols
            new_height = subimg_height * rows
            if new_width != original_width or new_height != original_height:
                image = image.crop((0, 0, new_width, new_height))
        else:
            # Check if divisible
            if subimg_width * cols != original_width or subimg_height * rows != original_height:
                raise ValueError(
                    f"Image size {original_width}x{original_height} cannot be evenly divided into {cols}x{rows} grid. "
                    f"Subimage size would be {subimg_width}x{subimg_height} with excess pixels. "
                    f"Use crop_excess=True or resize the image to {subimg_width * cols}x{subimg_height * rows}"
                )
    
    # Case 2: Only columns specified
    elif cols is not None:
        subimg_width = original_width // cols
        if subimg_width <= 0:
            raise ValueError(f"Cannot split image width {original_width} into {cols} columns")
        
        # Calculate rows based on maintaining aspect ratio or using available height
        rows = max(1, original_height // subimg_width)  # Ensure at least 1 row
        
        subimg_height = original_height // rows
        
        if crop_excess:
            new_width = subimg_width * cols
            new_height = subimg_height * rows
            if new_width != original_width or new_height != original_height:
                image = image.crop((0, 0, new_width, new_height))
        else:
            if subimg_width * cols != original_width or subimg_height * rows != original_height:
                raise ValueError(
                    f"Image size {original_width}x{original_height} cannot be evenly divided into {cols} columns. "
                    f"Subimage size would be {subimg_width}x{subimg_height} with {original_width - subimg_width * cols}x{original_height - subimg_height * rows} excess. "
                    f"Suggested grid: {cols}x{rows}"
                )
    
    # Case 3: Only rows specified  
    elif rows is not None:
        subimg_height = original_height // rows
        if subimg_height <= 0:
            raise ValueError(f"Cannot split image height {original_height} into {rows} rows")
        
        # Calculate columns based on maintaining aspect ratio or using available width
        cols = max(1, original_width // subimg_height)  # Ensure at least 1 column
        
        subimg_width = original_width // cols
        
        if crop_excess:
            new_width = subimg_width * cols
            new_height = subimg_height * rows
            if new_width != original_width or new_height != original_height:
                image = image.crop((0, 0, new_width, new_height))
        else:
            if subimg_width * cols != original_width or subimg_height * rows != original_height:
                raise ValueError(
                    f"Image size {original_width}x{original_height} cannot be evenly divided into {rows} rows. "
                    f"Subimage size would be {subimg_width}x{subimg_height} with {original_width - subimg_width * cols}x{original_height - subimg_height * rows} excess. "
                    f"Suggested grid: {cols}x{rows}"
                )
    
    # Case 4: Auto-detect (assume square grid)
    else:
        # Try to make square subimages
        if original_width >= original_height:
            cols = original_width // original_height
            rows = 1
            subimg_size = original_height
        else:
            rows = original_height // original_width
            cols = 1
            subimg_size = original_width
        
        if cols <= 0 or rows <= 0:
            raise ValueError(f"Cannot auto-split image {original_width}x{original_height} - too small")
        
        if crop_excess:
            new_width = subimg_size * cols
            new_height = subimg_size * rows
            if new_width != original_width or new_height != original_height:
                image = image.crop((0, 0, new_width, new_height))
        else:
            if subimg_size * cols != original_width or subimg_size * rows != original_height:
                raise ValueError(
                    f"Image size {original_width}x{original_height} cannot be auto-split into square subimages. "
                    f"Suggested grid: {cols}x{rows} with subimage size {subimg_size}"
                )
        subimg_width = subimg_height = subimg_size
    
    # Final validation
    if 'subimg_width' not in locals() or 'subimg_height' not in locals():
        subimg_width = original_width // cols
        subimg_height = original_height // rows
    
    if subimg_width <= 0 or subimg_height <= 0:
        raise ValueError(f"Calculated invalid subimage size: {subimg_width}x{subimg_height}")
    
    # Perform the actual splitting
    subimgs = []
    for i in range(rows):
        for j in range(cols):
            left = j * subimg_width
            upper = i * subimg_height
            right = left + subimg_width
            lower = upper + subimg_height
            
            # Safety check - ensure we don't go beyond image bounds
            if right > image.width:
                right = image.width
            if lower > image.height:
                lower = image.height
                
            # Only add if we have a valid region
            if left < right and upper < lower:
                subimg = image.crop((left, upper, right, lower))
                subimgs.append(subimg)
    
    # Final safety check - ensure we have at least one image
    if not subimgs:
        raise ValueError("No valid subimages could be created from the grid")
    
    return subimgs

def pil_make_image_grid(images, rows=None, cols=None):
    if rows is None and cols is None:
        rows = 1
        cols = len(images)
    if rows is None:
        rows = len(images) // cols
        if len(images) % cols != 0:
            rows += 1
    if cols is None:
        cols = len(images) // rows
        if len(images) % rows != 0:
            cols += 1
    total_imgs = rows * cols
    if total_imgs > len(images):
        images += [Image.new(images[0].mode, images[0].size) for _ in range(total_imgs - len(images))]

    w, h = images[0].size
    grid = Image.new(images[0].mode, size=(cols * w, rows * h))

    for i, img in enumerate(images):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid

#---------------------------------------------------------------------------------------------------------------------#
# Image Utilities from Layer Style
#---------------------------------------------------------------------------------------------------------------------#
def image_gray_offset(image:Image, offset:int) -> Image:
    image = image.convert('L')
    width = image.width
    height = image.height
    ret_image = Image.new('L', size=(width, height), color='black')
    for x in range(width):
        for y in range(height):
                pixel = image.getpixel((x, y))
                _pixel = pixel + offset
                if _pixel > 255:
                    _pixel = 255
                if _pixel < 0:
                    _pixel = 0
                ret_image.putpixel((x, y), _pixel)
    return ret_image

def RGB2RGBA(image:Image, mask:Image) -> Image:
    (R, G, B) = image.convert('RGB').split()
    return Image.merge('RGBA', (R, G, B, mask.convert('L')))

def image_channel_merge(channels:tuple, mode = 'RGB' ) -> Image:
    channel1 = channels[0].convert('L')
    channel2 = channels[1].convert('L')
    channel3 = channels[2].convert('L')
    channel4 = Image.new('L', size=channel1.size, color='white')
    if mode == 'RGBA':
        if len(channels) > 3:
            channel4 = channels[3].convert('L')
        ret_image = Image.merge('RGBA',[channel1, channel2, channel3, channel4])
    elif mode == 'RGB':
        ret_image = Image.merge('RGB', [channel1, channel2, channel3])
    elif mode == 'YCbCr':
        ret_image = Image.merge('YCbCr', [channel1, channel2, channel3]).convert('RGB')
    elif mode == 'LAB':
        ret_image = Image.merge('LAB', [channel1, channel2, channel3]).convert('RGB')
    elif mode == 'HSV':
        ret_image = Image.merge('HSV', [channel1, channel2, channel3]).convert('RGB')
    return ret_image
