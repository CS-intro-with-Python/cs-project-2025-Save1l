import sys
from urllib.parse import urljoin

import requests

BASE_URL = "http://127.0.0.1:5000"

ROUTES = [
    "/",
    "/home",
    "/pricing"
]


def check_route(path: str):
    url = urljoin(BASE_URL.rstrip("/") + "/", path.lstrip("/"))
    print(f"➡️  Checking {url}")

    response = requests.get(url)
    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        raise AssertionError(f"Expected status 200 for {path}, got {response.status_code}")


def main():
    try:
        for route in ROUTES:
            check_route(route)
    except (requests.RequestException, AssertionError) as exc:
        print(f"'\033[91m' Test failed: {exc}")
        sys.exit(1)

    print("'\033[92m' All routes responded successfully")


if __name__ == "__main__":
    main()
