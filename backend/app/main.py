from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import WebsiteRequest
from app.fetcher import fetch_page
from app.parser import parse_html, detect_article_candidates

from app.routes.configurations import (
    router as configuration_router
)
from app.routes.sources import (
    router as source_router
)
from app.routes.feeds import (
    router as feed_router
)
from app.routes.versions import (
    router as version_router
)
from app.routes.feed_runtime import (
    router as feed_runtime_router
)


app = FastAPI(
    title="RSS Xtract",
    description="Web to RSS Feed Builder API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    configuration_router
)

app.include_router(
    source_router
)

app.include_router(
    feed_router
)

app.include_router(
    version_router
)

app.include_router(
    feed_runtime_router
)


@app.get("/")
def root():
    return {
        "message": "RSS Xtract backend is running"
    }


@app.post("/preview")
def preview_website(
    request: WebsiteRequest
):

    try:

        html = fetch_page(
            str(request.url)
        )

        parsed = parse_html(html)

        candidates = (
            detect_article_candidates(
                html
            )
        )

        return {
            "message": (
                "Website fetched successfully"
            ),
            "url": str(request.url),
            "html_length": len(html),
            "page_title": parsed["title"],
            "html": html,
            "article_candidates": candidates
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
