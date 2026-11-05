# Song Arena

A CSV-first, self-hosted web app for rating songs and discovering favorites through head-to-head matches, tournament rounds, and guided questions.

## Run with Docker

```bash
docker compose up -d --build
```

Open `http://localhost:8080`, then upload a CSV with `title` and `artist` columns. See [`REPORT.md`](REPORT.md) for the product plan, deployment notes, and security posture.

## Install on umbrelOS

This repository is also a third-party Umbrel community app store. In umbrelOS,
open **App Store → Community App Stores → Add**, then enter:

```text
https://github.com/land-o1234/song-arena
```

Install **Song Arena** from the added store. The app stores its song library
and ratings in persistent Umbrel app storage. The container image is published
automatically to GitHub Container Registry when changes land on `main` or a
version tag is pushed.
