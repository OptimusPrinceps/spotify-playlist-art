import os
from PIL import Image


def resize_image(img_path, base_width=512, base_height=512):
    """Resizes the given image to specified dimensions."""
    img = Image.open(img_path)
    return img.resize((base_width, base_height), Image.ANTIALIAS)


def stitch_images(image_dir, output_path, margin=10):
    """Stitches all images in a directory together with a specified margin."""

    # List all images in directory
    images = [f for f in os.listdir(image_dir) if os.path.splitext(f)[1] in ['.jpg', '.jpeg', '.png']]

    if not images:
        print("No images found in the directory.")
        return

    # Load and resize images
    resized_images = [resize_image(os.path.join(image_dir, img)) for img in images]

    # Calculate total canvas size
    total_width = len(resized_images) * 512 + (len(resized_images) - 1) * margin
    total_height = 512

    # Create canvas for stitched image
    canvas = Image.new('RGB', (total_width, total_height), (255, 255, 255))

    x_offset = 0
    for img in resized_images:
        canvas.paste(img, (x_offset, 0))
        x_offset += 512 + margin

    # Save the stitched image
    canvas.save(output_path)


if __name__ == "__main__":
    image_dir = '../images'  # Replace with your directory path
    output_path = 'stitched_image.jpg'
    stitch_images(image_dir, output_path)
