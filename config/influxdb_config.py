from influxdb import DataFrameClient
import os

# 환경변수에 설정된 정보 받아오기
influxdb_host = os.environ.get('INFLUXDB_HOST', None)
influxdb_user_name = os.environ.get('INFLUXDB_USER_NAME', None)
influxdb_database_name = os.environ.get('INFLUXDB_DATABASE_NAME', None)
influxdb_password = os.environ.get('INFLUXDB_PASSWORD', None)

measurement_name = ""  # influxDB에서 데이터를 받아올 measurement명

# influxDB 연결 설정
influxdb_client = DataFrameClient(host=influxdb_host,
                                  port=8086,
                                  database=influxdb_database_name,
                                  username=influxdb_user_name,
                                  password=influxdb_password)