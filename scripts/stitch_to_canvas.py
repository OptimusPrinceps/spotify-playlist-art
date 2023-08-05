from PIL import Image
import os

def resize_images(directory):
    # List all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Filter only image files
    img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    img_objs = []

    # Resize each image to 512x512 and store in img_objs list
    for img_file in img_files:
        with Image.open(os.path.join(directory, img_file)) as img:
            img_objs.append(img.resize((512, 512)))

    return img_objs

def stitch_images(images, margin=10):
    # Number of images
    num_images = len(images)

    # Calculate canvas size
    canvas_width = 2 * 512 + 3 * margin
    canvas_height = ((num_images + 1) // 2) * 512 + ((num_images + 1) // 2 + 1) * margin

    # Create a blank white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    y_offset = margin
    for i, img in enumerate(images):
        x_offset = margin + (i % 2) * (512 + margin)
        canvas.paste(img, (x_offset, y_offset))
        if i % 2:
            y_offset += 512 + margin

    return canvas


def main():
    image_dir = '../images'  # Replace with your directory path
    images = resize_images(image_dir)
    result = stitch_images(images)

    # Saving the stitched image
    result.save('stitched_image.jpg', 'JPEG')


if __name__ == '__main__':
    main()
