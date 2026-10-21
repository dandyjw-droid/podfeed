# podfeed

Generate a podcast RSS 2.0 feed (with iTunes tags) from a folder of audio files.
No podcast host, no CMS, no dependencies — just Python 3 and your files.

Born from a real workflow: recording a daily radio show, merging the audio,
and publishing it as a private podcast feed to listen in the car. Everything
the big platforms automate, in one small script you can read in a sitting.

## Features

- Scans a folder of `.mp3` / `.m4a` / `.mp4` / `.wav` / `.ogg` / `.opus` files
- Emits valid RSS 2.0 with `itunes:` namespace: author, category, image,
  owner email, explicit flag, per-episode duration
- Episode dates from file mtime, newest first; GUIDs are stable permalinks
- Durations probed with `ffprobe` when available (graceful without it)
- Config is a tiny `key: value` file (or JSON) — no YAML dependency
- Zero third-party packages. Python 3.9+ standard library only

## Quick start

```bash
# 1. Write a starter config and edit it
python3 podfeed.py init

# 2. Build the feed from your episodes folder
python3 podfeed.py build ./episodes --config feed.yaml --out feed.xml

# 3. Upload feed.xml next to your audio files and subscribe in any podcast app
```

## Example `feed.yaml`

```yaml
title: My Daily Radio Recording
link: https://example.com/
description: Personal recordings published as a private podcast.
language: ko
author: Your Name
email: you@example.com
image_url: https://example.com/cover.jpg
base_url: https://example.com/episodes/
category: Society & Culture
explicit: no
```

Each audio file becomes one episode:

- **Title** — filename without extension (`_` and `-` become spaces)
- **pubDate** — file modification time (UTC)
- **enclosure** — `base_url + filename`, with real byte length and MIME type
- **duration** — `H:MM:SS` from ffprobe, omitted if ffprobe is unavailable

## Why not use a podcast host?

Hosts are great, until the content is *yours*: home recordings, radio captures
for personal use, language lessons, family audio letters. podfeed is for the
long tail of audio that should live on storage you already have (S3, Dropbox,
a home server) and play in the podcast app you already use.

## Roadmap

- Read ID3 / MP4 tags for episode titles and show notes
- Per-episode `.txt` sidecar files for descriptions
- `--watch` mode to rebuild on folder changes
- Optional static HTML index page next to the feed

## Contributing

Issues and PRs welcome. Keep it dependency-free — that's the point of the
project. Please run the test suite before opening a PR:

```bash
python3 -m unittest discover -s tests
```

## License

MIT — see [LICENSE](LICENSE).
