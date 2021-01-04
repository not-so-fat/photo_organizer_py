from photo_organizer.settings import TOP_BUTTON_HEIGHT, MARGIN_BOTTOM, MARGIN_LEFT_RIGHT


def get_new_image(pil_image, screenheight, screenwidth):
    original_width = pil_image.width
    original_height = pil_image.height
    max_height_image = screenheight - TOP_BUTTON_HEIGHT - MARGIN_BOTTOM
    max_width_image = screenwidth - 2 * MARGIN_LEFT_RIGHT

    scale_factor_height, scale_factor_width = 1, 1
    if original_height > max_height_image:
        scale_factor_height = max_height_image / original_height

    if original_width > max_width_image:
        scale_factor_width = max_width_image / original_width

    scale_factor = min(scale_factor_width, scale_factor_height)
    if scale_factor != 1:
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        pil_image = pil_image.resize((new_width, new_height))
    else:
        new_width = original_width
        new_height = original_height
    new_x = int((max_width_image - new_width) / 2)
    new_y = int((TOP_BUTTON_HEIGHT + max_height_image - new_height) / 2)
    return pil_image, new_x, new_y
