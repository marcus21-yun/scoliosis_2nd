import cv2
import numpy as np
from PIL import Image
import io

def load_image(image_bytes):
    """
    이미지 바이트 스트림을 OpenCV 이미지로 변환
    
    Args:
        image_bytes: 이미지 바이트 데이터
        
    Returns:
        OpenCV 형식의 이미지
    """
    try:
        # PIL 이미지로 변환
        pil_image = Image.open(io.BytesIO(image_bytes))
        # RGB to BGR (OpenCV 형식)
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"이미지 로드 오류: {e}")
        return None

def preprocess_image(image, target_size=(480, 640)):
    """
    이미지 전처리 (크기 조정, 대비 향상 등)
    
    Args:
        image: OpenCV 이미지
        target_size: 타겟 이미지 크기 (높이, 너비)
        
    Returns:
        전처리된 이미지
    """
    if image is None:
        return None
    
    # 이미지 크기 조정
    resized = cv2.resize(image, (target_size[1], target_size[0]))
    
    # 그레이스케일 변환
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # 히스토그램 평활화 (대비 향상)
    enhanced = cv2.equalizeHist(gray)
    
    # 가우시안 블러로 노이즈 제거
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 다시 RGB로 변환
    processed = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
    
    return processed

def detect_spine_points(image):
    """
    척추 포인트 감지 (이 예제에서는 가상의 랜덤 포인트 생성)
    실제 구현에서는 PoseNet이나 다른 AI 모델 사용
    
    Args:
        image: 처리할 이미지
        
    Returns:
        감지된 척추 포인트 좌표 리스트
    """
    if image is None:
        return []
    
    height, width = image.shape[:2]
    
    # 가상의 척추 포인트 생성 (실제로는 AI 모델 사용)
    # 예시: 7개의 척추 포인트 생성
    spine_points = []
    center_x = width // 2
    
    # 실제로는 모델에서 예측한 값을 사용해야 함
    # 여기서는 약간의 S자 형태로 포인트 생성
    for i in range(7):
        y = int(height * 0.3 + (height * 0.5 / 6) * i)
        
        # S자 형태로 x 좌표 계산
        offset = int(10 * np.sin((i / 6) * np.pi))
        x = center_x + offset
        
        spine_points.append((x, y))
    
    return spine_points

def calculate_cobb_angle(points):
    """
    척추 포인트로부터 Cobb 각도 계산
    
    Args:
        points: 척추 포인트 좌표 리스트
        
    Returns:
        계산된 Cobb 각도 (도 단위)
    """
    if len(points) < 4:
        return 0.0
    
    # 상부 척추 기울기 계산
    upper_slope = calculate_slope(points[0], points[2])
    
    # 하부 척추 기울기 계산
    lower_slope = calculate_slope(points[-3], points[-1])
    
    # 두 기울기 사이의 각도 계산
    angle = calculate_angle_between_slopes(upper_slope, lower_slope)
    
    return angle

def calculate_slope(point1, point2):
    """
    두 점 사이의 기울기 계산
    
    Args:
        point1: 첫 번째 점 (x, y)
        point2: 두 번째 점 (x, y)
        
    Returns:
        두 점 사이의 기울기
    """
    x1, y1 = point1
    x2, y2 = point2
    
    # x 차이가 0인 경우 (수직선)
    if x2 - x1 == 0:
        return float('inf')
    
    return (y2 - y1) / (x2 - x1)

def calculate_angle_between_slopes(slope1, slope2):
    """
    두 기울기 사이의 각도 계산
    
    Args:
        slope1: 첫 번째 기울기
        slope2: 두 번째 기울기
        
    Returns:
        두 기울기 사이의 각도 (도 단위)
    """
    # 수직선 처리
    if slope1 == float('inf') or slope2 == float('inf'):
        if slope1 == slope2:
            return 0.0
        elif slope1 == float('inf'):
            return 90.0 - np.degrees(np.arctan(slope2))
        else:
            return 90.0 - np.degrees(np.arctan(slope1))
    
    # 각도 계산
    angle_radians = np.arctan((slope2 - slope1) / (1 + slope1 * slope2))
    angle_degrees = np.abs(np.degrees(angle_radians))
    
    return angle_degrees

def draw_spine_analysis(image, spine_points, angle):
    """
    이미지에 척추 분석 결과 시각화
    
    Args:
        image: 원본 이미지
        spine_points: 감지된 척추 포인트
        angle: 계산된 Cobb 각도
        
    Returns:
        시각화된 이미지
    """
    if image is None or not spine_points:
        return image
    
    # 이미지 복사
    result = image.copy()
    
    # 포인트 그리기
    for point in spine_points:
        cv2.circle(result, point, 5, (0, 0, 255), -1)
    
    # 선 그리기
    for i in range(len(spine_points) - 1):
        cv2.line(result, spine_points[i], spine_points[i + 1], (0, 255, 0), 2)
    
    # 상부 척추선 연장
    if len(spine_points) >= 3:
        p1, p2 = spine_points[0], spine_points[2]
        extended_line(result, p1, p2, (255, 0, 0), 2)
    
    # 하부 척추선 연장
    if len(spine_points) >= 3:
        p1, p2 = spine_points[-3], spine_points[-1]
        extended_line(result, p1, p2, (255, 0, 0), 2)
    
    # 각도 표시
    height, width = result.shape[:2]
    text_pos = (width // 2 - 100, height - 30)
    cv2.putText(
        result,
        f"Cobb Angle: {angle:.1f} degrees",
        text_pos,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )
    
    return result

def extended_line(img, pt1, pt2, color, thickness):
    """
    두 점을 지나는 직선을 이미지 경계까지 확장하여 그림
    
    Args:
        img: 이미지
        pt1: 첫 번째 점
        pt2: 두 번째 점
        color: 선 색상
        thickness: 선 두께
    """
    height, width = img.shape[:2]
    
    # 기울기 계산
    x1, y1 = pt1
    x2, y2 = pt2
    
    # x 차이가 0인 경우 (수직선)
    if x2 - x1 == 0:
        cv2.line(img, (x1, 0), (x1, height), color, thickness)
        return
    
    slope = (y2 - y1) / (x2 - x1)
    
    # y = m(x - x1) + y1
    # x = (y - y1) / m + x1
    
    # 이미지 왼쪽 경계와의 교차점
    y_left = int(slope * (0 - x1) + y1)
    # 이미지 오른쪽 경계와의 교차점
    y_right = int(slope * (width - x1) + y1)
    # 이미지 상단 경계와의 교차점
    x_top = int((0 - y1) / slope + x1)
    # 이미지 하단 경계와의 교차점
    x_bottom = int((height - y1) / slope + x1)
    
    # 교차점들 중 이미지 내부에 있는 점 찾기
    points = []
    if 0 <= y_left <= height:
        points.append((0, y_left))
    if 0 <= y_right <= height:
        points.append((width, y_right))
    if 0 <= x_top <= width:
        points.append((x_top, 0))
    if 0 <= x_bottom <= width:
        points.append((x_bottom, height))
    
    # 가장 멀리 떨어진 두 점 찾기
    if len(points) >= 2:
        cv2.line(img, points[0], points[1], color, thickness) 