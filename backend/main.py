"""
Main FastAPI server for the Exam Paper Downloader.
Provides API endpoints for fetching boards, levels, subjects, and papers.
Updated for asynchronous operations and aiohttp session management.
"""
import os
import json
import uuid
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

try:
    from backend.scraper_service import ExamScraperService
except ImportError:
    from scraper_service import ExamScraperService

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage the lifecycle of the aiohttp ClientSession."""
    async with aiohttp.ClientSession() as session:
        fastapi_app.state.session = session
        yield

app = FastAPI(title="Exam Paper Downloader API", lifespan=lifespan)

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ExamScraperService()
CACHE_FILE = "subject_cache.json"

def load_cache():
    """Load the subject cache from a JSON file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    """Save the subject cache to a JSON file."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f)

@app.get("/boards")
async def get_boards():
    """Return a list of supported examination boards and sources."""
    return [
        {
            "id": "xtremepapers_caie",
            "name": "Cambridge (CAIE) - Xtremepapers",
            "source": "xtremepapers",
            "board": "CAIE"
        },
        {
            "id": "xtremepapers_edexcel",
            "name": "Edexcel - Xtremepapers",
            "source": "xtremepapers",
            "board": "Edexcel"
        },
        {
            "id": "papacambridge_caie",
            "name": "Cambridge (CAIE) - Papacambridge",
            "source": "papacambridge",
            "board": "CAIE"
        },
    ]

@app.get("/levels/{board_id}")
async def get_levels(board_id: str):
    """Return available levels for a specific board."""
    if "caie" in board_id:
        return ["IGCSE", "O Level", "AS and A Level"]
    return ["International GCSE", "Advanced Level"]

@app.get("/subjects")
async def get_subjects(request: Request, source: str, board: str, level: str):
    """Fetch subjects based on source, board, and level."""
    cache = load_cache()
    cache_key = f"{source}_{board}_{level}"

    if cache_key in cache:
        return cache[cache_key]

    session = request.app.state.session
    if source == 'xtremepapers':
        subjects = await service.get_xtremepapers_subjects(session, board, level)
    else:
        subjects = await service.get_papacambridge_subjects(session, level)

    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found")

    # Transform dict to list for easier frontend consumption
    subject_list = [{"name": name, "url": url} for name, url in subjects.items()]

    cache[cache_key] = subject_list
    save_cache(cache)

    return subject_list

@app.get("/papers")
async def get_papers(request: Request, subject_url: str, board: str, source: str):
    """Fetch PDF links for a specific subject."""
    session = request.app.state.session
    papers = await service.get_pdfs(session, subject_url, board, source)
    if not papers:
        raise HTTPException(status_code=404, detail="No papers found")

    # Categorize papers
    categorized = []
    for filename, url in papers.items():
        type_tag = service.categorize_pdf(filename, board)
        categorized.append({
            "name": filename,
            "url": url,
            "type": type_tag
        })

    return categorized

@app.get("/download")
async def download_file(request: Request, url: str, filename: str):
    """Download a specific paper."""
    # Strict reconstruction from constant prefix
    safe_url = service._get_safe_url(url) # pylint: disable=protected-access
    if not safe_url:
        raise HTTPException(status_code=400, detail="Untrusted URL")

    session = request.app.state.session
    try:
        # download_paper returns a safe path derived from a hash
        path = await service.download_paper(session, safe_url, filename)
        # Use only sanitized basename for attachment
        return FileResponse(path, filename=os.path.basename(filename))
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/merge")
async def merge_papers(request: Request, data: dict):
    """Merge multiple papers into a single PDF."""
    session = request.app.state.session
    try:
        papers = data.get("papers", [])
        # Generate an opaque output name
        opaque_output_name = f"merged_{uuid.uuid4().hex}.pdf"
        safe_output_path = service.get_safe_path(opaque_output_name)

        downloaded_paths = []
        for p in papers:
            p_url = p.get("url", "")
            safe_p_url = service._get_safe_url(p_url) # pylint: disable=protected-access
            if not safe_p_url:
                continue
            path = await service.download_paper(session, safe_p_url, p.get("name", "paper.pdf"))
            downloaded_paths.append(path)

        if not downloaded_paths:
            raise HTTPException(status_code=400, detail="No valid papers to merge")

        service.merge_pdfs(downloaded_paths, safe_output_path)
        return FileResponse(safe_output_path, filename="merged_papers.pdf")
    except Exception as e:  # pylint: disable=broad-exception-caught
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
