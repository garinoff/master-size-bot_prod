from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from database.models import User, Task, UserTask
from database.database import get_session
from services.token_service import add_tokens_to_user
from utils.keyboards import get_tasks_keyboard, get_task_keyboard

async def show_tasks(message: types.Message):
    """Показать доступные задания"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        # Получаем активные задания
        active_tasks = session.query(Task).filter(Task.is_active == True).all()
        
        # Получаем выполненные задания пользователя
        completed_task_ids = session.query(UserTask.task_id).filter(
            UserTask.user_id == user_id,
            UserTask.is_completed == True
        ).all()
        completed_ids = [t[0] for t in completed_task_ids]
        
        available_tasks = [t for t in active_tasks if t.id not in completed_ids]
        
        if not available_tasks:
            await message.answer(
                "🎉 **Все задания выполнены!**\n\n"
                "Следите за обновлениями - скоро появятся новые задания.",
                reply_markup=get_tasks_keyboard()
            )
            return
        
        tasks_text = "🎯 **Доступные задания:**\n\n"
        for task in available_tasks:
            tasks_text += f"• **{task.name}**\n"
            tasks_text += f"  💎 Награда: {task.reward_msz} MSZ\n"
            tasks_text += f"  📝 {task.description}\n\n"
        
        await message.answer(
            tasks_text,
            reply_markup=get_tasks_keyboard(),
            parse_mode="Markdown"
        )

async def complete_social_task(callback_query: types.CallbackQuery):
    """Выполнение социального задания"""
    task_id = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    
    async with get_session() as session:
        task = session.query(Task).filter(Task.id == task_id).first()
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if not task:
            await callback_query.answer("❌ Задание не найдено")
            return
        
        # Проверяем, не выполнено ли уже
        existing_task = session.query(UserTask).filter(
            UserTask.user_id == user_id,
            UserTask.task_id == task_id
        ).first()
        
        if existing_task and existing_task.is_completed:
            await callback_query.answer("✅ Задание уже выполнено")
            return
        
        # Создаем запись о выполнении
        if not existing_task:
            user_task = UserTask(
                user_id=user_id,
                task_id=task_id,
                is_completed=True,
                reward_given=task.reward_msz
            )
            session.add(user_task)
        else:
            existing_task.is_completed = True
            existing_task.reward_given = task.reward_msz
        
        session.commit()
    
    # Выдаем награду
    await add_tokens_to_user(user_id, task.reward_msz, f"Задание: {task.name}")
    
    await callback_query.message.edit_text(
        f"✅ **Задание выполнено!**\n\n"
        f"🎯 {task.name}\n"
        f"💎 Получено: {task.reward_msz} MSZ\n\n"
        f"Продолжайте выполнять задания для получения больше токенов!",
        reply_markup=get_task_keyboard()
    )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_tasks, Text(equals="🎯 Задания"))
    dp.register_callback_query_handler(complete_social_task, Text(startswith="complete_task_"))
