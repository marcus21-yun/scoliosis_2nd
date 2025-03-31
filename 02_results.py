import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import sys
import time
from datetime import datetime

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 페이지 설정
st.set_page_config(
    page_title="SpineCheck - 진단 결과",
    page_icon="📊",
    layout="wide"
)

# CSS 스타일 설정
st.markdown("""
<style>
    .header {
        font-size: 2rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .risk-low {
        color: green;
        font-weight: bold;
    }
    .risk-medium {
        color: #FF9800;
        font-weight: bold;
    }
    .risk-high {
        color: red;
        font-weight: bold;
    }
    .recommendation-item {
        margin-bottom: 10px;
        padding-left: 20px;
        position: relative;
    }
    .recommendation-item:before {
        content: "•";
        position: absolute;
        left: 0;
        color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# 결과가 없는 경우 리디렉션
if 'result' not in st.session_state and 'analysis_complete' not in st.session_state:
    st.warning("진단 결과가 없습니다. 먼저 진단을 수행해주세요.")
    st.button("진단 페이지로 이동", on_click=lambda: st.switch_page("pages/01_diagnosis.py"))
else:
    # 결과 페이지 표시
    st.markdown('<h1 class="header">척추측만증 진단 결과</h1>', unsafe_allow_html=True)
    
    # 가상의 결과 생성 (실제로는 st.session_state.result 사용)
    if 'result' not in st.session_state:
        st.session_state.result = {
            'angle': 15.7,
            'risk_level': '중간',
            'risk_color': 'medium',
            'recommendations': [
                '정형외과 전문의 상담 권장',
                '자세 교정 운동 시작 고려',
                '6개월 내 재검사 권장'
            ]
        }
    
    # 결과 표시 섹션
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<h2 class="subheader">척추 분석 결과</h2>', unsafe_allow_html=True)
        
        # 이미지 표시
        if st.session_state.result['angle'] < 10:
            st.image("https://img.freepik.com/free-vector/orthopedic-composition-with-flat-image-human-back_1284-63818.jpg", 
                    caption="척추 곡률 분석 결과", use_container_width=True)
        else:
            st.image("https://img.freepik.com/free-vector/orthopedic-composition-with-flat-image-human-back_1284-63818.jpg", 
                    caption="척추 곡률 분석 결과 (샘플)", use_container_width=True)
        
        # 스파인 곡률 그래프 (시각화)
        st.markdown("### 척추 곡률 시각화")
        
        # 샘플 데이터로 척추 곡률 그래프 생성
        x = np.linspace(0, 10, 100)
        # 약간의 곡률이 있는 사인파 생성 (약한 측만증 시뮬레이션)
        y = np.sin(x/2) * st.session_state.result['angle']/30
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='척추 라인',
                                line=dict(color='#1E88E5', width=4)))
        
        # 정상 척추 참조선 추가
        fig.add_trace(go.Scatter(x=x, y=np.zeros_like(x), mode='lines', name='정상 기준선',
                                line=dict(color='green', width=2, dash='dash')))
        
        fig.update_layout(
            title="측면 척추 곡률",
            xaxis_title="위치",
            yaxis_title="편향 (cm)",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 측정된 각도 및 위험도
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<h2 class="subheader">측정 결과</h2>', unsafe_allow_html=True)
        
        # 각도 표시
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("측정된 각도", f"{st.session_state.result['angle']}°")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 위험도 표시
        risk_level = st.session_state.result['risk_level']
        risk_color = st.session_state.result['risk_color']
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"### 위험도")
        
        if risk_level == '낮음':
            st.markdown(f'<p class="risk-low">{risk_level}</p>', unsafe_allow_html=True)
        elif risk_level == '중간':
            st.markdown(f'<p class="risk-medium">{risk_level}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="risk-high">{risk_level}</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 위험도 설명
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 위험도 기준")
        st.markdown("""
        - **낮음 (0-10°)**: 정상 범위 또는 경미한 측만
        - **중간 (10-20°)**: 경도~중등도 측만, 전문의 상담 권장
        - **높음 (20° 이상)**: 중증 측만, 즉시 전문의 상담 필요
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 권장사항
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<h2 class="subheader">권장사항</h2>', unsafe_allow_html=True)
        
        for recommendation in st.session_state.result['recommendations']:
            st.markdown(f'<div class="recommendation-item">{recommendation}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 다음 단계 안내
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">다음 단계</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("주변 병원 찾기", type="primary"):
            st.switch_page("pages/03_hospitals.py")
    
    with col2:
        if st.button("진단 결과 저장"):
            # 여기서는 단순 메시지로 표시 (실제로는 파일 저장 구현)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.success(f"진단 결과가 저장되었습니다. (spine_check_result_{now}.pdf)")
            
            # 실제 앱에서는 PDF 생성 및 다운로드 구현
            # with open(f"spine_check_result_{now}.pdf", "wb") as f:
            #     f.write(generate_pdf_report())
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 면책조항
    st.info("본 진단 결과는 참고용으로만 사용하시고, 정확한 진단은 반드시 전문의와 상담하세요.")
    
    # 홈으로 버튼
    if st.button("홈으로"):
        st.switch_page("app.py") 