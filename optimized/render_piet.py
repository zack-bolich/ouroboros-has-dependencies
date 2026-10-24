"""Create GitHub-friendly views of the canonical Piet raster. Requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
source = Image.open(ROOT / 'optimized/seven.ppm').convert('RGB')
assets = ROOT / 'assets'
assets.mkdir(exist_ok=True)
source.save(assets / 'piet-program.png', optimize=True)
# Fold the complete strip into labelled rows; this changes execution geometry.
chunk, margin, top, zoom_y, gap = 4096, 92, 58, 4, 7
rows = (source.width + chunk - 1) // chunk
row_height = source.height * zoom_y
preview = Image.new('RGB', (margin + chunk + 20, top + rows * (row_height + gap) + 16), '#101622')
draw = ImageDraw.Draw(preview)
draw.text((16, 12), f'PIET PROGRAM: {source.width:,} x {source.height} codels', fill='#f7edcf')
draw.text((16, 30), 'Entire raster folded left-to-right, top-to-bottom. Preview only; execute the original strip.', fill='#a8b9cd')
for row, start in enumerate(range(0, source.width, chunk)):
    end = min(start + chunk, source.width)
    part = source.crop((start, 0, end, source.height))
    part = part.resize((part.width, row_height), Image.Resampling.NEAREST)
    y = top + row * (row_height + gap)
    preview.paste(part, (margin, y))
    draw.text((12, y), f'{start:06d}', fill='#a8b9cd')
preview.save(assets / 'piet-overview.png', optimize=True)
assert Image.open(assets / 'piet-program.png').convert('RGB').tobytes() == source.tobytes()
print('Saved pixel-identical PNG and folded overview:', source.size)
