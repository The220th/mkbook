# -*- coding: utf-8 -*-

import argparse
import sys
import os

from pdf2image import convert_from_path as pdf_convert_from_path

from img_hundler import ImageHundler

def init_args(args: list) -> "ArgumentParser":
    parser = argparse.ArgumentParser(prog = "mkbook",
        description="Make book from pdf to print.")
    parser.add_argument("pdf_in", type=str, nargs=1,
                        help="Path to source pdf.")
    parser.add_argument("pdf_out", type=str, nargs=1,
                        help="Path to output pdf")
    parser.add_argument("--dpi", type=int, default=500, required=False,
                        help="More value means better quality, but larger file size.")
    parser.add_argument("--rotate_left", default=True, action='store_false',
                        help="When rotating landscape (horizontally) sheets, rotate them to the left (counterclockwise).")
    args = parser.parse_args(args[1:])

    return args

def solve_transform(imgs: list, args: list) -> list:
    left_right = not args.rotate_left
    for i, img_i in enumerate(imgs):
        new_img = ImageHundler(img_i)
        new_img.resize_4A4_fill()
        img_size = new_img.get().size
        if(img_size[0] > img_size[1]): # landscape
            new_img.rotate90(left_right)
        imgs[i] = new_img.get()
    
    max_w = max(imgs, key=lambda x:x.size[0]).size[0]
    max_h = int(max_w* (2**(0.5)) + 0.5)
    res = []
    for img_i in imgs:
        buff = ImageHundler(img_i)
        buff.resize((max_w, max_h))
        res.append(buff.get())

    return res

def fill_4(imgs: list) -> list:
    c = len(imgs)
    if(c % 4 == 0):
        return imgs
    else:
        buff = ImageHundler(imgs[0])
        diff = 4 - (c % 4)
        return imgs + [buff.get_as_empty() for _ in range(diff)]

def split(imgs: list) -> "([odd], [even])":
    odd, even = [], []
    for i, img_i in enumerate(imgs):
        if((i+1)%2 == 1): # odd
            odd.append(img_i)
        else: # even
            even.append(img_i)
    return (odd, even)

def A5_A4(imgs: list, odd_even: bool = False) -> list:
    """
    odd_even == False -> odd
    odd_even == True -> even
    """
    c = len(imgs)
    if(c % 2 != 0):
        raise ValueError(f"Len ({c}) of imgs must be even! ")

    res = []
    for i in range(c//2):
        img_l, img_r = imgs[i], imgs[c-1-i]
        if(odd_even == True):
            img_l, img_r = img_r, img_l
        img_l = ImageHundler(img_l)
        img_l.append_2right(img_r)
        res.append(img_l.get())
    return res

if __name__ == '__main__':
    """
    1. Получить все листы из pdf, как png.
    2. Сделать их все формата AX (1:1.41).
    3. Сделать все листы портретными.
    4. Добавить пустых листов, чтобы их кол-во было кратно 4.
    5. Делаем 2 множества: чётных и нечётных.
    6. Соединяем (append_2right) элементы этих множеств.
    7. Сохраняем
    """
    args = init_args(sys.argv)
    pdf_in = os.path.abspath(args.pdf_in[0])
    pdf_out = os.path.abspath(args.pdf_out[0])
    dpi = args.dpi
    imgs = pdf_convert_from_path(pdf_in, dpi)
    if(len(imgs) <= 0):
        print(f"\"pdf_in\" has {len(imgs)} pages. Exitting...")
        exit()

    imgs = solve_transform(imgs, args)
    
    imgs = fill_4(imgs)

    imgs_odd, imgs_even = split(imgs)

    imgs_odd = A5_A4(imgs_odd, False)
    imgs_even = A5_A4(imgs_even, True)

    imgs = imgs_odd + imgs_even # add mirror and insert

    imgs[0].save("test.pdf", save_all=True, append_images=imgs[1:])

    print("DONE!")