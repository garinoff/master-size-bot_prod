import os
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Config:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/mastersize")
    
    # TON Blockchain
    TON_API_KEY: str = os.getenv("TON_API_KEY", "")
    TON_WALLET_ADDRESS: str = os.getenv("TON_WALLET_ADDRESS", "")
    
    # MSZ Token Contract
    MSZ_CONTRACT_ADDRESS: str = os.getenv("MSZ_CONTRACT_ADDRESS", "")
    
    # Image Processing
    MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", "5242880"))  # 5MB
    ALLOWED_IMAGE_FORMATS: List[str] = ["JPEG", "JPG", "PNG"]
    
    # Rewards
    BASE_REWARD_MSZ: int = int(os.getenv("BASE_REWARD_MSZ", "300"))
    EXTENDED_REWARD_MSZ: int = int(os.getenv("EXTENDED_REWARD_MSZ", "200"))
    FULL_REWARD_MSZ: int = int(os.getenv("FULL_REWARD_MSZ", "800"))
    QUALITY_BONUS_MSZ: int = int(os.getenv("QUALITY_BONUS_MSZ", "200"))
    REFERRAL_L1_MSZ: int = int(os.getenv("REFERRAL_L1_MSZ", "250"))
    REFERRAL_L2_MSZ: int = int(os.getenv("REFERRAL_L2_MSZ", "100"))
    REFERRAL_L3_MSZ: int = int(os.getenv("REFERRAL_L3_MSZ", "50"))
    
    # Limits
    MAX_REFERRALS_PER_USER: int = int(os.getenv("MAX_REFERRALS_PER_USER", "50"))
    
    # Admin
    ADMIN_USER_IDS: List[int] = [int(id) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id]

config = Config()
