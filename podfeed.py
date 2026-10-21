#!/usr/bin/env python3
"""podfeed - Generate a podcast RSS 2.0 feed from a folder of audio files.

Usage:
    python3 podfeed.py build ./episodes --config feed.yaml --out feed.xml
    python3 podfeed.py init            # write a starter feed.yaml

No third-party dependencies. Durations are read with ffprobe when it is
available; without it, episodes are still listed (duration tag omitted).
"""

import argparse
import html
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

AUDIO_EXTS = {".mp3": "audio/mpeg", ".m4a": "audio/x-m4a", ".mp4": "audio/mp4",
              ".wav": "audio/wav", ".ogg": "audio/ogg", ".opus": "audio/ogg"}

DEFAULT_CONFIG = {
    "title": "My Podcast",
    "link": "https://example.com/",
    "description": "A podcast generated with podfeed.",
    "language": "en",
    "author": "",
    "email": "",
    "image_url": "",
    "base_url": "https://example.com/episodes/",
    "category": "Technology",
    "explicit": "no",
}


def load_config(path):
    """Load a tiny YAML-subset config (key: value lines) or JSON."""
    cfg = dict(DEFAULT_CONFIG)
    if not path:
        return cfg
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".json"):
        cfg.update(json.loads(text))
        return cfg
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


def probe_duration(path):
    """Return duration in seconds (float) via ffprobe, or None."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=15)
        return float(out.stdout.strip())
    except Exception:
        return None


def fmt_duration(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def collect_episodes(folder):
    episodes = []
    for name in sorted(os.listdir(folder)):
        ext = os.path.splitext(name)[1].lower()
        if ext not in AUDIO_EXTS:
            continue
        path = os.path.join(folder, name)
        stat = os.stat(path)
        episodes.append({
            "file": name,
            "path": path,
            "size": stat.st_size,
            "mime": AUDIO_EXTS[ext],
            "title": os.path.splitext(name)[0].replace("_", " ").replace("-", " ").strip(),
            "date": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            "duration": probe_duration(path),
        })
    # Newest first, the way podcast apps expect.
    episodes.sort(key=lambda e: e["date"], reverse=True)
    return episodes


def esc(text):
    return html.escape(str(text), quote=True)


def build_feed(folder, cfg):
    base = cfg["base_url"].rstrip("/") + "/"
    items = []
    for ep in collect_episodes(folder):
        url = base + ep["file"]
        guid = url
        dur = (f"\n      <itunes:duration>{fmt_duration(ep['duration'])}</itunes:duration>"
               if ep["duration"] else "")
        items.append(f"""    <item>
      <title>{esc(ep['title'])}</title>
      <pubDate>{format_datetime(ep['date'])}</pubDate>
      <guid isPermaLink="true">{esc(guid)}</guid>
      <enclosure url="{esc(url)}" length="{ep['size']}" type="{ep['mime']}"/>{dur}
    </item>""")
    image = (f'\n    <itunes:image href="{esc(cfg["image_url"])}"/>'
             if cfg.get("image_url") else "")
    owner = ""
    if cfg.get("email"):
        owner = (f"\n    <itunes:owner><itunes:email>{esc(cfg['email'])}</itunes:email>"
                 f"</itunes:owner>")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{esc(cfg['title'])}</title>
    <link>{esc(cfg['link'])}</link>
    <description>{esc(cfg['description'])}</description>
    <language>{esc(cfg['language'])}</language>{image}
    <itunes:author>{esc(cfg['author'])}</itunes:author>{owner}
    <itunes:category text="{esc(cfg['category'])}"/>
    <itunes:explicit>{esc(cfg['explicit'])}</itunes:explicit>
{chr(10).join(items)}
  </channel>
</rss>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(prog="podfeed", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build feed.xml from an episodes folder")
    b.add_argument("folder")
    b.add_argument("--config", default=None)
    b.add_argument("--out", default="feed.xml")
    sub.add_parser("init", help="write a starter feed.yaml")
    args = parser.parse_args(argv)

    if args.cmd == "init":
        sample = "\n".join(f"{k}: {v}" for k, v in DEFAULT_CONFIG.items()) + "\n"
        with open("feed.yaml", "w", encoding="utf-8") as f:
            f.write(sample)
        print("Wrote feed.yaml - edit it, then run: podfeed build ./episodes --config feed.yaml")
        return 0

    cfg = load_config(args.config)
    xml = build_feed(args.folder, cfg)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(xml)
    count = xml.count("<item>")
    print(f"Wrote {args.out} with {count} episode(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
