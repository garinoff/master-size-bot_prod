import json
from typing import Dict, Any, Optional
from database.models import User, SizeRecommendation
from database.database import get_session

class SizeGuru:
    """AI-агент для подбора размеров одежды"""
    
    def __init__(self):
        self.size_charts = self._load_size_charts()
        
    def _load_size_charts(self) -> Dict[str, Any]:
        """Загрузка размерных сеток брендов"""
        # В реальной реализации это будет загружаться из базы данных или API
        return {
            "zara": {
                "women": {
                    "tops": {
                        "XS": {"chest": (80, 84), "waist": (60, 64)},
                        "S": {"chest": (84, 88), "waist": (64, 68)},
                        "M": {"chest": (88, 92), "waist": (68, 72)},
                        "L": {"chest": (92, 96), "waist": (72, 76)},
                        "XL": {"chest": (96, 100), "waist": (76, 80)}
                    },
                    "bottoms": {
                        "XS": {"waist": (60, 64), "hips": (84, 88)},
                        "S": {"waist": (64, 68), "hips": (88, 92)},
                        "M": {"waist": (68, 72), "hips": (92, 96)},
                        "L": {"waist": (72, 76), "hips": (96, 100)},
                        "XL": {"waist": (76, 80), "hips": (100, 104)}
                    }
                },
                "men": {
                    "tops": {
                        "XS": {"chest": (86, 90), "waist": (70, 74)},
                        "S": {"chest": (90, 94), "waist": (74, 78)},
                        "M": {"chest": (94, 98), "waist": (78, 82)},
                        "L": {"chest": (98, 102), "waist": (82, 86)},
                        "XL": {"chest": (102, 106), "waist": (86, 90)}
                    }
                }
            },
            "hm": {
                "women": {
                    "tops": {
                        "XS": {"chest": (78, 82), "waist": (58, 62)},
                        "S": {"chest": (82, 86), "waist": (62, 66)},
                        "M": {"chest": (86, 90), "waist": (66, 70)},
                        "L": {"chest": (90, 94), "waist": (70, 74)},
                        "XL": {"chest": (94, 98), "waist": (74, 78)}
                    }
                }
            }
        }
    
    async def recommend_size(
        self,
        user_id: int,
        brand: str,
        clothing_type: str,
        fit_preference: str = "regular"
    ) -> Dict[str, Any]:
        """Рекомендация размера для конкретного пользователя"""
        
        async with get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user or not user.is_completed:
                return {
                    "success": False,
                    "error": "Профиль пользователя не завершен"
                }
            
            # Получаем размерную сетку бренда
            brand_data = self.size_charts.get(brand.lower())
            if not brand_data:
                return {
                    "success": False,
                    "error": f"Размерная сетка для бренда {brand} не найдена"
                }
            
            gender = "women" if user.gender == "female" else "men"
            gender_data = brand_data.get(gender)
            if not gender_data:
                return {
                    "success": False,
                    "error": f"Размерная сетка для {gender} не найдена"
                }
            
            # Определяем тип одежды
            category = self._get_clothing_category(clothing_type)
            category_data = gender_data.get(category)
            if not category_data:
                return {
                    "success": False,
                    "error": f"Размерная сетка для категории {category} не найдена"
                }
            
            # Подбираем размер
            recommended_size = self._calculate_best_size(
                user, category_data, fit_preference
            )
            
            # Сохраняем рекомендацию
            recommendation = SizeRecommendation(
                user_id=user_id,
                brand_name=brand,
                clothing_type=clothing_type,
                recommended_size=recommended_size["size"],
                confidence_score=recommended_size["confidence"]
            )
            session.add(recommendation)
            session.commit()
            
            return {
                "success": True,
                "recommendation": recommended_size,
                "brand": brand,
                "clothing_type": clothing_type
            }
    
    def _get_clothing_category(self, clothing_type: str) -> str:
        """Определение категории одежды"""
        tops = ["tshirt", "shirt", "jacket", "sweater", "hoodie", "dress"]
        bottoms = ["jeans", "pants", "shorts", "skirt"]
        
        clothing_type_lower = clothing_type.lower()
        
        if any(item in clothing_type_lower for item in tops):
            return "tops"
        elif any(item in clothing_type_lower for item in bottoms):
            return "bottoms"
        else:
            return "tops"  # По умолчанию
    
    def _calculate_best_size(
        self,
        user: User,
        size_chart: Dict[str, Dict[str, tuple]],
        fit_preference: str
    ) -> Dict[str, Any]:
        """Расчет оптимального размера"""
        
        user_measurements = {
            "chest": user.chest or 0,
            "waist": user.waist or 0,
            "hips": user.hips or 0
        }
        
        size_scores = {}
        
        for size, measurements in size_chart.items():
            score = 0
            total_params = 0
            
            for param, (min_val, max_val) in measurements.items():
                if user_measurements.get(param, 0) > 0:
                    user_val = user_measurements[param]
                    
                    # Расчет соответствия размера
                    if min_val <= user_val <= max_val:
                        # Идеальное попадание
                        score += 1.0
                    else:
                        # Штраф за выход за границы
                        if user_val < min_val:
                            penalty = (min_val - user_val) / min_val
                        else:
                            penalty = (user_val - max_val) / max_val
                        
                        score += max(0, 1.0 - penalty * 0.5)
                    
                    total_params += 1
            
            if total_params > 0:
                size_scores[size] = score / total_params
        
        # Находим лучший размер
        best_size = max(size_scores.items(), key=lambda x: x[1])
        
        # Корректировка в зависимости от предпочтений посадки
        adjusted_size = self._adjust_for_fit_preference(
            best_size[0], fit_preference, list(size_chart.keys())
        )
        
        return {
            "size": adjusted_size,
            "confidence": round(best_size[1], 2),
            "alternatives": self._get_alternative_sizes(size_scores, adjusted_size),
            "fit_notes": self._get_fit_notes(user, best_size[0], adjusted_size)
        }
    
    def _adjust_for_fit_preference(
        self,
        recommended_size: str,
        fit_preference: str,
        available_sizes: list
    ) -> str:
        """Корректировка размера в зависимости от предпочтений посадки"""
        
        size_order = ["XS", "S", "M", "L", "XL", "XXL"]
        current_index = size_order.index(recommended_size) if recommended_size in size_order else 2
        
        if fit_preference == "loose" and current_index < len(size_order) - 1:
            return size_order[current_index + 1]
        elif fit_preference == "tight" and current_index > 0:
            return size_order[current_index - 1]
        else:
            return recommended_size
    
    def _get_alternative_sizes(
        self,
        size_scores: Dict[str, float],
        recommended_size: str
    ) -> list:
        """Получение альтернативных размеров"""
        sorted_sizes = sorted(size_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [size for size, score in sorted_sizes if size != recommended_size][:2]
        return alternatives
    
    def _get_fit_notes(self, user: User, original_size: str, final_size: str) -> str:
        """Генерация заметок о посадке"""
        notes = []
        
        if original_size != final_size:
            notes.append(f"Размер скорректирован с {original_size} на {final_size} согласно вашим предпочтениям")
        
        if user.height and user.height > 175:
            notes.append("Учитывая ваш рост, обратите внимание на длину изделия")
        
        return "; ".join(notes) if notes else "Размер подобран оптимально для ваших параметров"

# Инициализация глобального экземпляра
size_guru = SizeGuru()
