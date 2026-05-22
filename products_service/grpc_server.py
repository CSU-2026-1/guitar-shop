import grpc
from sqlalchemy import select
from app.infra.db import AsyncSessionLocal
from app.infra.model import Product
from protobufs import product_pb2, product_pb2_grpc

class ProductServiceServicer(product_pb2_grpc.ProductServiceServicer):
    async def GetProduct(self, request, context):
        async with AsyncSessionLocal() as session:
            query = select(Product).where(Product.id == request.product_id)
            result = await session.execute(query)
            product = result.scalars().first()

            if not product:
                return product_pb2.GetProductResponse(exists=False)

            return product_pb2.GetProductResponse(
                exists=True,
                id=product.id,
                sku=product.sku,
                title=product.title,
                brand=product.brand,
                price=product.price,
                type=product.type.value,
                body_wood=product.body_wood,
                neck_wood=product.neck_wood,
                fretboard_wood=product.fretboard_wood,
                fret_count=product.fret_count,
                scale_length=product.scale_length,
                pickup_config=product.pickup_config.value,
                image_url=product.image_url or ""
            )

async def start_grpc_server():
    server = grpc.aio.server()
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("gRPC server successfully started on port 50051", flush=True)
    await server.wait_for_termination()