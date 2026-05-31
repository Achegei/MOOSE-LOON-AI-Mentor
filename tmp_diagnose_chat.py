"""Local health diagnostic without hardcoded learner credentials."""

import urllib.error
import urllib.request


API_URL = "http://127.0.0.1:8000"


def main() -> None:
    """Check whether the local FastAPI backend responds."""
    try:
        response = urllib.request.urlopen(f"{API_URL}/health", timeout=5)
        print(response.status, response.read().decode())
    except urllib.error.URLError as exc:
        print("health error", repr(exc))


if __name__ == "__main__":
    main()
