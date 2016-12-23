

import util 

from PIL import Image, ImageDraw
from warped import Warped
from comp import CompColor
from trianglecell import TriangleCell
from circlecell import CircleCell
from rectcell import RectCell
from pieslicecell import PieSliceCell
from halfcirclecell import HalfCircleCell
from skimage.color import rgb2grey
from skimage import io, feature
import numpy as np
from enum import Enum
from colorpalette import ColorPalette
import random 
    

"""
x - double half circle cells
x - refactor to put find best shapes in method
x - rotated 45 deg circles.
- 
"""
class Grid():
    def __init__(self, imgpath, pix):
        self.pixels = pix
        self.og_image = Image.open(imgpath)
        self.image = Image.new('RGB', self.og_image.size)
        self.draw = ImageDraw.Draw(self.image, 'RGBA')

        self.image_array = io.imread(imgpath)
        self.img_edges = feature.canny(rgb2grey(self.image_array), sigma=4)

        self.width,self.height = self.image.size
        
        self.color_palette = ColorPalette(imgpath, 4)

        self.cols = (self.width/self.pixels)
        self.rows = (self.height/self.pixels)
        self.grid_status = np.zeros([self.width/self.pixels, self.height/self.pixels])

    # By default we occupy one cell at a time.  x_total is number of additional horizontal
    # cells to occupy.  Vertical is number of additional vertical cells
    def occupy(self, x, y, x_total=1, y_total=1):
        for i in range(x_total):
            for j in range(y_total):
                if  x+i < self.width/self.pixels and y+j < self.height/self.pixels:
                    self.grid_status[x+i][y+j] = 1

    # Test vertical expansion
    def is_occupied(self, x, y):
        return self.grid_status[x][y] == 1

    def get_slope(self, img_seg):
        # if len(img_seg[img_seg==True]) > len(img_seg[img_seg==False])/50:
        if len(img_seg[img_seg==True]):
            x,y = np.where(img_seg==True)

            slope,_ = np.polyfit(x,y,1)

            if np.isnan(slope):
                return None

            return slope

    def best_shape(self, cropped_img):
        circle = CircleCell.find_best(cropped_img, n=3, sn=2)
        rect = RectCell.find_best(cropped_img, n=2, sn=2)
        triangle = TriangleCell.find_best(cropped_img, n=3, sn=2)
        pie = PieSliceCell.find_best(cropped_img, n=3, sn=2)
        halfc = HalfCircleCell.find_best(cropped_img, n=3, sn=2)

        circle_rms = util.rmsdiff(cropped_img, circle.draw())
        rect_rms = util.rmsdiff(cropped_img, rect.draw())
        triangle_rms = util.rmsdiff(cropped_img, triangle.draw())
        pie_rms = util.rmsdiff(cropped_img, pie.draw())+.1
        halfc_rms = util.rmsdiff(cropped_img, halfc.draw())
        
        shapes = [circle, rect, triangle, pie, halfc]
        rms_list = [circle_rms, rect_rms, triangle_rms, pie_rms, halfc_rms]
        shape = shapes[rms_list.index(min(rms_list))]
        return shape


    def n_pass(self, n_total=1):
        width,height = self.image.size
        pix = self.pixels


        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_occupied(col,row):
                    pix_w, pix_h = (pix, pix)

                    # create rect coords:
                    # if random.randint(0,50)==1:
                    #     pix_w, pix_h = (pix*2, pix*1)
                    # elif random.randint(0,50)==1:
                    #     pix_w, pix_h = (pix, pix*2)
                    # else:
                    #     pix_w, pix_h = (pix, pix)

                    x,y = col*pix, row*pix
                    rect_coords = [
                        x, y, 
                        util.clamp_int(x+pix_w, 0, width), util.clamp_int(y+pix_h, 0, height)
                    ]
                    #XXX: move colorpalette to TriangleCell.. same with shrink calc
                    og_color = util.average_color(self.og_image, rect=rect_coords)

                    edges_seg = self.img_edges[y:y+pix_w,x:x+pix_h]
                    if np.any(edges_seg) and len(np.where(edges_seg)[1]):
                        cropped_img = self.og_image.crop(rect_coords)

                        shape = self.best_shape(cropped_img)

                        if isinstance(shape, TriangleCell):
                            area = edges_seg.shape[0]*edges_seg.shape[1]
                            percent = (len(np.where(edges_seg)[1])*2)/float(area)
                            if percent <= .2:
                                shape.shrink = 1
                            if percent <= .1:
                                shape.shrink = 2
                        # else:
                        #     shape = circle

                        if random.randint(0,1):
                            """
                            vertical 
                            """
                            img = shape.draw()
                            rect_coords2 = rect_coords[:]
                            rect_coords2[1] = rect_coords2[1] + pix
                            rect_coords2[3] = util.clamp_int(rect_coords2[3] + pix, 0, height)
                            cropped_img2 = self.og_image.crop(rect_coords2)
                            rms_v = util.rmsdiff(cropped_img, cropped_img2)
                            if rms_v < 40:
                                bg,fg = ColorPalette.quantize_img(cropped_img, 2)
                                csize_w, csize_h = (pix-7,2*pix-7)
                                pix_h*=2
                                rect_coords3 = [rect_coords[0], rect_coords[1], rect_coords2[2], rect_coords2[3]]
                                big_crop_img = self.og_image.crop(rect_coords3)

                                shape = self.best_shape(big_crop_img)
                                img = shape.draw()


                        else:
                            """
                            horizontal 
                            """
                            pix_w,pix_h=pix,pix
                            img = shape.draw()
                            rect_coords2 = rect_coords[:]
                            rect_coords2[0] = rect_coords2[0] + pix
                            rect_coords2[2] = util.clamp_int(rect_coords2[2] + pix, 0, width)
                            cropped_img2 = self.og_image.crop(rect_coords2)
                            rms_v = util.rmsdiff(cropped_img, cropped_img2)
                            if rms_v < 40:
                                pix_w*=2
                                rect_coords3 = [rect_coords[0], rect_coords[1], rect_coords2[2], rect_coords2[3]]
                                big_crop_img = self.og_image.crop(rect_coords3)


                                shape = self.best_shape(big_crop_img)
                                img = shape.draw()

                        # """
                        # big triangle
                        # """
                        # if best_shape == TriangleCell:
                        #     # import pdb; pdb.set_trace()
                        #     pix_w,pix_h=pix,pix
                        #     img = shape.draw()
                        #     rect_coords2 = rect_coords[:]
                        #     rect_coords2[0] = rect_coords2[0] + pix #sx
                        #     rect_coords2[1] = rect_coords2[1] + pix #sy
                        #     rect_coords2[2] = util.clamp_int(rect_coords2[2] + pix, 0, width)
                        #     rect_coords2[3] = util.clamp_int(rect_coords2[3] + pix, 0, height)
                        #     cropped_img2 = self.og_image.crop(rect_coords2)

                        #     rms_v = util.rmsdiff(cropped_img, cropped_img2)

                        #     rect_coords3 = [rect_coords[0], rect_coords[1], rect_coords2[2], rect_coords2[3]]
                        #     big_crop_img = self.og_image.crop(rect_coords3)
                        #     if rms_v < 80:
                        #         bg,fg = ColorPalette.quantize_img(big_crop_img, 2)
                        #         csize_w, csize_h = (2*pix-7, 2*pix-7)
                        #         pix_w*=2
                        #         pix_h*=2
                        #         shape = TriangleCell.find_best(big_crop_img, n=1, sn=1)
                        #         img=shape.draw()

                                # import pdb; pdb.set_trace()

                    else:
                        ccolor = CompColor(size=(pix_w, pix_h), base_color=og_color, n=4)
                        img = ccolor.draw()

                    self.og_image.paste(img, (x,y))
                    self.occupy(col,row,pix_w/pix,pix_h/pix)

        self.og_image.show()
        self.og_image.save("out.JPEG", "jpeg", icc_profile=self.og_image.info.get('icc_profile'), quality=95, dpi=(200,200))
        import pdb; pdb.set_trace()


    def warp(self):
        width,height = self.image.size
        # print width,height
        pix = self.pixels

        for w in range(width/pix):
            for h in range(height/pix):
                if not self.is_occupied(w,h):

                    if random.randint(0,50)==1:
                        pix_w, pix_h = (pix*2, pix*1)
                    elif random.randint(0,50)==1:
                        pix_w, pix_h = (pix, pix*2)
                    else:
                        pix_w, pix_h = (pix, pix)

                    # create rect coords:
                    x,y = w*pix, h*pix
                    rect_coords = [
                        x, y, 
                        util.clamp_int(x+pix_w, 0, width), util.clamp_int(y+pix_h, 0, height)
                    ]
                    # img_seg = self.img_edges[y:y+pix_w,x:x+pix_h]
                    # slope = self.get_slope(img_seg)
                    slope = None
                    
                    if slope:
                        pass
                        # x_line,y_line = np.where(img_seg==True)
                        # prim_color = util.average_color_pixels(self.og_image, zip(x_line+x, y_line+y))

                        # x_bg,y_bg = np.where(img_seg==False)
                        # bg_color = util.average_color_pixels(self.og_image, zip(x_bg+x,y_bg+y))

                        # warped_rect = Warped(size=(pix,pix), fg_color=prim_color, bg_color=bg_color)
                        # img = warped_rect.draw(slope)

                        # # t_rect = TriangleCell(size=(pix,pix), fg_color=prim_color, bg_color=bg_color)
                        # # img = t_rect.draw(slope)

                        # self.image.paste(img, (w*pix,h*pix))
                        # self.og_image.paste(img, (w*pix,h*pix))

                    else:
                        color = util.average_color(self.og_image, rect=rect_coords)
                        # color = self.color_palette.translate_color(color)
                        color = np.asarray(color)/float(255)
                        color = color.reshape(1,-1)
                        label = self.color_palette.kmeans.predict(color)
                            

                        warped_rect = CompColor(size=(pix_w, pix_h), label=label)
                        img = warped_rect.draw()
                        # self.image.paste(img,    (w*pix, h*pix))
                        self.og_image.paste(img, (w*pix, h*pix))

                       

                        self.occupy(w,h,pix_w/pix,pix_h/pix)

            # if w%38 == 0:
            #     self.og_image.show()
            #     import pdb; pdb.set_trace()

        self.og_image.show()
