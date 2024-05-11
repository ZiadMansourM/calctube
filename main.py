from concurrent.futures import ThreadPoolExecutor
import re
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pytube import Playlist, YouTube


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/assets/{filename}")
async def read_item(filename: str):
    return FileResponse(f"templates/assets/{filename}")

def timeit(func):
    def wrapper(*args, **kwargs):
        print(f"Started {func.__name__}...")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Done {func.__name__} took {(end_time - start_time)*1000:.2f} ms to execute.")
        return result
    return wrapper


def get_playlist_id(link: str) -> str:
    video_pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=)?([a-zA-Z0-9_-]+)&?list=([a-zA-Z0-9_-]+)'
    if match := re.match(video_pattern, link):
        return match[5]

    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com/playlist\?list=)?([a-zA-Z0-9_-]+)'
    return match[4] if (match := re.match(playlist_pattern, link)) else link


def get_video_length(url: str) -> int:
    yt = YouTube(url)
    return yt.length


def get_playlist_duration(playlist_url: str) -> tuple[int, int, float]:
    playlist_id = get_playlist_id(playlist_url)
    playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")
    video_count = len(playlist.video_urls)

    total_seconds = 0
    with ThreadPoolExecutor(max_workers=video_count) as executor:
        total_seconds = sum(executor.map(get_video_length, playlist.video_urls))

    avg_video_length = total_seconds / video_count if video_count != 0 else 0

    return total_seconds, video_count, avg_video_length


def calculate_speed_times(total_seconds: int) -> dict:
    speeds = [1, 1.25, 1.5, 1.75, 2]
    times = {}

    for speed in speeds:
        time_at_speed = total_seconds / speed
        hours = int(time_at_speed // 3600)
        minutes = int((time_at_speed % 3600) // 60)
        seconds = int(time_at_speed % 60)
        times[speed] = f"{hours} hours, {minutes} minutes, {seconds} seconds"

    return times


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"


@timeit
def run(user_input: str):
    total_seconds, video_count, avg_video_length = get_playlist_duration(user_input)
    times = calculate_speed_times(total_seconds)

    return {
        "videoCount": video_count,
        "avgVideoLength": format_time(avg_video_length),
        "speedTimes": dict(times.items()),
    }

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class PlaylistUrl(BaseModel):
    playlistUrl: str

@app.post("/calculate")
async def calculate_playlist_duration(playlist_url: PlaylistUrl):
    response_data = run(playlist_url.playlistUrl)
    return JSONResponse(content=response_data)
