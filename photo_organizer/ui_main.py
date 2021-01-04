import os
import sys
import copy
import argparse

from PIL import Image, ImageTk
from tkinter import Canvas, Tk, Label, LEFT, RIGHT, Frame, filedialog, messagebox, Button

from photo_organizer.settings import BACKGROUND_COLOR, TOP_BAR_COLOR, TOP_BUTTON_HEIGHT, RATINGS, ACTIVE_FG_COLOR, NORMAL_FG_COLOR
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
        self.current_image_index = 0
        self.total_images = self.catalog.length
        self.tk_root = tk_root
        self.define_keyboard_operations()

        self.top_frame = Frame(self.tk_root, height=TOP_BUTTON_HEIGHT, bg=TOP_BAR_COLOR)
        self.top_frame.pack()
        self.photo_frame = Frame(self.tk_root, bg=BACKGROUND_COLOR)
        self.photo_frame.pack(expand="yes", fill="both")
        left_button = Button(
            self.photo_frame, fg=NORMAL_FG_COLOR, bg=BACKGROUND_COLOR, text="<", font=("Arial", 20),
            command=self.previous_image
        )
        left_button.pack(side=LEFT)
        self.photo_canvas = Canvas(self.photo_frame, bd=0, highlightthickness=0)
        self.photo_canvas.pack(side=LEFT)
        self.init_photo_frame()
        right_button = Button(
            self.photo_frame, fg=NORMAL_FG_COLOR, bg=BACKGROUND_COLOR, text=">", font=("Arial", 20),
            command=self.next_image
        )
        right_button.pack(side=RIGHT)

        self.image_counter_label = Label(
            self.top_frame, fg="grey", font=("Arial", 16), bg=TOP_BAR_COLOR
        )
        self.image_counter_label.pack(side=LEFT)
        self.rating_buttons = []
        self.rating_counters = []
        self.init_rating_display()
        move_button = Button(
            self.top_frame, text='MOVE FILES & QUIT', fg='#8b0000', bg=TOP_BAR_COLOR,
            font=("Arial", 15, "bold"), command=self.move_photos)
        move_button.pack(side=RIGHT)

        self.total_images = self.catalog.length
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
        self._rate_action(rating)

    def _rate_action(self, rating):
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
        self.photo_canvas["width"] = self.photo_canvas.winfo_screenwidth() - 80
        self.photo_canvas['height'] = self.photo_canvas.winfo_screenheight()
        self.photo_canvas['bg'] = BACKGROUND_COLOR

    def init_rating_display(self):
        # TODO: smarter way to define command...
        # define function in for loop refers `index` and always returns 4...
        command = [
            lambda :self._rate_action(0),
            lambda :self._rate_action(1),
            lambda :self._rate_action(2),
            lambda :self._rate_action(3),
            lambda :self._rate_action(4)
        ]
        for index in range(5):
            rating_button = Button(
                self.top_frame,
                font=("Arial", 20, "bold"),
                text='[{}] {}'.format(index, RATINGS[index].upper()),
                bg=TOP_BAR_COLOR,
                command=command[index]
            )
            rating_button.pack(side=LEFT)
            rating_counter = Label(
                self.top_frame,
                font=("Arial", 18),
                bg=TOP_BAR_COLOR,
                fg=NORMAL_FG_COLOR
            )
            rating_counter.pack(side=LEFT)
            self.rating_buttons.append(rating_button)
            self.rating_counters.append(rating_counter)

    def show_image(self):
        image_path = self.catalog.get_jpeg_path(self.current_image_index)
        pil_image = Image.open(image_path)
        pil_image, new_x, new_y = photo_size_adjuster.get_new_image(
            pil_image, int(self.photo_canvas['height']), int(self.photo_canvas["width"])
        )
        img = ImageTk.PhotoImage(pil_image)
        self.photo_canvas.allready = self.photo_canvas.create_image(new_x, new_y, image=img, anchor='nw', tag="bacl")
        self.photo_canvas.image = img
        self.tk_root.title("Photo Organizer ({})".format(os.path.split(image_path)[-1]))
        self.update_image_counter_label()
        self.update_rating_display()

    def update_image_counter_label(self):
        self.image_counter_label['text'] = ' {} / {} '.format(self.current_image_index + 1, self.total_images)

    def update_rating_display(self):
        rating_counter = self.catalog.get_rating_counter()
        current_rating = self.catalog.get_rating(self.current_image_index)
        for index, label in RATINGS.items():
            label_color = ACTIVE_FG_COLOR if index == current_rating else NORMAL_FG_COLOR
            self.rating_buttons[index]['fg'] = label_color
            self.rating_counters[index]['text'] = "({})   ".format(rating_counter[index])


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
