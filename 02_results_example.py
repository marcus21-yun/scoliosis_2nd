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
    page_title="SpineCheck - 결과 예시",
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
    .example-badge {
        background-color: #bbdefb;
        color: #0d47a1;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">척추측만증 진단 결과 예시</h1>', unsafe_allow_html=True)
st.markdown('<div class="example-badge">예시 결과</div>', unsafe_allow_html=True)

# 예시 데이터 생성 (3개의 예시 결과)
example_cases = [
    {
        "title": "경미한 측만증",
        "angle": 8.3,
        "risk_level": "낮음",
        "risk_color": "low",
        "recommendations": [
            "자세 교정 운동 권장",
            "척추 건강을 위한 스트레칭 유지",
            "12개월 이내 재검사 고려"
        ]
    },
    {
        "title": "중등도 측만증",
        "angle": 15.7,
        "risk_level": "중간",
        "risk_color": "medium",
        "recommendations": [
            "정형외과 전문의 상담 권장",
            "자세 교정 운동 시작 고려",
            "6개월 내 재검사 권장"
        ]
    },
    {
        "title": "심각한 측만증",
        "angle": 27.2,
        "risk_level": "높음",
        "risk_color": "high",
        "recommendations": [
            "즉시 척추 전문의 진료 필요",
            "전문적인 치료 계획 수립 필요",
            "정기적인 모니터링 요망"
        ]
    }
]

# 예시 선택 탭
selected_tab = st.radio("측만증 심각도 예시 선택", 
                        ["경미한 측만증", "중등도 측만증", "심각한 측만증"],
                        horizontal=True)

# 선택된 예시 데이터 가져오기
selected_case = None
for case in example_cases:
    if case["title"] == selected_tab:
        selected_case = case
        break

if selected_case:
    # 결과 표시 섹션
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<h2 class="subheader">척추 분석 결과</h2>', unsafe_allow_html=True)
        
        # 예시 이미지 선택 (심각도에 따른 이미지 변경)
        if selected_case["risk_level"] == "낮음":
            image_url = "https://img.freepik.com/free-vector/spine-care-concept-illustration_114360-7160.jpg"
        elif selected_case["risk_level"] == "중간":
            image_url = "https://img.freepik.com/free-vector/scoliosis-disease-concept-illustration_114360-7153.jpg"
        else:
            image_url = "https://img.freepik.com/free-vector/back-pain-concept-illustration_114360-7163.jpg"
            
        st.image(image_url, caption="척추 곡률 분석 결과 (샘플)", use_container_width=True)
        
        # 스파인 곡률 그래프 (시각화)
        st.markdown("### 척추 곡률 시각화")
        
        # 샘플 데이터로 척추 곡률 그래프 생성
        x = np.linspace(0, 10, 100)
        # 심각도에 따른 곡률 조정
        amplitude = selected_case["angle"] / 20
        # 약간의 곡률이 있는 사인파 생성
        y = np.sin(x/2) * amplitude
        
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
        st.metric("측정된 각도", f"{selected_case['angle']}°")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 위험도 표시
        risk_level = selected_case["risk_level"]
        risk_color = selected_case["risk_color"]
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"### 위험도")
        
        if risk_level == "낮음":
            st.markdown(f'<p class="risk-low">{risk_level}</p>', unsafe_allow_html=True)
        elif risk_level == "중간":
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
        
        for recommendation in selected_case["recommendations"]:
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
        if st.button("진단 시작하기"):
            st.switch_page("pages/01_diagnosis.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 면책조항
    st.info("본 진단 결과는 참고용으로만 사용하시고, 정확한 진단은 반드시 전문의와 상담하세요.")

# 홈으로 버튼
if st.button("홈으로"):
    st.switch_page("app.py") 