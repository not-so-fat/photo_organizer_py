from pathlib import Path
import shutil


def move_photos(catalog, raw_backup_dir, raw_for_edit_dir, jpeg_dir, delete_dir):
    messages = {0: ""}
    messages[4] = process_photos(catalog.get_photos_on_rating(4), raw_backup_dir, jpeg_dir)
    messages[3] = process_photos(catalog.get_photos_on_rating(3), delete_dir, jpeg_dir)
    messages[2] = process_photos(catalog.get_photos_on_rating(2), raw_for_edit_dir, delete_dir)
    messages[1] = process_photos(catalog.get_photos_on_rating(1), delete_dir, delete_dir)
    return messages


def process_photos(photos, raw_destination, jpeg_destination):
    num_success = 0
    error_list = []
    if len(photos):
        for i, photo in photos.iterrows():
            raw_dir = Path(photo["raw_path"]).parent
            raw_name = Path(photo["raw_path"]).name
            try:
                execute_both(
                    lambda : move_file(photo["raw_path"], raw_destination),
                    lambda : move_file(photo["jpeg_path"], jpeg_destination),
                    lambda : move_file(Path(raw_destination)/raw_name, Path(raw_dir))
                )
                num_success += 1
            except Exception as e:
                error_list.append("{}: {}".format(photo["photo_id"], e))
        message = "{}/{} photos are successfully moved\nRAW:{}\nJPEG:{}".format(
            num_success, len(photos), raw_destination, jpeg_destination)
        if error_list:
            message += "\nfollowing files cannot be moved:\n  "
            message += "\n  ".join(error_list)
        return message
    else:
        return ""


def move_file(from_path, to_path):
    if (Path(to_path) / Path(from_path).name).exists():
        raise Exception("file exists in destination")
    else:
        shutil.move(from_path, to_path)


def execute_both(command1, command2, undo_command1):
    command1()
    try:
        command2()
    except Exception as e:
        undo_command1()
        raise e
