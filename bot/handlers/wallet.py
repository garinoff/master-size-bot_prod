from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from database.models import User
from database.database import get_session
from services.ton_service import validate_ton_address, get_wallet_balance
from utils.keyboards import get_wallet_keyboard, get_tonconnect_keyboard
from config import config

class WalletStates(StatesGroup):
    waiting_for_address = State()

async def show_wallet_info(message: types.Message):
    """Показать информацию о кошельке"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if user.ton_wallet_address:
            # Получаем баланс кошелька
            wallet_balance = await get_wallet_balance(user.ton_wallet_address)
            
            wallet_text = f"""
💎 **Ваш TON Wallet**

📍 **Адрес кошелька:**
`{user.ton_wallet_address}`

💰 **Баланс:**
• TON: {wallet_balance.get('ton', 0):.4f}
• MSZ: {user.msz_balance}

🔄 **Доступные операции:**
• Просмотр транзакций
• Отправка MSZ другим пользователям
• Получение наград за активность

ℹ️ **Информация:**
TON Wallet интеграция позволяет вам полноценно управлять вашими цифровыми активами в экосистеме 3D ShopLine.
            """
        else:
            wallet_text = f"""
💎 **TON Wallet не подключен**

🚀 **Подключите кошелек и получите:**
• Полный контроль над токенами MSZ
• Возможность участия в IDO и NFT-дропах
• Доступ к премиум-функциям
• Участие в управлении проектом (DAO)

📱 **Поддерживаемые кошельки:**
• Tonkeeper
• MyTonWallet
• Tonhub
• TON Wallet

🎁 **Бонус:** {config.BASE_REWARD_MSZ // 2} MSZ за подключение кошелька!
            """
        
        await message.answer(
            wallet_text,
            reply_markup=get_wallet_keyboard(user.ton_wallet_address is not None),
            parse_mode="Markdown"
        )

async def connect_wallet_tonconnect(callback_query: types.CallbackQuery):
    """Подключение кошелька через TonConnect"""
    await callback_query.message.edit_text(
        "🔗 **Подключение TON Wallet**\n\n"
        "Выберите способ подключения:",
        reply_markup=get_tonconnect_keyboard(),
        parse_mode="Markdown"
    )

async def connect_wallet_manual(callback_query: types.CallbackQuery, state: FSMContext):
    """Ручное подключение кошелька"""
    await callback_query.message.edit_text(
        "📝 **Ручное подключение кошелька**\n\n"
        "Отправьте адрес вашего TON кошелька.\n\n"
        "⚠️ **Важно:** Убедитесь, что адрес указан правильно. "
        "Неверный адрес может привести к потере токенов.\n\n"
        "Пример: `EQD4FPq-PRDieyQKkizFTRtSDyucUIqrj0v_zXJmqaDp6_0t`",
        parse_mode="Markdown"
    )
    await WalletStates.waiting_for_address.set()

async def process_wallet_address(message: types.Message, state: FSMContext):
    """Обработка введенного адреса кошелька"""
    wallet_address = message.text.strip()
    user_id = message.from_user.id
    
    # Валидация адреса
    if not validate_ton_address(wallet_address):
        await message.answer(
            "❌ **Неверный формат адреса**\n\n"
            "Пожалуйста, проверьте адрес и отправьте его еще раз.\n"
            "Адрес должен начинаться с 'EQ' или 'UQ' и содержать 48 символов."
        )
        return
    
    # Сохранение адреса
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        user.ton_wallet_address = wallet_address
        session.commit()
    
    # Выдача бонуса за подключение
    bonus_amount = config.BASE_REWARD_MSZ // 2
    await add_tokens_to_user(user_id, bonus_amount, "Подключение TON Wallet")
    
    await message.answer(
        f"✅ **Кошелек успешно подключен!**\n\n"
        f"📍 Адрес: `{wallet_address}`\n"
        f"🎁 Бонус: {bonus_amount} MSZ\n\n"
        f"Теперь вы можете полноценно управлять своими токенами MSZ!",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.finish()

async def disconnect_wallet(callback_query: types.CallbackQuery):
    """Отключение кошелька"""
    user_id = callback_query.from_user.id
    
    async with get_session() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        user.ton_wallet_address = None
        session.commit()
    
    await callback_query.message.edit_text(
        "✅ **Кошелек отключен**\n\n"
        "Вы можете подключить его снова в любое время.",
        reply_markup=get_wallet_keyboard(False)
    )

async def show_transactions(callback_query: types.CallbackQuery):
    """Показать историю транзакций"""
    user_id = callback_query.from_user.id
    
    # Здесь должна быть логика получения истории транзакций
    # Пока показываем заглушку
    
    await callback_query.message.edit_text(
        "📊 **История транзакций**\n\n"
        "🔄 Загрузка данных...\n\n"
        "В будущих версиях здесь будет отображаться:\n"
        "• История получения MSZ токенов\n"
        "• Переводы между пользователями\n"
        "• Участие в IDO и NFT-покупках\n"
        "• Стейкинг и rewards",
        reply_markup=get_wallet_keyboard(True),
        parse_mode="Markdown"
    )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_wallet_info, Text(equals="💎 TON Wallet"))
    dp.register_callback_query_handler(connect_wallet_tonconnect, Text(equals="connect_tonconnect"))
    dp.register_callback_query_handler(connect_wallet_manual, Text(equals="connect_manual"))
    dp.register_callback_query_handler(disconnect_wallet, Text(equals="disconnect_wallet"))
    dp.register_callback_query_handler(show_transactions, Text(equals="show_transactions"))
    dp.register_message_handler(process_wallet_address, state=WalletStates.waiting_for_address)
