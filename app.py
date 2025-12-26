import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import json
import re

st.set_page_config(page_title="LinkedIn Visual Pipeline", layout="wide")

st.title("🎨 LinkedIn Visual Pipeline")
st.markdown("**Generate 4 high-converting LinkedIn slides from any text**")

# Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
    st.markdown("---")
    st.markdown("**Pipeline Steps:**")
    st.markdown("1️⃣ Analyze content (Russian prompt)")
    st.markdown("2️⃣ Generate 4 HTML slides")
    st.markdown("3️⃣ Preview & copy code")

# Main text area
user_text = st.text_area(
    "📝 Paste LinkedIn Post/Article Text",
    height=200,
    placeholder="Paste your LinkedIn article or post text here..."
)

# Generate button
if st.button("🚀 Generate Assets", type="primary", use_container_width=True):
    if not api_key:
        st.error("❌ Please enter your Gemini API Key in the sidebar")
    elif not user_text.strip():
        st.error("❌ Please paste some text to analyze")
    else:
        # Configure Gemini
        genai.configure(api_key=api_key)

        # PHASE A: EXTRACT INSIGHTS (The Analyst)
        st.markdown("---")
        st.subheader("🔍 PHASE A: Analyzing Content...")

        with st.spinner("Extracting visual concepts..."):
            # Russian prompt as specified
            analyst_prompt = f"""Проанализируй этот текст из импута. Я хочу создать один мощный слайд (картинку для поста LinkedIn).

Предложи мне 4 варианта концепции:

"Шпаргалка" (Cheat Sheet): Список из 5-7 шагов без воды.

"Сравнение" (Vs.): Таблица "Любитель vs Профи" или "До vs После".

"Процесс" (Diagram): Визуальная схема (Проблема -> Решение).

"Вирусная Обложка" (Authority Cover):
Структура как на обложках топовых креаторов (Lemlist/Justin Welsh).

Главный заголовок (HOOK): Придумай название методу из статьи. Формула: "The [Adjective] [Topic] Playbook/System". (Максимум 4-5 слов).

Нижний подзаголовок (SUB-HOOK): Конкретное доказательство эффективности. Используй цифры, доллары, проценты или часы из статьи. Формула: "Как [Кто-то] достиг [Результат] с помощью [Инструмент/Метод]".

CTA (Call to Action): Короткий призыв для подписи к посту (например: "Разбор системы внутри ⬇️").

ВАЖНО: Выведи результат СТРОГО в формате JSON со следующей структурой:
{{
  "CheatSheet": {{
    "title": "название шпаргалки",
    "items": ["шаг 1", "шаг 2", "шаг 3", "шаг 4", "шаг 5"]
  }},
  "VsComparison": {{
    "title": "название сравнения",
    "left_label": "название левой колонки",
    "right_label": "название правой колонки",
    "left_items": ["пункт 1", "пункт 2", "пункт 3"],
    "right_items": ["пункт 1", "пункт 2", "пункт 3"]
  }},
  "Process": {{
    "title": "название процесса",
    "steps": ["Шаг 1", "Шаг 2", "Шаг 3", "Результат"]
  }},
  "Cover": {{
    "hook": "главный заголовок",
    "subhook": "подзаголовок с доказательством",
    "cta": "призыв к действию"
  }}
}}

Текст для анализа:
{user_text}"""

            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(analyst_prompt)

                # Extract JSON from response
                response_text = response.text.strip()

                # Try to find JSON in the response
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    json_str = json_match.group(0)
                    insights = json.loads(json_str)
                else:
                    # If no JSON found, try to parse the whole response
                    insights = json.loads(response_text)

                st.success("✅ Concepts extracted successfully!")
                with st.expander("📊 View Extracted Insights JSON"):
                    st.json(insights)

            except Exception as e:
                st.error(f"❌ Error in Phase A: {str(e)}")
                st.stop()

        # PHASE B: GENERATE CODE (The Coder)
        st.markdown("---")
        st.subheader("🎨 PHASE B: Generating HTML Slides...")

        slide_types = {
            "CheatSheet": {
                "name": "📋 Cheat Sheet",
                "visual_rules": """Slide Type: Cheat Sheet

Visual Rules:
- Clear checklist structure
- Strong vertical rhythm
- Emphasis on scannability
- Headline at top
- Compact list with strong spacing"""
            },
            "VsComparison": {
                "name": "⚖️ VS Comparison",
                "visual_rules": """Slide Type: Comparison (VS)

Visual Rules:
- Two-column layout
- Strong contrast between left and right
- Clear visual separation
- Minimal text per column
- One central tension point"""
            },
            "Process": {
                "name": "🔄 Process Diagram",
                "visual_rules": """Slide Type: Process Diagram

Visual Rules:
- Vertical flow
- Clear stages
- Directional guidance (arrows, spacing)
- Highlight the transformation point"""
            },
            "Cover": {
                "name": "🏆 Authority Cover",
                "visual_rules": """Slide Type: Authority Cover

Visual Rules:
- Ultra-bold typography
- Minimal elements
- Strong headline dominance
- Sub-headline as payoff
- Optional CTA at bottom"""
            }
        }

        for slide_key, slide_info in slide_types.items():
            st.markdown(f"### {slide_info['name']}")

            with st.spinner(f"Generating {slide_info['name']}..."):
                # Get the brief from insights
                brief = insights.get(slide_key, {})
                brief_json = json.dumps(brief, ensure_ascii=False, indent=2)

                # Create the coder prompt
                coder_prompt = f"""You are a senior visual content designer for top LinkedIn creators.

Task:
Generate ONE standalone HTML + Tailwind CSS slide
(1080x1350, 4:5 ratio) for LinkedIn.

Input:
I will provide a content skeleton.
You must NOT invent new ideas.
You must translate the skeleton into a visual slide.

Content Brief:
{brief_json}

{slide_info['visual_rules']}

Constraints:
- One slide only
- Max visual clarity
- Scroll-stopping hierarchy
- Clean, modern, authority-first design
- Dark or neutral background
- No emojis
- No explanations
- Use Tailwind CSS via CDN
- Container: 1080x1350px, centered, overflow-hidden
- Fonts: Use Google Fonts (Inter, Anton, Roboto)
- Style: High-contrast, big typography, "Gumroad/SaaS" aesthetic

Design Rules:
- CheatSheet: Dark background, checkmark icons
- VsComparison: Split screen (Red left/Green right)
- Process: Vertical line with nodes
- Cover: Massive Title, bold colors

Output:
Return ONLY the HTML + Tailwind CSS inside ```html``` code blocks.
No commentary."""

                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(coder_prompt)

                    # Extract HTML from response
                    html_code = response.text.strip()

                    # Try to extract code from markdown code blocks
                    code_match = re.search(r'```html\s*([\s\S]*?)\s*```', html_code)
                    if code_match:
                        html_code = code_match.group(1)
                    else:
                        # Try without language specifier
                        code_match = re.search(r'```\s*([\s\S]*?)\s*```', html_code)
                        if code_match:
                            html_code = code_match.group(1)

                    # Display the preview
                    st.markdown("**Live Preview:**")
                    components.html(html_code, height=600, scrolling=True)

                    # Show code in expander
                    with st.expander("📄 View/Copy HTML Code"):
                        st.code(html_code, language="html")

                    st.success(f"✅ {slide_info['name']} generated!")

                except Exception as e:
                    st.error(f"❌ Error generating {slide_info['name']}: {str(e)}")

        st.markdown("---")
        st.success("🎉 All 4 slides generated successfully! Scroll up to view and copy the HTML code.")

# Footer
st.markdown("---")
st.markdown("**💡 Tip:** Each slide is self-contained HTML with Tailwind CSS. Copy and save as .html files.")
