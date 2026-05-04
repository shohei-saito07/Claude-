from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from url_shortener.db import DEFAULT_DATABASE_URL, init_db, make_engine
from url_shortener.models import Link
from url_shortener.schemas import LinkInfo, ShortenRequest, ShortenResponse
from url_shortener.shortcode import generate

MAX_CODE_GENERATION_ATTEMPTS = 5


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    engine: Engine = make_engine(database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db(engine)
        yield

    app = FastAPI(title="URL Shortener", version="0.1.0", lifespan=lifespan)

    def get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(get_session)]

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/shorten", status_code=201, response_model=ShortenResponse)
    def shorten(
        payload: ShortenRequest,
        request: Request,
        session: SessionDep,
    ) -> ShortenResponse:
        if payload.code:
            if session.exec(select(Link).where(Link.code == payload.code)).first():
                raise HTTPException(status_code=409, detail="code already taken")
            code = payload.code
        else:
            code = _generate_unique_code(session)

        link = Link(code=code, target_url=str(payload.url))
        session.add(link)
        session.commit()
        session.refresh(link)

        short_url = str(request.base_url).rstrip("/") + "/" + code
        return ShortenResponse(code=link.code, short_url=short_url, target_url=link.target_url)

    @app.get("/api/links", response_model=list[LinkInfo])
    def list_links(session: SessionDep) -> list[Link]:
        return list(session.exec(select(Link).order_by(Link.id)).all())

    @app.get("/api/links/{code}", response_model=LinkInfo)
    def get_link(code: str, session: SessionDep) -> Link:
        link = session.exec(select(Link).where(Link.code == code)).first()
        if not link:
            raise HTTPException(status_code=404, detail="not found")
        return link

    @app.get("/{code}")
    def redirect(code: str, session: SessionDep) -> RedirectResponse:
        link = session.exec(select(Link).where(Link.code == code)).first()
        if not link:
            raise HTTPException(status_code=404, detail="not found")
        link.clicks += 1
        session.add(link)
        session.commit()
        return RedirectResponse(url=link.target_url, status_code=307)

    return app


def _generate_unique_code(session: Session) -> str:
    for _ in range(MAX_CODE_GENERATION_ATTEMPTS):
        code = generate()
        if not session.exec(select(Link).where(Link.code == code)).first():
            return code
    raise HTTPException(status_code=500, detail="could not generate unique code")


app = create_app()


def cli() -> None:
    import uvicorn

    uvicorn.run("url_shortener.main:app", host="0.0.0.0", port=8000, reload=False)
