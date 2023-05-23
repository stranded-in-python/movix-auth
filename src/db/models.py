# from pydantic import BaseModel


# пока не знаю что будет возвращаться пользователю так что оставлю пустым
# orm_mode позволит обращаться к атрибутам, а не так: Item['id']

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True