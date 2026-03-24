from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class CategoryORM(Base):
    '''Модель для таблицы категории в Базе Данных'''
    __tablename__ = 'categories'
    name: Mapped[str]
