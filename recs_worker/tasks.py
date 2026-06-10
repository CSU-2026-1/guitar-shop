import logging
import random
from .app import app
from .db import SessionLocal
from .recommender import RecommendationEngine
from orders_service.infra.database.models import OrderORM, OrderItemORM, GuitarType, PickupConfig
from orders_service.app.schemas.orders_schemas import OrderStatus
from sqlalchemy import text

logger = logging.getLogger(__name__)

@app.task(name="recs_worker.tasks.generate_dummy_data")
def generate_dummy_data(count=100):
    db = SessionLocal()
    try:
        # 1. Извлекаем реальные гитары, созданные сидером в таблице products
        # Используем сырой SQL, чтобы не плодить зависимости моделей между сервисами
        result = db.execute(text("SELECT id, title, sku, brand, type, pickup_config FROM products"))
        db_products = result.all()
        
        if not db_products:
            logger.error("Таблица продуктов пуста! Сначала запустите сидер в products_service.")
            return

        usernames = ["alexey", "ivan", "maria", "john", "doe"]
        logger.info(f"Найдено {len(db_products)} реальных товаров. Начинаем генерацию {count} заказов...")
        
        for _ in range(count):
            order = OrderORM(
                username=random.choice(usernames),
                status=OrderStatus.CREATED
            )
            db.add(order)
            db.flush()
            
            num_items = random.randint(1, 3)
            selected_products = random.sample(db_products, num_items)
            
            for p in selected_products:
                item = OrderItemORM(
                    order_id=order.id,
                    product_id=p.id, # Используем реальный ID
                    title=p.title,
                    sku=p.sku,
                    brand=p.brand,
                    quantity=random.randint(1, 2),
                    price=random.uniform(500, 2000),
                    type=p.type,
                    body_wood="Alder",
                    neck_wood="Maple",
                    fretboard_wood="Rosewood",
                    fret_count=22,
                    scale_length=25.5,
                    pickup_config=p.pickup_config
                )
                db.add(item)
        
        db.commit()
        logger.info(f"Успешно сгенерировано {count} заказов на основе РЕАЛЬНЫХ товаров!")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка генерации данных: {e}")
    finally:
        db.close()

@app.task(name="recs_worker.tasks.calculate_recommendations")
def calculate_recommendations():
    logger.info("Recommendation calculation started")
    try:
        engine = RecommendationEngine()
        engine.run_update()
        logger.info("Recommendation calculation finished successfully")
        return True
    except Exception as e:
        logger.error(f"Error in recommendation calculation: {e}")
        return False
