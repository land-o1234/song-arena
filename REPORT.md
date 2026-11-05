# Song Arena — project report

## What it is

Song Arena is a self-hosted, CSV-first web app for turning a personal song list into a favorite ranking. The first release includes head-to-head choices, a lightweight tournament mode, vibe-based questions, and a favorites view that surfaces repeated choices.

Spotify is intentionally not required. A future adapter can import a Spotify playlist into the same normalized song shape without coupling the core app to OAuth, external availability, or third-party tracking.

## Home-server deployment

1. Copy the project to the server.
2. Run `docker compose up -d --build`.
3. Open `http://SERVER_IP:8080` on the home network.
4. Upload a CSV based on `sample-songs.csv`.

Put a reverse proxy with HTTPS and authentication in front of the app before exposing it beyond the trusted LAN. The app stores its library and ratings in the named Docker volume `song-arena-data`.

## Security posture

- The container runs as an unprivileged user, drops all Linux capabilities, disables privilege escalation, and uses a read-only root filesystem.
- Persistent writes are limited to `/data`; `/tmp` is a memory-backed filesystem.
- CSV uploads are capped at 2 MB, decoded as UTF-8, and reduced to a small allow-list of fields with bounded lengths.
- The app uses JSON APIs and does not render imported song text as HTML; browser output is escaped.
- There is no Spotify credential, analytics, or outbound network requirement.
- The default compose file binds the port on all host interfaces. Restrict it with a firewall or bind to `127.0.0.1` when using a reverse proxy.

This is a LAN-oriented MVP, not an internet-facing identity system. Add authentication, CSRF protection, rate limiting, and HTTPS termination at the proxy before public exposure.

## Next milestones

1. Add a proper tournament bracket with persisted rounds and Elo/Bradley-Terry scoring.
2. Add optional Spotify playlist import behind a server-side OAuth integration.
3. Add weighted questions and an explainable recommendation algorithm.
4. Add account/profile separation if multiple household users need independent rankings.
