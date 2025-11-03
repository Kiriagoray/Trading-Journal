"""
Generate favicon for Trading Journal application
Creates a modern, minimalist trading dashboard themed favicon
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Color definitions
DARK_NAVY = (26, 26, 46)  # #1a1a2e - dark navy background
CHARCOAL = (30, 30, 40)    # #1e1e28 - alternative dark
EMERALD_GREEN = (0, 255, 176)  # #00ffb0 - emerald green accent
AQUA_BLUE = (0, 230, 255)      # #00e6ff - aqua blue accent
LIGHT_GRAY = (240, 240, 245)   # For light mode variant
WHITE = (255, 255, 255)

def create_favicon_design(size=512, color_scheme='dark'):
    """Create the favicon design"""
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background
    bg_color = DARK_NAVY if color_scheme == 'dark' else LIGHT_GRAY
    draw.rectangle([0, 0, size, size], fill=bg_color)
    
    # Grid pattern (subtle matrix effect)
    grid_spacing = size // 8
    grid_color = (40, 40, 60, 80) if color_scheme == 'dark' else (200, 200, 210, 60)
    
    for i in range(1, 8):
        # Vertical lines
        draw.line([(i * grid_spacing, 0), (i * grid_spacing, size)], 
                 fill=grid_color, width=1)
        # Horizontal lines
        draw.line([(0, i * grid_spacing), (size, i * grid_spacing)], 
                 fill=grid_color, width=1)
    
    # Main accent color (emerald green for trading feel)
    accent_color = EMERALD_GREEN if color_scheme == 'dark' else (0, 180, 140)
    
    # Draw stylized "T" letter with trading elements
    center_x, center_y = size // 2, size // 2
    thickness = size // 12
    
    # Horizontal bar of "T" (top)
    bar_width = size // 2.5
    bar_y = center_y - size // 4
    draw.rectangle([
        center_x - bar_width // 2, bar_y - thickness // 2,
        center_x + bar_width // 2, bar_y + thickness // 2
    ], fill=accent_color)
    
    # Vertical bar of "T" (center)
    draw.rectangle([
        center_x - thickness // 2, bar_y - thickness // 2,
        center_x + thickness // 2, center_y + size // 6
    ], fill=accent_color)
    
    # Add graph/candlestick elements around the T
    # Right side - ascending trend line
    line_color = AQUA_BLUE if color_scheme == 'dark' else (0, 160, 200)
    points_right = [
        (center_x + size // 3, center_y),
        (center_x + size // 2.2, center_y - size // 6),
        (center_x + size // 2.2, center_y - size // 8),
    ]
    if len(points_right) >= 2:
        for i in range(len(points_right) - 1):
            draw.line([points_right[i], points_right[i+1]], 
                     fill=line_color, width=size//50)
    
    # Left side - candlestick representation
    candle_width = size // 25
    candle_x = center_x - size // 2.5
    candle_base = center_y + size // 8
    candle_height = size // 6
    
    # Candlestick body
    draw.rectangle([
        candle_x - candle_width, candle_base - candle_height,
        candle_x + candle_width, candle_base
    ], fill=line_color)
    
    # Candlestick wick
    draw.line([
        (candle_x, candle_base),
        (candle_x, candle_base + size // 12)
    ], fill=line_color, width=size//80)
    
    # Add small accent dots for tech feel
    dot_size = size // 30
    dots_positions = [
        (size // 6, size // 6),
        (size * 5 // 6, size // 6),
        (size // 6, size * 5 // 6),
        (size * 5 // 6, size * 5 // 6),
    ]
    
    for dot_x, dot_y in dots_positions:
        draw.ellipse([
            dot_x - dot_size, dot_y - dot_size,
            dot_x + dot_size, dot_y + dot_size
        ], fill=accent_color)
    
    return img

def generate_favicon_files():
    """Generate both PNG and ICO favicon files"""
    # Ensure directories exist
    static_images_dir = os.path.join('static', 'images')
    os.makedirs(static_images_dir, exist_ok=True)
    
    # Generate 512x512 PNG (for high-res displays)
    print("Generating 512x512 PNG favicon...")
    favicon_512 = create_favicon_design(512, 'dark')
    png_path = os.path.join(static_images_dir, 'favicon-512x512.png')
    favicon_512.save(png_path, 'PNG')
    print(f"[OK] Created: {png_path}")
    
    # Generate 32x32 ICO (standard favicon)
    print("Generating 32x32 ICO favicon...")
    favicon_32 = create_favicon_design(32, 'dark')
    ico_path = os.path.join(static_images_dir, 'favicon.ico')
    
    # ICO format requires multiple sizes, so we'll save as PNG and convert
    # For now, save as ICO (PIL supports ICO)
    favicon_32.save(ico_path, 'ICO', sizes=[(32, 32)])
    print(f"[OK] Created: {ico_path}")
    
    # Also create additional sizes for better browser support
    sizes = [16, 32, 48, 64, 96, 128, 256]
    for size in sizes:
        favicon = create_favicon_design(size, 'dark')
        favicon_path = os.path.join(static_images_dir, f'favicon-{size}x{size}.png')
        favicon.save(favicon_path, 'PNG')
    
    print(f"[OK] Created additional sizes: {', '.join([f'{s}x{s}' for s in sizes])}")
    print("\n[SUCCESS] Favicon generation complete!")
    return png_path, ico_path

if __name__ == '__main__':
    try:
        generate_favicon_files()
    except Exception as e:
        print(f"Error generating favicon: {e}")
        print("\nNote: This script requires the Pillow library.")
        print("Install it with: pip install Pillow")

