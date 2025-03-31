import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import time
import os
import sys
import base64
from io import BytesIO
import requests

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 페이지 설정
st.set_page_config(
    page_title="SpineCheck - 척추측만증 진단",
    page_icon="📷",
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
    .guide-box {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .step-counter {
        background-color: #1E88E5;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
    }
    .btn-next {
        background-color: #1E88E5;
        color: white;
    }
    .btn-prev {
        background-color: #757575;
        color: white;
    }
    .timer-container {
        font-size: 6rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .timer-message {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 20px;
    }
    .upload-container {
        border: 2px dashed #1E88E5;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .tab-content {
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'diagnosis_step' not in st.session_state:
    st.session_state.diagnosis_step = 1

if 'images' not in st.session_state:
    st.session_state.images = {'back': None, 'side': None, 'front': None}

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
    
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 5  # 기본 타이머 시간 (5초)

# 이미지 저장 상태 초기화
for img_type in ['back', 'side', 'front']:
    if f'{img_type}_saved' not in st.session_state:
        st.session_state[f'{img_type}_saved'] = False

# 함수 정의
def next_step():
    st.session_state.diagnosis_step += 1

def prev_step():
    st.session_state.diagnosis_step -= 1

def reset_diagnosis():
    st.session_state.diagnosis_step = 1
    st.session_state.images = {'back': None, 'side': None, 'front': None}
    st.session_state.analysis_complete = False

def start_timer():
    st.session_state.timer_active = True
    
def stop_timer():
    st.session_state.timer_active = False

def get_image_download_link(img, filename, text):
    """이미지 다운로드 링크 생성"""
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/jpg;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def get_sample_image(image_type):
    """샘플 이미지 생성 - 실제 인체 실루엣과 유사한 형태로 생성"""
    width, height = 300, 400
    
    # 배경색 생성
    if image_type == 'back':
        # 후면 이미지 - 파란색 배경
        bg_color = (0, 100, 200)
    elif image_type == 'side':
        # 측면 이미지 - 녹색 배경
        bg_color = (0, 150, 100)
    else:  # front
        # 전면 이미지 - 빨간색 배경
        bg_color = (150, 0, 50)
    
    # 이미지 생성 및 간단한 도형 그리기
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 인체 실루엣 그리기 (단순화된 형태)
    if image_type == 'back':
        # 후면 실루엣 - 어깨, 등, 허리 표현
        draw.ellipse((120, 50, 180, 100), fill=(255, 255, 255))  # 머리
        draw.rectangle((135, 100, 165, 250), fill=(200, 200, 200))  # 몸통
        draw.line((135, 150, 100, 200), fill=(255, 255, 255), width=3)  # 왼팔
        draw.line((165, 150, 200, 200), fill=(255, 255, 255), width=3)  # 오른팔
        draw.line((145, 250, 120, 350), fill=(255, 255, 255), width=3)  # 왼다리
        draw.line((155, 250, 180, 350), fill=(255, 255, 255), width=3)  # 오른다리
        # 척추 라인 표시
        for i in range(10):
            y = 110 + i * 15
            offset = 3 if i % 2 == 0 else -3  # 척추가 약간 구부러진 형태
            draw.ellipse((145 + offset, y, 155 + offset, y + 10), fill=(255, 100, 100))
    
    elif image_type == 'side':
        # 측면 실루엣
        draw.ellipse((120, 50, 180, 100), fill=(255, 255, 255))  # 머리
        # 구부러진 등 표현
        draw.arc((120, 100, 170, 300), 0, 180, fill=(255, 255, 255), width=3)
        draw.line((145, 150, 190, 190), fill=(255, 255, 255), width=3)  # 팔
        draw.line((135, 250, 160, 350), fill=(255, 255, 255), width=3)  # 다리
    
    else:  # front
        # 전면 실루엣
        draw.ellipse((120, 50, 180, 100), fill=(255, 255, 255))  # 머리
        draw.rectangle((130, 100, 170, 250), fill=(200, 200, 200))  # 몸통
        draw.line((130, 150, 100, 200), fill=(255, 255, 255), width=3)  # 왼팔
        draw.line((170, 150, 200, 200), fill=(255, 255, 255), width=3)  # 오른팔
        draw.line((145, 250, 120, 350), fill=(255, 255, 255), width=3)  # 왼다리
        draw.line((155, 250, 180, 350), fill=(255, 255, 255), width=3)  # 오른다리
    
    return img

# 이미지 처리 및 저장 함수
def process_and_save_image(img, image_type):
    """이미지 처리 및 세션 상태에 저장"""
    # 이미지를 세션 상태에 저장
    st.session_state.images[image_type] = img
    
    # 성공 메시지 표시
    st.success(f"{image_type} 이미지가 성공적으로 저장되었습니다!")
    
    # 세션 상태에 이미지 저장 여부 기록
    st.session_state[f'{image_type}_saved'] = True
    
    return img

# 타이머 컴포넌트
def timer_component(seconds, image_type):
    if st.session_state.timer_active:
        # 타이머 표시
        timer_placeholder = st.empty()
        message_placeholder = st.empty()
        
        for remaining in range(seconds, 0, -1):
            timer_placeholder.markdown(f'<div class="timer-container">{remaining}</div>', unsafe_allow_html=True)
            message_placeholder.markdown(f'<div class="timer-message">잠시 후 자동으로 촬영됩니다. 자세를 유지하세요.</div>', unsafe_allow_html=True)
            time.sleep(1)
        
        # 타이머 완료 후 카메라 촬영
        timer_placeholder.markdown(f'<div class="timer-container">📸</div>', unsafe_allow_html=True)
        message_placeholder.markdown(f'<div class="timer-message">촬영 완료!</div>', unsafe_allow_html=True)
        
        # 샘플 이미지 생성 및 저장
        sample_image = get_sample_image(image_type)
        process_and_save_image(sample_image, image_type)
        
        st.session_state.timer_active = False
        st.rerun()

# 진단 과정 표시 함수
def show_progress():
    col1, col2, col3, col4 = st.columns(4)
    
    # 단계별 진행 상태 표시
    step1_status = "완료 ✓" if st.session_state.diagnosis_step > 1 else "현재" if st.session_state.diagnosis_step == 1 else "대기"
    step2_status = "완료 ✓" if st.session_state.diagnosis_step > 2 else "현재" if st.session_state.diagnosis_step == 2 else "대기"
    step3_status = "완료 ✓" if st.session_state.diagnosis_step > 3 else "현재" if st.session_state.diagnosis_step == 3 else "대기"
    step4_status = "완료 ✓" if st.session_state.diagnosis_step > 4 else "현재" if st.session_state.diagnosis_step == 4 else "대기"
    
    col1.markdown(f"**1. 준비** - {step1_status}")
    col2.markdown(f"**2. 후면 촬영** - {step2_status}")
    col3.markdown(f"**3. 측면 촬영** - {step3_status}")
    col4.markdown(f"**4. 전면 촬영** - {step4_status}")
    
    # 진행 표시줄
    progress_value = (st.session_state.diagnosis_step - 1) * 25
    st.progress(progress_value)

# 헤더
st.markdown('<h1 class="header">척추측만증 진단</h1>', unsafe_allow_html=True)

# 진행 상태 표시
show_progress()

# 단계별 진행
if st.session_state.diagnosis_step == 1:
    st.markdown('<h2 class="subheader">촬영 가이드</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="guide-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 정확한 진단을 위한 촬영 가이드
    
    **촬영 환경:**
    - 밝은 공간에서 촬영해주세요
    - 단색 배경 앞에서 촬영하면 더 정확합니다
    - 카메라와 2미터 거리를 유지하세요
    
    **복장:**
    - 꼭 맞는 옷을 입거나 상반신을 노출하세요
    - 헐렁한 옷은 정확한 진단을 방해합니다
    
    **자세:**
    - 자연스러운 서 있는 자세를 유지하세요
    - 각 안내에 따라 정확한 위치에서 촬영하세요
    - 촬영 중 움직이지 마세요
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 샘플 이미지 - 로컬 생성
    sample_img = get_sample_image('back')
    st.image(sample_img, caption="촬영 가이드 (샘플 이미지)", width=400)
    
    st.markdown("""
    ### 진단 과정
    1. 후면(등 쪽) 사진 촬영
    2. 측면(오른쪽) 사진 촬영
    3. 전면(정면) 사진 촬영
    4. AI 분석 진행 (약 1분 소요)
    """)
    
    # 타이머 설정
    st.markdown("### 타이머 설정")
    st.session_state.timer_duration = st.slider("촬영 타이머 시간 (초)", 3, 10, 5)
    
    st.button("진단 시작하기", on_click=next_step, type="primary")

elif st.session_state.diagnosis_step == 2:
    st.markdown('<h2 class="subheader">후면 촬영 (1/3)</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 후면 촬영 가이드
        
        - 등이 카메라를 향하도록 서주세요
        - 양팔을 자연스럽게 몸 옆에 붙이세요
        - 어깨가 이미지에 완전히 보이도록 해주세요
        - 발은 어깨 너비로 벌리고 정면을 보세요
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 샘플 이미지 - 로컬 생성
        sample_img = get_sample_image('back')
        st.image(sample_img, caption="후면 촬영 예시 (샘플 이미지)", width=300)
    
    with col2:
        # 탭으로 카메라와 업로드 옵션 구분
        tab1, tab2 = st.tabs(["📷 카메라 촬영", "📁 이미지 업로드"])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            if not st.session_state.timer_active and not st.session_state.images['back']:
                if st.button("타이머로 촬영하기", key="back_timer"):
                    st.session_state.timer_active = True
                    st.rerun()
                
                camera_input = st.camera_input("직접 촬영하기")
                if camera_input:
                    img = Image.open(camera_input)
                    process_and_save_image(img, 'back')
            
            # 타이머 활성화 시 표시
            if st.session_state.timer_active:
                timer_component(st.session_state.timer_duration, 'back')
                
            # 이미지가 있으면 표시
            if st.session_state.images['back']:
                st.image(st.session_state.images['back'], caption="촬영된 후면 이미지", width=300)
                if st.button("다시 촬영", key="retake_back"):
                    st.session_state.images['back'] = None
                    st.session_state.back_saved = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown('<div class="upload-container">', unsafe_allow_html=True)
            st.markdown("### 이미지 업로드")
            uploaded_file = st.file_uploader("후면 이미지 업로드", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                process_and_save_image(img, 'back')
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 이미지가 업로드/촬영되었을 때만 다음 버튼 활성화
    col1, col2 = st.columns(2)
    with col1:
        st.button("처음으로", on_click=reset_diagnosis)
    with col2:
        if st.session_state.images['back']:
            st.button("다음 단계", on_click=next_step, type="primary")

elif st.session_state.diagnosis_step == 3:
    st.markdown('<h2 class="subheader">측면 촬영 (2/3)</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 측면 촬영 가이드
        
        - 오른쪽 측면이 카메라를 향하도록 서주세요
        - 양팔을 자연스럽게 몸 옆에 붙이세요
        - 머리부터 발까지 모두 프레임에 들어오게 해주세요
        - 자연스러운 자세를 유지하세요
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 샘플 이미지 - 로컬 생성
        sample_img = get_sample_image('side')
        st.image(sample_img, caption="측면 촬영 예시 (샘플 이미지)", width=300)
    
    with col2:
        # 탭으로 카메라와 업로드 옵션 구분
        tab1, tab2 = st.tabs(["📷 카메라 촬영", "📁 이미지 업로드"])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            if not st.session_state.timer_active and not st.session_state.images['side']:
                if st.button("타이머로 촬영하기", key="side_timer"):
                    st.session_state.timer_active = True
                    st.rerun()
                
                camera_input = st.camera_input("직접 촬영하기")
                if camera_input:
                    img = Image.open(camera_input)
                    process_and_save_image(img, 'side')
            
            # 타이머 활성화 시 표시
            if st.session_state.timer_active:
                timer_component(st.session_state.timer_duration, 'side')
                
            # 이미지가 있으면 표시
            if st.session_state.images['side']:
                st.image(st.session_state.images['side'], caption="촬영된 측면 이미지", width=300)
                if st.button("다시 촬영", key="retake_side"):
                    st.session_state.images['side'] = None
                    st.session_state.side_saved = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown('<div class="upload-container">', unsafe_allow_html=True)
            st.markdown("### 이미지 업로드")
            uploaded_file = st.file_uploader("측면 이미지 업로드", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                process_and_save_image(img, 'side')
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 이미지가 업로드/촬영되었을 때만 다음 버튼 활성화
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 단계", on_click=prev_step)
    with col2:
        if st.session_state.images['side']:
            st.button("다음 단계", on_click=next_step, type="primary")

elif st.session_state.diagnosis_step == 4:
    st.markdown('<h2 class="subheader">전면 촬영 (3/3)</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 전면 촬영 가이드
        
        - 정면이 카메라를 향하도록 서주세요
        - 양팔을 자연스럽게 몸 옆에 붙이세요
        - 어깨가 이미지에 완전히 보이도록 해주세요
        - 발은 어깨 너비로 벌리고 정면을 보세요
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 샘플 이미지 - 로컬 생성
        sample_img = get_sample_image('front')
        st.image(sample_img, caption="전면 촬영 예시 (샘플 이미지)", width=300)
    
    with col2:
        # 탭으로 카메라와 업로드 옵션 구분
        tab1, tab2 = st.tabs(["📷 카메라 촬영", "📁 이미지 업로드"])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            if not st.session_state.timer_active and not st.session_state.images['front']:
                if st.button("타이머로 촬영하기", key="front_timer"):
                    st.session_state.timer_active = True
                    st.rerun()
                
                camera_input = st.camera_input("직접 촬영하기")
                if camera_input:
                    img = Image.open(camera_input)
                    process_and_save_image(img, 'front')
            
            # 타이머 활성화 시 표시
            if st.session_state.timer_active:
                timer_component(st.session_state.timer_duration, 'front')
                
            # 이미지가 있으면 표시
            if st.session_state.images['front']:
                st.image(st.session_state.images['front'], caption="촬영된 전면 이미지", width=300)
                if st.button("다시 촬영", key="retake_front"):
                    st.session_state.images['front'] = None
                    st.session_state.front_saved = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown('<div class="upload-container">', unsafe_allow_html=True)
            st.markdown("### 이미지 업로드")
            uploaded_file = st.file_uploader("전면 이미지 업로드", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                process_and_save_image(img, 'front')
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 이미지 공유 옵션
    if st.session_state.images['front']:
        with st.expander("이미지 저장 옵션"):
            st.markdown("촬영한 이미지를 저장하려면 아래 링크를 클릭하세요.")
            st.markdown(get_image_download_link(st.session_state.images['front'], 'spine_front.jpg', '전면 이미지 저장'), unsafe_allow_html=True)
            st.markdown(get_image_download_link(st.session_state.images['side'], 'spine_side.jpg', '측면 이미지 저장'), unsafe_allow_html=True)
            st.markdown(get_image_download_link(st.session_state.images['back'], 'spine_back.jpg', '후면 이미지 저장'), unsafe_allow_html=True)
    
    # 이미지가 업로드/촬영되었을 때만 다음 버튼 활성화
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 단계", on_click=prev_step)
    with col2:
        if st.session_state.images['front']:
            if st.button("분석 시작", type="primary"):
                # 분석 시작 페이지로 이동
                st.session_state.diagnosis_step = 5
                st.rerun()

elif st.session_state.diagnosis_step == 5:
    st.markdown('<h2 class="subheader">이미지 분석 중...</h2>', unsafe_allow_html=True)
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 분석 과정 시뮬레이션
    for i in range(101):
        progress_bar.progress(i)
        if i < 20:
            status_text.text("이미지 전처리 중...")
        elif i < 40:
            status_text.text("척추 포인트 검출 중...")
        elif i < 60:
            status_text.text("척추 곡률 분석 중...")
        elif i < 80:
            status_text.text("측만 각도 계산 중...")
        else:
            status_text.text("결과 생성 중...")
        time.sleep(0.05)  # 실제 앱에서는 실제 처리 시간에 따라 조정
    
    # 분석 완료 후 결과 페이지로 이동
    st.session_state.analysis_complete = True
    st.success("분석이 완료되었습니다!")
    
    # 예시 결과 생성 (실제로는 AI 모델을 통한 예측 결과)
    if 'result' not in st.session_state:
        st.session_state.result = {
            'angle': 15.7,
            'risk_level': '중간',
            'risk_color': 'yellow',
            'recommendations': [
                '정형외과 전문의 상담 권장',
                '자세 교정 운동 시작 고려',
                '6개월 내 재검사 권장'
            ]
        }
    
    time.sleep(1)  # 결과 표시 전 잠시 대기
    
    # 결과 페이지로 이동
    st.switch_page("pages/02_results.py") 