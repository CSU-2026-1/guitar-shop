from typing import List
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from app.containers.gateway import Container
from app.core.security import require_admin
from app.repositories.product_repo import ProductRepository
from app.schemas.product_DTOs import ProductCreate
from app.schemas.product_DTOs import ProductResponse
from app.schemas.product_DTOs import ProductUpdate
from app.schemas.product_DTOs import ChatRequest, ChatResponse, ChatHistoryResponse
from app.use_cases.product import DeleteProductUseCase
from app.use_cases.product import GetProductUseCase
from app.use_cases.product import GetRecommendationsUseCase
from app.use_cases.product import TriggerRecommendationUpdateUseCase
from app.use_cases.product import UpdateProductUseCase
from app.use_cases.ai_assistant import AiAssistantUseCase
from redis.asyncio import Redis

router = APIRouter(prefix="/api/v1/guitars", tags=["Guitars"])


@router.get("/{product_id}/recommendations", response_model=List[ProductResponse])
@inject
async def get_recommendations(
    product_id: int,
    use_case: GetRecommendationsUseCase = Depends(Provide[Container.get_recs_use_case]),
):
    return await use_case.execute(product_id)


@router.post("/recompute-recommendations")
@inject
async def trigger_recommendations(
    current_user: dict = Depends(require_admin),
    use_case: TriggerRecommendationUpdateUseCase = Depends(Provide[Container.trigger_recs_use_case]),
):
    return await use_case.execute()


@router.post("/assistant", response_model=ChatResponse)
@inject
async def ask_ai_assistant(
    request: ChatRequest,
    use_case: AiAssistantUseCase = Depends(Provide[Container.ai_assistant_use_case])
):
    try:
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI: {str(e)}")


@router.get("/assistant/history/{session_id}", response_model=ChatHistoryResponse)
@inject
async def get_chat_history(
    session_id: str,
    use_case: AiAssistantUseCase = Depends(Provide[Container.ai_assistant_use_case])
):
    """Получить историю диалога по session_id"""
    try:
        history = await use_case._get_history(session_id, limit=50)
        return ChatHistoryResponse(
            session_id=session_id,
            messages=history,
            total=len(history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.delete("/assistant/history/{session_id}")
@inject
async def clear_chat_history(
    session_id: str,
    use_case: AiAssistantUseCase = Depends(Provide[Container.ai_assistant_use_case])
):
    """Очистить историю диалога"""
    try:
        success = await use_case.clear_history(session_id)
        if success:
            return {"status": "cleared", "session_id": session_id}
        raise HTTPException(status_code=404, detail="История не найдена")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/assistant/new-session")
async def create_new_session():
    """Создать новую пустую сессию (возвращает session_id)"""
    import hashlib
    import time
    session_id = hashlib.md5(f"session:{time.time_ns()}".encode()).hexdigest()[:16]
    return {"session_id": session_id, "status": "created"}


# === CRUD операции (остаются без изменений) ===

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_guitar(
    product_in: ProductCreate,
    current_user: dict = Depends(require_admin),
    repo: ProductRepository = Depends(Provide[Container.product_repo]),
):
    return await repo.create(product_in.model_dump())


@router.get("/", response_model=List[ProductResponse])
@inject
async def get_guitars(
    skip: int = 0,
    limit: int = 50,
    repo: ProductRepository = Depends(Provide[Container.product_repo]),
):
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
@inject
async def get_guitar(
    product_id: int,
    use_case: GetProductUseCase = Depends(Provide[Container.get_product_use_case]),
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
    current_user: dict = Depends(require_admin),
    use_case: UpdateProductUseCase = Depends(Provide[Container.update_product_use_case]),
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
    current_user: dict = Depends(require_admin),
    use_case: DeleteProductUseCase = Depends(Provide[Container.delete_product_use_case]),
):
    success = await use_case.execute(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Гитара не найдена для удаления")
    return None