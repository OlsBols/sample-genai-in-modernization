from PIL import Image
import base64
from io import BytesIO


def resize_image(image_bytes, max_size_mb=3.75, max_width_px=8000, max_height_px=8000):
    image = Image.open(BytesIO(image_bytes))

    # Check image size
    image_size = len(image_bytes) / (1024 * 1024)  # Convert bytes to MB
    image_width, image_height = image.size

    if (
        image_size > max_size_mb
        or image_width > max_width_px
        or image_height > max_height_px
    ):
        # Calculate resize ratio
        resize_ratio = min(max_width_px / image_width, max_height_px / image_height)
        new_size = (int(image_width * resize_ratio), int(image_height * resize_ratio))

        # Resize image
        image = image.resize(new_size, Image.ANTIALIAS)

    # Convert resized image to bytes
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()


def convert_image_to_base64(image_bytes):
    # Convert image to base64
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    return base64_image


def get_image_type(image_file_name):
    # Determine the image type based on the file extension
    if image_file_name.endswith(".png"):
        image_type = "image/png"
    elif image_file_name.endswith(".jpg") or image_file_name.endswith(".jpeg"):
        image_type = "image/jpeg"
    elif image_file_name.endswith(".webp"):
        image_type = "image/webp"
    elif image_file_name.endswith(".gif"):
        image_type = "image/gif"
    else:
        raise ValueError(
            "Only 'jpeg', 'png', 'webp', and 'gif' image formats are currently supported"
        )
    return image_type
