import argparse
import os
import sys
from configparser import ConfigParser
from pathlib import Path


def read_config(config: Path):
    if not config.exists():
        raise FileNotFoundError(f"Config file not found: {config}")

    try:
        parser = ConfigParser()
        parser.read(config, encoding="utf-8")
        if parser.has_section("tmdb"):
            return {key.strip(): value.strip() for key, value in parser["tmdb"].items()}
        return None
    except BaseException as e:
        raise (e)


def parse_tmdb(tmdb_mapping: dict, files: list[Path]):
    videos: list[dict] = []

    if not files or not tmdb_mapping:
        return videos

    separators = [".ep", "_ep_"]

    for file in files:
        file_name = file.name
        file_root = file.parent

        name_lower = file_name.lower()
        found = False
        for sep in separators:
            if sep in name_lower:
                idx = name_lower.find(sep)
                old_title = file_name[:idx]
                suffix = file_name[idx + len(sep) :]
                found = True
                break
        if not found:
            continue

        old_title = old_title.rstrip("._- ").strip()
        ep_str, ext = os.path.splitext(suffix)

        norm_old_title = old_title.lower().strip()
        for tmdb_key, tmdb_value in tmdb_mapping.items():
            if norm_old_title == tmdb_key.lower().strip():
                new_title = tmdb_value if tmdb_value else f"{old_title}.S01"
                new_filename = f"{new_title}EP{ep_str}{ext}"
                new_filepath = file_root / new_filename
                videos.append({"old_filepath": str(file), "new_filepath": str(new_filepath)})
                break
        else:
            new_title = f"{old_title}.S01"
            new_filename = f"{new_title}EP{ep_str}{ext}"
            new_filepath = file_root / new_filename
            videos.append({"old_filepath": str(file), "new_filepath": str(new_filepath)})

    return videos


def get_files(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: file does not exist: {filepath}")
        sys.exit(2)

    files: list[Path] = []
    if os.path.isdir(filepath):
        rootpath = os.path.abspath(filepath)
        entries = [os.path.join(rootpath, f) for f in os.listdir(rootpath)]
        for entry in entries:
            if os.path.isfile(entry):
                files.append(Path(os.path.join(rootpath, entry)))
        return files
    else:
        files.append(Path(filepath))

    return files


def get_args_parser():
    parser = argparse.ArgumentParser(description="TMDB File Renamer")
    parser.add_argument("-c", dest="config", type=str, help="ini config file")
    parser.add_argument("-f", dest="filepath", type=str, help="file or directory")
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="print planned renames without performing them",
    )
    return parser


def cli():
    main()


def main():
    args_parser = get_args_parser()
    args = args_parser.parse_args()

    filepath = args.filepath
    config = args.config
    dry_run = args.dry_run

    if filepath and config:
        tmdb_mapping = read_config(Path(config))
        if not tmdb_mapping:
            print("Error: no TMDB mapping found in config")
            sys.exit(2)

        files = get_files(filepath)
        tasks = parse_tmdb(tmdb_mapping, files)
        for task in tasks:
            old = Path(task["old_filepath"])
            new = Path(task["new_filepath"])
            print(f"{old} -> {new}")
            if dry_run:
                continue
            if old.samefile(new) if new.exists() and old.exists() else old == new:
                print(f"Skip: source and target are same: {old}")
                continue
            if new.exists():
                print(f"Warning: target already exists, skip: {new}")
                continue
            try:
                os.rename(str(old), str(new))
            except Exception as e:
                print(f"Error renaming {old} -> {new}: {e}")
    else:
        args_parser.print_help()
        print("Error: missing required arguments")
        sys.exit(2)


if __name__ == "__main__":
    main()
