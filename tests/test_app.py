import io
import unittest

from app import normalize_song, parse_csv


class InMemoryUpload:
    def __init__(self, text):
        self.stream = io.BytesIO(text.encode("utf-8"))

    def read(self, limit=-1):
        return self.stream.read(limit)


class ParseCsvTests(unittest.TestCase):
    def test_supports_spotify_export_headers(self):
        upload = InMemoryUpload("Track name,Artist name,Album,Spotify - id\nSong A,Artist A,Album A,abc123\n")
        songs = parse_csv(upload)
        self.assertEqual(1, len(songs))
        self.assertEqual("Song A", songs[0]["title"])
        self.assertEqual("Artist A", songs[0]["artist"])
        self.assertEqual("Album A", songs[0]["album"])
        self.assertEqual("abc123", songs[0]["spotify_id"])

    def test_normalize_song_adds_required_display_fields(self):
        song = normalize_song({"name": "N", "artist": "A", "album": "B"})
        self.assertEqual("N", song["title"])
        self.assertEqual("N", song["name"])
        self.assertEqual("A", song["artist"])
        self.assertEqual("B", song["album"])
        self.assertIn("image_url", song)


if __name__ == "__main__":
    unittest.main()
