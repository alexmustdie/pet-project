from uuid import uuid4
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Generator

from contextlib import asynccontextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = 'postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    '''Базовый класс для всех моделей таблиц БД'''
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    '''Модель для таблицы задачи в Базе Данных'''
    __tablename__ = 'tasks'
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False) # по умолчанию False

class CategoryORM(Base):
    '''Модель для таблицы категории в Базе Данных'''
    __tablename__ = 'categories'
    name: Mapped[str]

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db() -> Generator[Session, None, None]:
    '''Функция для создания сессий с БД'''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
    ],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)

class Task(BaseModel):
    '''Модель задачи'''
    id: str
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None

def task_to_model(task: TaskORM) -> Task:
    '''Конвертация объекта ORM в Pydantic'''
    return Task(id=task.id, title=task.title, completed=task.completed)

@app.post('/tasks', response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    '''Создать новую задачу'''
    task = TaskORM(title=payload.title, completed=False)
    db.add(task)
    db.commit()
    return task_to_model(task)

@app.get('/tasks', response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)) -> list[Task]:
    '''Получить список задач'''
    tasks = db.scalars(select(TaskORM)).all()
    return [task_to_model(task) for task in tasks]

@app.patch('/tasks/{task_id}', response_model=Task)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    '''
    Обновить существующую задачу
    task_id получаем из url
    payload получаем из тела запроса
    '''
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    task.title = payload.title if payload.title is not None else task.title
    task.completed = payload.completed if payload.completed is not None else task.completed
    db.commit()
    return task_to_model(task)

@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)) -> None:
    '''Удалить задачу'''
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    db.delete(task)
    db.commit()

class Category(BaseModel):
    '''Модель задачи'''
    id: str
    name: str

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str | None = None

def category_to_model(category: CategoryORM) -> Category:
    '''Конвертация объекта ORM в Pydantic'''
    return Category(id=category.id, name=category.name)

@app.post('/category', response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    '''Создать новую категорию'''
    category = CategoryORM(name=payload.name)
    db.add(category)
    db.commit()
    return category_to_model(category)

@app.get('/categories', response_model=list[Category])
def get_categories(db: Session = Depends(get_db)) -> list[Category]:
    '''Получить список категорий'''
    categories = db.scalars(select(CategoryORM)).all()
    return [category_to_model(category) for category in categories]

@app.patch('/categories/{category_id}', response_model=Category)
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)) -> Category:
    '''
    Обновить существующую категорию
    category_id получаем из url
    payload получаем из тела запроса
    '''
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Категория не найдена')
    category.name = payload.name if payload.name is not None else category.name
    db.commit()
    return category_to_model(category)

@app.delete('/category/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category_id(category_id: str, db: Session = Depends(get_db)) -> None:
    '''Удалить категорию'''
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Категория не найдена')
    db.delete(category)
    db.commit()

class Book(BaseModel):
    '''Модель книги'''
    title: str

class BookSet(BaseModel):
    title: str

class BookResponse(BaseModel):
    message: str

book: Optional[Book] = None

@app.post('/book', response_model=Book, status_code=status.HTTP_201_CREATED)
def set_book(payload: BookSet):
    '''Запомнить любимую книгу'''
    global book
    book = Book(title=payload.title)
    return book

@app.get('/book', response_model=str)  # Возвращаем строку
def get_book():
    if book is None:
        return 'Любимая книга: не выбрана'
    return f'Любимая книга: {book.title}'
