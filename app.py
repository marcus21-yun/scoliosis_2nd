import streamlit as st
import os

# 파일 감시 기능 비활성화
os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '0'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# 페이지 설정
st.set_page_config(
    page_title="SpineCheck - 척추측만증 자가진단",
    page_icon="🧍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 설정
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 2rem;
        text-align: center;
    }
    .feature-header {
        font-size: 1.2rem;
        color: #1E88E5;
        margin-top: 1rem;
    }
    .feature-box {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        height: 100%;
    }
    .btn-primary {
        background-color: #1E88E5;
        color: white;
        padding: 0.75rem 1.5rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        border-radius: 4px;
        margin: 10px 0;
        cursor: pointer;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #757575;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown('<h1 class="main-header">SpineCheck</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">스마트폰으로 1분만에 척추측만증 진단하기</h2>', unsafe_allow_html=True)

# 메인 이미지
# 이미지 파일이 없으므로 텍스트로 대체
st.image("https://img.freepik.com/free-vector/spine-health-concept-illustration_114360-7155.jpg", 
         caption="척추 건강 관리 (샘플 이미지)")

# 3가지 주요 기능 소개
st.markdown('### 주요 기능')
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="feature-header">자가진단</h3>', unsafe_allow_html=True)
    st.write("AI 기반 척추측만증 진단으로 척추의 건강 상태를 빠르게 확인할 수 있습니다.")
    if st.button("진단 시작하기", key="btn_diagnosis"):
        st.switch_page("pages/01_diagnosis.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="feature-header">결과 분석</h3>', unsafe_allow_html=True)
    st.write("측만 각도 및 위험도 평가를 통해 척추 건강 상태를 정확히 파악할 수 있습니다.")
    if st.button("예시 결과 보기", key="btn_results"):
        st.switch_page("pages/02_results_example.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="feature-header">병원 찾기</h3>', unsafe_allow_html=True)
    st.write("가까운 전문병원 정보를 제공하여 전문의 상담을 쉽게 받을 수 있습니다.")
    if st.button("병원 찾기", key="btn_hospitals"):
        st.switch_page("pages/03_hospitals.py")
    st.markdown('</div>', unsafe_allow_html=True)

# 앱 사용 통계
st.markdown('### SpineCheck 현황')
stats_col1, stats_col2, stats_col3 = st.columns(3)
stats_col1.metric("진단 완료", "15,234건")
stats_col2.metric("사용자 평점", "4.8/5.0")
stats_col3.metric("제휴 병원", "358개")

# 앱 소개 및 사용 방법
with st.expander("SpineCheck 소개"):
    st.markdown("""
    **SpineCheck**은 사용자가 스마트폰 카메라를 이용해 척추측만증을 빠르게 자가 진단하고, 
    주변 전문 의료 기관을 찾을 수 있는 애플리케이션입니다.
    
    사용자는 약 1분 이내에 측만증 여부 및 심각도를 확인하고, 필요시 가장 가까운 병원 정보를 
    즉시 확인할 수 있습니다.
    """)

with st.expander("앱 사용 방법"):
    st.markdown("""
    1. **진단 시작하기** 버튼을 클릭합니다.
    2. 안내에 따라 전면, 측면, 후면 총 3장의 이미지를 촬영합니다.
    3. AI 분석 후 척추 곡률 분석 및 측만 각도 측정 결과를 확인합니다.
    4. 필요시 가까운 병원을 찾아 전문의 상담을 받으세요.
    """)

# 면책조항
st.info("본 앱은 의학적 진단 도구가 아닌 참고용 서비스입니다. 정확한 진단은 전문의와 상담하세요.")

# 푸터
st.markdown('<div class="footer">© 2023 SpineCheck. All rights reserved.</div>', unsafe_allow_html=True) 
