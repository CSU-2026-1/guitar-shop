import json
import hashlib
from typing import Optional, List
from openai import AsyncOpenAI
from redis.asyncio import Redis
from app.repositories.product_repo import ProductRepository
from app.schemas.product_DTOs import ChatResponse, ChatRequest
from config import settings
import logging

logger = logging.getLogger(__name__)


class AiAssistantUseCase:
    def __init__(self, product_repo: ProductRepository, redis_client: Redis):
        self.product_repo = product_repo
        self.redis = redis_client
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Префикс для prompt caching (минимум 1024 токена для кэширования в Groq)
        self._catalog_cache_key = "ai:catalog_prompt"
        self._catalog_cache_ttl = 3600  # 1 час

    async def _get_catalog_prompt(self) -> str:
        """Получаем кэшированный промпт с каталогом товаров"""
        cached = await self.redis.get(self._catalog_cache_key)
        if cached:
            return cached

        products = await self.product_repo.get_all(limit=100)
        
        catalog_lines = []
        for p in products:
            catalog_lines.append(
                f"ID:{p.id} | {p.brand} {p.title} | Тип:{p.type.value} | "
                f"Цена:{int(p.price)}₽ | Корпус:{p.body_wood} | Датчики:{p.pickup_config.value}"
            )
        
        catalog_text = "\n".join(catalog_lines)
        
        # Формируем базовый system prompt
        system_prompt = f"""<cache>
Ты профессиональный AI-консультант в магазине гитар "Guitar Shop".
Твоя задача — помогать клиентам выбирать гитары, учитывая их опыт, бюджет и музыкальные предпочтения.

ПРАВИЛА ОТВЕТА:
1. Рекомендуй ТОЛЬКО товары из каталога ниже. Если подходящего нет — честно скажи.
2. Всегда указывай: ID товара, название, цену и краткое объяснение почему подходит.
3. Если клиент не указал бюджет — спроси. Типичные диапазоны: до 30к (новичок), 30-80к (любитель), 80-150к (профи), 150к+ (коллекционные).
4. Учитывай музыкальный стиль: рок/метал → электрогитары с HH/HSH, блюз/джаз → полуакустики с P90/SS, кантри → телекастеры, фингерстайл → акустики.
5. Дерево корпуса влияет на звук: ольха/липа — универсально, красное дерево — тёплый звук, клён — яркий.
6. Отвечай кратко (2-4 предложения), дружелюбно, используй эмодзи 🎸.
7. Если спрашивают про сравнение — сравни конкретные модели из каталога.
8. Не придумывай товары, которых нет в списке!

АССОРТИМЕНТ МАГАЗИНА (всегда актуальный):
{catalog_text}
</cache>"""
        
        # Кэшируем в Redis
        await self.redis.set(self._catalog_cache_key, system_prompt, ex=self._catalog_cache_ttl)
        return system_prompt

    async def _get_history(self, session_id: str, limit: int = 20) -> List[dict]:
        """Получить историю диалога из Redis"""
        key = f"ai:history:{session_id}"
        history_data = await self.redis.lrange(key, -limit, -1)
        return [json.loads(msg) for msg in history_data]

    async def _save_message(self, session_id: str, role: str, content: str, max_history: int = 40):
        """Сохранить сообщение в историю"""
        key = f"ai:history:{session_id}"
        message = {"role": role, "content": content}
        await self.redis.rpush(key, json.dumps(message))
        await self.redis.ltrim(key, -max_history, -1)  # Храним только последние N сообщений
        await self.redis.expire(key, 86400)  # TTL 24 часа

    def _generate_session_id(self, request: ChatRequest) -> str:
        """Генерируем session_id из запроса или используем переданный"""
        if request.session_id:
            return request.session_id
        # Fallback: хэш от user_id + timestamp
        return hashlib.md5(f"anon:{id(request)}".encode()).hexdigest()[:16]

    async def execute(self, request: ChatRequest) -> ChatResponse:
        session_id = self._generate_session_id(request)
        user_message = request.message
        
        # 1. Получаем кэшированный system prompt
        system_prompt = await self._get_catalog_prompt()
        
        # 2. Загружаем историю диалога
        history = await self._get_history(session_id)
        
        # 3. Сохраняем текущее сообщение пользователя
        await self._save_message(session_id, "user", user_message)
        
        # 4. Формируем сообщения для API
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"[AI] Session {session_id} | History: {len(history)} msgs | Query: {user_message[:50]}...")
        
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4,
                max_tokens=600,
                # Prompt caching параметры для Groq
                extra_headers={
                    "X-Cache-Control": "max-age=3600"  # Подсказка для кэширования
                }
            )
            
            reply_text = response.choices[0].message.content
            
            # Логируем usage для мониторинга
            if hasattr(response, 'usage'):
                logger.info(f"[AI] Tokens: prompt={response.usage.prompt_tokens}, "
                          f"completion={response.usage.completion_tokens}, "
                          f"cached={getattr(response.usage, 'prompt_cache_hit_tokens', 0)}")
            
            # 5. Сохраняем ответ бота в историю
            await self._save_message(session_id, "assistant", reply_text)
            
            return ChatResponse(reply=reply_text, session_id=session_id)
            
        except Exception as e:
            logger.error(f"[AI] Error: {e}")
            return ChatResponse(
                reply="Извините, сейчас испытываю технические трудности. Попробуйте задать вопрос чуть позже! 🎸",
                session_id=session_id
            )

    async def clear_history(self, session_id: str) -> bool:
        """Очистить историю диалога"""
        key = f"ai:history:{session_id}"
        deleted = await self.redis.delete(key)
        return deleted > 0