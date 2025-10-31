#!/usr/bin/env python3
"""
Simple icon generator for PWA
Creates basic colored squares as placeholder icons
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available, creating simple HTML-based icons")

import os

def create_simple_icon(size, filename):
    """Create a simple colored square icon"""
    if PIL_AVAILABLE:
        # Create image with PIL
        img = Image.new('RGB', (size, size), color='#007bff')
        draw = ImageDraw.Draw(img)
        
        # Add white circle
        margin = size // 6
        draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
        
        # Add "TL" text if size is large enough
        if size >= 72:
            try:
                font_size = size // 4
                font = ImageFont.load_default()
                text = "TL"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                draw.text((x, y), text, fill='#007bff', font=font)
            except:
                pass
        
        img.save(filename, 'PNG')
        print(f"Created {filename} ({size}x{size})")
    else:
        # Create SVG as fallback
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" fill="#007bff"/>
  <circle cx="{size//2}" cy="{size//2}" r="{size//3}" fill="white"/>
  <text x="{size//2}" y="{size//2 + size//12}" text-anchor="middle" fill="#007bff" font-family="Arial, sans-serif" font-size="{size//4}" font-weight="bold">TL</text>
</svg>'''
        
        # Convert SVG filename to PNG
        png_filename = filename.replace('.svg', '.png')
        with open(png_filename, 'w') as f:
            f.write(svg_content)
        print(f"Created {png_filename} ({size}x{size}) as SVG")

def main():
    # Icon sizes for PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    icons_dir = os.path.dirname(os.path.abspath(__file__))
    
    for size in sizes:
        filename = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        create_simple_icon(size, filename)
    
    print(f"\nGenerated {len(sizes)} icons in {icons_dir}")
    print("Note: These are placeholder icons. Replace with your actual app icons for production.")

if __name__ == '__main__':
    main()