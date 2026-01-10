from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from backend.scraper_service import ExamScraperService
except ImportError:
    from scraper_service import ExamScraperService
import os
import json

app = FastAPI(title="Exam Paper Downloader API")

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
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@app.get("/boards")
async def get_boards():
    return [
        {"id": "xtremepapers_caie", "name": "Cambridge (CAIE) - Xtremepapers", "source": "xtremepapers", "board": "CAIE"},
        {"id": "xtremepapers_edexcel", "name": "Edexcel - Xtremepapers", "source": "xtremepapers", "board": "Edexcel"},
        {"id": "papacambridge_caie", "name": "Cambridge (CAIE) - Papacambridge", "source": "papacambridge", "board": "CAIE"},
    ]

@app.get("/levels/{board_id}")
async def get_levels(board_id: str):
    if "caie" in board_id:
        return ["IGCSE", "O Level", "AS and A Level"]
    return ["International GCSE", "Advanced Level"]

@app.get("/subjects")
async def get_subjects(source: str, board: str, level: str):
    cache = load_cache()
    cache_key = f"{source}_{board}_{level}"

    if cache_key in cache:
        return cache[cache_key]

    if source == 'xtremepapers':
        subjects = service.get_xtremepapers_subjects(board, level)
    else:
        subjects = service.get_papacambridge_subjects(level)

    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found")

    # Transform dict to list for easier frontend consumption
    subject_list = [{"name": name, "url": url} for name, url in subjects.items()]

    cache[cache_key] = subject_list
    save_cache(cache)

    return subject_list

@app.get("/papers")
async def get_papers(subject_url: str, board: str, source: str):
    papers = service.get_pdfs(subject_url, board, source)
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

from fastapi.responses import FileResponse, JSONResponse
import uuid

@app.get("/download")
async def download_file(url: str, filename: str):
    try:
        path = await service.download_paper(url, filename)
        return FileResponse(path, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/merge")
async def merge_papers(data: dict):
    # data format: {"papers": [{"url": "...", "name": "..."}, ...], "output_name": "..."}
    try:
        papers = data.get("papers", [])
        output_name = data.get("output_name", f"merged_{uuid.uuid4().hex[:8]}.pdf")

        downloaded_paths = []
        for p in papers:
            path = await service.download_paper(p["url"], p["name"])
            downloaded_paths.append(path)

        output_path = os.path.join("temp_downloads", output_name)
        service.merge_pdfs(downloaded_paths, output_path)

        return FileResponse(output_path, filename=output_name)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
