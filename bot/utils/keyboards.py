from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 Профиль"),
                KeyboardButton(text="🎯 Задания")
            ],
            [
                KeyboardButton(text="📏 Подбор размера"),
                KeyboardButton(text="👥 Рефералы")
            ],
            [
                KeyboardButton(text="💎 TON Wallet"),
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_gender_keyboard():
    """Клавиатура выбора пола"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
            ]
        ]
    )
    return keyboard

def get_tasks_keyboard():
    """Клавиатура заданий"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Подписаться на канал", callback_data="complete_task_1")
            ],
            [
                InlineKeyboardButton(text="📤 Поделиться ботом", callback_data="complete_task_2")
            ],
            [
                InlineKeyboardButton(text="👥 Пригласить друга", callback_data="complete_task_3")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
            ]
        ]
    )
    return keyboard

def get_profile_keyboard():
    """Клавиатура профиля"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Редактировать", callback_data="edit_profile"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")
            ]
        ]
    )
    return keyboard

def get_wallet_keyboard(is_connected: bool = False):
    """Клавиатура TON Wallet"""
    if is_connected:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📊 История транзакций", callback_data="show_transactions")
                ],
                [
                    InlineKeyboardButton(text="💸 Отправить MSZ", callback_data="send_tokens")
                ],
                [
                    InlineKeyboardButton(text="❌ Отключить кошелек", callback_data="disconnect_wallet")
                ],
                [
                    InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
                ]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔗 Подключить через TonConnect", callback_data="connect_tonconnect")
                ],
                [
                    InlineKeyboardButton(text="📝 Подключить вручную", callback_data="connect_manual")
                ],
                [
                    InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
                ]
            ]
        )
    return keyboard
