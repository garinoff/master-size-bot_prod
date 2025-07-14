import cv2
import numpy as np
from typing import Dict, Any
import io
from PIL import Image
import mediapipe as mp

from config import config

mp_pose = mp.solutions.pose

async def process_user_photo(photo, user_id: int) -> Dict[str, Any]:
    """Обработка и валидация фотографии пользователя"""
    
    try:
        # Скачиваем фото
        photo_file = await photo.download(destination=io.BytesIO())
        photo_file.seek(0)
        
        # Конвертируем в OpenCV формат
        image = Image.open(photo_file)
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Валидация размера
        if photo_file.getbuffer().nbytes > config.MAX_IMAGE_SIZE:
            return {
                "is_valid": False,
                "reason": "Размер файла превышает 5MB",
                "score": 0.0
            }
        
        # Валидация формата
        if image.format not in config.ALLOWED_IMAGE_FORMATS:
            return {
                "is_valid": False,
                "reason": "Неподдерживаемый формат изображения",
                "score": 0.0
            }
        
        # AI валидация позы с помощью MediaPipe
        validation_result = await validate_pose(opencv_image)
        
        if validation_result["is_valid"]:
            # Обработка изображения (анонимизация, оптимизация)
            processed_image = await anonymize_and_optimize(opencv_image)
            
            return {
                "is_valid": True,
                "reason": "Фото прошло валидацию",
                "score": validation_result["score"],
                "processed_image": processed_image
            }
        else:
            return validation_result
            
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"Ошибка обработки: {str(e)}",
            "score": 0.0
        }

async def validate_pose(image: np.ndarray) -> Dict[str, Any]:
    """Валидация позы человека на фото"""
    
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5
    ) as pose:
        
        # Конвертируем BGR в RGB для MediaPipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return {
                "is_valid": False,
                "reason": "Человек не обнаружен на фото",
                "score": 0.0
            }
        
        # Проверяем ключевые точки
        landmarks = results.pose_landmarks.landmark
        
        # Проверка видимости ключевых точек
        required_points = [
            mp_pose.PoseLandmark.NOSE,
            mp_pose.PoseLandmark.LEFT_SHOULDER,
            mp_pose.PoseLandmark.RIGHT_SHOULDER,
            mp_pose.PoseLandmark.LEFT_HIP,
            mp_pose.PoseLandmark.RIGHT_HIP,
            mp_pose.PoseLandmark.LEFT_KNEE,
            mp_pose.PoseLandmark.RIGHT_KNEE
        ]
        
        visible_count = 0
        total_visibility = 0
        
        for point in required_points:
            landmark = landmarks[point.value]
            if landmark.visibility > 0.5:
                visible_count += 1
                total_visibility += landmark.visibility
        
        if visible_count < 5:  # Минимум 5 из 7 ключевых точек
            return {
                "is_valid": False,
                "reason": "Поза недостаточно четкая. Убедитесь, что вся фигура видна",
                "score": visible_count / len(required_points)
            }
        
        # Проверка фронтальности позы
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        if shoulder_diff > 0.1:  # Плечи слишком наклонены
            return {
                "is_valid": False,
                "reason": "Выпрямитесь и смотрите прямо в камеру",
                "score": 0.6
            }
        
        # Вычисляем общий скор качества
        avg_visibility = total_visibility / visible_count
        pose_quality = 1.0 - shoulder_diff * 2  # Штраф за наклон
        
        final_score = (avg_visibility + pose_quality) / 2
        
        return {
            "is_valid": True,
            "reason": "Поза корректна",
            "score": final_score
        }

async def anonymize_and_optimize(image: np.ndarray) -> np.ndarray:
    """Анонимизация лица и оптимизация изображения"""
    
    # Загружаем каскад для обнаружения лиц
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Обнаруживаем лица
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Размываем лица
    for (x, y, w, h) in faces:
        face_region = image[y:y+h, x:x+w]
        blurred_face = cv2.GaussianBlur(face_region, (51, 51), 30)
        image[y:y+h, x:x+w] = blurred_face
    
    # Оптимизация размера изображения
    height, width = image.shape[:2]
    if height > 1080 or width > 1080:
        # Пропорциональное уменьшение
        scale = min(1080/height, 1080/width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return image
