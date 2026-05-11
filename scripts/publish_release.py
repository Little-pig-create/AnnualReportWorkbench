from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = Path(__file__).resolve().parent
REQUEST_TIMEOUT_SECONDS = 900
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from app_metadata import (
    APP_VERSION,
    GITHUB_URL,
    GITEE_URL,
    UPDATE_PORTABLE_ASSET_NAME,
    build_installer_asset_name,
)
from sync_update_manifest import (
    UPDATE_MANIFEST_PATHS,
    compute_sha256,
    sync_update_manifest,
    update_app_metadata,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update GitHub and Gitee releases, then upload exe assets."
    )
    parser.add_argument("--version", help="Release version, for example 1.0.0.")
    parser.add_argument(
        "--target-commitish",
        default="main",
        help="Remote branch or commit used when creating a missing tag. Default: main.",
    )
    parser.add_argument(
        "--portable-asset",
        help="Portable exe path. Default: dist/AnnualReportWorkbench.exe",
    )
    parser.add_argument(
        "--installer-asset",
        help="Installer exe path. Default: dist/installer/<computed-name>",
    )
    parser.add_argument(
        "--release-name",
        help="Optional release title. Default: version string.",
    )
    parser.add_argument(
        "--release-body-file",
        help="Optional markdown file used as release body.",
    )
    parser.add_argument(
        "--github-token",
        default=os.environ.get("GITHUB_PAT_TOKEN", ""),
        help="GitHub PAT. Default: env GITHUB_PAT_TOKEN.",
    )
    parser.add_argument(
        "--gitee-token",
        default=os.environ.get("GITEE_RELEASE_TOKEN") or os.environ.get("GITEE_MCP_AUTHORIZATION", ""),
        help="Gitee token. Default: env GITEE_RELEASE_TOKEN or GITEE_MCP_AUTHORIZATION.",
    )
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub publishing.")
    parser.add_argument("--skip-gitee", action="store_true", help="Skip Gitee publishing.")
    parser.add_argument(
        "--skip-manifest-sync",
        action="store_true",
        help="Skip app_metadata and update.json synchronization.",
    )
    parser.add_argument(
        "--overwrite-assets",
        action="store_true",
        help="Delete same-name assets before upload when the platform supports it.",
    )
    parser.add_argument("--prerelease", action="store_true", help="Publish as prerelease.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve inputs without calling remote APIs.")
    return parser.parse_args()


def parse_owner_repo(repo_url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(repo_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"Invalid repository url: {repo_url}")
    return parts[0], parts[1]


def default_asset_paths(version: str) -> tuple[Path, Path]:
    portable_path = PROJECT_ROOT / "dist" / UPDATE_PORTABLE_ASSET_NAME
    installer_path = PROJECT_ROOT / "dist" / "installer" / build_installer_asset_name(version)
    return portable_path, installer_path


def ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def encode_json(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def encode_form(payload: dict[str, str]) -> bytes:
    return urllib.parse.urlencode(payload).encode("utf-8")


def encode_multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----AnnualReportWorkbench{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    segments: list[bytes] = []

    for key, value in fields.items():
        segments.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )

    segments.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'.encode("utf-8"),
            f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(segments), f"multipart/form-data; boundary={boundary}"


def request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
) -> tuple[object, int]:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read()
            status = response.getcode()
            if not body:
                return None, status
            charset = response.headers.get_content_charset() or "utf-8"
            text = body.decode(charset)
            return json.loads(text), status
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code} {payload}") from exc


def github_headers(token: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "AnnualReportWorkbench-ReleaseScript",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if extra:
        headers.update(extra)
    return headers


def read_release_notes() -> list[str]:
    payload = json.loads((PROJECT_ROOT / "update.json").read_text(encoding="utf-8"))
    notes = payload.get("notes") or []
    return [str(note).strip() for note in notes if str(note).strip()]


def build_release_body(version: str, installer_name: str, portable_name: str, body_file: str | None) -> str:
    if body_file:
        return Path(body_file).read_text(encoding="utf-8").strip()

    lines = [
        f"Annual Report Workbench {version}",
        "",
        f"- 安装包：`{installer_name}`",
        f"- 便携版：`{portable_name}`",
        "- 渠道：GitHub / Gitee",
    ]
    notes = read_release_notes()
    if notes:
        lines.extend(["", "## 更新内容"])
        lines.extend([f"- {note}" for note in notes])
    return "\n".join(lines).strip()


def github_get_release(owner: str, repo: str, tag: str, token: str) -> dict | None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{urllib.parse.quote(tag)}"
    try:
        payload, _ = request("GET", url, headers=github_headers(token))
        return payload  # type: ignore[return-value]
    except RuntimeError as exc:
        if "HTTP 404" in str(exc):
            return None
        raise


def github_create_or_update_release(
    owner: str,
    repo: str,
    version: str,
    token: str,
    *,
    release_name: str,
    release_body: str,
    target_commitish: str,
    prerelease: bool,
) -> dict:
    payload = {
        "tag_name": version,
        "target_commitish": target_commitish,
        "name": release_name,
        "body": release_body,
        "draft": False,
        "prerelease": prerelease,
    }
    existing = github_get_release(owner, repo, version, token)
    if existing:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/{existing['id']}"
        updated, _ = request(
            "PATCH",
            url,
            headers=github_headers(token, {"Content-Type": "application/json; charset=utf-8"}),
            data=encode_json(payload),
        )
        return updated  # type: ignore[return-value]

    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    created, _ = request(
        "POST",
        url,
        headers=github_headers(token, {"Content-Type": "application/json; charset=utf-8"}),
        data=encode_json(payload),
    )
    return created  # type: ignore[return-value]


def github_delete_asset(owner: str, repo: str, asset_id: int, token: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    request("DELETE", url, headers=github_headers(token))


def github_upload_asset(release: dict, asset_path: Path, token: str) -> str:
    upload_url = str(release["upload_url"]).split("{", 1)[0]
    query = urllib.parse.urlencode({"name": asset_path.name})
    url = f"{upload_url}?{query}"
    content_type = mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
    payload, _ = request(
        "POST",
        url,
        headers=github_headers(token, {"Content-Type": content_type}),
        data=asset_path.read_bytes(),
    )
    return str(payload["browser_download_url"])  # type: ignore[index]


def gitee_list_releases(owner: str, repo: str, token: str) -> list[dict]:
    query = urllib.parse.urlencode({"access_token": token, "per_page": "100"})
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases?{query}"
    payload, _ = request("GET", url)
    return payload  # type: ignore[return-value]


def gitee_get_release(owner: str, repo: str, tag: str, token: str) -> dict | None:
    for release in gitee_list_releases(owner, repo, token):
        if release.get("tag_name") == tag:
            return release
    return None


def gitee_create_or_update_release(
    owner: str,
    repo: str,
    version: str,
    token: str,
    *,
    release_name: str,
    release_body: str,
    target_commitish: str,
    prerelease: bool,
) -> dict:
    payload = {
        "access_token": token,
        "tag_name": version,
        "name": release_name,
        "body": release_body,
        "target_commitish": target_commitish,
        "prerelease": "true" if prerelease else "false",
    }
    existing = gitee_get_release(owner, repo, version, token)
    if existing:
        url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/{existing['id']}"
        try:
            updated, _ = request(
                "PATCH",
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
                data=encode_form(payload),
            )
            return updated  # type: ignore[return-value]
        except RuntimeError:
            return existing

    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases"
    created, _ = request(
        "POST",
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
        data=encode_form(payload),
    )
    return created  # type: ignore[return-value]


def gitee_list_assets(owner: str, repo: str, release_id: int, token: str) -> list[dict]:
    query = urllib.parse.urlencode({"access_token": token})
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/{release_id}/attach_files?{query}"
    payload, _ = request("GET", url)
    return payload  # type: ignore[return-value]


def gitee_delete_asset(owner: str, repo: str, release_id: int, asset_id: int, token: str) -> None:
    query = urllib.parse.urlencode({"access_token": token})
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/{release_id}/attach_files/{asset_id}?{query}"
    request("DELETE", url)


def gitee_upload_asset(owner: str, repo: str, release_id: int, token: str, asset_path: Path) -> str:
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/{release_id}/attach_files"
    body, content_type = encode_multipart({"access_token": token}, "file", asset_path)
    payload, _ = request("POST", url, headers={"Content-Type": content_type}, data=body)
    return str(payload["browser_download_url"])  # type: ignore[index]


def sync_release_files(version: str, installer_path: Path) -> str:
    sha256 = compute_sha256(installer_path)
    update_app_metadata(version)
    for path in UPDATE_MANIFEST_PATHS:
        sync_update_manifest(path, version, sha256=sha256)
    return sha256


def publish_github(
    version: str,
    release_name: str,
    release_body: str,
    token: str,
    target_commitish: str,
    prerelease: bool,
    asset_paths: list[Path],
    overwrite_assets: bool,
) -> dict[str, object]:
    owner, repo = parse_owner_repo(GITHUB_URL)
    release = github_create_or_update_release(
        owner,
        repo,
        version,
        token,
        release_name=release_name,
        release_body=release_body,
        target_commitish=target_commitish,
        prerelease=prerelease,
    )
    existing_assets = {asset["name"]: asset for asset in release.get("assets", [])}
    uploaded_assets: dict[str, str] = {}
    for asset_path in asset_paths:
        existing = existing_assets.get(asset_path.name)
        if existing and overwrite_assets:
            github_delete_asset(owner, repo, int(existing["id"]), token)
        elif existing:
            uploaded_assets[asset_path.name] = str(existing["browser_download_url"])
            continue
        uploaded_assets[asset_path.name] = github_upload_asset(release, asset_path, token)
    return {
        "platform": "github",
        "release_id": release["id"],
        "html_url": release["html_url"],
        "assets": uploaded_assets,
    }


def publish_gitee(
    version: str,
    release_name: str,
    release_body: str,
    token: str,
    target_commitish: str,
    prerelease: bool,
    asset_paths: list[Path],
    overwrite_assets: bool,
) -> dict[str, object]:
    owner, repo = parse_owner_repo(GITEE_URL)
    release = gitee_create_or_update_release(
        owner,
        repo,
        version,
        token,
        release_name=release_name,
        release_body=release_body,
        target_commitish=target_commitish,
        prerelease=prerelease,
    )
    release_id = int(release["id"])
    existing_assets = {asset["name"]: asset for asset in gitee_list_assets(owner, repo, release_id, token)}
    uploaded_assets: dict[str, str] = {}
    for asset_path in asset_paths:
        existing = existing_assets.get(asset_path.name)
        if existing and overwrite_assets:
            gitee_delete_asset(owner, repo, release_id, int(existing["id"]), token)
        elif existing:
            uploaded_assets[asset_path.name] = str(existing["browser_download_url"])
            continue
        uploaded_assets[asset_path.name] = gitee_upload_asset(owner, repo, release_id, token, asset_path)
    return {
        "platform": "gitee",
        "release_id": release_id,
        "html_url": release.get("html_url") or f"{GITEE_URL}/releases/tag/{version}",
        "assets": uploaded_assets,
    }


def main() -> int:
    args = parse_args()
    version = args.version or APP_VERSION
    release_name = args.release_name or version
    default_portable_path, default_installer_path = default_asset_paths(version)
    portable_path = Path(args.portable_asset).resolve() if args.portable_asset else default_portable_path
    installer_path = Path(args.installer_asset).resolve() if args.installer_asset else default_installer_path
    asset_paths = [portable_path, installer_path]

    if not args.dry_run:
        ensure_exists(portable_path, "Portable asset")
        ensure_exists(installer_path, "Installer asset")

    if not args.skip_manifest_sync:
        if args.dry_run:
            raise RuntimeError("Dry run mode requires --skip-manifest-sync when release assets are not being verified.")
        sha256 = sync_release_files(version, installer_path)
        print(f"Synced manifests with installer sha256: {sha256}")

    release_body = build_release_body(version, installer_path.name, portable_path.name, args.release_body_file)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "version": version,
                    "target_commitish": args.target_commitish,
                    "prerelease": args.prerelease,
                    "release_name": release_name,
                    "portable_asset": str(portable_path),
                    "installer_asset": str(installer_path),
                    "publish_github": not args.skip_github,
                    "publish_gitee": not args.skip_gitee,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    results: list[dict[str, object]] = []
    if not args.skip_github:
        if not args.github_token:
            raise RuntimeError("GitHub token is required. Use --github-token or set GITHUB_PAT_TOKEN.")
        results.append(
            publish_github(
                version,
                release_name,
                release_body,
                args.github_token,
                args.target_commitish,
                args.prerelease,
                asset_paths,
                args.overwrite_assets,
            )
        )

    if not args.skip_gitee:
        if not args.gitee_token:
            raise RuntimeError("Gitee token is required. Use --gitee-token or set GITEE_RELEASE_TOKEN.")
        results.append(
            publish_gitee(
                version,
                release_name,
                release_body,
                args.gitee_token,
                args.target_commitish,
                args.prerelease,
                asset_paths,
                args.overwrite_assets,
            )
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
