#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы AI-агента без веб-интерфейса
"""

import google.generativeai as genai
import requests
from PIL import Image
import json
import re

# Конфигурация
API_KEY = "AIzaSyAY0AFJlssDEOZyqe6bwxNPvUc8W5bnZBU"

def test_gemini_api():
    """Проверка API Gemini"""
    print("🔍 Тестирование Google Gemini API...")
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Простой текстовый запрос
    response = model.generate_content("""
Ты эксперт по 1С. Напиши краткий код обработчика события ПриЗаписи для формы 1С.
Ответ должен быть в формате JSON с полями: code, description
""")
    
    print(f"✅ Gemini API работает!")
    print(f"Ответ: {response.text[:200]}...\n")
    return True

def test_pollinations_api():
    """Проверка Pollinations.ai API"""
    print("🎨 Тестирование Pollinations.ai API...")
    
    prompt = "Professional 1C Enterprise form interface design, clean layout, orange accents"
    encoded_prompt = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=384&nologo=true"
    
    # Проверка доступности URL
    response = requests.head(image_url, timeout=10)
    if response.status_code == 200:
        print(f"✅ Pollinations.ai API работает!")
        print(f"URL изображения: {image_url}\n")
        return True
    else:
        print(f"⚠️ Pollinations.ai вернул статус: {response.status_code}\n")
        return False

def test_full_pipeline():
    """Полный тест пайплайна с имитацией запроса"""
    print("🚀 Полный тест пайплайна...")
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Имитация промпта для анализа формы
    analysis_prompt = """
Ты эксперт по эргономике интерфейсов 1С Предприятие.
ОПИСАНИЕ ОТ ПОЛЬЗОВАТЕЛЯ: Форма заказа, неудобно что кнопки далеко от полей

ВЫПОЛНИ СЛЕДУЮЩЕЕ:
1. Анализ элементов и стилистики
2. Промпт для генерации макета (на английском, до 500 символов)
3. Код обработчиков событий 1С (на русском)

ОТВЕТ СТРОГО В ФОРМАТЕ JSON:
{
    "analysis": "текст анализа...",
    "elements": ["список элементов"],
    "style_description": "описание стиля...",
    "problems": ["список проблем"],
    "improvements": ["список улучшений"],
    "image_prompt": "промпт для генерации изображения на английском",
    "code_1c": "код обработчиков 1С"
}
"""
    
    response = model.generate_content(analysis_prompt)
    response_text = response.text
    
    # Извлекаем JSON из ответа
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        result_data = json.loads(json_match.group())
        print("✅ JSON успешно распарсен!")
        print(f"   - Анализ: {len(result_data.get('analysis', ''))} символов")
        print(f"   - Элементы: {len(result_data.get('elements', []))} шт.")
        print(f"   - Проблемы: {len(result_data.get('problems', []))} шт.")
        print(f"   - Промпт для изображения: {result_data.get('image_prompt', '')[:50]}...")
        print(f"   - Код 1С: {len(result_data.get('code_1c', ''))} символов")
        
        # Генерация URL изображения
        image_prompt = result_data.get("image_prompt", "Professional 1C Enterprise form")
        encoded_prompt = requests.utils.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
        print(f"\n🖼️ URL изображения: {image_url[:100]}...")
        
        return True
    else:
        print("⚠️ Не удалось найти JSON в ответе")
        print(f"Ответ модели: {response_text[:500]}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AI-Агент для форм 1С - Тестирование компонентов")
    print("=" * 60 + "\n")
    
    tests = [
        ("Gemini API", test_gemini_api),
        ("Pollinations API", test_pollinations_api),
        ("Полный пайплайн", test_full_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка теста '{name}': {e}\n")
            results.append((name, False))
    
    print("=" * 60)
    print("Итоги тестирования:")
    print("=" * 60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️ Некоторые тесты не прошли")
    print("=" * 60)
