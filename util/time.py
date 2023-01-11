import datetime
import calendar
import time
from pytz import timezone, utc


class TimeUtil:

    """
    각종 시간 데이터 변경
    """
    @staticmethod
    def transfer_time_type(request, data):
        # 타임스탬프를 날짜형식으로 변환
        if (isinstance(data, float) or isinstance(data, int)) and request == "datetime":
            data = datetime.datetime.fromtimestamp(data / 1000)
        # 날짜형식을 타임스탬프로 변환
        if isinstance(data, datetime.datetime) and request == "timestamp":
            data = int(time.mktime(data.timetuple())) * 1000
        # 날짜형식을 타임스탬프로 변환 - UTC
        if isinstance(data, datetime.datetime) and request == "timestamp_utc":
            data = calendar.timegm(data.timetuple()) * 1000 # calendar.timegm는 UTC기준으로 변형
        # 문자형을 날짜형으로 변환
        if isinstance(data, str) and request == "datetime":
            data = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        # 문자형을 타임스탬프로 변환
        if isinstance(data, str) and request == "timestamp":
            data = int(time.mktime(datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').timetuple())) * 1000
        # 날짜형식을 문자열로 변환
        if isinstance(data, datetime.datetime) and request == "string":
            data = data.strftime('%Y-%m-%d %H:%M:%S')

        return data

    """
    타임존 변경 - UTC, KST 기본은 KST로 변경
    """
    @staticmethod
    def transfer_timezone(data, request=''):
        kst = timezone('Asia/Seoul')
        try:
            # datetime 형식이 아니면 datetime형식으로 변경
            if not isinstance(data, datetime.datetime):
                data = TimeUtil.transfer_time_type(request="datetime", data=data)

            if request == "utc":
                data = utc.localize(data)
            else:  # default = kst로 변환
                data = utc.localize(data).astimezone(kst)

        except Exception as e:
            print(e)
            raise Exception

        return data
