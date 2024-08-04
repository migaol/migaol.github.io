import re
from typing import Tuple

def hex2rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def replace(text: str) -> str:
    hex_pattern = re.compile(r'#([0-9a-fA-F]{6})')

    def hex2rgb_str(match: re.Match) -> str:
        hex_color = match.group(0)
        rgb_color = hex2rgb(hex_color)
        return f'rgb{rgb_color}'
    
    return hex_pattern.sub(hex2rgb_str, text)

if __name__ == '__main__':
    input_file = '../_sass/colors/syntax-dark.scss'
    output_file = '../_sass/colors/syntax-dark.scss'

    with open(input_file, 'r') as file:
        content = file.read()

    converted_content = replace(content)

    with open(output_file, 'w') as file:
        file.write(converted_content)