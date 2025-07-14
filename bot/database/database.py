from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
import logging

from config import config
from .models import Base

logger = logging.getLogger(__name__)

# Создание асинхронного движка базы данных
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создание фабрики сессий
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    """Контекстный менеджер для работы с сессией базы данных"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """Инициализация базы данных"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Создание базовых задач
        await create_default_tasks()
        
        logger.info("✅ База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

async def create_default_tasks():
    """Создание базовых заданий"""
    from .models import Task
    
    default_tasks = [
        {
            "name": "Завершение онбординга",
            "description": "Пройдите полный процесс регистрации и создания профиля",
            "reward_msz": 300,
            "task_type": "onboarding",
            "is_active": True
        },
        {
            "name": "Подключение TON Wallet",
            "description": "Подключите ваш TON кошелек для управления токенами",
            "reward_msz": 200,
            "task_type": "wallet",
            "is_active": True
        },
        {
            "name": "Первый реферал",
            "description": "Пригласите друга и получите бонус",
            "reward_msz": 250,
            "task_type": "referral",
            "is_active": True
        },
        {
            "name": "Социальная активность",
            "description": "Поделитесь ботом в социальных сетях",
            "reward_msz": 150,
            "task_type": "social",
            "is_active": True
        }
    ]
    
    async with get_session() as session:
        for task_data in default_tasks:
            result = await session.execute(
                select(Task).where(Task.name == task_data["name"])
            )
            existing_task = result.scalar_one_or_none()
            
            if not existing_task:
                task = Task(**task_data)
                session.add(task)
        
        await session.commit()
