import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

for month in range(1,13):
    
    month_str = f'{month:02d}'

    file_pattern = f'u_component_of_wind_0_daily-mean_*{month_str}.nc'
    output_file_path = f'u_component_of_wind_0_daily-mean_850_{month_str}_mean.nc'
    variable_name = 'u'
    
    print(file_pattern)
    
    try:
        # 🌟 xarray를 사용하여 netCDF 파일 열기
        # xr.open_dataset() 함수가 파일을 열고 DataArray 객체들을 포함하는 Dataset 객체를 반환합니다.
        ds = xr.open_mfdataset(
            file_pattern,
            combine='by_coords',
            chunks='auto'
            )
        
        

        print("--- 📂 Dataset 로드 완료 ---")
        # Dataset 구조(차원, 좌표, 변수, 속성) 출력
        print(ds)
        print("\n-------------------------------------")
        print(f"Time 범위: {ds.valid_time.values[0]} 부터 {ds.valid_time.values[-1]} 까지")

        # 🌡️ 특정 변수(예: 2m 기온, 't2m') 선택
        # ERA5의 변수 이름은 파일마다 다르니, 위 ds 출력을 통해 정확한 변수 이름을 확인하세요.
        # 이 예시에서는 't2m' (2m temperature)을 가정합니다.
        
        print("\n--- 전체 기간 평균 계산 중 ---")
        mean_data = ds.mean(dim='valid_time')
        
        mean_data.to_netcdf(
            path=output_file_path
        )

    except Exception as e:
        print(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")