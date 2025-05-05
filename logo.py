from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image_data = None
        self.bbox = None

    def load_image(self):
        img = Image.open(self.image_path)
        self.image_data = np.asarray(img)

    def threshold(self, threshold:int=125):
        image_data_thresh = self.image_data.copy()

        for row in range(image_data_thresh.shape[0]):
            for col in range(image_data_thresh.shape[1]):
                rgba = image_data_thresh[row][col]
                if not all(i == 255 for i in rgba):
                    if rgba[0] < threshold and rgba[1] < threshold and rgba[2] < threshold:
                        image_data_thresh[row][col][0:3] = [0, 0, 0]
                    else:
                        image_data_thresh[row][col][0:3] = [255, 255, 255]

        self.image_data = image_data_thresh

    def trim_whitespace(self):
        rows = []
        cols = []
        n_pixels = 0

        for row in range(self.image_data.shape[0]):
            for col in range(self.image_data.shape[1]):
                rgba = self.image_data[row][col]
                if not all(i == 255 for i in rgba):
                    rows.append(row)
                    cols.append(col)
                    n_pixels += 1

        self.bbox = (min(rows), min(cols), max(rows), max(cols))

        image_data_cropped = self.image_data[self.bbox[0]:self.bbox[2]+1, self.bbox[1]:self.bbox[3]+1]
        return image_data_cropped, n_pixels

class ColorGenerator:
    def generate_hex_colors(self, n_points):
        t = [0, 0.2, 0.4, 0.6, 0.8, 1]
        f_r = [255, 255, 0, 0, 0, 0]
        f_g = [0, 0, 0, 255, 255, 0]
        f_b = [0, 255, 255, 0, 255, 0]

        t_new = np.linspace(0, 1, n_points)
        r = np.interp(t_new, t, f_r).astype(int)
        g = np.interp(t_new, t, f_g).astype(int)
        b = np.interp(t_new, t, f_b).astype(int)

        hex_colors = []
        for i in range(n_points):
            hex_colors.append(f"{r[i]:02x}{g[i]:02x}{b[i]:02x}")

        return hex_colors

class SvgGenerator:
    def __init__(self, image_data, pixel_pitch):
        self.image_data = image_data
        self.pixel_pitch = pixel_pitch
        self.svg_string = ""

        html_preamble = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>create SVG landing in HTML from a PNG</title>
    <style>
        body {
            font-family:'Lucida Console', monospace;
            font-size: 18px;
            color: #111;
            background-color: white;
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 50px;
            box-sizing: border-box;
        }
        .landing {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height:100vh; min-height:100dvh;
            text-align: center;
        }
        svg { width: 100%; height: auto; }
        .svg-container { width: 100%; max-width: 800px; display: inline-block; }
        .separator { letter-spacing: -9px; }
    </style>
</head>
<body>
  <div class="landing">
    <div class="svg-container">"""

        self.svg_string = html_preamble + f"""<svg viewBox="0 0 {self.image_data.shape[1]*self.pixel_pitch} {self.image_data.shape[0]*self.pixel_pitch}" xmlns="http://www.w3.org/2000/svg">"""

    def add_svg_pixels(self, pixel_size, hex_colors):
        offset = np.floor((self.pixel_pitch - pixel_size) / 2)

        for col in range(self.image_data.shape[1]):    
            for row in range(self.image_data.shape[0]):
                rgba = self.image_data[row][col]

                if not all(i == 255 for i in rgba):
                    if type(hex_colors) == list:
                        color = hex_colors.pop(0)
                    else:
                        color = hex_colors

                    self.svg_string += f"""\n\t<rect x="{col*self.pixel_pitch+offset}" y="{row*self.pixel_pitch+offset}" width="{pixel_size}" height="{pixel_size}" fill="#{color}"/>"""

    def finalize_svg(self):
        self.svg_string += "\n</svg>\n</div>\n</body>\n</html>"

        return self.svg_string

def main():
    image_path = "test2.png"
    processor = ImageProcessor(image_path)
    processor.load_image()
    processor.threshold(threshold=220)
    cropped_image, n_pixels = processor.trim_whitespace()

    hex_colors = ColorGenerator().generate_hex_colors(n_pixels)

    svg_generator = SvgGenerator(image_data=cropped_image, pixel_pitch=14)
    svg_generator.add_svg_pixels(pixel_size=13, hex_colors='000000')
    svg_generator.add_svg_pixels(pixel_size=11, hex_colors=hex_colors)
    html_string = svg_generator.finalize_svg()

    with open("output.html", "w") as f:
        f.write(html_string)

if __name__ == "__main__":
    main()