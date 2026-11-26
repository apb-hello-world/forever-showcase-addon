"""Build a ForeverShowcase-only ZIP and upload it through the CurseForge author API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request
import uuid
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
API = "https://wow.curseforge.com/api"
PROJECT = int(os.environ.get("CF_PROJECT_ID", "1832297"))
GAME_TYPE = 88568  # WoW Forever
GAME_VERSION = "1.60.1"
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+(?:-(?:alpha|beta)\.[0-9]+)?"


def version():
    toc = (ROOT / "ForeverShowcase" / "ForeverShowcase.toc").read_text(encoding="utf-8")
    found = re.search(r"^## Version: (.+)$", toc, re.M)
    if not found or not re.fullmatch(VERSION_PATTERN, found[1]):
        raise ValueError("Invalid addon version")
    return found[1]


def build(tag=None):
    from package import package
    current = version()
    if tag != 'addon-v' + current:
        raise ValueError('Tag must match the addon version')
    changelog = ROOT / 'changelogs' / (current + '.txt')
    if not changelog.read_text(encoding='utf-8').strip():
        raise ValueError('A changelog is required')
    return package()[0], changelog


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def api(path, payload=None, content_type=None):
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token:
        raise ValueError("Add the CF_API_TOKEN repository secret before using CurseForge")
    headers = {"X-Api-Token": token, "Accept": "application/json", "User-Agent": "ForeverShowcase-release/1"}
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(API + path, data=payload, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=90) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise ValueError("CurseForge returned HTTP " + str(error.code) + "; no automatic retry was made") from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError("CurseForge connection failed. Check whether the file arrived before retrying an upload.") from None


def game_version():
    versions = api("/game/wow/versions")
    matches = [v["id"] for v in versions if v.get("name") == GAME_VERSION and v.get("gameVersionTypeID") == GAME_TYPE]
    if len(matches) != 1:
        raise ValueError("Expected exactly one WoW Forever " + GAME_VERSION + " version; refusing to guess")
    print("CurseForge credentials accepted; Forever " + GAME_VERSION + " version ID " + str(matches[0]))
    return matches[0]


def upload(tag):
    if os.environ.get("GITHUB_EVENT_NAME") != "push" or os.environ.get("GITHUB_REF") != "refs/tags/" + tag:
        raise ValueError("Uploads are only allowed from a pushed release tag")
    if os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise ValueError("Automatic reuploads are disabled. Check CurseForge for the previous upload first.")
    if PROJECT <= 0:
        raise ValueError("Set CF_PROJECT_ID to the CurseForge project ID")
    archive, changelog = build(tag)
    current = version()
    metadata = {"displayName": "ForeverShowcase " + current, "gameVersions": [game_version()],
                "releaseType": "alpha" if "-alpha." in current else "beta" if "-beta." in current else "release",
                "changelogType": "text", "changelog": changelog.read_text(encoding="utf-8")}
    boundary = "ForeverShowcase" + uuid.uuid4().hex
    body = ("--" + boundary + '\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n').encode()
    body += json.dumps(metadata).encode() + b"\r\n"
    body += ("--" + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="' + archive.name + '"\r\nContent-Type: application/zip\r\n\r\n').encode()
    body += archive.read_bytes() + ("\r\n--" + boundary + "--\r\n").encode()
    result = api("/projects/" + str(PROJECT) + "/upload-file", body, "multipart/form-data; boundary=" + boundary)
    if not isinstance(result, dict) or not isinstance(result.get("id"), int):
        raise ValueError("Upload returned no file ID; inspect CurseForge before retrying")
    summary = "Uploaded ForeverShowcase " + current + " to CurseForge. File ID: " + str(result["id"])
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(summary + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "check", "upload"])
    parser.add_argument("--tag")
    args = parser.parse_args()
    try:
        if args.command == "check":
            game_version()
        elif args.command == "upload":
            if not args.tag:
                raise ValueError("A version tag is required")
            upload(args.tag)
        else:
            build(args.tag)
    except (ValueError, OSError) as error:
        sys.exit(str(error))
