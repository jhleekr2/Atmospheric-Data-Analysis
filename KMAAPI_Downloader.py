import requests
import re
from urllib.parse import urlparse, parse_qs
import time
import sys
import os # <-- 경로 설정을 위해 os 모듈 추가

# --- 설정 변수 ---
# 다운로드할 자료의 기준 날짜 (YYYYMMDDHH, 예: 2024년 6월 10일 12시)
DATA_DATE = '2024061012' 
# 개인 인증키를 입력
AUTH_KEY = '인증키' 

# GRIB2 파일 다운로드의 기본 URL (파일 이름과 인증키는 변수로 대체됨)
BASE_URL_FORMAT = 'https://apihub-pub.kma.go.kr/api/typ06/url/nwp_file_down.php?file={filename}&authKey={authKey}'
# 파일 이름의 고정된 접두사 (r030_v040_ne36_pres_은 예시이며, 필요한 자료에 맞게 수정 가능)
FILE_PREFIX = 'r030_v040_ne36_pres'
# 다운로드할 예측 시간 범위 (h000 ~ h072, 73개 파일)
HF_START = 0
HF_END = 54

# **[수정 사항 2] 파일 저장 경로 설정:**
# Windows NAS 경로를 안전하게 사용하기 위해 raw string (r"...") 사용
# 참고: 이 경로는 스크립트가 실행되는 환경에서 접근 가능해야 함
SAVE_DIR = r"fakepath\수치모델\RDAPS-KIM\202506"
# -----------------

def download_file(file_url, grib_filename, default_filename='downloaded_data'):
    """
    API URL에서 파일을 다운로드하고, 파일 헤더 또는 인자에서 파일명을 추출하여 저장
    다운로드 진행 상황을 콘솔에 5% 단위로 실시간 표시
    """
    
    # URL에 이미 파일명이 포함되어 있으므로, 이를 기본 저장 경로로 사용
    # 최종 저장 경로: 설정된 디렉토리 + 파일명
    save_path = os.path.join(SAVE_DIR, grib_filename)
    
    # 저장 디렉토리가 없으면 생성
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    try:
        response = requests.get(file_url, stream=True, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"  [오류] 요청 중 예외 발생: {e}")
        return False
        
    # HTTP 상태 코드 확인
    if response.status_code == 200:
        # 1. 파일 크기 확인 (Content-Length 헤더)
        total_size_str = response.headers.get('Content-Length')
        total_size = int(total_size_str) if total_size_str else 0
        downloaded_size = 0
        
        # 2. Content-Disposition 헤더에서 파일 이름 확인 (안정성 확보)
        try:
            if 'Content-Disposition' in response.headers:
                # ... (파일 이름 추출 로직은 그대로 유지)
                disposition = response.headers['Content-Disposition']
                fname_match = re.search(r'filename\*?=(?:UTF-8\'\')?"?(.+?)"?$', disposition, re.I)
                if fname_match:
                    header_filename = fname_match.group(1).strip().strip('"')
                    # 헤더 파일명을 사용하더라도 최종 경로는 SAVE_DIR 내에 저장
                    save_path = os.path.join(SAVE_DIR, header_filename) 
        except Exception:
             pass
        
        print(f"  [성공] 파일을 '{save_path}'로 저장합니다.")

        # 파일 저장
        last_percent = -1 # <-- 5% 단위 표시를 위한 변수
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 3. 다운로드 진행 상황 표시 (Progress Bar 효과)
                    if total_size > 0:
                        percent = int((downloaded_size / total_size) * 100)
                        
                        # **[수정 사항 1] 5% 단위로만 진행률 표시**
                        if percent >= last_percent + 5 or percent == 100:
                            sys.stdout.write(f"\r  [진행] {downloaded_size:,} bytes / {total_size:,} bytes ({percent}%)")
                            sys.stdout.flush()
                            last_percent = percent
                    else:
                        sys.stdout.write(f"\r  [진행] {downloaded_size:,} bytes 다운로드 중...")
                        sys.stdout.flush()

        # 줄바꿈 및 완료 메시지 출력
        sys.stdout.write('\n')
        print("  [완료] 다운로드 완료.")
        return True
    else:
        print(f"  [실패] HTTP 상태 코드: {response.status_code}")
        try:
            print(f"  [응답] {response.text.strip()[:150]}...")
        except:
            print("  [응답] 서버에서 텍스트 응답을 가져올 수 없습니다.")
        return False

# --- 메인 다운로드 루프 실행 ---
if __name__ == "__main__":
    print(f"--- KIM 모델 GRIB2 파일 다운로드 시작 ---")
    print(f"기준 날짜: {DATA_DATE}")
    print(f"예측 시간: h{HF_START:03d} 부터 h{HF_END:03d} 까지 (총 {HF_END - HF_START + 1}개)")
    print(f"저장 경로: {SAVE_DIR}")
    print("-" * 40)
    
    success_count = 0
    fail_count = 0
    
    for hf in range(HF_START, HF_END + 1):
        hf_str = f'h{hf:03d}' 
        grib_filename = f'{FILE_PREFIX}_{hf_str}.{DATA_DATE}.gb2'
        file_url = BASE_URL_FORMAT.format(filename=grib_filename, authKey=AUTH_KEY)
        
        print(f"[{hf_str} 파일 다운로드 시도] 파일명: {grib_filename}")
        
        if download_file(file_url, grib_filename):
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5) 
        print("-" * 40)

    print(f"--- 다운로드 종료 ---")
    print(f"총 시도: {HF_END - HF_START + 1}개")
    print(f"성공: {success_count}개, 실패: {fail_count}개")
