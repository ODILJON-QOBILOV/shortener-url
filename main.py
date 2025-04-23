from fastapi import FastAPI, Depends, HTTPException
import random, string
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.database import get_db
from app.models import URL
from app.schemas import URLCreate

app = FastAPI()

def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/make/url/short", status_code=status.HTTP_201_CREATED, tags=["shorting-url"])
async def shorting_url(request: URLCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(URL).filter_by(original_url=str(request.url)))
    existing_url = res.scalar_one_or_none()
    if existing_url:
        return {
            "shorted_url": f"http://127.0.0.1:8080/{existing_url.short_id}",
            "original_url": existing_url.original_url
        }

    url_short_id = generate_short_id()

    while True:
        res = await db.execute(select(URL).filter_by(short_id=url_short_id))
        if not res.scalar_one_or_none():
            break
        url_short_id = generate_short_id()

    url = URL(short_id=url_short_id, original_url=str(request.url))
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return {
        "shorted_url": f"http://127.0.0.1:8080/{url_short_id}",
        "original_url": url.original_url
    }

@app.get("/{short_url_id}", tags=["shorting-url"])
async def redirecting(short_url_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(URL).filter_by(short_id=short_url_id))
    url = res.scalar_one_or_none()
    if url:
        return RedirectResponse(url=str(url.original_url), status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="shorted url not found")


# uvicorn main:app --reload --port 8080
# use it to run