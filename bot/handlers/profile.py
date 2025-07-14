from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from database.models import User, UserPhoto, UserTask
from database.database import get_session
from utils.keyboards import get_profile_keyboard, get_main_menu_keyboard
from services.token_service import get_user_balance
from config import config

async def show_profile(message: types.Message):
    """Отображение профиля пользователя"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if not user:
            await message.answer(
                "❌ Профиль не найден. Пожалуйста, начните с команды /start"
            )
            return
        
        # Подсчет статистики
        total_photos = session.query(UserPhoto).filter(
            UserPhoto.user_id == user_id
        ).count()
        
        completed_tasks = session.query(UserTask).filter(
            UserTask.user_id == user_id,
            UserTask.is_completed == True
        ).count()
        
        # Определение уровня пользователя
        level = calculate_user_level(user.total_earned_msz)
        status = get_user_status(level)
        
        profile_text = f"""
👤 **Ваш профиль**

🏷️ **Имя:** {user.first_name or 'Не указано'}
🆔 **ID:** {user.telegram_id}
🏆 **Уровень:** {level} ({status})

📊 **Основные параметры:**
📏 Рост: {user.height or 'Не указан'} см
⚖️ Вес: {user.weight or 'Не указан'} кг
👕 Грудь: {user.chest or 'Не указан'} см
👖 Талия: {user.waist or 'Не указан'} см
👗 Бедра: {user.hips or 'Не указан'} см

💎 **Токены MSZ:**
💰 Текущий баланс: {user.msz_balance} MSZ
📈 Всего заработано: {user.total_earned_msz} MSZ

📸 **Активность:**
🖼️ Загружено фото: {total_photos}
✅ Выполнено заданий: {completed_tasks}
👥 Приглашено друзей: {user.referral_count_l1}

🔗 **TON Wallet:** {'✅ Подключен' if user.ton_wallet_address else '❌ Не подключен'}
        """
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="Markdown"
        )

async def edit_profile(callback_query: types.CallbackQuery, state: FSMContext):
    """Редактирование профиля"""
    await callback_query.message.edit_text(
        "⚙️ **Редактирование профиля**\n\n"
        "Выберите параметр для изменения:",
        reply_markup=get_edit_profile_keyboard(),
        parse_mode="Markdown"
    )

async def show_statistics(callback_query: types.CallbackQuery):
    """Показать детальную статистику"""
    user_id = callback_query.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        # Статистика по заданиям
        tasks_stats = session.query(UserTask).filter(
            UserTask.user_id == user_id
        ).all()
        
        # Статистика по фото
        photos_stats = session.query(UserPhoto).filter(
            UserPhoto.user_id == user_id
        ).all()
        
        validated_photos = [p for p in photos_stats if p.is_validated]
        avg_score = sum(p.validation_score for p in validated_photos if p.validation_score) / len(validated_photos) if validated_photos else 0
        
        stats_text = f"""
📊 **Детальная статистика**

💎 **Токены:**
• Текущий баланс: {user.msz_balance} MSZ
• Всего заработано: {user.total_earned_msz} MSZ
• Средний доход за задание: {user.total_earned_msz // max(len(tasks_stats), 1)} MSZ

📸 **Качество данных:**
• Всего фото: {len(photos_stats)}
• Прошли валидацию: {len(validated_photos)}
• Средний балл качества: {avg_score:.2f}/1.0

👥 **Реферальная программа:**
• Приглашено L1: {user.referral_count_l1}
• Лимит рефералов: {config.MAX_REFERRALS_PER_USER}
• Оставшиеся слоты: {config.MAX_REFERRALS_PER_USER - user.referral_count_l1}

📅 **Активность:**
• Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}
• Дней в проекте: {(datetime.utcnow() - user.created_at).days}
        """
        
        await callback_query.message.edit_text(
            stats_text,
            reply_markup=get_back_to_profile_keyboard(),
            parse_mode="Markdown"
        )

def calculate_user_level(total_earned: int) -> int:
    """Вычисление уровня пользователя"""
    if total_earned < 500:
        return 1
    elif total_earned < 1500:
        return 2
    elif total_earned < 3000:
        return 3
    elif total_earned < 6000:
        return 4
    else:
        return 5

def get_user_status(level: int) -> str:
    """Получение статуса пользователя"""
    statuses = {
        1: "Новичок",
        2: "Активный",
        3: "Опытный", 
        4: "Эксперт",
        5: "Мастер"
    }
    return statuses.get(level, "Новичок")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_profile, Text(equals="👤 Профиль"))
    dp.register_callback_query_handler(edit_profile, Text(equals="edit_profile"))
    dp.register_callback_query_handler(show_statistics, Text(equals="show_stats"))
