#!/bin/bash

START_YEAR=1992
END_YEAR=2020

BASE_URL="https://download.apcc21.org/ERA5/DAILY/single/t2m"
LOG_FILE="wget_apcc_batch.log"

for YEAR in $(seq $START_YEAR $END_YEAR); do
  for MONTH in 01 02 03 04 05 06 07 08 09 10 11 12; do
    YEARMONTH="${YEAR}${MONTH}"
    
    URL="${BASE_URL}/t2m_${YEARMONTH}.nc"
    FILENAME="t2m_${YEARMONTH}.nc"
    
    if [ -f "$FILENAME" ]; then
      echo "파일이 이미 존재합니다(건너뛰기): $FILENAME" | tee -a $LOG_FILE
      continue
    fi
    
    echo "--- $FILENAME 요청 시작 ---" | tee -a $LOG_FILE
    
    DOWNLOAD_SUCCESS=1 # 1은 다운로드 실패를 의미(성공할 때까지 다운로드 무한 시도)
    
    while [ $DOWNLOAD_SUCCESS -ne 0 ]; do
    
      wget -t 5 --wait=10 "$URL" >> $LOG_FILE -O $FILENAME
    
      DOWNLOAD_SUCCESS=$?
    
      if [ $DOWNLOAD_SUCCESS -eq 0 ]; then
        echo "다운로드 완료: $FILENAME" | tee -a $LOG_FILE
      else
        echo "다운로드 실패: $FILENAME" | tee -a $LOG_FILE
        sleep 10
      fi
    done
    # 무한 루프 종료(다운로드 성공) 후 다음 MONTH 루프로 이동
  done
done
