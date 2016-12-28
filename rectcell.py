


from PIL import Image, ImageDraw
import numpy as np
from colorpalette import ColorPalette
import random
import matplotlib.pyplot as plt
import util
from cell import Cell

class RectCell(Cell):
    def __init__(self, size=(200,200), csize=(200,200), base_color=(0,0,0), second_color=(0,0,0), n=4, sn=1):

        self.width = size[0]
        self.height = size[1]
        self.cwidth = csize[0]
        self.cheight = csize[1]
        self.base_color = base_color

        self.colors = Cell.gen_colors(base_color, n)
        self.colors_secondary = Cell.gen_colors(second_color,sn)


    @staticmethod
    def find_best(img, n=2, sn=2):
        second_color,base_color = ColorPalette.quantize_img(img, 2)

        color_combos = [[base_color, second_color], [second_color, base_color]]

        width,height = img.size
        best_rcell = None
        best_score = 10000

        w = width 
        h = height

        # XXX: will cause probs if image size is less than 10 pixels
        for w in range(width-10, width):
            for h in range(height-10, height):

                for color_combo in color_combos:
                    for i in range(2):
                        h = w
                        rcell = RectCell(size=(width,height), csize=(w,h), 
                            base_color=color_combo[0], second_color=color_combo[1], 
                            n=n, sn=sn)

                        cimg = rcell.draw()
                        score = util.rmsdiff(img, cimg)
                        if score <= best_score:
                            best_rcell = rcell
                            best_score = score

        return best_rcell

    # return the perceived hue / luminance for now
    def draw(self):
        paper = Image.new('RGBA', (self.width, self.height))
        canvas = ImageDraw.Draw(paper)

        pw = 6#(self.width/len(self.colors))/3
        if random.randrange(2):
            self.colors = list(reversed(self.colors))
            
        if len(self.colors)>=3:
            self.colors[1], self.colors[2] = self.colors[2], self.colors[1]

        """
        draw border square
        """
        for idx, color in enumerate(self.colors_secondary):
            paper.paste(color, [pw*idx,pw*idx, self.width-pw*idx, self.height-pw*idx])

        """
        draw rect
        """
        for idx, color in enumerate(self.colors):
            color = int(color[0]),int(color[1]),int(color[2])
            sx = int(round(len(self.colors)*pw/2))
            sx += (pw*idx)
            sy = int(round(len(self.colors)*pw/2))
            sy += (pw*idx)
            ex = self.width - sx
            ey = self.height - sy
            paper.paste(color, [sx, sy, ex, ey])

        return paper






