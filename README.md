# Song Arena

A CSV-first, self-hosted web app for rating songs and discovering favorites through head-to-head matches, tournament rounds, and guided questions.

## Run with Docker

```bash
docker compose up -d --build
```

Open `http://localhost:8080`, then upload a CSV with `title` and `artist` columns. See [`REPORT.md`](REPORT.md) for the product plan, deployment notes, and security posture.
