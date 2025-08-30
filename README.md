# Photo Organizer

Web-based application to view & rate photos, and move RAW/JPEG files based on rating.


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
- Open the web app and rate photos as one of "Excellent" / "OK" / "EDIT" / "BAD"
- App move files based on rating

| Rating    | RAW Destination | JPEG destination |
|-----------|-----------------|------------------|
| EXCELLENT | `raw_for_backup`    | `delete`         |
| OK        | `delete`        | `jpeg`           |
| EDIT      | `raw_for_edit`      | `delete`         |
| BAD       | `delete`        | `delete`         |


## Installation

1. Install Python 3.9 or later
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `config.yaml`:
   - `raw_extension` / `jpeg_extension`: Extension for RAW / JPEG files
   - `input_directory`: Input directory for RAW+JPEG files
   - `save_directory`: Please specify where you want to save RAW / JPEG files (refer above table)
   - `delete_directory`: To be safe, instead of deleting files we move files into specified directory

## How to use

1. Start the web application:
   ```bash
   python -m photo_organizer.web_app config.yaml
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use keyboard shortcuts to operate the app:
   - **Left/Right Arrow Keys**: Navigate to previous/next photo
   - **Number Keys (0-4)**: Rate photos
     - 0: Undefined
     - 1: Bad
     - 2: Edit
     - 3: OK
     - 4: Excellent
   - **R Key**: Rotate photo
   - **Enter Key**: Move rated photos to their destinations and exit
   - **Escape Key**: Exit without moving files

## Features

- **Cross-platform**: Works on any OS with a web browser
- **Keyboard-focused**: Optimized for keyboard navigation and rating
- **Photo display**: Shows photos with proper scaling to fit the screen
- **File management**: Automatically moves RAW/JPEG pairs based on ratings
- **Safe operation**: Moves files to a delete directory instead of permanent deletion

