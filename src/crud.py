from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import MovieModel


async def get_movie(db: AsyncSession, **kwargs):
    result = await db.execute(
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        ).filter_by(**kwargs)
    )

    movie = result.unique().scalar_one_or_none()
    return movie


async def get_movies_count(db: AsyncSession) -> int:
    return await db.scalar(select(func.count()).select_from(MovieModel))


async def get_movies(db: AsyncSession, page: int, per_page: int):
    movies = await db.execute(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .order_by(MovieModel.id.desc())
    )
    return movies.scalars().all()


async def get_or_create(model, db: AsyncSession, **kwargs):
    obj = await db.execute(select(model).filter_by(**kwargs))
    result = obj.scalar_one_or_none()

    if result:
        return result

    new_obj = model(**kwargs)
    db.add(new_obj)
    await db.flush()

    return new_obj


async def delete_movie(db: AsyncSession, movie_id: int):
    result = await db.execute(
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        )
        .where(MovieModel.id == movie_id)
    )
    movie = result.unique().scalar_one_or_none()
    if not movie:
        return None
    await db.delete(movie)
    await db.commit()
    return movie


async def update_movie(db: AsyncSession, movie_id: int, payload: dict):
    result = await db.execute(
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        )
        .where(MovieModel.id == movie_id)
    )
    movie = result.unique().scalar_one_or_none()
    if not movie:
        return None
    for field, value in payload.items():
        setattr(movie, field, value)
    await db.commit()
    await db.refresh(movie)
    return movie
