import uvicorn
from fastapi import FastAPI, Depends, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from typing import Annotated

app = FastAPI()

engine = create_async_engine('sqlite+aiosqlite:///products.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

class ProductModel(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    image1: Mapped[str]
    image2: Mapped[str]
    image3: Mapped[str]

@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image1: str
    image2: str
    image3: str

@app.get("/products")
async def get_products(session: SessionDep) -> list[ProductSchema]:
    query = select(ProductModel)
    result = await session.execute(query)
    return result.scalars().all()

@app.post("/add-product")
async def add_product(name: str, description: str, price: float, img1: UploadFile, img2: UploadFile, img3: UploadFile, session: SessionDep):
    new_product = ProductModel(name=name, description=description, price=price, image1=img1.filename, image2=img2.filename, image3=img3.filename)
    session.add(new_product)
    await session.commit()
    return {"ok": True}



if __name__ == "__main__":
    uvicorn.run("main:app")