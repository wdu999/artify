#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 17:25:54 2022

for drop shadow, refer: https://en.wikibooks.org/wiki/Python_Imaging_Library/Drop_Shadows

to simulate the artify: https://github.com/NghiaTranUIT/artify-macos

@author: weidu
"""

import os
import glob
import time
from PIL import Image, ImageFilter, ImageFile
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True  # to solve *** OSError: image file is truncated (2 bytes not processed)

for_imac = False
if for_imac:
    screen_x = 5760
    screen_y = 3240
else:
    screen_x = 2880
    screen_y = 1880
screen_ratio = screen_x / screen_y

menu_bar_height = 48  # 5K iMac menu bar height
shadow_border = 100
scale_for_retina = True

root_folder = '/Users/weidu/Pictures/art'
# museum = 'the Art Institute of Chicago'
# museum = 'the MET'
# museum = 'The Cleveland Museum of Art'
# museum = 'The British Museum'
# museum = '中华珍宝馆 油画风景'
museum = '中华珍宝馆'
# museum = 'temp'
image_file_path = os.path.join(root_folder, museum)

root_folder_output = '/Users/weidu/Pictures/art_wallpapers_with_shadow_{}x{}'.format(screen_x, screen_y)

image_file_path_output = os.path.join(root_folder_output, museum)

debug = False


def create_folder(p):
    ''' create folder if it doesn't exist
    '''
    if not os.path.exists(p):
        os.makedirs(p)
        print()
        print('creat folder: {}'.format(p))
        print()
    else:
        print()
        print('folder exist: {}'.format(p))
        print()


def get_images_list_from_folder(p):
    file_types = ('*.png', '*.jpg', '*.jpeg', '*.tif')

    images = []
    for f in file_types:
        images.extend(glob.glob(os.path.join(p, f)))

    return [os.path.basename(_) for _ in images]


def get_images_list_from_file(file):
    with open(file) as f:
        image_file_list = f.readlines()
        image_file_list = [line.strip() for line in image_file_list]

    return image_file_list


def scale(image):
    ''' scale up or scale down to fix width or hegith of the screen
    '''

    x, y = image.size

    if (x / y) > screen_ratio:
        new_image = image.resize((int(screen_y / y * x), screen_y))
    else:
        new_image = image.resize((screen_x, int(screen_x / x * y)))

    return new_image


def crop(image):
    ''' crop to the size of the screen
    '''
    x, y = image.size

    if x == screen_x:
        box = (0, int((y - screen_y) / 2), screen_x, int((y - screen_y) / 2) + screen_y)
    else:
        box = (int((x - screen_x) / 2), 0, int((x - screen_x) / 2) + screen_x, screen_y)

    return image.crop(box)


def image_thumbnail(image):
    x, y = image.size

    # scale = 3 / 4
    # scale = 0.85
    scale = 0.9

    new_image = image.copy()
    new_image.thumbnail((int(scale * screen_x) - 2 * shadow_border, int(scale * screen_y) - 2 * shadow_border))

    return new_image


def blur(image):
    ''' blur the background
    '''
    # return image.filter(ImageFilter.GaussianBlur(100))
    return image.filter(ImageFilter.BoxBlur(100))


def makeShadow(image, iterations, border, offset, backgroundColour, shadowColour):
    # image: base image to give a drop shadow
    # iterations: number of times to apply the blur filter to the shadow
    # border: border to give the image to leave space for the shadow
    # offset: offset of the shadow as [x,y]
    # backgroundCOlour: colour of the background
    # shadowColour: colour of the drop shadow

    # Calculate the size of the shadow's image
    fullWidth = image.size[0] + abs(offset[0]) + 2 * border
    fullHeight = image.size[1] + abs(offset[1]) + 2 * border

    # Create the shadow's image. Match the parent image's mode.
    # shadow = Image.new(image.mode, (fullWidth, fullHeight), backgroundColour)
    shadow = Image.new('RGBA', (fullWidth, fullHeight), backgroundColour)

    # Place the shadow, with the required offset
    shadowLeft = border + max(offset[0], 0)  # if <0, push the rest of the image right
    shadowTop = border + max(offset[1], 0)  # if <0, push the rest of the image down
    # Paste in the constant colour
    shadow.paste(
        shadowColour,
        [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]]
    )

    # Apply the BLUR filter repeatedly
    for i in range(iterations):
        shadow = shadow.filter(ImageFilter.BLUR)

    if debug:
        shadow.save('4_debug_thumbnail_shadow.png')

    # Paste the original image on top of the shadow
    imgLeft = border - min(offset[0], 0)  # if the shadow offset was <0, push right
    imgTop = border - min(offset[1], 0)  # if the shadow offset was <0, push down
    shadow.paste(image, (imgLeft, imgTop))

    return shadow


def generate_wallpaper_with_shadow(image_file):
    ''' 1. scale up or scale down the image to fix width or height of the screen
    2. crop it to the size of the screen
    3. blur it, use it as background
    4. scale it to proper size for
    5. make shadow
    6. paste the image with shadow to the background
    '''
    image = Image.open(image_file)
    x, y = image.size
    if debug:
        print('original image size: {}'.format(image.size))

    if scale_for_retina and ((x < screen_x * 2 / 3) or (y < screen_y * 2 / 3)):
        image = image.resize((2 * x, 2 * y))
        x, y = image.size

        if debug:
            print('original image size x 2: {}'.format(image.size))

    bg_scaled = scale(image)
    if debug:
        bg_scaled.save('0_debug_bg_scaled.jpg')
        print('scale image to screen as bg: {}'.format(bg_scaled.size))

    bg_cropped = crop(bg_scaled)
    if debug:
        bg_cropped.save('1_debug_bg_cropped.jpg')
        print('bg cropped: {}'.format(bg_cropped.size))

    bg_blurred = blur(bg_cropped)
    if debug:
        bg_blurred.save('2_debug_bg_blur.jpg')

    image_fitted = image_thumbnail(image)
    if debug:
        image_fitted.save('3_debug_thumbnail.jpg')
        print('image fitted: {}'.format(image_fitted.size))

    # image_with_shadow = makeShadow(image_fitted, iterations=200, border=shadow_border, offset=(0, 0), backgroundColour=0x000000, shadowColour=(0x00, 0x00, 0x00, 0xff))  # black
    # image_with_shadow = makeShadow(image_fitted, iterations=200, border=shadow_border, offset=(0, 0), backgroundColour=0x000000, shadowColour='#444444FF')  # grey
    image_with_shadow = makeShadow(image_fitted, iterations=50, border=shadow_border, offset=(0, 0), backgroundColour=0x000000, shadowColour='#808080FF')  # grey
    if debug:
        image_with_shadow.save('4_debug_thumbnail_with_shadow.png')
        print('image fitted + shadow: {}'.format(image_with_shadow.size))

    x, y = image_with_shadow.size
    position = (int((screen_x - x) / 2), int((screen_y - menu_bar_height - y) / 2 + menu_bar_height))
    if debug:
        print('past to bg, position: {}'.format(position))
    bg_blurred.paste(image_with_shadow, position, image_with_shadow)

    return bg_blurred


def generate_wallpapers():

    image_file_list = get_images_list_from_folder(image_file_path)
    # image_file_list = get_images_list_from_file('list.txt')

    n = len(image_file_list)

    create_folder(image_file_path_output)

    start_time = time.time()

    for i, image_file in enumerate(image_file_list):

        start = time.time()

        s = '{}/{} ---> {}'.format(i + 1, n, image_file)
        if debug:
            print()
            print('-' * len(s))
            print(s)
            print('-' * len(s))
            print()
        else:
            print('{} ... '.format(s), end='')

        # try:
        #     image = Image.open(image_file)
        # except DecompressionBombErrors:
        #     print()
        #     print('file size {:.2f}Mb, skip this file'.format(image_file_size))
        #     continue
        # image_file_size = os.path.getsize(os.path.join(image_file_path, image_file)) / (1024 * 1024)
        # image_file_size = os.path.getsize(os.path.join(image_file_path, image_file)) / (1000 * 1000)
        # if image_file_size > 100:
        #     print('file size {:.2f}Mb, skip this file'.format(image_file_size))
        #     continue

        wallpaper = generate_wallpaper_with_shadow(os.path.join(image_file_path, image_file))
        wallpaper.save(os.path.join(image_file_path_output, image_file))
        if debug:
            wallpaper.save('5_debug_final.jpg')
        # wallpaper.show()
        del wallpaper

        end = time.time()

        if debug:
            print()
            print('Runtime {:.2f} seconds'.format(end - start))
        else:
            print('{:.2f} seconds'.format(end - start), end='\n')

    print()
    print('Total Runtime {:.2f} minutes'.format((time.time() - start_time) / 60))


def main():
    generate_wallpapers()


if __name__ == '__main__':
    main()
