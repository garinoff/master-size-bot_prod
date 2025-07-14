from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from sqlalchemy import select

from database.models import User, UserPhoto
from database.database import get_session
from services.image_service import process_user_photo
from services.token_service import add_tokens_to_user
from utils.keyboards import get_main_menu_keyboard, get_gender_keyboard
from utils.validators import validate_height, validate_weight
from config import config

router = Router()

class OnboardingStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_chest = State()
    waiting_for_waist = State()
    waiting_for_hips = State()
    waiting_for_foot_size = State()
    waiting_for_head_circumference = State()
    waiting_for_bra_size = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start - начало онбординга"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                onboarding_step="photo"
            )
            session.add(user)
            await session.commit()
        
        if user.is_completed:
            # Пользователь уже прошел онбординг
            await message.answer(
                f"🎉 Добро пожаловать обратно, {user.first_name}!\n\n"
                f"💎 Ваш баланс: {user.msz_balance} MSZ\n\n"
                f"Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            return
    
    # Приветственное сообщение
    welcome_text = """
🎯 **Добро пожаловать в Мастер-размер!**

Я помогу вам:
✨ Создать персональный 3D-аватар
🎯 Точно подобрать размер одежды  
💎 Заработать токены MSZ
🚀 Стать соратником революции в fashion e-commerce

**Шаг 1/8: Загрузите фото**

📸 Пожалуйста, отправьте фотографию в облегающей одежде (спереди):

⚠️ **Важно:**
• Хорошее освещение
• Ровная поза
• Видно всю фигуру
• Облегающая одежда

*Ваши данные защищены и используются только для создания 3D-аватара*
    """
    
    await message.answer(welcome_text)
    await state.set_state(OnboardingStates.waiting_for_photo)

@router.message(OnboardingStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработка загруженного фото"""
    user_id = message.from_user.id
    
    # Получаем наибольшее разрешение фото
    photo = message.photo[-1]
    
    # Обработка изображения
    try:
        validation_result = await process_user_photo(photo, user_id)
        
        if not validation_result["is_valid"]:
            await message.answer(
                f"❌ **Фото не прошло валидацию**\n\n"
                f"Причина: {validation_result['reason']}\n\n"
                f"🔄 Пожалуйста, загрузите другое фото следуя рекомендациям."
            )
            return
            
    except Exception as e:
        await message.answer(
            "⚠️ Произошла ошибка при обработке фото. "
            "Пожалуйста, попробуйте еще раз."
        )
        return
    
    # Сохраняем фото в базу
    async with get_session() as session:
        user_photo = UserPhoto(
            user_id=user_id,
            file_id=photo.file_id,
            photo_type="front",
            is_validated=True,
            validation_score=validation_result["score"]
        )
        session.add(user_photo)
        await session.commit()
    
    await message.answer(
        "✅ **Отлично! Фото принято.**\n\n"
        "📊 **Шаг 2/8: Укажите пол**",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(OnboardingStates.waiting_for_gender)

@router.callback_query(OnboardingStates.waiting_for_gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = callback.data.split("_")[1]  # gender_male/gender_female
    user_id = callback.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.gender = gender
            user.onboarding_step = "age"
            await session.commit()
    
    await callback.message.edit_text(
        f"✅ Пол: {'Мужской' if gender == 'male' else 'Женский'}\n\n"
        f"📊 **Шаг 3/8: Возраст**\n\n"
        f"Укажите ваш возраст (число от 16 до 80):"
    )
    await state.set_state(OnboardingStates.waiting_for_age)
    await callback.answer()

@router.message(OnboardingStates.waiting_for_age, F.text)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    try:
        age = int(message.text)
        if not (16 <= age <= 80):
            raise ValueError()
    except ValueError:
        await message.answer("❌ Укажите корректный возраст (число от 16 до 80)")
        return
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.age = age
            user.onboarding_step = "height"
            await session.commit()
    
    await message.answer(
        f"✅ Возраст: {age} лет\n\n"
        f"📊 **Шаг 4/8: Рост**\n\n"
        f"Укажите ваш рост в сантиметрах (например: 175):"
    )
    await state.set_state(OnboardingStates.waiting_for_height)

@router.message(OnboardingStates.waiting_for_height, F.text)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    height = validate_height(message.text)
    if not height:
        await message.answer("❌ Укажите корректный рост в см (от 140 до 220)")
        return
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.height = height
            user.onboarding_step = "weight"
            await session.commit()
    
    await message.answer(
        f"✅ Рост: {height} см\n\n"
        f"📊 **Шаг 5/8: Вес**\n\n"
        f"Укажите ваш вес в килограммах (например: 70):"
    )
    await state.set_state(OnboardingStates.waiting_for_weight)

@router.message(OnboardingStates.waiting_for_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    weight = validate_weight(message.text)
    if not weight:
        await message.answer("❌ Укажите корректный вес в кг (от 40 до 200)")
        return
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.weight = weight
            user.onboarding_step = "chest"
            await session.commit()
    
    await message.answer(
        f"✅ Вес: {weight} кг\n\n"
        f"📊 **Шаг 6/8: Обхват груди**\n\n"
        f"Укажите обхват груди в сантиметрах (например: 90):"
    )
    await state.set_state(OnboardingStates.waiting_for_chest)

# Аналогично реализуются остальные шаги...

@router.message(OnboardingStates.waiting_for_chest, F.text)
async def complete_onboarding(message: Message, state: FSMContext):
    """Завершение онбординга и выдача базовой награды"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_completed = True
            user.onboarding_step = "completed"
            await session.commit()
    
    # Выдаем базовую награду
    base_reward = config.BASE_REWARD_MSZ
    await add_tokens_to_user(user_id, base_reward, "Завершение онбординга")
    
    completion_text = f"""
🎉 **Поздравляем! Онбординг завершен!**

✅ Ваш 3D-аватар создан
💎 Получено {base_reward} MSZ токенов

🚀 **Что дальше?**
• Выполняйте задания и зарабатывайте MSZ
• Приглашайте друзей (реферальная программа)  
• Получайте рекомендации по размерам
• Подключите TON Wallet

📈 **Ваша статистика:**
💰 Баланс: {base_reward} MSZ
🎯 Уровень: Новичок
⭐ Статус: Активен
    """
    
    await message.answer(
        completion_text,
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
