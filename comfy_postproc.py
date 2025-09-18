import os
from PIL import Image, ImageOps, ImageEnhance
import math
import random
import torch
import numpy as np

import datetime

LUTS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets/luts")
DATE_NOW = str(datetime.datetime.now().strftime("%d%m%Y_%H:%M:%S"))
DATE_DAY = str(datetime.date.today())

class ReturnDateString:     

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):               
        return {
                "required": {
                    "folder_fmt": (["%Y%m%d"], ),
                    "file_fmt": (["%d%m%Y_%H:%M:%S", "%H:%M:%S"], ),
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "return_date_string"
    CATEGORY = "✨ PersonalPostProc"

    def return_date_string(self, folder_fmt: str, file_fmt: str):
        folder = str(datetime.datetime.now().strftime(folder_fmt))
        filename = str(datetime.datetime.now().strftime(file_fmt))
        text_out = folder + "/" + filename + "_COMFYUI"
        
        return (text_out,)
     
    @classmethod
    def IS_CHANGED(s, folder_fmt, file_fmt):
        return random.random()

class ApplyHaldClut:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "lut_file": ([f for f in os.listdir(LUTS_DIR) if f.lower().endswith('.png')], ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_hald_clut"

    CATEGORY = "✨ PersonalPostProc"

    def apply_hald_clut(self, image: torch.Tensor, lut_file: str):
        hald_img = Image.open(os.path.join(LUTS_DIR, lut_file))
        hald_w, hald_h = hald_img.size
        clut_size = int(round(math.pow(hald_w, 1/3)))
        # We square the clut_size because a 12-bit HaldCLUT has the same amount of information as a 144-bit 3D CLUT
        scale = (clut_size * clut_size - 1) / 255
        # We are reshaping to (144 * 144 * 144, 3) - it helps with indexing
        hald_img = np.asarray(hald_img).reshape(clut_size ** 6, 3)
        
        batch_size, height, width, _ = image.shape
        result = torch.zeros_like(image)

        for b in range(batch_size):
            img = (image[b] * 255).to(torch.uint8).numpy()
                        
            # Figure out the 3D CLUT indexes corresponding to the pixels in our image
            clut_r = np.rint(img[:, :, 0] * scale).astype(int)
            clut_g = np.rint(img[:, :, 1] * scale).astype(int)
            clut_b = np.rint(img[:, :, 2] * scale).astype(int)
            filtered_image = np.zeros((img.shape))
            
            # Convert the 3D CLUT indexes into indexes for our HaldCLUT numpy array and copy over the colors to the new image
            filtered_image[:, :] = hald_img[clut_r + clut_size ** 2 * clut_g + clut_size ** 4 * clut_b]
            filtered_image = Image.fromarray(filtered_image.astype('uint8'), 'RGB')
            
            filtered_image = torch.tensor(np.array(filtered_image.convert("RGB"))).float() / 255
            result[b] = filtered_image
            
        return(result, )

class RealGrainAndAutocontrast:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "intensity": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.00,
                    "max": 1.00,
                    "step": 0.05
                }),
                "sharpening_factor": ("FLOAT", {
                    "default": 1.3,
                    "min": 0.00,
                    "max": 4.00,
                    "step": 0.25
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "film_grain"

    CATEGORY = "✨ PersonalPostProc"

    def film_grain(self, image, intensity: float, sharpening_factor: float):
        grain = Image.open('/var/home/user/stabdif/ComfyUI/custom_nodes/aaaa-WIP_comfy_postproc/assets/grain.png').convert('RGB')

        batch_size, height, width, _ = image.shape
        result = torch.zeros_like(image)

        for b in range(batch_size):
            im = Image.fromarray((image[b] * 255).to(torch.uint8).numpy(), mode='RGB')

            grain_w, grain_h = grain.size
            im_w, im_h = im.size

            # Determine the amount of times the grain is larger than the target image
            w_it = 1
            h_it = 1

            if (im_w > grain_w):
                w_it = math.ceil(im_w / grain_w)
            if (im_h > grain_h):
                h_it = math.ceil(im_h / grain_h)    

            # Create grain image larger than the size of the target image
            def repeat_width(im, column):
                im_int = Image.new('RGB', (im.width * column, im.height))
                for x in range(column):
                    im_int.paste(im, (x * im.width, 0))
                return im_int

            def repeat_height(im, row):
                im_int = Image.new('RGB', (im.width, im.height * row))
                for y in range(row):
                    im_int.paste(im, (0, y * im.height))
                return im_int

            def repeated_height_width(im, row, column):
                im_int = repeat_width(im, column)
                return repeat_height(im_int, row)
                
            new_grain = repeated_height_width(grain, h_it, w_it)

            new_grain = new_grain.crop((0, 0, im_w, im_h)) # Cut grain to target image size 
            
            enhancer = ImageEnhance.Sharpness(im) # Sharpen the image
            im = enhancer.enhance(sharpening_factor)
            
            new_im = Image.blend(im, new_grain, intensity) # Blend the target image with the grain (which reduces the brightness of the output)
            new_im = ImageOps.autocontrast(new_im.copy(), cutoff=0, preserve_tone=True) # Use Autocontrast to control for loss of brightness
            grained_im = torch.tensor(np.array(new_im.convert("RGB"))).float() / 255
            
            result[b] = grained_im
            
        return(result, )

NODE_CLASS_MAPPINGS = {
    "✨ Return DateString": ReturnDateString,
    "✨ Sharpen, RealGrain & Autocontrast": RealGrainAndAutocontrast,
    "✨ Apply HaldClut": ApplyHaldClut,
}
