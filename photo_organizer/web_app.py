#!/usr/bin/env python3
"""
Flask-based Photo Organizer Web Application
"""

import os
import sys
import json
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from photo_organizer.objects import catalog, config
from photo_organizer.logic import file_mover
from photo_organizer.settings import RATINGS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global variables
catalog_obj = None
current_index = 0
input_directory = None


def init_catalog(config_obj):
    """Initialize the photo catalog"""
    global catalog_obj, input_directory
    input_directory = config_obj.input_directory
    catalog_obj = catalog.Catalog(input_directory, config_obj.jpeg_extension, config_obj.raw_extension)
    return catalog_obj


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         total_photos=catalog_obj.length if catalog_obj else 0,
                         ratings=RATINGS)


@app.route('/api/current_photo')
def get_current_photo():
    """Get current photo information"""
    global current_index
    
    if not catalog_obj or catalog_obj.length == 0:
        return jsonify({'error': 'No photos available'})
    
    # Ensure index is within bounds
    current_index = current_index % catalog_obj.length
    
    # Get photo info
    jpeg_path = catalog_obj.get_jpeg_path(current_index)
    raw_path = catalog_obj.get_raw_path(current_index)
    rating = int(catalog_obj.get_rating(current_index))  # Convert to native int
    angle = int(catalog_obj.get_angle(current_index))    # Convert to native int
    
    # Get rating counts
    rating_counts = catalog_obj.get_rating_counter()
    # Convert rating counts to native Python types
    rating_counts = {int(k): int(v) for k, v in rating_counts.items()}
    
    return jsonify({
        'index': int(current_index),  # Convert to native int
        'total': int(catalog_obj.length),  # Convert to native int
        'jpeg_path': str(jpeg_path),
        'raw_path': str(raw_path) if raw_path else None,
        'rating': rating,
        'angle': angle,
        'rating_counts': rating_counts,
        'filename': os.path.basename(jpeg_path)
    })


@app.route('/api/photo/<int:photo_index>')
def get_photo(photo_index):
    """Get photo by index"""
    global current_index
    
    if not catalog_obj or photo_index >= catalog_obj.length:
        return jsonify({'error': 'Invalid photo index'})
    
    current_index = photo_index
    return get_current_photo()


@app.route('/api/rate/<int:rating>')
def rate_photo(rating):
    """Rate the current photo"""
    global current_index
    
    if not catalog_obj or current_index >= catalog_obj.length:
        return jsonify({'error': 'Invalid photo index'})
    
    if rating not in RATINGS:
        return jsonify({'error': 'Invalid rating'})
    
    catalog_obj.rate_photo(current_index, rating)
    
    # Get updated rating counts
    rating_counts = catalog_obj.get_rating_counter()
    rating_counts = {int(k): int(v) for k, v in rating_counts.items()}
    
    return jsonify({
        'success': True,
        'rating': rating,
        'rating_counts': rating_counts
    })


@app.route('/api/rotate/<int:direction>')
def rotate_photo(direction):
    """Rotate the current photo"""
    global current_index
    
    if not catalog_obj or current_index >= catalog_obj.length:
        return jsonify({'error': 'Invalid photo index'})
    
    # direction: 1 for right, -1 for left
    angle_change = 90 if direction == 1 else -90
    catalog_obj.update_angle(current_index, angle_change)
    
    return jsonify({
        'success': True,
        'angle': int(catalog_obj.get_angle(current_index))
    })


@app.route('/api/navigate/<direction>')
def navigate(direction):
    """Navigate to next/previous photo"""
    global current_index
    
    if not catalog_obj or catalog_obj.length == 0:
        return jsonify({'error': 'No photos available'})
    
    # Handle direction properly
    if direction == '-1':
        # Go to previous photo
        current_index = (current_index - 1) % catalog_obj.length
    elif direction == '1':
        # Go to next photo
        current_index = (current_index + 1) % catalog_obj.length
    else:
        return jsonify({'error': 'Invalid direction'})
    
    return get_current_photo()


@app.route('/api/move_files')
def move_files():
    """Move files based on ratings"""
    global catalog_obj
    
    if not catalog_obj:
        return jsonify({'error': 'No catalog available'})
    
    try:
        messages = file_mover.move_photos(
            catalog_obj,
            config_obj.raw_backup_directory,
            config_obj.raw_edit_directory,
            config_obj.jpeg_directory,
            config_obj.delete_directory
        )
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error moving files: {str(e)}'
        })


@app.route('/photos/<path:filename>')
def serve_photo(filename):
    """Serve photo files"""
    global input_directory
    
    if not input_directory:
        return jsonify({'error': 'No input directory available'})
    
    # Security: ensure the file is within the input directory
    file_path = os.path.join(input_directory, filename)
    
    if not os.path.commonpath([input_directory]) == os.path.commonpath([input_directory, file_path]):
        return jsonify({'error': 'Access denied'})
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    # Check if file is readable
    if not os.access(file_path, os.R_OK):
        print(f"File not readable: {file_path}")
        return jsonify({'error': f'File not readable: {filename}'}), 403
    
    try:
        return send_from_directory(input_directory, filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python web_app.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config_obj = config.read_config(config_file)
    
    # Initialize catalog
    init_catalog(config_obj)
    
    print(f"Photo Organizer Web App")
    print(f"Total photos: {catalog_obj.length}")
    print(f"Input directory: {input_directory}")
    print(f"Open your browser to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
