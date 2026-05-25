from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from app.containers.gateway import Container
from app.repositories.product_repo import ProductRepository
from app.schemas.product_DTOs import ProductResponse, ProductCreate, ProductUpdate
from app.use_cases.product import UpdateProductUseCase, DeleteProductUseCase, GetProductUseCase, GetRecommendationsUseCase, TriggerRecommendationUpdateUseCase
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/guitars", tags=["Guitars"])

@router.get("/{product_id}/recommendations", response_model=List[ProductResponse])
@inject
async def get_recommendations(
    product_id: int,
    use_case: GetRecommendationsUseCase = Depends(Provide[Container.get_recs_use_case])
):
    return await use_case.execute(product_id)

@router.post("/recompute-recommendations")
@inject
async def trigger_recommendations(
    use_case: TriggerRecommendationUpdateUseCase = Depends(Provide[Container.trigger_recs_use_case])
):
    return await use_case.execute()

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_guitar(
    product_in: ProductCreate,
    current_user: dict = Depends(get_current_user),
    repo: ProductRepository = Depends(Provide[Container.product_repo])
):
    return await repo.create(product_in.model_dump())

@router.get("/", response_model=List[ProductResponse])
@inject
async def get_guitars(
    skip: int = 0,
    limit: int = 50,
    repo: ProductRepository = Depends(Provide[Container.product_repo])
):
    return await repo.get_all(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
@inject
async def get_guitar(
    product_id: int,
    use_case: GetProductUseCase = Depends(Provide[Container.get_product_use_case])
):
    product_data = await use_case.execute(product_id)
    if not product_data:
        raise HTTPException(status_code=404, detail="Гитара не найдена")
    return product_data

@router.patch("/{product_id}", response_model=ProductResponse)
@inject
async def update_guitar(
    product_id: int,
    product_in: ProductUpdate,
    use_case: UpdateProductUseCase = Depends(Provide[Container.update_product_use_case])
):
    update_data = product_in.model_dump(exclude_unset=True)
    product = await use_case.execute(product_id, update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Гитара не найдена для обновления")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_guitar(
    product_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: DeleteProductUseCase = Depends(Provide[Container.delete_product_use_case])
):
    success = await use_case.execute(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Гитара не найдена для удаления")
    return None