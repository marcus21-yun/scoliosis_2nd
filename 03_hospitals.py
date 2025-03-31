import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import time
import random
from datetime import datetime

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 페이지 설정
st.set_page_config(
    page_title="SpineCheck - 주변 병원 찾기",
    page_icon="🏥",
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
    .hospital-box {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .hospital-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .hospital-name {
        font-size: 1.3rem;
        color: #1E88E5;
        margin-bottom: 10px;
    }
    .hospital-address {
        color: #757575;
        margin-bottom: 5px;
    }
    .hospital-phone {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .hospital-distance {
        color: #1E88E5;
        font-weight: bold;
    }
    .hospital-rating {
        color: #FF9800;
    }
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<h1 class="header">주변 병원 찾기</h1>', unsafe_allow_html=True)

# 가상의 샘플 병원 데이터 생성 함수
def generate_sample_hospitals(user_lat, user_lon, count=10):
    # 병원 이름 목록
    hospital_names = [
        "바른척추병원", "튼튼정형외과의원", "건강한의원", 
        "척추전문병원", "연세정형외과", "미소정형외과",
        "서울척추병원", "대학병원정형외과", "척추관절센터",
        "바른자세의원", "현대정형외과", "척추신경외과"
    ]
    
    # 병원 주소 목록
    addresses = [
        "서울시 강남구 삼성동", "서울시 서초구 서초동", "서울시 송파구 잠실동", 
        "서울시 강남구 역삼동", "서울시 마포구 홍대동", "서울시 종로구 종로동",
        "서울시 영등포구 여의도동", "서울시 중구 명동", "서울시 강동구 천호동",
        "서울시 성북구 안암동", "서울시 동작구 상도동", "서울시 광진구 건대입구"
    ]
    
    # 랜덤 위치 생성 (사용자 위치 주변)
    hospitals = []
    for i in range(count):
        # 랜덤 위치 생성 (사용자 위치 주변)
        lat_offset = random.uniform(-0.01, 0.01)
        lon_offset = random.uniform(-0.01, 0.01)
        
        lat = user_lat + lat_offset
        lon = user_lon + lon_offset
        
        # 거리 계산 (간단한 근사치)
        distance = np.sqrt(lat_offset**2 + lon_offset**2) * 111  # 1도는 약 111km
        
        # 병원 정보 생성
        hospital_name = f"{hospital_names[i % len(hospital_names)]}" if i < len(hospital_names) else f"{hospital_names[i % len(hospital_names)]} {i//len(hospital_names)+1}"
        address = f"{addresses[i % len(addresses)]} {random.randint(100, 999)}번지"
        phone = f"02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        rating = round(random.uniform(3.0, 5.0), 1)
        
        hospitals.append({
            "id": i+1,
            "name": hospital_name,
            "lat": lat,
            "lon": lon,
            "address": address,
            "phone": phone,
            "rating": rating,
            "distance": round(distance, 2),
            "reviews": random.randint(5, 100)
        })
    
    # 거리 순으로 정렬
    hospitals.sort(key=lambda x: x["distance"])
    
    return pd.DataFrame(hospitals)

# 위치 정보 입력 섹션
st.markdown('<h2 class="subheader">내 위치 입력</h2>', unsafe_allow_html=True)

# 검색 위치 옵션
location_option = st.radio(
    "위치 선택 방법",
    ["현재 위치 사용", "주소 입력"],
    horizontal=True
)

# 사용자 위치 정보
user_location = {"lat": None, "lon": None, "address": None}

if location_option == "현재 위치 사용":
    # 실제 앱에서는 브라우저 geolocation API를 연동하여 현재 위치를 가져옴
    # 여기서는 서울 강남역 위치로 가정
    user_location["lat"] = 37.498095
    user_location["lon"] = 127.027610
    user_location["address"] = "서울특별시 강남구 강남대로 396"
    
    st.success("현재 위치를 성공적으로 가져왔습니다.")
    st.info(f"위치: {user_location['address']}")
else:
    # 주소 입력
    address_input = st.text_input("주소 입력", "서울특별시 강남구")
    
    if address_input:
        # 실제 앱에서는 지오코딩 API를 사용하여 주소를 좌표로 변환
        # 여기서는 샘플 데이터 사용
        user_location["lat"] = 37.498095 + random.uniform(-0.005, 0.005)
        user_location["lon"] = 127.027610 + random.uniform(-0.005, 0.005)
        user_location["address"] = address_input
        
        st.success("입력하신 주소의 좌표를 가져왔습니다.")

# 검색 반경 설정
search_radius = st.slider("검색 반경 (km)", min_value=1, max_value=10, value=3)

# 전문 분야 필터
specialty_filter = st.multiselect(
    "전문 분야 필터",
    ["정형외과", "척추전문", "재활의학과", "통증의학과", "신경외과"],
    default=["정형외과", "척추전문"]
)

# 검색 버튼
if user_location["lat"] and user_location["lon"]:
    if st.button("주변 병원 검색", type="primary"):
        with st.spinner("주변 병원을 검색 중입니다..."):
            # 샘플 병원 데이터 생성
            hospitals_df = generate_sample_hospitals(
                user_location["lat"], 
                user_location["lon"],
                count=10
            )
            
            # 검색 반경 필터링
            hospitals_df = hospitals_df[hospitals_df["distance"] <= search_radius]
            
            # 맵 표시 (실제 앱에서는 folium 또는 mapbox 등으로 구현)
            st.markdown('<h2 class="subheader">병원 위치</h2>', unsafe_allow_html=True)
            
            # 지도 표시 (실제 앱에서는 지도 API 사용)
            st.markdown("<h3>지도</h3>", unsafe_allow_html=True)
            st.image("https://img.freepik.com/free-vector/city-map-with-street-navigation-GPS-scheme_107791-1365.jpg", 
                    caption="지도 (실제 앱에서는 실시간 지도로 표시됩니다)", use_container_width=True)
            
            # 병원 목록 표시
            st.markdown('<h2 class="subheader">주변 병원 목록</h2>', unsafe_allow_html=True)
            
            if hospitals_df.empty:
                st.warning(f"검색 반경 {search_radius}km 내에 병원을 찾을 수 없습니다.")
            else:
                st.success(f"{len(hospitals_df)}개의 병원을 찾았습니다.")
                
                # 가장 가까운 2개 병원 상세 정보
                st.markdown('<h3 class="subheader">가장 가까운 병원</h3>', unsafe_allow_html=True)
                
                for _, hospital in hospitals_df.head(2).iterrows():
                    st.markdown(f'<div class="hospital-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="hospital-name">{hospital["name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="hospital-address">{hospital["address"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="hospital-phone">☎ {hospital["phone"]}</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f'<div class="hospital-distance">🚶‍♂️ {hospital["distance"]} km</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f'<div class="hospital-rating">⭐ {hospital["rating"]} ({hospital["reviews"]}건의 리뷰)</div>', unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        st.button(f"📞 전화하기", key=f"call_{hospital['id']}")
                    
                    with btn_col2:
                        st.button(f"🗺️ 길찾기", key=f"navi_{hospital['id']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # 전체 병원 목록 (테이블로 표시)
                with st.expander("전체 병원 목록 보기"):
                    view_df = hospitals_df[["name", "address", "phone", "rating", "distance"]].copy()
                    view_df.columns = ["병원명", "주소", "전화번호", "평점", "거리(km)"]
                    st.dataframe(view_df, use_container_width=True)
else:
    st.warning("위치 정보를 가져올 수 없습니다. 주소를 정확히 입력하시거나 위치 접근을 허용해주세요.")

# 하단 안내
st.info("본 검색 결과는 참고용이며, 정확한 병원 정보는 병원에 직접 문의하시기 바랍니다.")

# 홈으로 버튼
if st.button("홈으로"):
    st.switch_page("app.py") 