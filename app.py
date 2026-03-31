import streamlit as st
import google.generativeai as genai
import PIL.Image
import io

# --- 1. 환경 설정 ---
# Google AI Studio에서 발급받은 API 키를 입력하세요.
# 배포 시에는 st.secrets["GEMINI_API_KEY"]를 사용하는 것이 안전합니다.
API_KEY = "AIzaSyCQ9QbdslK7VF_5SVhFTHfpMKYcyRM-3x8" 
genai.configure(api_key=API_KEY)

# 모델 로드 (텍스트/SVG용: Gemini 1.5 Flash, 이미지용: Nano Banana 2)
model_text = genai.GenerativeModel('gemini-1.5-flash')
model_image = genai.GenerativeModel('gemini-3-flash-image') # Nano Banana 2

# --- 2. 시스템 가이드라인 정의 ---
SKT_GUIDELINE = """
너는 SKT 공식 아이콘 디자인 시스템 전문 도구야. 아래 규격을 엄격히 따라야 해.

[공통 규칙]
1. 사용자가 요청한 아이콘이 기존 인벤토리(191종 Line / 44종 2D)에 있는지 먼저 확인해.
2. 존재하면 기존 에셋 사용을 권장하고, 없으면 새로 생성해.

[Line Icon 이미지 생성 (Nano Banana 2용 프롬프트)]
A minimal line icon of [주제], designed in the SKT brand icon style.
- Single-weight outline stroke only (#040000), no fill.
- Stroke weight: 0.85dp at 20dp. All corners rounded.
- Incorporates a 120-degree diagonal cut as a brand signature.
- White background, square canvas, 10% padding.

[2D Icon 이미지 생성 (Nano Banana 2용 프롬프트)]
A 2.5D isometric-style icon of [주제], designed in the SKT brand 2D style.
- Color palette: #3617CE, #6E78FF, #9BAAFF, #B7C0FF, #D2DBFF.
- Transparent background (solid white if transparency is not possible).
- No outlines, purely filled shapes with tonal variation.
- 2.5D perspective, modern corporate aesthetic.
"""

# --- 3. UI 구성 ---
st.set_page_config(page_title="SKT Icon Generator", page_icon="🎨")
st.title("🎨 SKT Icon Generator")
st.caption("SKT 디자인 시스템 기반 아이콘 생성기 (Powered by Nano Banana 2)")

with st.sidebar:
    st.header("설정")
    style = st.radio("스타일", ["2D Icon", "Line Icon"], index=0, horizontal=True)
    method = st.radio("포맷", ["PNG", "SVG"], index=0, horizontal=True)
    
keyword = st.text_input("아이콘 주제 입력", placeholder="예: 5G 기지국, 클라우드 서버...")

# --- 4. 생성 로직 ---
if st.button("아이콘 생성하기"):
    if not keyword:
        st.warning("키워드를 입력해주세요.")
    else:
        # Step 2: 기존 인벤토리 확인 (Gemini에게 먼저 물어봄)
        check_prompt = f"사용자가 '{keyword}' 아이콘을 요청했어. SKT 가이드라인에 이미 이 아이콘이 있는지 확인해주고, 없으면 새로 생성하겠다는 메시지를 줘."
        response_check = model_text.generate_content(SKT_GUIDELINE + check_prompt)
        st.info(response_check.text)

        if method == "PNG":
            # 이미지 생성 프롬프트 조립
            prompt_type = "Line Icon" if style == "Line Icon" else "2D Icon"
            gen_prompt = f"Create a {prompt_type} for '{keyword}' following SKT brand guidelines."
            
            with st.spinner("Nano Banana 2가 이미지를 생성 중입니다..."):
                try:
                    result = model_image.generate_content(gen_prompt)
                    # 모델 결과에서 이미지 추출 (API 사양에 따라 조정 필요)
                    image = result.candidates[0].content.parts[0].inline_data.data 
                    st.image(image, caption=f"Generated {style}: {keyword}")
                except Exception as e:
                    st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")

        else:
            # SVG 코드 생성
            svg_prompt = f"Generate SVG code for a {style} of '{keyword}' based on SKT specs (20x20 viewbox, 0.85 stroke weight for Line, or T-Blue palette for 2D)."
            with st.spinner("SVG 코드를 작성 중입니다..."):
                response_svg = model_text.generate_content(SKT_GUIDELINE + svg_prompt)
                st.code(response_svg.text, language="xml")
                st.markdown("위 코드를 복사하여 .svg 파일로 저장하거나 피그마에 붙여넣으세요.")

# --- 5. 정보 출력 ---
st.divider()
st.markdown("""
### 💡 사용 팁
- **Line Icon**: 미니멀한 UI 요소에 적합합니다.
- **2D Icon**: 마케팅 배너나 강조가 필요한 서비스 화면에 적합합니다.
""")