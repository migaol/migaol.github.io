from PIL import Image
from typing import List
import os

def crop_image(fname: str, crop_size=(1125, 1557)):
    with Image.open(fname) as img:
        l = 0
        u = 0
        r = min(crop_size[0], img.width)
        d = min(crop_size[1], img.height)

        cropped_img = img.crop((l, u, r, d))
        cropped_img.save(fname)

def main(folder: str, to_edit: List[str], ext):
    for fname in to_edit:
        fname = os.path.join(folder, fname + ext)
        if not fname:
            print(f'File not found: {fname}')
            continue
        crop_image(fname)

if __name__ == '__main__':
    folder = '../assets/img/2024-08-03-flow_solver'
    to_edit = ['large_pipe_pct']
    ext = '.jpg'
    main(folder, to_edit, ext)