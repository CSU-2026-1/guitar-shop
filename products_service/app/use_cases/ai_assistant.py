from openai import AsyncOpenAI
from app.repositories.product_repo import ProductRepository
from app.schemas.product_DTOs import ChatResponse
from config import settings

class AiAssistantUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
        
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url="https://api.groq.com/openai/v1" 
        )

    async def execute(self, user_message: str) -> ChatResponse:
       
        products = await self.product_repo.get_all(limit=100)
        
        
        catalog_text = "НАШ АССОРТИМЕНТ:\n"
        for p in products:
            catalog_text += f"- ID {p.id}: {p.brand} {p.title}, Тип: {p.type.value}, Цена: {p.price} руб, Дерево: {p.body_wood}, Датчики: {p.pickup_config.value}\n"

        
        system_prompt = f"""Ты профессиональный консультант в музыкальном интернет-магазине. 
Твоя задача — помогать клиентам выбирать гитары. 
ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
1. Рекомендуй ТОЛЬКО те гитары, которые есть в списке 'НАШ АССОРТИМЕНТ'.
2. Если в ассортименте нет подходящего товара, честно скажи об этом.
3. Обязательно указывай название гитары и её цену, чтобы клиент мог добавить её в корзину.
4. Отвечай кратко, вежливо и по делу. Объясняй, почему эта гитара подходит под запрос.

{catalog_text}"""

        
        response = await self.client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3, 
            max_tokens=500
        )

        
        reply_text = response.choices[0].message.content
        return ChatResponse(reply=reply_text)