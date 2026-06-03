from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import os
import urllib.parse
from backend.app.scrapers.instagram import scraper_engine
from backend.app.services.downloader import process_media_download
from backend.app.websocket.manager import manager
from backend.app.core.config import settings

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str
    client_id: Optional[str] = None

class DownloadRequest(BaseModel):
    url: str
    compression: Optional[str] = "original" # "original" or "compressed"
    client_id: Optional[str] = None

@router.post("/analyze")
async def analyze_url(payload: AnalyzeRequest):
    """Sanitizes URL and parses Instagram media items, triggering progress notifications via WebSockets."""
    client_id = payload.client_id
    url = payload.url
    
    if client_id:
        await manager.send_progress(client_id, status="Validating URL target...", progress=5.0, stage="validating")
        
    try:
        if client_id:
            await manager.send_progress(client_id, status="Connecting to Instagram nodes...", progress=15.0, stage="connecting")
            
        # Call scrape pipeline
        scraped_data = scraper_engine.scrape(url)
        
        if client_id:
            msg = "Media extracted successfully!"
            if scraped_data.get("fallback_active"):
                msg = scraped_data.get("fallback_message", "Instagram server rate limit reached. Fallback simulation enabled.")
            await manager.send_progress(client_id, status=msg, progress=100.0, stage="finalized", data=scraped_data)
            
        return scraped_data
    except Exception as e:
        error_msg = str(e)
        if "PrivateProfile" in error_msg or "private account" in error_msg.lower():
            resolved_err = "Private Account Detected: Content from private profiles cannot be scraped for security constraints."
        else:
            resolved_err = f"Extraction failed: {error_msg}"
            
        if client_id:
            await manager.send_progress(client_id, status=resolved_err, progress=0.0, stage="error")
            
        raise HTTPException(status_code=400, detail=resolved_err)

@router.post("/download")
async def download_media(payload: DownloadRequest):
    """Processes final download (fetching media, compression, ZIP compilation as needed) and returns cache reference."""
    client_id = payload.client_id
    url = payload.url
    compression = payload.compression or "original"
    
    if client_id:
        await manager.send_progress(client_id, status="Initiating secure data download sequence...", progress=10.0, stage="initializing")
        
    try:
        # Step 1: Extract meta details again (or fetch from scraper cache)
        meta = scraper_engine.scrape(url)
        
        # Step 2: Download segments, compress, compile package archive
        file_path, filename, mimetype = await process_media_download(
            client_id=client_id or "default",
            media_data=meta,
            compression=compression
        )
        
        # Encode file path securely to prevent directory traversal
        encoded_filename = urllib.parse.quote(os.path.basename(file_path))
        download_url = f"/api/download-file?token={encoded_filename}"
        
        # Return package path metadata to trigger client browser click
        return {
            "success": True,
            "filename": filename,
            "mimetype": mimetype,
            "download_url": download_url
        }
        
    except Exception as e:
        error_msg = str(e)
        if client_id:
            await manager.send_progress(client_id, status=f"Download failed: {error_msg}", progress=0.0, stage="error")
        raise HTTPException(status_code=400, detail=f"Compile failure: {error_msg}")

@router.get("/media/info")
async def get_media_info(url: str = Query(..., description="The Instagram URL to inspect")):
    """Helper GET endpoint to fetch simple parsing info without progress trackers."""
    try:
        scraped_data = scraper_engine.scrape(url)
        return scraped_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download-file")
async def serve_downloaded_file(token: str):
    """Serves the generated media or zip file and handles client header naming."""
    # Prevent basic directory traversal
    safe_token = os.path.basename(token)
    filepath = os.path.join(settings.TEMP_DIR, safe_token)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File has expired or is no longer available inside active vault transit.")
        
    # Serve file download
    return FileResponse(
        path=filepath,
        filename=safe_token,
        media_type="application/octet-stream"
    )
