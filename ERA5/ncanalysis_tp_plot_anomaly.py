import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

file_path = 'tp_200607_anomaly.nc'

try:
    # 🌟 xarray를 사용하여 netCDF 파일 열기
    # xr.open_dataset() 함수가 파일을 열고 DataArray 객체들을 포함하는 Dataset 객체를 반환합니다.
    ds = xr.open_dataset(file_path)

    print("--- 📂 Dataset 구조 및 메타데이터 ---")
    # Dataset 구조(차원, 좌표, 변수, 속성) 출력
    print(ds)
    print("\n-------------------------------------")

	# 🌡️ 특정 변수(예: 2m 기온, 't2m') 선택
    # ERA5의 변수 이름은 파일마다 다르니, 위 ds 출력을 통해 정확한 변수 이름을 확인하세요.
    # 이 예시에서는 't2m' (2m temperature)을 가정합니다.
    variable_name = 'tp'
    
    if variable_name in ds:
        da = ds[variable_name]
        print(f"\n--- 🌡️ '{variable_name}' DataArray 정보 ---")
        print(da)
        print("------------------------------------------")

        # ✨ 시간 평균 계산 (예시)
        # 모든 시간 차원에 걸쳐 평균을 계산합니다.
        # time_mean_da = da.mean(dim='time')
        
        # 온도 단위 변환(이미 평균값을 구한 상태이므로)
        # time_mean_celsius = da - 273.15
        
        print(f"\n--- 🌐 시간 평균 데이터 정보 ---")
        print(da)
        print("------------------------------------------")
        
        # 강수량은 시간당 강수량이고 m 단위기 때문에 mm 단위로 변환
        da = da * 1000
        
        # 🗺️ 간단한 시각화
        plt.figure(figsize=(10, 6))
        
        # .plot() 메서드는 자동으로 xarray의 좌표 정보를 사용하여 레이블을 지정합니다.
        da.plot(
			cmap='gist_rainbow_r',
            vmin=-0.5,
            vmax=0.5,
			cbar_kwargs={'label': 'Preciptation Anomaly(mm/hr)'}
		)
        
        plt.title(f'{variable_name} - Anomaly')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()
    
    else:
        print(f"오류: 파일에 '{variable_name}' 변수가 없습니다. Dataset 구조를 확인하세요.")

except FileNotFoundError:
    print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인하세요: {file_path}")
except Exception as e:
    print(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")