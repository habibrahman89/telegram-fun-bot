from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_welcome_image(user):
    bg = Image.open(os.path.join(ASSETS_DIR, "welcome_bg.png")).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # Use Windows system font
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font = ImageFont.truetype(font_path, 40)

    draw.text((50, 50), f"Welcome {user.first_name}", fill="white", font=font)

    output_path = os.path.join(OUTPUT_DIR, f"welcome_{user.id}.png")
    bg.save(output_path)

    return output_path