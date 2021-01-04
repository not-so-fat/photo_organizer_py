import os
import sys
import argparse

from PIL import Image, ImageTk
from tkinter import Canvas, Tk, Label, LEFT, Frame, filedialog, messagebox

from photo_organizer.settings import BACKGROUND_COLOR, TOP_BAR_COLOR, TOP_BUTTON_HEIGHT, RATINGS
from photo_organizer.objects import (
    catalog,
    config
)
from photo_organizer.logic import (
    photo_size_adjuster,
    file_mover
)


class PhotoOrganizer(Canvas):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        input_directory = self.config.input_directory or filedialog.askdirectory()
        self.catalog = catalog.Catalog(input_directory, self.config.jpeg_extension, self.config.raw_extension)
        if self.catalog.only_jpegs:
            messagebox.showinfo("Only JPEG files", "{} files does not have RAW files:\n{}".format(
                len(self.catalog.only_jpegs), ",".join(self.catalog.only_jpegs)))
        if self.catalog.length == 0:
            messagebox.showerror("No target photos", "No files to display")
            self.terminate()

        self['width'] = self.winfo_screenwidth()
        self['height'] = self.winfo_screenheight()
        self['bg'] = BACKGROUND_COLOR
        self.top_frame = Frame(self.master, height=TOP_BUTTON_HEIGHT, bg=TOP_BAR_COLOR)
        self.top_frame.pack()

        # Define keyboard control
        self.master.bind('<Escape>', self.ask_quit)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<Return>', self.move_photos)
        for index in RATINGS.keys():
            self.master.bind(str(index), self._rate_action)
        # self.master.bind("<Configure>", self.on_resize)  # TODO: find a way to make resize window work nicely

        self.current_image_index = 0

        # Set rating counter
        self.total_images = self.catalog.length
        self._init_rating_display()
        self.update_rating_display()

        # Set image counter
        self.image_counter_label = Label(self.top_frame, font=('Helvetica', 16), fg="grey", bg=TOP_BAR_COLOR)
        self.image_counter_label.pack(side=LEFT)
        self.show_image()

    def ask_quit(self, event=None):
        if messagebox.askyesno("Question", "Quit this application?"):
            self.terminate()

    def terminate(self):
        self.quit()
        sys.exit()

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

    def _init_rating_display(self):
        """
        Initialize counter displayed on top
        """
        for index, label in RATINGS.items():
            setattr(
                self,
                label,
                Label(
                    self.top_frame,
                    text='[{}] {}'.format(index, label.upper()),
                    font=('Helvetica', 20),
                    bg=TOP_BAR_COLOR
                )
            )
            tk_label = getattr(self, label)
            getattr(tk_label, 'pack')(side=LEFT)

    def show_image(self):
        image_path = self.catalog.get_jpeg_path(self.current_image_index)
        pil_image = Image.open(image_path)
        pil_image, new_x, new_y = photo_size_adjuster.get_new_image(
            pil_image, self.winfo_screenheight(), self.winfo_screenwidth()
        )
        img = ImageTk.PhotoImage(pil_image)
        self.allready = self.create_image(new_x, new_y, image=img, anchor='nw', tag="bacl")
        self.image = img
        self.master.title("Photo Organizer ({})".format(os.path.split(image_path)[-1]))
        self.update_image_counter_label()
        self.update_rating_display()

    def _rate_action(self, event):
        rating = int(event.char)
        self.catalog.rate_photo(self.current_image_index, rating)
        self.show_image()

    def previous_image(self, event=None):
        self.current_image_index = (self.current_image_index - 1) % self.total_images
        self.show_image()

    def next_image(self, event=None):
        self.current_image_index = (self.current_image_index + 1) % self.total_images
        self.show_image()

    def update_image_counter_label(self):
        self.image_counter_label['text'] = ' {} / {} '.format(self.current_image_index + 1, self.total_images)

    def update_rating_display(self):
        rating_counter = self.catalog.get_rating_counter()
        current_rating = self.catalog.get_rating(self.current_image_index)
        for index, label in RATINGS.items():
            label_color = '#c4b643' if index == current_rating else '#92e4dd'
            tk_label = getattr(self, label)
            tk_label['fg'] = label_color
            tk_label['text'] = '[{}]  {} ({})  '.format(
                index, label.upper(), rating_counter[index]
            )


def main(config_file):
    config_obj = config.read_config(config_file)
    root = Tk(className="Photo Organizer")
    PhotoOrganizer(config=config_obj, master=root).pack(expand="yes", fill="both")
    root.bg = BACKGROUND_COLOR
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
