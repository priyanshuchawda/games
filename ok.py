from PIL import Image
import os

# Path to your images folder
folder_path = r"c:\Users\Admin\Desktop\tech_pc\games\assets\images"
os.makedirs(folder_path, exist_ok=True)

# List of placeholder file names
filenames = [
    "brickbaker.png",
    "pacman.png"  # Add Pacman icon
]

# Create simple 100x100 pixel placeholder images
for name in filenames:
    img = Image.new('RGB', (100, 100), color=(100, 100, 100))
    img.save(os.path.join(folder_path, name))
print("Placeholder PNGs created!")
