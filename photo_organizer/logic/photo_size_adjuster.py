from photo_organizer.settings import TOP_BUTTON_HEIGHT, MARGIN_BOTTOM, MARGIN_LEFT_RIGHT


def get_new_image(pil_image, screenheight, screenwidth):
    original_width = pil_image.width
    original_height = pil_image.height
    max_height = screenheight - TOP_BUTTON_HEIGHT - MARGIN_BOTTOM
    max_width = screenwidth - 2 * MARGIN_LEFT_RIGHT
    scale_factor = determine_scale(original_height, original_width, max_height, max_width)
    if scale_factor != 1:
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        pil_image = pil_image.resize((new_width, new_height))
    else:
        new_width = original_width
        new_height = original_height
    new_x = int((max_width - new_width) / 2)
    new_y = int((TOP_BUTTON_HEIGHT + max_height - new_height) / 2)
    return pil_image, new_x, new_y


def determine_scale(original_height, original_width, max_height, max_width):
    scale_factor_height, scale_factor_width = 1, 1
    if original_height > max_height:
        scale_factor_height = max_height / original_height
    if original_width > max_width:
        scale_factor_width = max_width / original_width
    return min(scale_factor_width, scale_factor_height)
