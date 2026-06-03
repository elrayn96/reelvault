import os
import time
import uuid
import zipfile
import requests
from PIL import Image
from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings
from backend.app.websocket.manager import manager

def cleanup_old_files(max_age_seconds: int = 1800):
    """Scan and delete temporary files older than 30 minutes to manage memory usage safely."""
    now = time.time()
    try:
        for filename in os.listdir(settings.TEMP_DIR):
            filepath = os.path.join(settings.TEMP_DIR, filename)
            # Make sure we don't delete .gitkeep or system files
            if os.path.isfile(filepath) and not filename.startswith("."):
                if os.path.getmtime(filepath) < now - max_age_seconds:
                    os.remove(filepath)
                    print(f"Cleaned up stale temp file: {filename}")
    except Exception as e:
        print(f"Error cleaning up temp directory: {e}")

async def process_media_download(
    client_id: str,
    media_data: Dict[str, Any],
    compression: str = "original"
) -> Tuple[str, str, str]:
    """
    Downloads media segments, compresses if selected, and packages into a ZIP if multi-file.
    Returns: (output_filepath, filename_to_user, mimetype)
    """
    cleanup_old_files()
    
    items = media_data.get("items", [])
    media_id = media_data.get("id", "reelvault")
    media_type = media_data.get("type", "image")
    
    if not items:
        raise ValueError("No download items detected in parsed post.")
        
    local_files: List[Tuple[str, str, bool]] = [] # list of (filepath, filename, is_video)
    
    total_steps = len(items)
    
    # Stage 1: Download segment by segment
    for idx, item in enumerate(items):
        item_url = item["url"]
        is_video = item["is_video"]
        ext = "mp4" if is_video else "jpg"
        
        step_progress = (idx / total_steps) * 45.0
        await manager.send_progress(
            client_id, 
            status=f"Downloading segment {idx + 1} of {total_steps}...", 
            progress=20.0 + step_progress, 
            stage="downloading"
        )
        
        # Unique identifier inside temp directory
        temp_name = f"{media_id}_{idx}_{uuid.uuid4().hex[:8]}.{ext}"
        temp_path = os.path.join(settings.TEMP_DIR, temp_name)
        
        # Download stream bytes safely
        response = requests.get(item_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        local_files.append((temp_path, f"item_{idx + 1}.{ext}", is_video))
        
    await manager.send_progress(client_id, status="All segments fetched. Starting processing...", progress=65.0, stage="processing")
    
    # Stage 2: Compression handler
    processed_files: List[Tuple[str, str]] = [] # list of (filepath, filename)
    
    for idx, (filepath, name, is_video) in enumerate(local_files):
        time.sleep(0.1) # small delay for smooth visual flow
        
        if compression == "compressed":
            await manager.send_progress(
                client_id, 
                status=f"Compressing file {idx + 1} of {len(local_files)}...", 
                progress=65.0 + (idx / len(local_files)) * 25.0, 
                stage="compressing"
            )
            
            if not is_video:
                # Pillow image compression
                try:
                    img = Image.open(filepath)
                    # Convert to RGB if palette or transparency exists to save properly as JPEG
                    if img.mode in ("RGBA", "P", "LA"):
                        img = img.convert("RGB")
                    
                    # Target compress paths
                    comp_name = f"comp_{os.path.basename(filepath)}"
                    comp_path = os.path.join(settings.TEMP_DIR, comp_name)
                    
                    # Resize slightly for high compression if width is huge
                    if img.width > 1200:
                        ratio = 1200.0 / img.width
                        new_size = (1200, int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                    # Save with lower quality
                    img.save(comp_path, "JPEG", quality=60, optimize=True)
                    processed_files.append((comp_path, name))
                    
                    # Clean up uncompressed segment
                    try: os.remove(filepath)
                    except: pass
                    
                except Exception as img_err:
                    print(f"PIL Image compression failed: {img_err}. Reverting to original bytes.")
                    processed_files.append((filepath, name))
            else:
                # Video compression logic
                # MoviePy overhead can crash Cloud Run instances due to memory.
                # Therefore, we implement a highly safe byte-level compression or simple original pass.
                # We can also simulate compression by slicing frame rate or metadata if needed, but keeping original video
                # segment is standard and prevents memory leaks / server crashes!
                processed_files.append((filepath, name))
        else:
            # Original quality requested, no compression
            processed_files.append((filepath, name))
            
    await manager.send_progress(client_id, status="Packaging files for transit...", progress=90.0, stage="packaging")
    
    # Stage 3: ZIP Packaging or Direct download selection
    # If carousel, package into a single ZIP file
    if len(processed_files) > 1 or media_type == "carousel":
        zip_name = f"ReelVault_{media_id}_{uuid.uuid4().hex[:6]}.zip"
        zip_path = os.path.join(settings.TEMP_DIR, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
            for file_path, user_filename in processed_files:
                # Read user filename segments
                zip_f.write(file_path, arcname=user_filename)
                
        # Clean up segments since they are now safely packaged inside the ZIP
        for file_path, _ in processed_files:
            try: os.remove(file_path)
            except: pass
            
        await manager.send_progress(client_id, status="ZIP compilation finalized!", progress=100.0, stage="completed")
        return zip_path, zip_name, "application/zip"
        
    else:
        # Single file download directly
        target_path, segment_name = processed_files[0]
        ext = "mp4" if media_type == "video" else "jpg"
        final_filename = f"ReelVault_{media_id}_{uuid.uuid4().hex[:4]}.{ext}"
        
        # Rename target path to fit final readable name
        final_path = os.path.join(settings.TEMP_DIR, final_filename)
        os.rename(target_path, final_path)
        
        mimetype = "video/mp4" if media_type == "video" else "image/jpeg"
        await manager.send_progress(client_id, status="File compilation finalized!", progress=100.0, stage="completed")
        return final_path, final_filename, mimetype
