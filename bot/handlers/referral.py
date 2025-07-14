import uuid
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from datetime import datetime

from database.models import User
from database.database import get_session
from services.token_service import add_tokens_to_user, process_referral_rewards
from utils.keyboards import get_referral_keyboard
from config import config

async def show_referral_info(message: types.Message):
    """Показать информацию о реферальной программе"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if not user.referral_code:
            # Генерируем уникальный реферальный код
            user.referral_code = generate_referral_code()
            session.commit()
        
        bot_username = (await message.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
        
        # Статистика рефералов
        l1_referrals = session.query(User).filter(User.referred_by == user_id).count()
        
        # Расчет потенциального дохода
        potential_l1 = config.REFERRAL_L1_MSZ * (config.MAX_REFERRALS_PER_USER - l1_referrals)
        
        referral_text = f"""
👥 **Реферальная программа**

🎯 **Ваша реферальная ссылка:**
`{referral_link}`

📊 **Ваша статистика:**
• Приглашено друзей: {l1_referrals}/{config.MAX_REFERRALS_PER_USER}
• Заработано с рефералов: {calculate_referral_earnings(user_id)} MSZ

💰 **Система вознаграждений:**
• За каждого друга L1: {config.REFERRAL_L1_MSZ} MSZ
• За друга друга L2: {config.REFERRAL_L2_MSZ} MSZ  
• За друга друга друга L3: {config.REFERRAL_L3_MSZ} MSZ

🚀 **Потенциальный доход:**
• Можете заработать еще: {potential_l1} MSZ

⚡ **Бонусы для активных рефереров:**
• При >80% качественных рефералов: +15% к наградам
• Дополнительные бонусы за достижения

📋 **Как это работает:**
1. Поделитесь своей ссылкой
2. Друг регистрируется и проходит онбординг
3. Вы получаете награду после валидации его данных
4. Друзья ваших друзей тоже приносят доход!
        """
        
        await message.answer(
            referral_text,
            reply_markup=get_referral_keyboard(),
            parse_mode="Markdown"
        )

async def process_referral_start(message: types.Message, referral_code: str):
    """Обработка перехода по реферальной ссылке"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # Проверяем, не зарегистрирован ли уже пользователь
        existing_user = session.query(User).filter(User.telegram_id == user_id).first()
        if existing_user:
            return False  # Пользователь уже зарегистрирован
        
        # Находим реферера
        referrer = session.query(User).filter(User.referral_code == referral_code).first()
        if not referrer:
            return False  # Неверный реферальный код
        
        if referrer.telegram_id == user_id:
            return False  # Нельзя быть рефералом самого себя
        
        # Проверяем лимит рефералов
        if referrer.referral_count_l1 >= config.MAX_REFERRALS_PER_USER:
            return False  # Превышен лимит рефералов
        
        # Создаем нового пользователя с привязкой к рефереру
        new_user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            referred_by=referrer.telegram_id,
            referral_code=generate_referral_code()
        )
        session.add(new_user)
        session.commit()
        
        # Отправляем приветственное сообщение
        await message.answer(
            f"🎉 Добро пожаловать! Вас пригласил {referrer.first_name}.\n\n"
            f"За регистрацию по реферальной ссылке вы получите дополнительные бонусы!"
        )
        
        return True

async def complete_referral_reward(user_id: int):
    """Выдача реферальных наград после завершения онбординга"""
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if not user or not user.referred_by:
            return
        
        # Обрабатываем реферальные награды
        success = await process_referral_rewards(user.referred_by, user_id)
        
        if success:
            # Уведомляем реферера
            try:
                referrer = session.query(User).filter(User.telegram_id == user.referred_by).first()
                if referrer:
                    await message.bot.send_message(
                        user.referred_by,
                        f"🎉 Ваш реферал {user.first_name} завершил онбординг!\n"
                        f"💎 Вы получили {config.REFERRAL_L1_MSZ} MSZ"
                    )
            except Exception:
                pass  # Игнорируем ошибки отправки уведомлений

async def share_referral_link(callback_query: types.CallbackQuery):
    """Поделиться реферальной ссылкой"""
    user_id = callback_query.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        bot_username = (await callback_query.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
        
        share_text = (
            f"🚀 Присоединяйся к революции в онлайн-шоппинге одежды!\n\n"
            f"🎯 Telegram-бот 'Мастер-размер' поможет:\n"
            f"• Создать твой 3D-аватар\n"
            f"• Точно подобрать размер одежды\n" 
            f"• Заработать токены MSZ\n\n"
            f"💎 По моей ссылке ты получишь бонусы: {referral_link}"
        )
        
        await callback_query.message.edit_text(
            f"📤 **Поделиться ссылкой**\n\n"
            f"Скопируйте текст ниже и отправьте друзьям:\n\n"
            f"`{share_text}`",
            parse_mode="Markdown",
            reply_markup=get_referral_keyboard()
        )

def generate_referral_code() -> str:
    """Генерация уникального реферального кода"""
    return str(uuid.uuid4()).replace('-', '')[:8].upper()

def calculate_referral_earnings(user_id: int) -> int:
    """Подсчет заработка с рефералов"""
    # Здесь должна быть логика подсчета всех реферальных наград
    # Это упрощенная версия
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        return user.referral_count_l1 * config.REFERRAL_L1_MSZ

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_referral_info, Text(equals="👥 Рефералы"))
    dp.register_callback_query_handler(share_referral_link, Text(equals="share_referral"))
