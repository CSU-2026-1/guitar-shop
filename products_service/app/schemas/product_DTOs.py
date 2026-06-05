from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.infra.model import GuitarType, PickupConfig


class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, examples=["Fender Stratocaster Player"])
    brand: str = Field(..., min_length=1, max_length=50, examples=["Fender"])
    sku: str = Field(..., description="Заводской артикул", examples=["FEN-PL-STRAT-OW"])
    price: float = Field(..., gt=0, description="Цена должна быть больше нуля")
    type: GuitarType = Field(..., description="Тип инструмента")
    body_wood: str = Field(..., max_length=50, examples=["Красное дерево"])
    neck_wood: str = Field(..., max_length=50, examples=["Клен"])
    fretboard_wood: str = Field(..., max_length=50, examples=["Палисандр"])
    fret_count: int = Field(..., ge=12, le=36, examples=[22])
    scale_length: float = Field(..., gt=0, examples=[25.5])
    pickup_config: PickupConfig = Field(default=PickupConfig.NONE, description="Конфигурация датчиков")
    image_url: Optional[str] = Field(None, description="Ссылка на изображение")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, gt=0)
    type: Optional[GuitarType] = None
    body_wood: Optional[str] = None
    neck_wood: Optional[str] = None
    fretboard_wood: Optional[str] = None
    fret_count: Optional[int] = Field(None, ge=12, le=36)
    scale_length: Optional[float] = Field(None, gt=0)
    pickup_config: Optional[PickupConfig] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(..., description="Сообщение от пользователя", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(
        None, 
        description="ID сессии для сохранения истории диалога. Если не указан — генерируется автоматически."
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Ответ ИИ-ассистента")
    session_id: str = Field(..., description="ID сессии — передавайте его в следующих запросах для сохранения контекста")


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    total: int