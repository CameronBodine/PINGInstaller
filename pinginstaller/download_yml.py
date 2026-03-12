import os
import time
import urllib.error
import urllib.parse
import urllib.request

home_path = os.path.expanduser('~')


def _normalize_github_url(url):
    """
    Convert GitHub blob URLs to raw.githubusercontent.com URLs.
    Leaves non-GitHub URLs unchanged.
    """
    if isinstance(url, bytes):
        url = url.decode("utf-8", errors="ignore")
    else:
        url = str(url)

    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()

    if host in ("github.com", "www.github.com"):
        # Expected: /owner/repo/blob/branch/path/to/file.yml
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 5 and parts[2] == "blob":
            owner, repo, _, branch = parts[:4]
            file_path = "/".join(parts[4:])
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"

    # Some callers append ?raw=true. It is unnecessary for raw URLs.
    if host == "raw.githubusercontent.com" and parsed.query:
        return urllib.parse.urlunparse(parsed._replace(query=""))

    return url

def get_yml(url, retries=5, initial_backoff=1.0):
    """
    Download a remote YML file to a temporary location.
    Retries with exponential backoff on transient HTTP failures (including 429).
    """
    url = _normalize_github_url(url)
    headers = {
        "User-Agent": "PINGInstaller/1.0 (+https://github.com/CameronBodine/PINGInstaller)",
        "Accept": "text/plain, text/yaml, text/x-yaml, */*",
    }

    last_error = None
    backoff = float(initial_backoff)

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as f:
                yml_data = f.read().decode("utf-8")

            # Make a temporary file
            temp_file = os.path.join(home_path, "pinginstaller_conda_file.yml")

            # Remove file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)

            # Write yml data to temporary file
            with open(temp_file, "w", encoding="utf-8") as t:
                t.write(yml_data)

            return temp_file

        except urllib.error.HTTPError as e:
            last_error = e
            # Retry only transient failures
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                retry_after = e.headers.get("Retry-After") if e.headers else None
                wait_s = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                print(f"HTTP {e.code} while downloading YML; retrying in {wait_s:.1f}s (attempt {attempt}/{retries})")
                time.sleep(wait_s)
                backoff = min(backoff * 2.0, 30.0)
                continue
            raise
        except urllib.error.URLError as e:
            last_error = e
            if attempt < retries:
                print(f"Network error while downloading YML; retrying in {backoff:.1f}s (attempt {attempt}/{retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)
                continue
            raise

    # Defensive fallback; loop normally returns or raises.
    if last_error is not None:
        raise last_error

    raise RuntimeError("Failed to download YML for an unknown reason")