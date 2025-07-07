from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.routers.auth import get_current_user
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateProduct

from slugify import slugify

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where((Product.is_active == True) & (Product.stock > 0)))
    return products.all()


@router.post('/create')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(name=create_product.name,
                                          image_url=create_product.image_url,
                                          description=create_product.description,
                                          supplier_id=get_user.get('id'),
                                          price=create_product.price,
                                          stock=create_product.stock,
                                          category_id=create_product.category,
                                          rating=0.0,
                                          slug=slugify(create_product.name,)))
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


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id)).all()
    categories_and_subcategories = [category.id] + [i.id for i in subcategories]
    products_category = await db.scalars(
        select(Product).where(Product.category_id.in_(categories_and_subcategories),
                              Product.is_active == True,
                              Product.stock > 0))
    return products_category.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where((Product.is_active == True)
                                                & (Product.stock > 0)
                                                & (Product.slug == product_slug) ))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return product


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, update_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No product found'
        )

    is_admin = get_user.get('is_admin')
    is_owner_supplier = get_user.get('is_supplier') and get_user.get('id') == product.supplier_id

    if not (is_admin or is_owner_supplier):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

    await db.execute(update(Product).where(Product.slug == product_slug).values(
                                      name=update_product.name,
                                      image_url=update_product.image_url,
                                      description=update_product.description,
                                      price=update_product.price,
                                      stock=update_product.stock,
                                      category_id=update_product.category,
                                      slug=slugify(update_product.name)
                                      ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }



@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No product found'
        )
    is_admin = get_user.get('is_admin')
    is_owner_supplier = get_user.get('is_supplier') and get_user.get('id') == product.supplier_id

    if not (is_admin or is_owner_supplier):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

    await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
