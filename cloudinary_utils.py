import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app
import os
from datetime import datetime

def init_cloudinary(app):
    """Initialize Cloudinary with app config"""
    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )

def upload_to_cloudinary(file_data, folder='markets', resource_type='image'):
    """
    Upload file to Cloudinary
    
    Args:
        file_data: File data (base64 or file object)
        folder: Folder name in Cloudinary
        resource_type: 'image' or 'video'
    
    Returns:
        dict: Upload result with URL and public_id
    """
    try:
        # Handle both base64 and file uploads
        if isinstance(file_data, str) and file_data.startswith('data:'):
            # Base64 data
            upload_result = cloudinary.uploader.upload(
                file_data,
                folder=folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True
            )
        else:
            # File object
            upload_result = cloudinary.uploader.upload(
                file_data,
                folder=folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True
            )
        
        return {
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id'],
            'success': True
        }
    except Exception as e:
        print(f"Cloudinary upload error: {str(e)}")
        return {
            'url': None,
            'public_id': None,
            'success': False,
            'error': str(e)
        }

def delete_from_cloudinary(public_id, resource_type='image'):
    """Delete file from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Cloudinary delete error: {str(e)}")
        return False

def get_optimized_url(public_id, width=400, height=400, crop='fill'):
    """Get optimized Cloudinary URL"""
    return cloudinary.CloudinaryImage(public_id).build_url(
        width=width,
        height=height,
        crop=crop,
        quality='auto',
        fetch_format='auto'
    )

def get_video_url(public_id):
    """Get optimized video URL from Cloudinary"""
    return cloudinary.CloudinaryImage(public_id).build_url(
        resource_type='video',
        quality='auto',
        fetch_format='auto'
    )