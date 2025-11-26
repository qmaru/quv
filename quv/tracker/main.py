import asyncio
import os
import sys
from pathlib import Path

import httpx

TRACKER_URLS = [
    # https://github.com/ngosang/trackerslist
    "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best_ip.txt",
    # https://trackerslist.com/#/zh
    "https://raw.githubusercontent.com/XIU2/TrackersListCollection/refs/heads/master/best.txt",
    # https://github.com/DeSireFire/animeTrackerList
    "https://raw.githubusercontent.com/DeSireFire/animeTrackerList/master/AT_best.txt",
]


async def fast_get(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPError as err:
        print(f"get tracker url error: {err} (url={url})")
        return None
    except Exception as err:
        print(f"unexpected error fetching {url}: {err}")
        return None


def parse_tracker(body: str) -> set[str]:
    trackers: set[str] = set()
    if not body:
        return trackers
    body = body.lstrip("\ufeff")
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        trackers.add(s)
    return trackers


async def get_tracker_list() -> list[str]:
    trackers: set[str] = set()

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [fast_get(client, url) for url in TRACKER_URLS]
        results = await asyncio.gather(*tasks)

        for body in results:
            if not body:
                continue
            trackers |= parse_tracker(body)

    trackers_sorted = sorted(trackers)
    return trackers_sorted


def save_to_file(trackers: list[str], filepath: Path) -> None:
    with filepath.open("w", encoding="utf-8") as f:
        data = "\r\n".join(trackers)
        f.write(data)


def get_folder() -> Path:
    if len(sys.argv) < 2:
        print("Error: missing required directory argument")
        sys.exit(2)

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"Error: directory does not exist: {root}", file=sys.stderr)
        sys.exit(2)

    if not root.is_dir():
        print(f"Error: path is not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    if not os.access(root, os.W_OK):
        print(f"Error: directory is not writable: {root}", file=sys.stderr)
        sys.exit(2)

    return root


def cli():
    asyncio.run(main())


async def main():
    work_dir = get_folder()
    track_output = work_dir / "tracker.txt"
    try:
        trackers = await get_tracker_list()
        save_to_file(trackers, track_output)
        print(f"Tracker list saved to: {track_output}")
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
