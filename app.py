import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image
import io
import base64

# Настройка страницы
st.set_page_config(
    page_title="AI-Агент: Эргономичные формы 1С",
    page_icon="📋",
    layout="wide"
)

# Стили CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4D00;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f8f9fa;
        border-left: 4px solid #FF4D00;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .code-block {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 4px;
        overflow-x: auto;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9rem;
    }
    st-code {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<h1 class="main-header">📋 AI-Агент: Эргономичные формы 1С</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Генерация улучшенных интерфейсов форм на основе скриншота и описания</p>', unsafe_allow_html=True)

# Боковая панель с настройками
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # API ключ Gemini
    api_key = st.text_input(
        "API ключ Google Gemini *",
        type="password",
        help="Получите ключ в Google AI Studio (https://aistudio.google.com/app/apikey). Ключ не сохраняется и используется только для текущей сессии."
    )
    
    if api_key:
        st.success("✅ API ключ принят")
    else:
        st.warning("⚠️ Введите API ключ для работы")
    
    st.info("💡 Все сервисы бесплатные:\n- Google Gemini (Free Tier)\n- Pollinations.ai")
    
    st.markdown("---")
    st.markdown("**Как это работает:**")
    st.markdown("""
    1. Загрузите скриншот формы 1С
    2. Опишите задачу и проблемы
    3. AI проанализирует и предложит улучшения
    4. Получите визуальный макет и код обработчиков
    """)

# Основная часть
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Входные данные")
    
    # Загрузка скриншота
    uploaded_file = st.file_uploader(
        "Загрузите скриншот формы 1С",
        type=["png", "jpg", "jpeg"],
        help="Скриншот существующей формы для анализа стиля и элементов"
    )
    
    # Текстовое описание
    description = st.text_area(
        "Описание задачи",
        placeholder="""Опишите:
- Какая задача решается формой
- Что неудобно в текущем варианте
- Что хотелось бы улучшить
- Какие элементы критически важны""",
        height=200
    )
    
    # Кнопка запуска
    generate_btn = st.button("🚀 Сгенерировать форму", type="primary", disabled=not api_key)

# Переменные состояния
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'generated_image_url' not in st.session_state:
    st.session_state.generated_image_url = None
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None

# Обработка кнопки
if generate_btn and uploaded_file and description:
    with st.spinner("🔄 Анализ формы и генерация..."):
        try:
            # Настройка Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Загрузка изображения
            image = Image.open(uploaded_file)
            
            # Промпт для анализа
            analysis_prompt = f"""Ты эксперт по эргономике интерфейсов 1С Предприятие. 
Проанализируй скриншот формы 1С и текстовое описание пользователя.

ОПИСАНИЕ ОТ ПОЛЬЗОВАТЕЛЯ:
{description}

ВЫПОЛНИ СЛЕДУЮЩЕЕ:

1. **АНАЛИЗ ЭЛЕМЕНТОВ И СТИЛИСТИКИ:**
   - Перечисли основные элементы формы (реквизиты, кнопки, таблицы, поля ввода)
   - Опиши цветовую схему и стиль (цвета, шрифты, расположение)
   - Отметь проблемы эргономики
   - Выяви узкие места в UX

2. **ПРОМПТ ДЛЯ ГЕНЕРАЦИИ МАКЕТА** (на английском, до 500 символов):
   Создай детальный промпт для генерации изображения улучшенной формы 1С.
   Сохрани стилистику 1С (светлый фон, оранжевые/серые акценты, табличная структура),
   но улучши эргономику: логичная группировка, правильные отступы, удобная навигация.
   Формат: "Professional 1C Enterprise form interface design, clean layout, ..."

3. **КОД ОБРАБОТЧИКОВ СОБЫТИЙ 1С** (на русском):
   Сгенерируй рабочий код модуля формы для 1С 8.3 (управляемые формы).
   Включи:
   - Обработчики событий для основных элементов
   - Проверки заполнения полей
   - Логику проведения/записи документа
   - Комментарии на русском языке
   
   Формат кода должен быть готов для вставки в модуль формы в Конфигураторе 1С.

ОТВЕТ СТРОГО В ФОРМАТЕ JSON:
{{
    "analysis": "текст анализа...",
    "elements": ["список элементов"],
    "style_description": "описание стиля...",
    "problems": ["список проблем"],
    "improvements": ["список улучшений"],
    "image_prompt": "промпт для генерации изображения на английском",
    "code_1c": "код обработчиков 1С с экранированными кавычками"
}}
"""
            
            # Отправка запроса к Gemini
            response = model.generate_content([analysis_prompt, image])
            
            # Парсинг ответа (ищем JSON в ответе)
            response_text = response.text
            
            # Извлекаем JSON из ответа
            import json
            import re
            
            # Пытаемся найти JSON в ответе
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result_data = json.loads(json_match.group())
            else:
                # Если JSON не найден, создаем структуру вручную
                result_data = {
                    "analysis": response_text[:1000],
                    "elements": [],
                    "style_description": "",
                    "problems": [],
                    "improvements": [],
                    "image_prompt": f"Professional 1C Enterprise form interface, {description[:200]}",
                    "code_1c": "// Код будет сгенерирован отдельно\n"
                }
            
            st.session_state.analysis_result = result_data
            
            # Генерация изображения через Pollinations.ai
            image_prompt = result_data.get("image_prompt", "Professional 1C Enterprise form interface design")
            
            # Кодируем промпт для URL
            encoded_prompt = requests.utils.quote(image_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
            
            # Проверяем доступность изображения
            image_available = False
            try:
                head_response = requests.head(image_url, timeout=5)
                if head_response.status_code == 200:
                    # Пробуем получить изображение
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200 and len(img_response.content) > 1000:
                        # Проверяем что это действительно изображение (не JSON ошибка)
                        if not img_response.content.startswith(b'{'):
                            image_available = True
                            # Сохраняем изображение в session state
                            st.session_state.generated_image_data = img_response.content
            except Exception:
                pass
            
            if image_available:
                st.session_state.generated_image_url = image_url
                st.session_state.generated_image_error = None
            else:
                # Если Pollinations недоступен, показываем сообщение
                st.session_state.generated_image_url = None
                st.session_state.generated_image_error = (
                    "⚠️ Сервис Pollinations.ai временно недоступен. "
                    f"Вы можете сгенерировать изображение вручную по ссылке: {image_url}"
                )
            
            # Получаем код 1С
            code_1c = result_data.get("code_1c", "// Код не сгенерирован")
            # Декодируем экранированные символы
            code_1c = code_1c.replace('\\"', '"').replace('\\n', '\n')
            st.session_state.generated_code = code_1c
            
            st.success("✅ Генерация завершена!")
            
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
            st.session_state.analysis_result = None
            st.session_state.generated_image_url = None
            st.session_state.generated_code = None

elif generate_btn and not uploaded_file:
    st.warning("⚠️ Загрузите скриншот формы")
elif generate_btn and not description:
    st.warning("⚠️ Введите описание задачи")

# Отображение результатов
if st.session_state.analysis_result:
    st.markdown("---")
    st.subheader("📊 Результаты анализа")
    
    result = st.session_state.analysis_result
    
    # Табы для разных результатов
    tab_analysis, tab_image, tab_code = st.tabs(["🔍 Анализ", "🎨 Визуальный макет", "💻 Код 1С"])
    
    with tab_analysis:
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("### 📋 Анализ элементов")
            st.info(result.get("analysis", "Анализ не выполнен"))
            
            if result.get("elements"):
                st.markdown("#### Элементы формы:")
                for elem in result["elements"]:
                    st.write(f"• {elem}")
        
        with col_a2:
            st.markdown("### ⚠️ Проблемы эргономики")
            if result.get("problems"):
                for problem in result["problems"]:
                    st.warning(f"• {problem}")
            else:
                st.write("Нет данных")
            
            st.markdown("### 💡 Рекомендации по улучшению")
            if result.get("improvements"):
                for improvement in result["improvements"]:
                    st.success(f"• {improvement}")
            else:
                st.write("Нет данных")
        
        st.markdown("### 🎨 Описание стиля:")
        st.markdown(f'<div class="result-box">{result.get("style_description", "Не указано")}</div>', unsafe_allow_html=True)
    
    with tab_image:
        st.markdown("### 🖼️ Сгенерированный макет формы")
        
        if st.session_state.generated_image_url:
            try:
                st.image(st.session_state.generated_image_url, caption="Макет улучшенной формы 1С", use_container_width=True)
                
                # Кнопка для скачивания
                st.download_button(
                    label="📥 Скачать макет",
                    data=requests.get(st.session_state.generated_image_url).content,
                    file_name="form_layout_1c.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Ошибка загрузки изображения: {e}")
                st.info(f"URL изображения: {st.session_state.generated_image_url}")
        else:
            st.warning("Изображение не сгенерировано")
    
    with tab_code:
        st.markdown("### 💻 Код обработчиков событий 1С")
        
        st.info("""
        **Инструкция по использованию:**
        1. Откройте форму в Конфигураторе 1С
        2. Перейдите в модуль формы (F7)
        3. Скопируйте код ниже и вставьте в модуль
        4. Адаптируйте имена реквизитов под вашу конфигурацию
        """)
        
        if st.session_state.generated_code:
            st.code(st.session_state.generated_code, language="bsl")
            
            # Кнопка копирования
            st.download_button(
                label="📥 Скачать код (.txt)",
                data=st.session_state.generated_code.encode('utf-8'),
                file_name="form_handlers_1c.txt",
                mime="text/plain"
            )
        else:
            st.warning("Код не сгенерирован")

# Футер
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
AI-Агент для генерации эргономичных форм 1С | Powered by Google Gemini + Pollinations.ai
</div>
""", unsafe_allow_html=True)
