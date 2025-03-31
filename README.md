# SpineCheck - 척추측만증 자가진단 앱

SpineCheck은 스마트폰 카메라를 이용해 척추측만증을 빠르게 자가 진단하고, 주변 전문 의료 기관을 찾을 수 있는 웹 애플리케이션입니다. 사용자는 약 1분 이내에 측만증 여부 및 심각도를 확인하고, 필요시 가장 가까운 병원 정보를 즉시 확인할 수 있습니다.

## 주요 기능

- 다중 각도 촬영을 통한 척추측만증 자가 진단
- AI 기반 척추 곡률 분석 및 측만 각도 측정
- 위치 기반 주변 척추 전문 병원 검색
- 진단 결과 저장 및 이력 관리

## 기술 스택

- **프론트엔드**: Streamlit
- **데이터 분석**: NumPy, Pandas, OpenCV
- **시각화**: Plotly, Folium
- **AI 모델**: TensorFlow
- **위치 서비스**: Geopy

## 설치 방법

1. 저장소 클론
   ```
   git clone https://github.com/yourusername/SpineCheckApp.git
   cd SpineCheckApp
   ```

2. 가상환경 생성 및 활성화
   ```
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. 의존성 패키지 설치
   ```
   pip install -r requirements.txt
   ```

## 실행 방법

```
streamlit run app.py
```

웹 브라우저가 자동으로 열리면서 애플리케이션에 접근할 수 있습니다. 기본 주소는 `http://localhost:8501` 입니다.

## 사용 방법

1. **진단 시작하기**: 메인 화면에서 "진단 시작하기" 버튼을 클릭합니다.
2. **촬영 안내**: 화면의 안내에 따라 전면, 측면, 후면 총 3장의 이미지를 촬영합니다.
3. **분석 대기**: AI가 약 1분간 이미지를 분석합니다.
4. **결과 확인**: 측정된 척추 각도와 위험도, 권장 조치 사항을 확인합니다.
5. **병원 찾기**: 필요시 "주변 병원 찾기" 버튼을 클릭하여 가까운 병원 정보를 확인합니다.

## 프로젝트 구조

```
SpineCheckApp/
├── app.py                  # 메인 애플리케이션 파일
├── requirements.txt        # 의존성 패키지 목록
├── pages/                  # 멀티페이지 앱 구성
│   ├── 01_diagnosis.py     # 진단 페이지
│   ├── 02_results.py       # 결과 페이지
│   ├── 02_results_example.py # 예시 결과 페이지
│   └── 03_hospitals.py     # 병원 찾기 페이지
├── utils/                  # 유틸리티 함수
│   └── image_processing.py # 이미지 처리 유틸리티
├── assets/                 # 정적 파일
│   ├── images/             # 이미지 리소스
│   └── guide/              # 사용자 가이드 이미지
└── data/                   # 데이터 파일
```

## 주의사항

- 본 앱은 의학적 진단 도구가 아닌 참고용 서비스입니다.
- 정확한 진단은 반드시 전문의와 상담하세요.
- 위치 정보와 카메라 접근 권한이 필요합니다.

## 향후 계획

- 모바일 앱 버전 출시 (Flutter/React Native)
- 더 정확한 진단을 위한 AI 모델 개선
- 원격 의료 상담 기능 추가
- 다국어 지원 확대

## 기여 방법

1. 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다.

## 라이선스

MIT License 