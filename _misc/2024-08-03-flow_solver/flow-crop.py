'''Crop screenshots of flow puzzles.'''

from PIL import Image
from typing import List
import os

# board only: 583
# include pipe%: -
def crop_image(fname: str, crop_top=583, final_size=(1125, 1125)):
    with Image.open(fname) as img:
        l = 0
        u = crop_top
        r = final_size[0]
        d = final_size[1] + crop_top

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
    folder = '../../assets/img/2024-08-03-flow_solver'
    to_edit = ['puzzle3-blank']
    ext = '.jpg'
    main(folder, to_edit, ext)