"""
Generate square icon (icon.png 512x512) and favicon.ico (multiple sizes)
Design: centered "TG" text, background #4e54c8, white text.
Run:
  pip install pillow
  python make_icon.py
Outputs: icon.png and favicon.ico in the current directory.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def make_square_icon(text="TG", bg="#4e54c8", fg="#ffffff", size=512, out_png="icon.png", out_ico="favicon.ico"):
    # Create base image
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)

    # Try to load a bold TTF, fall back to default
    font_size = int(size * 0.45)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    # Measure and draw text centered
    w, h = draw.textsize(text, font=font)
    draw.text(((size - w) / 2, (size - h) / 2), text, font=font, fill=fg)

    # Save PNG
    img.save(out_png)
    print(f"Saved {out_png} ({size}x{size})")

    # Save ICO with multiple embedded sizes
    sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
    img.save(out_ico, sizes=sizes)
    print(f"Saved {out_ico} with sizes: {', '.join(str(s[0]) for s in sizes)}")

if __name__ == '__main__':
    make_square_icon()