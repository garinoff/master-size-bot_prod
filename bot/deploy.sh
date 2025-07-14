#!/bin/bash

# Скрипт развертывания Telegram-бота "Мастер-размер"

echo "🚀 Начинаем развертывание бота 'Мастер-размер'..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и повторите попытку."
    exit 1
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️ Файл .env не найден. Создается из .env.example..."
    cp .env.example .env
    echo "📝 Пожалуйста, отредактируйте файл .env и запустите скрипт снова."
    exit 1
fi

# Создание сети Docker
docker network create mastersize-network 2>/dev/null || true

# Сборка и запуск контейнеров
echo "🔨 Собираем Docker-контейнеры..."
docker-compose build

echo "📦 Запускаем сервисы..."
docker-compose up -d

# Ожидание готовности базы данных
echo "⏳ Ждем готовности базы данных..."
sleep 10

# Проверка статуса
echo "✅ Проверяем статус сервисов..."
docker-compose ps

echo "🎉 Развертывание завершено!"
echo "📱 Бот должен быть доступен в Telegram"
echo "📊 Логи: docker-compose logs -f bot"
echo "🛑 Остановка: docker-compose down"
