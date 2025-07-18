# 🤖 Telegram-бот "Мастер-размер"

## 📋 Описание проекта

**Мастер-размер** - это инновационный Telegram-бот, разработанный в рамках программы "TON-Старт" проекта 3D ShopLine. Бот предназначен для сбора антропометрических данных пользователей, их геймификации через систему токенов MSZ и формирования активного сообщества вокруг будущей платформы виртуальной примерочной.

### 🎯 Основные функции

- **Онбординг пользователей** с пошаговым сбором данных о теле
- **AI-валидация фотографий** с помощью MediaPipe
- **Геймификация** через систему заданий и вознаграждений
- **Реферальная программа** с трехуровневой системой наград
- **Интеграция с TON Wallet** для управления токенами MSZ
- **Базовые рекомендации по размерам** одежды
- **Админ-панель** для управления пользователями и заданиями

### 🌟 Ключевые особенности

- Полная интеграция с экосистемой TON
- Анонимизация персональных данных
- Масштабируемая архитектура
- Многоуровневая система безопасности
- Готовность к развертыванию в производстве

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker и Docker Compose
- TON Wallet для тестирования

### Установка

1. **Клонирование репозитория**
git clone https://github.com/your-username/master-size-bot.git
cd master-size-bot

text

2. **Настройка окружения**
cp .env.example .env

Отредактируйте .env файл с вашими настройками
text

3. **Запуск через Docker**
chmod +x deploy.sh
./deploy.sh

text

4. **Альтернативный запуск (локально)**
pip install -r requirements.txt
python bot/main.py

text

## 📁 Структура проекта

master-size-bot/
├── bot/ # Основной код бота
│ ├── init.py
│ ├── main.py # Точка входа
│ ├── config.py # Конфигурация
│ ├── database/ # Модели и работа с БД
│ │ ├── init.py
│ │ ├── database.py # Подключение к БД
│ │ ├── models.py # ORM модели
│ │ └── migrations/ # Миграции БД
│ ├── handlers/ # Обработчики команд
│ │ ├── init.py
│ │ ├── start.py # Онбординг пользователей
│ │ ├── profile.py # Профиль пользователя
│ │ ├── tasks.py # Геймификация
│ │ ├── referral.py # Реферальная программа
│ │ ├── size_guru.py # Рекомендации размеров
│ │ ├── wallet.py # TON Wallet интеграция
│ │ └── admin.py # Админ-панель
│ ├── services/ # Бизнес-логика
│ │ ├── init.py
│ │ ├── token_service.py # Работа с токенами MSZ
│ │ ├── image_service.py # Обработка изображений
│ │ ├── size_service.py # Подбор размеров
│ │ └── ton_service.py # Блокчейн TON
│ ├── utils/ # Утилиты
│ │ ├── init.py
│ │ ├── keyboards.py # Клавиатуры
│ │ ├── validators.py # Валидация данных
│ │ └── filters.py # Фильтры изображений
│ └── middleware/ # Middleware
│ ├── init.py
│ └── auth.py # Аутентификация
├── requirements.txt # Python зависимости
├── docker-compose.yml # Композиция сервисов
├── Dockerfile # Образ Docker
├── cloudbuild.yaml # Google Cloud Build
├── .env.example # Пример конфигурации
├── deploy.sh # Скрипт развертывания
├── README.md # Этот файл
└── logs/ # Логи приложения

## ⚙️ Конфигурация

### Переменные окружения (.env)

Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/mastersize

TON Blockchain Configuration
TON_API_KEY=your_ton_api_key_here
TON_WALLET_ADDRESS=your_main_wallet_address_here
MSZ_CONTRACT_ADDRESS=your_msz_contract_address_here

Image Processing Configuration
MAX_IMAGE_SIZE=5242880
ALLOWED_IMAGE_FORMATS=JPEG,JPG,PNG

Rewards Configuration
BASE_REWARD_MSZ=300
EXTENDED_REWARD_MSZ=200
FULL_REWARD_MSZ=800
QUALITY_BONUS_MSZ=200
REFERRAL_L1_MSZ=250
REFERRAL_L2_MSZ=100
REFERRAL_L3_MSZ=50

System Limits
MAX_REFERRALS_PER_USER=50

Admin Configuration
ADMIN_USER_IDS=123456789,987654321

Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

## 🗄️ База данных

### Основные таблицы

- **users** - Пользователи бота
- **user_photos** - Фотографии пользователей
- **tasks** - Доступные задания
- **user_tasks** - Выполненные задания
- **size_recommendations** - Рекомендации размеров

### Миграции

Инициализация базы данных выполняется автоматически при запуске
Все миграции находятся в bot/database/migrations/

## 🎮 Использование

### Основные команды бота

- `/start` - Начать работу с ботом
- `/help` - Справка по командам
- `👤 Профиль` - Просмотр профиля пользователя
- `🎯 Задания` - Доступные задания
- `📏 Подбор размера` - Рекомендации по размерам
- `👥 Рефералы` - Реферальная программа
- `💎 TON Wallet` - Управление кошельком

### Процесс онбординга

1. **Приветствие** - Знакомство с ботом
2. **Загрузка фото** - AI-валидация изображения
3. **Ввод параметров** - Пол, возраст, рост, вес, обхваты
4. **Подключение кошелька** - Интеграция с TON Wallet
5. **Получение токенов** - Вознаграждение за регистрацию

### Система вознаграждений

| Действие | Награда (MSZ) | Условие |
|----------|---------------|---------|
| Базовый пакет данных | 300 | 2 фото + основные параметры |
| Расширенный пакет | +200 | Дополнительные измерения |
| Полный пакет | 800 | Все данные |
| Бонус за качество | +200 | AI-валидация пройдена |
| Реферал L1 | 250 | За каждого приглашенного |
| Реферал L2 | 100 | За реферала реферала |
| Реферал L3 | 50 | За реферала L2 |

## 🚀 Развертывание

### Локальная разработка

1. Установка зависимостей
pip install -r requirements.txt

2. Настройка базы данных
export DATABASE_URL="sqlite:///./bot.db"

3. Запуск бота
python bot/main.py

### Docker

Сборка образа
docker build -t master-size-bot .

Запуск контейнера
docker run -d --name master-size-bot
--env-file .env
master-size-bot

### Docker Compose

Запуск всех сервисов
docker-compose up -d

Просмотр логов
docker-compose logs -f bot

Остановка
docker-compose down

### Google Cloud Platform

Развертывание на Cloud Run
gcloud builds submit --config cloudbuild.yaml .

## 🔧 API документация

### Основные сервисы

#### TokenService
Добавление токенов пользователю
await add_tokens_to_user(telegram_id, amount, reason)

Получение баланса
balance = await get_user_balance(telegram_id)

Обработка реферальных наград
await process_referral_rewards(referrer_id, new_user_id)

#### ImageService
Обработка фотографии пользователя
result = await process_user_photo(photo, user_id)

Валидация позы
validation = await validate_pose(image)

Анонимизация изображения
anonymized = await anonymize_and_optimize(image)

#### SizeService
Рекомендация размера
recommendation = await size_guru.recommend_size(
user_id, brand, clothing_type, fit_preference
)

## 🔒 Безопасность

### Защита данных

- **Анонимизация лиц** на всех фотографиях
- **Шифрование** персональных данных
- **Валидация** всех пользовательских вводов
- **Лимиты** на количество запросов
- **Защита от Sybil-атак**

### Антифрод меры

- Device fingerprinting
- IP-ограничения
- KYC-light (верификация номера телефона)
- AI-детекция качества фото
- Вестинг для реферальных наград

## 📊 Мониторинг и аналитика

### Ключевые метрики

- Количество активных пользователей (DAU/MAU)
- Коэффициент конверсии онбординга
- Качество собранных данных (AI-валидация)
- Эффективность реферальной программы
- Распределение токенов MSZ

### Логирование

Все действия логируются в structured формате
logger.info("User completed onboarding", extra={
"user_id": user_id,
"completion_time": completion_time,
"data_quality_score": score
})

## 🧪 Тестирование

### Запуск тестов

Unit тесты
pytest tests/unit/

Integration тесты
pytest tests/integration/

Все тесты
pytest tests/

### Покрытие кода

Генерация отчета о покрытии
coverage run -m pytest
coverage report
coverage html

## 📈 Масштабирование

### Производительность

- **Асинхронная архитектура** для обработки множественных запросов
- **Кеширование** часто используемых данных в Redis
- **Оптимизация изображений** для быстрой обработки
- **Горизонтальное масштабирование** через Docker Swarm/Kubernetes

### Мониторинг производительности

- Prometheus метрики
- Grafana дашборды
- Health checks для всех сервисов
- Alerting при критических ошибках

## 🤝 Вклад в проект

### Правила разработки

1. **Форкните** репозиторий
2. **Создайте** feature branch (`git checkout -b feature/amazing-feature`)
3. **Коммитьте** изменения (`git commit -m 'Add amazing feature'`)
4. **Пушьте** в branch (`git push origin feature/amazing-feature`)
5. **Откройте** Pull Request

### Код стайл

- Следуйте PEP 8 для Python кода
- Используйте type hints
- Документируйте публичные функции
- Пишите тесты для нового функционала

## 📄 Лицензия

Проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка и контакты

### Команда разработки

- **Основатель**: Дмитрий Городецкий
- **CTO**: AI Assistant
- **Email**: theartofaiai@gmail.com

### Сообщество

- **Telegram канал**: [@3DShopLineNews](https://t.me/3DShopLineNews)
- **Telegram чат**: [@3DShopLineChat](https://t.me/3DShopLineChat)
- **GitHub**: [github.com/3DShopLine](https://github.com/3DShopLine)

### Техническая поддержка

Если у вас возникли проблемы или вопросы:

1. Проверьте [FAQ](docs/FAQ.md)
2. Создайте [Issue](https://github.com/3DShopLine/master-size-bot/issues)
3. Напишите в [Telegram чат](https://t.me/3DShopLineChat)

## 🚀 Дорожная карта

### Ближайшие планы

- [ ] Запуск beta-версии бота
- [ ] Интеграция с TON Connect 2.0
- [ ] Добавление поддержки мультиязычности
- [ ] Улучшение AI-валидации фотографий
- [ ] Создание web-интерфейса для админов

### Долгосрочные цели

- [ ] Интеграция с платформой 3D ShopLine
- [ ] Поддержка NFT "Master Size Genesis Collection"
- [ ] Интеграция с метавселенными
- [ ] DAO для управления токеномикой
- [ ] Глобальное масштабирование

---

**3D ShopLine** - Революция в fashion e-commerce начинается здесь! 🌟

*Последнее обновление: Декабрь 2024*
Этот README.md файл предоставляет полную документацию для проекта "Мастер-размер", включая:

Детальное описание проекта и его возможностей

Пошаговые инструкции по установке и настройке

Полную структуру проекта с объяснением каждого компонента

Конфигурацию всех необходимых переменных окружения

API документацию для основных сервисов

Инструкции по развертыванию для различных сред

Информацию о безопасности и мониторинге

Гайдлайны для участия в разработке

Файл создан в соответствии с лучшими практиками документирования open-source проектов и готов для использования в производственной среде.