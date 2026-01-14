# ***************************************
# version. 20250917. 
# This process calculates CALPUFF nc file to Li area average
# add address code number
# And Unify CALMET nc file and CALPUFF nc file
# ***************************************

import pandas as pd
import os
import netCDF4 as nc
import numpy as np
import sys
import logging

# ***************************************
# logging 설정
# ***************************************

# log_dir = "./logs"
log_dir = f"{sys.argv[7]}/{sys.argv[1]}/{sys.argv[3]}"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"calpuff_process_{sys.argv[1]}_{sys.argv[3]}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)  # 콘솔 출력도 동시에
    ]
)
logger = logging.getLogger(__name__)
logger.info(log_file)
# ***************************************
# set
# ***************************************

# ===== 영향지수 등급 함수 =====
def grade_nh3(value):
    if value < 50:
        return 1
    elif value < 100:
        return 2
    elif value < 200:
        return 3
    else:
        return 4

def grade_co(value):
    if value < 10:
        return 1
    elif value < 15:
        return 2
    elif value < 20:
        return 3
    else:
        return 4

# =====   사용자 설정   =====
# print(f"[1] 영향지수 생산 시작 ")
logger.info("[1] 영향지수 생산 시작")
date = sys.argv[1] # smaple: klaps 2024091203, rdaps 2024091121
target = sys.argv[2]  # 'jb' or 'ns'
target_model = sys.argv[3] # "klaps" or "rdaps"

# === input - CALMET nc file
input_dir = f"{sys.argv[4]}" # CALMET nc file ex: /windlidar/model_output/CALMET/2024091121_rdaps_ns/
input_folder_name = f"{date}_{target_model}_{target}" # nc file
calmet_file = os.path.join(input_dir, input_folder_name, f"{target_model}_{date}_{target}.nc")

# === input - CALPUFF nc file
input_dir2 = f"{sys.argv[5]}" # CALPUFF nc file ex: /windlidar/model_output/CALPUFF/2024091121_rdaps_ns/nc_nh3/

# === latlon-address information file for Li average
info_dir = f"{sys.argv[6]}" # latlon-address information
region_info_file = f"{info_dir}/addresses_code_{target}.csv"

# print(f"[1] input nc폴더: {input_folder_name}, 지역: {target}, 모델: {target_model}, 날짜 = {date}")
logger.info(f"[1] input nc폴더: {input_folder_name}, 지역: {target}, 모델: {target_model}, 날짜 = {date}")


# === set case
if target_model == "klaps": # set model fcst time numbur
    # files_num = 12
    files_num = 13
else:
    # files_num = 48
    files_num = 49
    

# =====   nc 경로 지정   =====
nh3_dir = os.path.join(input_dir2, input_folder_name, "nc_nh3")
co_dir = os.path.join(input_dir2, input_folder_name, "nc_co")

if not os.path.exists(nh3_dir):
    logger.error(f"❌ NH3 폴더 없음: {nh3_dir}")
    raise FileNotFoundError(f"❌ NH3 폴더 없음: {nh3_dir}")
if not os.path.exists(co_dir):
    logger.error(f"❌ CO 폴더 없음: {co_dir}")
    raise FileNotFoundError(f"❌ CO 폴더 없음: {co_dir}")
if not os.path.exists(calmet_file):
    logger.error(f"❌ CALMET 파일 없음: {calmet_file}")
    raise FileNotFoundError(f"❌ CALMET 파일 없음: {calmet_file}")

logger.info(f"[2] 폴더 경로 확인 완료")
logger.info(f"nh3_dir = {nh3_dir}")
logger.info(f"co_dir = {co_dir}")
logger.info(f"calmet_file = {calmet_file}")
# print(f"[2] 폴더 경로 확인 완료")
# print(f"nh3_dir = {nh3_dir}")
# print(f"co_dir = {co_dir}")

# =====   결과 저장 리스트   =====
all_data = []
nc_all_data = []
df_nc = pd.DataFrame()
df_merged = pd.DataFrame()

# ***************************************
# process - load and merge
# ***************************************

# =====   NH3와 CO 파일 이름 매칭 후 처리   =====
nh3_files = sorted(f for f in os.listdir(nh3_dir) if f.endswith(".nc"))
co_files = sorted(f for f in os.listdir(co_dir) if f.endswith(".nc"))
common_files = sorted(set(nh3_files) & set(co_files))[:files_num] # klaps forecast 12h, file nums 12 / rdaps forecast 48h, file nums 48

# === 지역 정보 불러오기
logger.info(f"[3] 지역 정보 파일 로드 중: {region_info_file}")
# print(f"[3] 지역 정보 파일 로드 중: {region_info_file}")
df_region_info = pd.read_csv(region_info_file)

# =====   지수 프로페스   =====

# === nc를 dataframe으로
logger.info(f"[4] nc to dataframe")
logger.info(common_files)

# CALMET 파일 로드
try:
    ds_calmet = nc.Dataset(calmet_file)
    logger.info("✅ CALMET 데이터 추출 완료")

except Exception as e:
    logger.error(f"Error processing CALMET file: {e}")
    ds_calmet = None # 오류 발생 시 빈 DataFrame 생성


# print(f"[4] nc to dataframe")
# for file_name in common_files[:files_num]:

for i, file_name in enumerate(common_files[:files_num]):  
    nh3_path = os.path.join(nh3_dir, file_name)
    co_path = os.path.join(co_dir, file_name)
    logger.info(f"{nh3_path}")
    try:
        
        # === load calpuff nc file
        ds_nh3 = nc.Dataset(nh3_path)
        ds_co = nc.Dataset(co_path)
        
        nh3 = ds_nh3.variables['NH3'][0, 0, :, :]
        co = ds_co.variables['OU'][0, 0, :, :]
        lat = ds_nh3.variables['lat'][:] # ns, co 동일
        lon = ds_nh3.variables['lon'][:] # ns, co 동일
        x = ds_nh3.variables['x'][:]
        y = ds_nh3.variables['y'][:]

        # Flatten calpuff data
        lat_flat = lat.flatten()
        lon_flat = lon.flatten()
        x_grid, y_grid = np.meshgrid(x, y)
        x_flat = x_grid.flatten()
        y_flat = y_grid.flatten()
        nh3_flat = nh3.flatten()
        co_flat = co.flatten()

        # 날짜와 시간 추출
        parts = file_name.replace(".nc", "").split("_")  # ['rdaps', '2024091121', '2024091201', 'jb']
        date_part = parts[2][:8]  # yyyymmdd
        time_part = parts[2][8:]  # hh

        nc_df = pd.DataFrame({
            "Date": [date_part] * len(nh3_flat),
            "Time": [time_part] * len(nh3_flat),
            "X": x_flat,
            "Y": y_flat,
            "Lat": lat_flat,
            "Lon": lon_flat,
            "NH3": nh3_flat,
            "CO": co_flat
        })
        
        # === CALMET 데이터 추출 및 병합
        if ds_calmet:
            # CALMET 파일에서 해당하는 시간(i)과 첫 번째 레벨(0)의 데이터를 추출
            # 담당자 문의 결과 CALMET 영역을 CALPUFF와 맞춰야 한다고 함
            # 상대습도(RH)는 3차원이 아닌 2차원 데이터
            calmet_u_wind = ds_calmet.variables['U'][i, 0, 10:-10, 10:-10]
            calmet_v_wind = ds_calmet.variables['V'][i, 0, 10:-10:, 10:-10]
            calmet_temp = ds_calmet.variables['T'][i, 0, 10:-10, 10:-10]
            calmet_rh = ds_calmet.variables['RH'][i, 10:-10, 10:-10]
            
            # 풍속(wind speed) 계산
            calmet_wind_speed = np.sqrt(calmet_u_wind**2 + calmet_v_wind**2)
            
            # 풍향 계산
            # np.arctan2(v, u)는 y축과 x축 벡터를 인자로 받으며, atan2(y, x)로 계산.
            # 90도를 더하고 360으로 나눈 나머지를 취하여 북쪽을 0도로 맞춤.
            calmet_wind_dir = (270 - np.degrees(np.arctan2(calmet_v_wind, calmet_u_wind))) % 360

            # Flatten
            calmet_wind_speed_flat = calmet_wind_speed.flatten()
            calmet_wind_dir_flat = calmet_wind_dir.flatten()
            calmet_temp_flat = calmet_temp.flatten()
            calmet_rh_flat = calmet_rh.flatten()

            # 임시 DataFrame 생성
            df_calmet_temp = pd.DataFrame({
                "X": x_flat, # CALPUFF와 동일한 X, Y 사용
                "Y": y_flat, # CALPUFF와 동일한 X, Y 사용
                "Temperature": calmet_temp_flat,
                "Relative_Humidity": calmet_rh_flat,
                "Wind_Speed": calmet_wind_speed_flat,
                "Wind_Direction": calmet_wind_dir_flat
            })
            
            # CALPUFF 데이터에 CALMET 풍속 데이터 병합
            nc_df = pd.merge(nc_df, df_calmet_temp, on=['X', 'Y'], how='left')

        nc_all_data.append(nc_df)

    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")
        # print(f"Error processing {file_name}: {e}")
        continue
    
# === nc와 지역 정보 dataframe 합치기
logger.info(f"[5] nc와 지역 정보 합치기")
# print(f"[5] nc와 지역 정보 합치기")
df_nc = pd.concat(nc_all_data, ignore_index=True) # nc to dataframe

# nc dataframe을 csv로 저장한 후에 불러와서 지역 정보와 합침(오류 대책)
csv_name_sdate = common_files[0].split('_')[-2] # for csv file name date
csv_name_edate = common_files[-1].split('_')[-2]
data_csv_path = f"{sys.argv[7]}/{date}/{target_model}"
# data_csv_name = f"{target_model}_{csv_name_sdate}_{csv_name_edate}_{target}_data"
data_csv_name = f"{target_model}_{csv_name_sdate}_{csv_name_edate}_index_data"
data_csv = f"{data_csv_path}/{data_csv_name}.csv"

# print(f"[6] 농도 데이터를 가진 nc와 지역 정보 합친 data csv 저장 {data_csv}")
# print(f"{data_csv}")
logger.info(f"[6] 농도 데이터를 가진 nc와 지역 정보 합친 data csv 저장 {data_csv}")
df_nc.to_csv(data_csv, index=False, encoding='utf-8-sig')

df_data = pd.read_csv(f"{data_csv_path}/{data_csv_name}.csv")
# print(f"df_data  → {len(df_data):,}건 로드됨")
logger.info(f"df_data  → {len(df_data):,}건 로드됨")

df_merged = pd.merge(df_region_info, df_data, how="outer", on=['X','Y','Lat','Lon'])
# print(f"df_merged  → {len(df_merged):,}건 로드됨")
logger.info(f"df_merged  → {len(df_merged):,}건 로드됨")

# ***************************************
# process - calculate
# ***************************************

# =====   리 지명(LI_KOR_NM)과 코드(LI_CD) 채우기   =====
# LI_KOR_NM(리) 값이 없는 경우, EMD_KOR_NM(읍면동)으로 채움
df_merged.loc[:, 'LI_KOR_NM'] = df_merged['LI_KOR_NM'].fillna(df_merged['EMD_KOR_NM'])
df_merged.loc[:, 'LI_CD'] = df_merged['LI_CD'].fillna(df_merged['EMD_CD'])

# =====   level2 지역 필터   =====
# SIG_KOR_NM(시군구) 값에서 논산시만 필터
if target == 'ns':
    df_merged = df_merged[(df_merged['SIG_KOR_NM'] == '논산시')]

# =====   평균 계산   =====
# print(f"[6] 리 단위 그룹화 및 평균 산출")
logger.info(f"[6] 리 단위 그룹화 및 평균 산출")

df_grouped = df_merged.groupby(['Date','Time','CTP_KOR_NM','CTPRVN_CD','SIG_KOR_NM','SIG_CD','EMD_KOR_NM','EMD_CD','LI_KOR_NM','LI_CD']).agg({
    'NH3':'mean',
    'CO':'mean',
    'Temperature':'mean',
    'Relative_Humidity':'mean',
    'Wind_Speed':'mean',
    'Wind_Direction':'mean'
}).reset_index()

df_grouped['NH3'] = df_grouped['NH3'].apply(grade_nh3).astype(int)
df_grouped['CO'] = df_grouped['CO'].apply(grade_co).astype(int)

# 온도단위 K에서 C로 변환
df_grouped['Temperature_C'] = df_grouped['Temperature'] - 273.15

# 변환한 온도단위 기존의 온도변수에 대입
df_grouped['Temperature'] = df_grouped['Temperature_C']

# 변환할때 쓴 데이터 변수 드롭
df_grouped.drop(columns=['Temperature_C'], inplace=True)

# ***************************************
# save
# ***************************************

# print(f"[7] 리 평균 csv 저장")
logger.info(f"[7] 리 평균 csv 저장")
output_dir = f"{sys.argv[7]}/{date}/{target_model}"
output_name = f"{target_model}_{csv_name_sdate}_{csv_name_edate}_index_li.csv" # ex. {target_model}_20250702122_2025070223_index.csv

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    # print(f"[8] 출력 디렉토리 생성됨: {output_dir}")
    logger.info(f"[8] 출력 디렉토리 생성됨: {output_dir}")
else:
    # print(f"[8] 출력 디렉토리 존재 확인됨")
    logger.info(f"[8] 출력 디렉토리 존재 확인됨")

out_path = os.path.join(output_dir, output_name)
df_grouped.to_csv(out_path, index=False, encoding='utf-8-sig')
# print(f"✅ 저장 완료: {out_path}")
logger.info(f"✅ 저장 완료: {out_path}")
