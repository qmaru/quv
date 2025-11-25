import asyncio
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


async def get_tracker_list() -> list[str]:
    trackers: set[str] = set()

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [fast_get(client, url) for url in TRACKER_URLS]
        results = await asyncio.gather(*tasks)

        trackers: set[str] = set()
        for body in results:
            if not body:
                continue

            body_normalized = body.replace("\r\n\r\n", "\n").replace("\n\n", "\n")
            for line in body_normalized.splitlines():
                s = line.strip()
                if s and not s.startswith("#"):
                    trackers.add(s)
    trackers_sorted = sorted(trackers)
    return trackers_sorted


def save_to_file(trackers: list[str], filepath: Path) -> None:
    with filepath.open("w", encoding="utf-8") as f:
        data = "\r\n".join(trackers)
        f.write(data)


def cli():
    asyncio.run(main())


async def main():
    if len(sys.argv) < 2:
        print("Error: missing required dir argument")
        sys.exit(2)

    work_dir = Path(sys.argv[1]).expanduser().resolve()
    if not work_dir.exists():
        print(f"Error: dir does not exist: {work_dir}", file=sys.stderr)
        sys.exit(2)

    track_output = work_dir / "tracker.txt"
    trackers = await get_tracker_list()
    save_to_file(trackers, track_output)


if __name__ == "__main__":
    asyncio.run(main())
