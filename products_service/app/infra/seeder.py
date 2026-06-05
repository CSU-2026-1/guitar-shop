import logging
from sqlalchemy import select, func
from app.infra.db import AsyncSessionLocal
from app.infra.model import Product, GuitarType, PickupConfig

logger = logging.getLogger(__name__)

async def seed_guitars():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(Product.id)))
        count = result.scalar()
        
        if count > 0:
            logger.info(f"База данных уже заполнена. Количество товаров: {count}")
            return

        logger.info("База пуста! Начинаем автоматическое заполнение (20 гитар)...")
        
        guitars_data = [
            {"title": "Fender Player Stratocaster", "brand": "Fender", "sku": "FEN-STR-01", "price": 85000.0, "type": GuitarType.ELECTRIC, "body_wood": "Ольха", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 22, "scale_length": 25.5, "pickup_config": PickupConfig.SSS, "image_url": "/images/strat.jpg"},
            {"title": "Gibson Les Paul Standard", "brand": "Gibson", "sku": "GIB-LP-02", "price": 240000.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Красное дерево", "fretboard_wood": "Палисандр", "fret_count": 22, "scale_length": 24.75, "pickup_config": PickupConfig.HH, "image_url": "/images/lespaul.jpg"},
            {"title": "Ibanez RG550", "brand": "Ibanez", "sku": "IBZ-RG-03", "price": 110000.0, "type": GuitarType.ELECTRIC, "body_wood": "Липа", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 24, "scale_length": 25.5, "pickup_config": PickupConfig.HSH, "image_url": "/images/ibanez_rg.jpg"},
            {"title": "Yamaha Pacifica 112V", "brand": "Yamaha", "sku": "YAM-PAC-04", "price": 35000.0, "type": GuitarType.ELECTRIC, "body_wood": "Ольха", "neck_wood": "Клен", "fretboard_wood": "Палисандр", "fret_count": 22, "scale_length": 25.5, "pickup_config": PickupConfig.HSS, "image_url": "/images/yamaha_pac.jpg"},
            {"title": "ESP LTD EC-1000", "brand": "ESP", "sku": "ESP-EC-05", "price": 130000.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Красное дерево", "fretboard_wood": "Эбеновое дерево", "fret_count": 24, "scale_length": 24.75, "pickup_config": PickupConfig.HH, "image_url": "/images/esp_ec.jpg"},
            {"title": "Martin D-28", "brand": "Martin", "sku": "MAR-D28-06", "price": 300000.0, "type": GuitarType.ACOUSTIC, "body_wood": "Палисандр", "neck_wood": "Красное дерево", "fretboard_wood": "Эбеновое дерево", "fret_count": 20, "scale_length": 25.4, "pickup_config": PickupConfig.NONE, "image_url": "/images/martin.jpg"},
            {"title": "Taylor 214ce", "brand": "Taylor", "sku": "TAY-214-07", "price": 120000.0, "type": GuitarType.ACOUSTIC, "body_wood": "Коа", "neck_wood": "Сапеле", "fretboard_wood": "Эбеновое дерево", "fret_count": 20, "scale_length": 25.5, "pickup_config": PickupConfig.PIEZO, "image_url": "/images/taylor.jpg"},
            {"title": "Fender Player Precision Bass", "brand": "Fender", "sku": "FEN-PB-08", "price": 85000.0, "type": GuitarType.BASS, "body_wood": "Ольха", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 20, "scale_length": 34.0, "pickup_config": PickupConfig.SS, "image_url": "/images/pbass.jpg"},
            {"title": "Epiphone SG Standard", "brand": "Epiphone", "sku": "EPI-SG-09", "price": 55000.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Красное дерево", "fretboard_wood": "Лаурель", "fret_count": 22, "scale_length": 24.75, "pickup_config": PickupConfig.HH, "image_url": "/images/sg.jpg"},
            {"title": "Jackson Soloist SL2", "brand": "Jackson", "sku": "JAC-SL2-10", "price": 145000.0, "type": GuitarType.ELECTRIC, "body_wood": "Ольха", "neck_wood": "Клен", "fretboard_wood": "Эбеновое дерево", "fret_count": 24, "scale_length": 25.5, "pickup_config": PickupConfig.HH, "image_url": "/images/jackson.jpg"},
            {"title": "Squier Affinity Telecaster", "brand": "Squier", "sku": "SQU-TEL-11", "price": 32000.0, "type": GuitarType.ELECTRIC, "body_wood": "Тополь", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 21, "scale_length": 25.5, "pickup_config": PickupConfig.SS, "image_url": "/images/tele.jpg"},
            {"title": "Schecter Hellraiser C-1", "brand": "Schecter", "sku": "SCH-HC1-12", "price": 115000.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Красное дерево", "fretboard_wood": "Палисандр", "fret_count": 24, "scale_length": 25.5, "pickup_config": PickupConfig.HH, "image_url": "/images/schecter.jpg"},
            {"title": "Yamaha F310", "brand": "Yamaha", "sku": "YAM-F310-13", "price": 18000.0, "type": GuitarType.ACOUSTIC, "body_wood": "Ель", "neck_wood": "Нато", "fretboard_wood": "Палисандр", "fret_count": 20, "scale_length": 25.0, "pickup_config": PickupConfig.NONE, "image_url": "/images/yamaha_f310.jpg"},
            {"title": "PRS SE Custom 24", "brand": "PRS", "sku": "PRS-SE-14", "price": 95000.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Клен", "fretboard_wood": "Палисандр", "fret_count": 24, "scale_length": 25.0, "pickup_config": PickupConfig.HH, "image_url": "/images/prs.jpg"},
            {"title": "Music Man StingRay Ray4", "brand": "Sterling", "sku": "MM-RAY4-15", "price": 45000.0, "type": GuitarType.BASS, "body_wood": "Липа", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 21, "scale_length": 34.0, "pickup_config": PickupConfig.HH, "image_url": "/images/stingray.jpg"},
            {"title": "Cort KX307 Black", "brand": "Cort", "sku": "CRT-KX307-16", "price": 38500.0, "type": GuitarType.ELECTRIC, "body_wood": "Красное дерево", "neck_wood": "Клен", "fretboard_wood": "Амарант", "fret_count": 24, "scale_length": 25.5, "pickup_config": PickupConfig.HH, "image_url": "/images/cort.jpg"},
            {"title": "Fender American Pro II Strat", "brand": "Fender", "sku": "FEN-AM-17", "price": 190000.0, "type": GuitarType.ELECTRIC, "body_wood": "Ольха", "neck_wood": "Клен", "fretboard_wood": "Клен", "fret_count": 22, "scale_length": 25.5, "pickup_config": PickupConfig.SSS, "image_url": "/images/fender_am.jpg"},
            {"title": "Schecter Omen-8", "brand": "Schecter", "sku": "SCH-OM8-18", "price": 65000.0, "type": GuitarType.ELECTRIC, "body_wood": "Липа", "neck_wood": "Клен", "fretboard_wood": "Палисандр", "fret_count": 24, "scale_length": 26.5, "pickup_config": PickupConfig.HH, "image_url": "/images/omen8.jpg"},
            {"title": "Washburn HB15", "brand": "Washburn", "sku": "WSH-HB15-19", "price": 42000.0, "type": GuitarType.ELECTRIC, "body_wood": "Клен", "neck_wood": "Красное дерево", "fretboard_wood": "Палисандр", "fret_count": 20, "scale_length": 24.75, "pickup_config": PickupConfig.P90, "image_url": "/images/washburn.jpg"},
            {"title": "Cordoba C5", "brand": "Cordoba", "sku": "CRD-C5-20", "price": 36000.0, "type": GuitarType.CLASSICAL, "body_wood": "Кедр", "neck_wood": "Красное дерево", "fretboard_wood": "Палисандр", "fret_count": 19, "scale_length": 25.6, "pickup_config": PickupConfig.NONE, "image_url": "/images/cordoba.jpg"}
        ]

        for data in guitars_data:
            product = Product(**data)
            session.add(product)
        
        await session.commit()
        logger.info("База успешно заполнена тестовыми гитарами!")