from flask import Flask, jsonify
from collections import OrderedDict
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# 데이터 경로
temperature_file = "./실시간기온.xlsx"
passenger_file1 = "./우대권병합데이터06.csv"
passenger_file2 = "./우대권병합데이터12.csv"


# 데이터 불러오기
temperature_df = pd.read_excel(temperature_file)
temperature_df.set_index('일.시', inplace=True)

# 두 승객 데이터 병합
df1 = pd.read_csv(passenger_file1, encoding='cp949')
df2 = pd.read_csv(passenger_file2, encoding='cp949')
passenger_df = pd.concat([df1, df2], ignore_index=True)

# '일시' 열을 datetime 형식으로 변환
passenger_df['일시'] = pd.to_datetime(passenger_df['일시'])

@app.route('/get-hourly-passengers')
def get_hourly_passengers():
    # 현재 날짜와 시간 가져오기
    now = datetime.now()
    current_date = float(now.strftime('%m.%d'))  # '11.21' 형식으로 변환
    fixed_hour = f"{now.hour}H"  # 현재 시간을 기준으로 시간 생성

    # 기온 데이터에서 현재 날짜와 시간에 해당하는 값 추출
    try:
        temperature = temperature_df.loc[current_date, fixed_hour]
    except KeyError:
        temperature = None  # 데이터가 없으면 None 반환

    # 승객 데이터에서 현재 시간과 날짜를 기준으로 필터링
    passenger_data = passenger_df[
        (passenger_df['일시'].dt.month == now.month) &
        (passenger_df['일시'].dt.day == now.day) &
        (passenger_df['일시'].dt.hour == now.hour)
    ]
    total_passengers = passenger_data['인원수'].sum()

    # 노약자 좌석 수 결정
    elderly_seat_count = 27 if total_passengers >= 17000 else 12

    # 순서를 지정한 JSON 응답 생성
    response = OrderedDict([
        ("date", now.strftime('%m/%d')),
        ("hour", now.strftime('%H:%M')),
        ("temperature", temperature),
        ("total_passengers", total_passengers),
        ("number of seats", f"{elderly_seat_count}seats")
    ])
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
