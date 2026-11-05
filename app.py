import csv
import io
import json
import os
import random
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory


DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
SONGS_PATH = DATA_DIR / "songs.json"
RATINGS_PATH = DATA_DIR / "ratings.json"
MAX_UPLOAD_BYTES = 2 * 1024 * 1024

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


def load_json(path, fallback):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def save_json(path, value):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2))
    temporary.replace(path)


def songs():
    return load_json(SONGS_PATH, [])


def ratings():
    return load_json(RATINGS_PATH, {})


def normalize_song(song):
    title = (song.get("title") or song.get("name") or "").strip()
    artist = (song.get("artist") or "Unknown artist").strip() or "Unknown artist"
    album = (song.get("album") or "").strip()
    return {
        "id": song.get("id", secrets.token_hex(8)),
        "title": title[:200],
        "name": title[:200],
        "artist": artist[:200],
        "album": album[:200],
        "genre": (song.get("genre") or "").strip()[:100],
        "image_url": (song.get("image_url") or song.get("image") or "").strip(),
        "spotify_id": (song.get("spotify_id") or "").strip(),
    }


def parse_csv(file_storage):
    raw = file_storage.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("CSV is larger than 2 MB.")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV needs a header row.")
    fields = {field.strip().lower(): field for field in reader.fieldnames if field}
    title_key = fields.get("title") or fields.get("track") or fields.get("track name") or fields.get("name")
    artist_key = fields.get("artist") or fields.get("artist name") or fields.get("album artist")
    album_key = fields.get("album") or fields.get("album name")
    image_key = (
        fields.get("album image url")
        or fields.get("album image")
        or fields.get("image url")
        or fields.get("artwork url")
        or fields.get("cover url")
    )
    spotify_id_key = fields.get("spotify - id") or fields.get("spotify id")
    if not title_key:
        raise ValueError("CSV needs a title, track, or name column.")
    result = []
    for row in reader:
        title = (row.get(title_key) or "").strip()
        artist = (row.get(artist_key) or "Unknown artist").strip() if artist_key else "Unknown artist"
        if title:
            result.append(
                normalize_song(
                    {
                        "id": secrets.token_hex(8),
                        "title": title[:200],
                        "artist": artist[:200] or "Unknown artist",
                        "album": (row.get(album_key) or "").strip()[:200] if album_key else "",
                        "genre": (row.get(fields.get("genre", "")) or "").strip()[:100],
                        "image_url": (row.get(image_key) or "").strip() if image_key else "",
                        "spotify_id": (row.get(spotify_id_key) or "").strip() if spotify_id_key else "",
                    }
                )
            )
    if not result:
        raise ValueError("No songs with titles were found.")
    return result


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/songs")
def get_songs():
    return jsonify({"songs": [normalize_song(song) for song in songs()], "ratings": ratings()})


@app.post("/api/songs/import")
def import_songs():
    if "file" not in request.files:
        return jsonify(error="Choose a CSV file."), 400
    try:
        imported = parse_csv(request.files["file"])
    except (UnicodeDecodeError, ValueError) as error:
        return jsonify(error=str(error)), 400
    save_json(SONGS_PATH, imported)
    save_json(RATINGS_PATH, {})
    return jsonify(count=len(imported))


@app.post("/api/rate")
def rate_song():
    payload = request.get_json(silent=True) or {}
    song_id = payload.get("song_id")
    score = payload.get("score")
    if not isinstance(song_id, str) or not any(song["id"] == song_id for song in songs()):
        return jsonify(error="Unknown song."), 400
    if not isinstance(score, (int, float)) or not 1 <= score <= 5:
        return jsonify(error="Score must be between 1 and 5."), 400
    current = ratings()
    current[song_id] = {"score": score, "votes": current.get(song_id, {}).get("votes", 0) + 1}
    save_json(RATINGS_PATH, current)
    return jsonify(rating=current[song_id])


@app.get("/api/sample")
def sample():
    pool = [normalize_song(song) for song in songs()]
    random.shuffle(pool)
    return jsonify({"songs": pool[:2]})


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
