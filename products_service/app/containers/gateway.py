from dependency_injector import containers, providers
from app.infra.db import AsyncSessionLocal
from app.infra.redis import get_redis_client, get_recs_redis_client
from app.repositories.product_repo import ProductRepository
from app.use_cases.product import (
    GetProductUseCase, UpdateProductUseCase, DeleteProductUseCase,
    GetRecommendationsUseCase, TriggerRecommendationUpdateUseCase
)
from app.use_cases.ai_assistant import AiAssistantUseCase


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.product_router"])
    
    redis_client = providers.Singleton(get_redis_client)
    recs_redis = providers.Singleton(get_recs_redis_client)
    db_session_factory = providers.Object(AsyncSessionLocal)
    
    product_repo = providers.Factory(
        ProductRepository,
        session_factory=db_session_factory
    )
    
    get_product_use_case = providers.Factory(
        GetProductUseCase,
        product_repo=product_repo,
        redis_client=redis_client
    )
    
    get_recs_use_case = providers.Factory(
        GetRecommendationsUseCase,
        product_repo=product_repo,
        redis_recs=recs_redis
    )
    
    trigger_recs_use_case = providers.Factory(
        TriggerRecommendationUpdateUseCase
    )
    
    update_product_use_case = providers.Factory(
        UpdateProductUseCase, product_repo=product_repo, redis_client=redis_client
    )
    
    delete_product_use_case = providers.Factory(
        DeleteProductUseCase, product_repo=product_repo, redis_client=redis_client
    )
    
    # ✅ Обновлённый AI Assistant — теперь с Redis
    ai_assistant_use_case = providers.Factory(
        AiAssistantUseCase,
        product_repo=product_repo,
        redis_client=redis_client
    )