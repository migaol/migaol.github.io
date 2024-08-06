'''Generate graph representations of flow puzzles.'''

from manim import *

COLORS = {
    ".": rgb_to_color((96, 96, 96)), # empty / gray
    "R": rgb_to_color((234,  51,  35)), # red
    "G": rgb_to_color(( 61, 138,  38)), # green
    "B": rgb_to_color(( 20,  40, 245)), # blue
    "Y": rgb_to_color((232, 223,  73)), # yellow
    "O": rgb_to_color((235, 142,  52)), # orange
    "C": rgb_to_color((117, 251, 253)), # cyan
    "M": rgb_to_color((234,  53, 193)), # magenta
    "m": rgb_to_color((151,  52,  48)), # maroon
    "P": rgb_to_color((116,  20, 123)), # purple
    "W": rgb_to_color((255, 255, 255))  # white
}

def from_txt(fname: str):
    with open(fname, 'r') as file:
        grid = [list(row.strip()) for row in file]
    return grid

class GridGraph(Scene):
    def construct(self):
        self.camera.frame_width = self.camera.frame_height = grid_size = 10
        grid = from_txt('puzzle.txt')

        radius = 0.35
        spacing = 1

        # center offset
        x_offset = - (grid_size - 1) * spacing / 2
        y_offset = - (grid_size - 1) * spacing / 2

        circles: List[Circle] = []
        for r in range(grid_size):
            for c in range(grid_size):
                color = COLORS.get(grid[c][r], WHITE)
                circle = Circle(radius=radius, color=color)
                if not grid[c][r] == ".": circle.set_fill(color, opacity=1)
                circle.move_to(np.array([r * spacing + x_offset, (grid_size - 1 - c) * spacing + y_offset, 0])) # invert coords
                circles.append(circle)

        edges = []
        for r in range(grid_size):
            for c in range(grid_size):
                if r < grid_size - 1: # horizontal
                    line = Line(circles[r * grid_size + c].get_center() + np.array([radius, 0, 0]),
                                circles[(r+1) * grid_size + c].get_center() + np.array([-radius, 0, 0]),
                                color=COLORS["."])
                    edges.append(line)
                if c < grid_size - 1: # vertical
                    line = Line(circles[r * grid_size + c].get_center() + np.array([0, -radius, 0]),
                                circles[r * grid_size + (c+1)].get_center() + np.array([0, radius, 0]), color=COLORS["."])
                    edges.append(line)

        self.add(*edges)
        self.add(*circles)

        self.wait(2)

'''
manim -s -r 1200,1200 flow2graph.py GridGraph    
'''