from pathlib import Path
IMAGE_DIR = Path(__file__).parent

def get_product_image(product_code):
    """
    Finds a product image using its product_code.

    Examples:
        PRN001.jpg
        PRN002.png
        PRN003.jpeg
    """
    if not product_code:
        return None
    product_code = str(product_code).strip()

    for extension in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        image_path = IMAGE_DIR / f"{product_code}{extension}"

        if image_path.is_file():
            return image_path
    return None

def get_category_image(category_name):
    """
    Finds the image for a catalog category.
    Put category images inside this same folder:

        pump.jpg
        gun.jpg
        nozzle.jpg

    The function also accepts common Persian/English names.
    """
    if not category_name:
        return None

    name = str(category_name).strip().lower()

    # Common category names -> image filename
    category_images = {
        "pump": "pump.jpg",
        "pumps": "pump.jpg",
        "diaphragm pump": "pump.jpg",
        "diaphragm pumps": "pump.jpg",
        "پمپ": "pump.jpg",
        "پمپ دیافراگمی": "pump.jpg",
        "پمپ های دیافراگمی": "pump.jpg",
        "پمپ‌های دیافراگمی": "pump.jpg",

        "gun": "gun.jpg",
        "guns": "gun.jpg",
        "powder gun": "gun.jpg",
        "powder guns": "gun.jpg",
        "pistol": "gun.jpg",
        "پیستوله": "gun.jpg",
        "پیستول": "gun.jpg",
        "پیستول پودری": "gun.jpg",

        "nozzle": "nozzle.jpg",
        "nozzles": "nozzle.jpg",
        "نازل": "nozzle.jpg",
        "نازل ها": "nozzle.jpg",
        "نازل‌ها": "nozzle.jpg",
    }

    filename = category_images.get(name)

    if not filename:
        return None

    image_path = IMAGE_DIR / filename

    if image_path.is_file():
        return image_path

    return None
