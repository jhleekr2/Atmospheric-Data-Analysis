import xarray as xr
import pandas as pd
import glob
import re

# -------------------------------------------------------------
# 1. 🔑 전처리 함수 정의 (핵심 수정 부분)
# -------------------------------------------------------------
def assign_month_coordinate(ds):
    """
    파일 이름에서 월 정보(MM)를 추출하여 DataArray에 새로운 'time' 좌표로 할당합니다.
    """
    filepath = ds.encoding['source']
    
    # 정규표현식을 사용하여 파일 이름에서 **두 자리 월(MM)**을 추출
    # 예: t2m_01_mean.nc -> '01' 추출
    # 정규표현식: [0-9]{2} 는 두 자리 숫자를 찾습니다.
    match = re.search(r'_(\d{2})_monthly_sum_mean\.nc$', filepath)
    
    if match:
        month_str = match.group(1)
        # 월 정보 (1-12)를 datetime 객체로 변환하여 새로운 'time' 좌표를 만듭니다.
        # 연도를 1991년으로 임의로 지정 (중요하지 않음, 월만 필요)
        # 30년 전체 월평균이 이미 계산된 상태이므로, 이 'time'은 1년의 월을 나타냄
        new_time_point = pd.to_datetime(f'1991-{month_str}-01')
        
        # ds에 'time'이라는 새로운 차원과 좌표를 추가하고 반환
        return ds.expand_dims(time=[new_time_point])
    else:
        # 파일명 패턴이 맞지 않으면 원래 데이터셋을 반환
        return ds

# -------------------------------------------------------------
# 2. 📝 기존 코드 활용 (open_mfdataset에 preprocess 적용)
# -------------------------------------------------------------
# 파일 패턴은 실제 저장된 이름에 맞게 수정하세요.
monthly_mean_files = 'tp_*_mean.nc' 

# 🌟 open_mfdataset의 preprocess 인수에 위에서 정의한 함수를 전달
# 각 파일이 열릴 때마다 month 좌표가 붙여지므로, combine='by_coords'가 작동합니다.
ds_yearly_mean = xr.open_mfdataset(
    monthly_mean_files, 
    combine='by_coords',
    preprocess=assign_month_coordinate # 🚨 이 부분이 핵심 수정입니다.
)

# -------------------------------------------------------------
# 3. 🎯 특정 지점 선택 및 CSV 저장 (기존 코드 유지)
# -------------------------------------------------------------

# 'time' 좌표가 새로 생성되었으므로, 이제 ds_yearly_mean은 time 차원을 가집니다.
print("--- 📂 합쳐진 Dataset 구조 ---")
print(ds_yearly_mean) 

# 2. 원하는 특정 지점 선택

target_lat=28.75
target_long=169.00

point_data = ds_yearly_mean.sel(
    latitude=target_lat,
    longitude=target_long,
    method='nearest'
)

# 3. DataArray를 Pandas DataFrame으로 변환합니다.
# 't2m' 변수 선택
df = point_data['tp'].to_dataframe()

# 4. CSV 파일로 저장
csv_output_path = f'{target_lat}_{target_long}_tp_monthly.csv'
df.to_csv(csv_output_path)

print(f"\n🎉 성공: 특정 지점 시계열 데이터가 '{csv_output_path}'로 저장되었습니다.")