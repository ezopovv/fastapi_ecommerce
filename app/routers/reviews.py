import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.routers.auth import get_current_user
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateReview

from slugify import slugify

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/{product_id}')
async def review_by_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    ratings = await db.scalars(select(Rating).where((Rating.is_active == True)&(Rating.product_id == product_id)))
    ratings = ratings.all()

    result = []

    for rating in ratings:
        # Получаем связанный review
        review = await db.scalar(
            select(Review).where(
                Review.rating_id == rating.id,
                Review.is_active == True
            )
        )
        result.append({
            "rating": rating,
            "review": review
        })
    return result


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    ratings = await db.scalars(select(Rating).where(Rating.is_active == True))
    ratings = ratings.all()

    result = []

    for rating in ratings:
        # Получаем связанный review
        review = await db.scalar(
            select(Review).where(
                Review.rating_id == rating.id,
                Review.is_active == True
            )
        )
        result.append({
            "rating": rating,
            "review": review
        })
    return result


@router.post('/create')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)], create_review: CreateReview,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        rating_stmt = insert(Rating).values(
            grade=create_review.grade,
            user_id=get_user.get('id'),
            product_id=create_review.product_id,
            is_active=True
        ).returning(Rating.id)  # Получим id созданной записи

        rating_result = await db.execute(rating_stmt)
        rating_id = rating_result.scalar()

        review_stmt = insert(Review).values(
            user_id=get_user.get('id'),
            product_id=create_review.product_id,
            rating_id=rating_id,
            comment=create_review.comment,
            comment_date=datetime.datetime.now().date(),
            is_active=True
        )

        await db.execute(review_stmt)
        await db.commit()

        product_ratings = await db.scalars(select(Rating).where((Rating.is_active == True)
                                          & (Rating.product_id == create_review.product_id)))

        product_ratings = product_ratings.all()
        #print(f"product_ratings_len = {len(product_ratings)}")
        sum_rating = 0
        for i in product_ratings:
            sum_rating += i.grade
        average_rating = sum_rating/len(product_ratings)
        print(average_rating)

        product = await db.scalar(select(Product).where(Product.id == create_review.product_id))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No product found'
            )
        await db.execute(update(Product).where(Product.id == create_review.product_id).values(
            rating=average_rating
        ))
        await db.commit()

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.delete('/delete')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    review = await db.scalar(select(Review).where(Review.id == review_id))
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No review found'
        )
    rating = await db.scalar(select(Rating).where(Rating.id == Review.rating_id))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No rating found'
        )

    is_admin = get_user.get('is_admin')

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

    await db.execute(update(Review).where(Review.id == review_id).values(is_active=False))
    if review.rating_id:
        await db.execute(update(Rating).where(Rating.id == review.rating_id).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Review delete is successful'
    }
