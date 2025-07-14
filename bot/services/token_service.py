from datetime import datetime
from typing import Optional

from database.models import User
from database.database import get_session

async def add_tokens_to_user(
    telegram_id: int, 
    amount: int, 
    reason: str,
    transaction_type: str = "reward"
) -> bool:
    """Добавление токенов MSZ пользователю"""
    
    try:
        async with get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                return False
            
            user.msz_balance += amount
            user.total_earned_msz += amount
            user.updated_at = datetime.utcnow()
            
            session.commit()
            
            # Логирование транзакции (можно добавить отдельную таблицу)
            print(f"💎 Токены добавлены: User {telegram_id}, Amount: {amount}, Reason: {reason}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка добавления токенов: {e}")
        return False

async def get_user_balance(telegram_id: int) -> Optional[int]:
    """Получение баланса пользователя"""
    
    try:
        async with get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user.msz_balance if user else None
    except Exception as e:
        print(f"❌ Ошибка получения баланса: {e}")
        return None

async def process_referral_rewards(referrer_id: int, new_user_id: int):
    """Обработка реферальных наград"""
    
    async with get_session() as session:
        referrer = session.query(User).filter(User.telegram_id == referrer_id).first()
        new_user = session.query(User).filter(User.telegram_id == new_user_id).first()
        
        if not referrer or not new_user:
            return False
        
        # Проверяем лимит рефералов
        if referrer.referral_count_l1 >= 50:
            return False
        
        # L1 награда рефереру
        l1_reward = 250
        await add_tokens_to_user(referrer_id, l1_reward, f"Реферал L1: {new_user.first_name}")
        
        # Обновляем счетчик рефералов
        referrer.referral_count_l1 += 1
        
        # L2 награда (рефереру реферера)
        if referrer.referred_by:
            l2_referrer = session.query(User).filter(User.telegram_id == referrer.referred_by).first()
            if l2_referrer:
                l2_reward = 100
                await add_tokens_to_user(l2_referrer.telegram_id, l2_reward, f"Реферал L2: {new_user.first_name}")
                
                # L3 награда
                if l2_referrer.referred_by:
                    l3_referrer = session.query(User).filter(User.telegram_id == l2_referrer.referred_by).first()
                    if l3_referrer:
                        l3_reward = 50
                        await add_tokens_to_user(l3_referrer.telegram_id, l3_reward, f"Реферал L3: {new_user.first_name}")
        
        session.commit()
        return True
