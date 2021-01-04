# Photo Organizer

GUI app to view & rate photos, and move RAW/JPEG files based on rating.


## Motivation

To help users to organize RAW+JPEG files in easier way.
RAW and JPEG has pros and cons for different objectives and some photographer prefer to shoot both RAW and JPEG.
However it is troublesome to manage both files.

In my case, I would like to manage photos based on rating.
- For photos I plan to print / display in the future, I would like to keep both  RAW and JPEG files
- For photos which is good for daily records, I would like to keep only JPEG file
- For photos which need post processing,  I would like to keep only RAW file
- For photos I do not need, I would like to delete both files.

By this idea, this app moves files based on rating.



## Expected workflow

- Put all RAW+JPEG files in a directory
    - RAW and JPEG should have the same name except for extension, i.e. "A.JPG" and "A.RAF"
    - Extension is configurable
- Open the app and rate photos as one of "Excellent" / "OK" / "EDIT" / "BAD"
- App move files based on rating

| Rating    | RAW Destination | JPEG destination |
|-----------|-----------------|------------------|
| EXCELLENT | `raw_for_backup`    | `delete`         |
| OK        | `delete`        | `jpeg`           |
| EDIT      | `raw_for_edit`      | `delete`         |
| BAD       | `delete`        | `delete`         |


## Installation

- Please install python, and install dependent libraries in `requirements.txt`
- Please fill fields in `config.yaml`
    - `raw_extension` / `jpeg_extension`: Extension for RAW / JPEG files
    - `input_directory`: Input directory for RAW+JPEG files, if it is null, you can configure it on GUI
    - `save_directory`: Please specify where you want to save RAW / JPEG files (refer above table)
    - `delete_directory`: To be safe, instead of deleting files we move files into specified directory
- RUN `python ui_main.py config.yaml`
    
## How to use GUI

- (If `input_directory` is null) app asks you to specify directory on GUI
- You can operate app by ***your keyboard*** (no buttons there yet)
    - Right / Left key shows next / previous image
    - 0 / 1 / 2 / 3 / 4 key rate your photo
    - Return key starts file transfer, and terminates app
    - ESC key just terminates app

