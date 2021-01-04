import os
import sys
import argparse

from PIL import Image, ImageTk
from tkinter import Canvas, Tk, Label, LEFT, Frame, filedialog, messagebox, Button

from photo_organizer.settings import BACKGROUND_COLOR, TOP_BAR_COLOR, TOP_BUTTON_HEIGHT, RATINGS
from photo_organizer.objects import (
    catalog,
    config
)
from photo_organizer.logic import (
    photo_size_adjuster,
    file_mover
)


class PhotoOrganizer(object):
    def __init__(self, config, tk_root):
        self.config = config
        self.catalog = self.load_catalog()
        self.total_images = self.catalog.length
        self.tk_root = tk_root
        self.define_keyboard_operations()

        self.top_frame = Frame(self.tk_root, height=TOP_BUTTON_HEIGHT, bg=TOP_BAR_COLOR)
        self.top_frame.pack()
        self.photo_frame = Canvas(self.tk_root)
        self.photo_frame.pack(expand="yes", fill="both")
        self.init_photo_frame()

        self.rating_buttons = []
        self.init_rating_display()

        self.current_image_index = 0
        self.total_images = self.catalog.length
        self.image_counter_label = Label(self.top_frame, fg="grey", bg=TOP_BAR_COLOR)
        self.image_counter_label.pack(side=LEFT)
        self.update_rating_display()
        self.show_image()

    def define_keyboard_operations(self):
        self.tk_root.bind('<Escape>', self.ask_quit)
        self.tk_root.bind('<Left>', self.previous_image)
        self.tk_root.bind('<Right>', self.next_image)
        self.tk_root.bind('<Return>', self.move_photos)
        for index in RATINGS.keys():
            self.tk_root.bind(str(index), self.rate_action)

    def ask_quit(self, event=None):
        if messagebox.askyesno("Question", "Quit this application?"):
            self.terminate()

    def terminate(self):
        self.tk_root.quit()
        sys.exit()

    def previous_image(self, event=None):
        self.current_image_index = (self.current_image_index - 1) % self.total_images
        self.show_image()

    def next_image(self, event=None):
        self.current_image_index = (self.current_image_index + 1) % self.total_images
        self.show_image()

    def rate_action(self, event):
        rating = int(event.char)
        self.catalog.rate_photo(self.current_image_index, rating)
        self.show_image()

    def move_photos(self, event=None):
        if messagebox.askyesno("Question", "Move photos?"):
            messages = file_mover.move_photos(
                self.catalog,
                self.config.raw_backup_directory,
                self.config.raw_edit_directory,
                self.config.jpeg_directory,
                self.config.delete_directory
            )
            for index, label in RATINGS.items():
                if messages[index]:
                    messagebox.showinfo("Files were moved", "{} photos\n{}".format(
                        label.upper(), messages[index]))
            self.terminate()

    def load_catalog(self):
        input_directory = self.config.input_directory or filedialog.askdirectory()
        catalog_obj = catalog.Catalog(input_directory, self.config.jpeg_extension, self.config.raw_extension)
        if catalog_obj.only_jpegs:
            messagebox.showinfo("Only JPEG files", "{} files does not have RAW files:\n{}".format(
                len(self.catalog.only_jpegs), ",".join(self.catalog.only_jpegs)))
        if catalog_obj.length == 0:
            messagebox.showerror("No target photos", "No files to display")
            self.terminate()
        return catalog_obj

    def init_photo_frame(self):
        self.photo_frame["width"] = self.photo_frame.winfo_screenwidth()
        self.photo_frame['height'] = self.photo_frame.winfo_screenheight()
        self.photo_frame['bg'] = BACKGROUND_COLOR

    def init_rating_display(self):
        for index in range(5):
            rating_button = Button(
                self.top_frame,
                text='[{}] {}'.format(index, RATINGS[index].upper()),
                bg=TOP_BAR_COLOR
            )
            rating_button.pack(side=LEFT)
            self.rating_buttons.append(rating_button)

    def show_image(self):
        image_path = self.catalog.get_jpeg_path(self.current_image_index)
        pil_image = Image.open(image_path)
        pil_image, new_x, new_y = photo_size_adjuster.get_new_image(
            pil_image, self.photo_frame.winfo_screenheight(), self.photo_frame.winfo_screenwidth()
        )
        img = ImageTk.PhotoImage(pil_image)
        self.photo_frame.allready = self.photo_frame.create_image(new_x, new_y, image=img, anchor='nw', tag="bacl")
        self.photo_frame.image = img
        self.tk_root.title("Photo Organizer ({})".format(os.path.split(image_path)[-1]))
        self.update_image_counter_label()
        self.update_rating_display()

    def update_image_counter_label(self):
        self.image_counter_label['text'] = ' {} / {} '.format(self.current_image_index + 1, self.total_images)

    def update_rating_display(self):
        rating_counter = self.catalog.get_rating_counter()
        current_rating = self.catalog.get_rating(self.current_image_index)
        for index, label in RATINGS.items():
            label_color = '#c4b643' if index == current_rating else '#92e4dd'
            tk_button = self.rating_buttons[index]
            tk_button['fg'] = label_color
            tk_button['text'] = '[{}]  {} ({})  '.format(
                index, label.upper(), rating_counter[index]
            )


def main(config_file):
    config_obj = config.read_config(config_file)
    root = Tk(className="Photo Organizer")
    root.config(bg=BACKGROUND_COLOR)
    PhotoOrganizer(config=config_obj, tk_root=root)
    root.resizable()
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run photo organizer to move/delete RAW+JPEG files"
    )
    parser.add_argument(
        "config_file",
        help="YAML file of configuration"
    )
    args = parser.parse_args()
    main(args.config_file)
