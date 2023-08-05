from PIL import Image
import os


def resize_images(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    img_objs = []

    for img_file in img_files:
        with Image.open(os.path.join(directory, img_file)) as img:
            img_objs.append(img.resize((512, 512)))

    return img_objs


def stitch_images(images, columns=2, margin=10):
    if columns < 1:
        raise ValueError("Number of columns must be at least 1")

    num_images = len(images)

    # Calculate canvas size
    canvas_width = columns * 512 + (columns + 1) * margin
    rows = (num_images + columns - 1) // columns
    canvas_height = rows * 512 + (rows + 1) * margin

    # Create a blank white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    y_offset = margin
    for i, img in enumerate(images):
        x_offset = margin + (i % columns) * (512 + margin)
        canvas.paste(img, (x_offset, y_offset))
        if (i + 1) % columns == 0:
            y_offset += 512 + margin

    return canvas


def main():
    directory = '../images'
    columns = 2  # Adjust the number of columns as needed
    images = resize_images(directory)
    result = stitch_images(images, columns)

    result.save('stitched_image.jpg', 'JPEG')


if __name__ == '__main__':
    main()
