from PIL import Image
import os

# List of directories containing the images
dirs = ["_out1", "_out2", "_out3", "_out4", "_out5", "_out6"]



# A set to hold all image file names
image_names = set()

# Collect all image file names
for dir in dirs:
    if os.path.exists(dir):
        for file in os.listdir(dir):
            if file.endswith('.png'):
                image_names.add(file)
    else:
        print(f"Directory {dir} does not exist.")

# For each image file name, open corresponding image from each directory and merge
for image_name in image_names:
    images = []
    for dir in dirs:
        file_path = os.path.join(dir, image_name)
        if os.path.exists(file_path):
            try:
                images.append(Image.open(file_path))
            except Exception as e:
                print(f"Could not open image at {file_path}, error: {e}")
        else:
            print(f"No file {image_name} in directory {dir}")

    if images:
        img_width = images[0].width
        img_height = images[0].height
        total_width = img_width * 3
        total_height = img_height * 2
        new_img = Image.new('RGB', (total_width, total_height))

        for i, img in enumerate(images):
            x_offset = (i % 3) * img_width
            y_offset = (i // 3) * img_height
            new_img.paste(img, (x_offset, y_offset))

        new_img.save(f"merged_{image_name}")
    else:
        print(f"No images loaded for {image_name}")

