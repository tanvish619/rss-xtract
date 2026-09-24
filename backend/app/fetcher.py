import httpx

def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 RSS-Xtract/1.0"
    }

    response = httpx.get(
        url,
        headers=headers,
        timeout=20,
        follow_redirects=True,
        verify=False,
    )

    response.raise_for_status()
    return response.text