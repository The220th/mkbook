# -*- coding: utf-8 -*-

import PIL
import PIL.Image
import io
import math
from pdf2image import convert_from_path

class ImageHundler():

    def __init__(self, 
    pillow_img: "PIL.Image" = None,
    path: str = None, 
    img_bytes: bytes = None, 
    pdf_path: "first pdf-page" = None):
        vars = [path, img_bytes, pillow_img, pdf_path]
        c = 0
        for var_i in vars:
            if(var_i != None):
                c += 1
        if(c != 1):
            raise ValueError("Only one attr must be init")

        if(path != None):
            self.img = PIL.Image.open(path).convert("RGB")
        elif(img_bytes != None):
            self.img = PIL.Image.open(io.BytesIO(img_bytes))
        elif(pillow_img != None):
            self.img = pillow_img
        elif(pdf_path != None):
            self.img = convert_from_path(pdf_path, 500)[0]

    def get(self) -> "PIL.Image":
        return self.img

    def rotate90(self, left_right: bool = False):
        """
        left_right == False -> left
        left_right == True -> right
        """
        # https://pythonexamples.org/python-pillow-rotate-image-90-180-270-degrees/
        if(left_right == False):
            self.img = self.img.rotate(90, expand=True)
        else:
            self.img = self.img.rotate(-90, expand=True)
    
    def append_2right(self, second_image: "PIL.Image"):
        img_size = self.img.size
        if(img_size[0] != second_image.size[0]
        or img_size[1] != second_image.size[1]):
            raise ValueError(f"Images must be same size: 1={self.img.size}, 2={second_image.size}")
        
        img1 = self.img.copy()
        img2 = second_image.copy()
        img3 = PIL.Image.new(self.img.mode, (img_size[0]*2, img_size[1]), "white")
        img3.paste(img1, (0, 0))
        img3.paste(img2, (img_size[0], 0))

        self.img = img3

    def resize_4A4_fill(self):
        img_size = self.img.size
        if(img_size[0] > img_size[1]): # horizontally
            new_param = int(img_size[0]/math.sqrt(2) + 0.5)
            new_size = (img_size[0], new_param)
        else: # vertically
            new_param = int(img_size[1]/math.sqrt(2) + 0.5)
            new_size = (new_param, img_size[1])
        self.img = self.img.resize(new_size, PIL.Image.Resampling.NEAREST)

    def get_as_empty(self) -> "PIL.Image":
        return PIL.Image.new(self.img.mode, self.img.size, "white")
    
    def resize(self, new_size: tuple):
        self.img = self.img.resize(new_size, PIL.Image.Resampling.NEAREST)