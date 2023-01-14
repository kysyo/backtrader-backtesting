import ccxt
import pandas as pd
import datetime
import time
import sys
import util
from config.common_config import ccxt_config


class CcxtData:

    def __init__(self, request_start_time, request_end_time=None):
        '''
        ccxt 라이브러리를 사용해 바이낸스 코인 시세를 받아오는 메소드
        요청한 시작시간, 종료시간의 차이를 시간타입별로 계산하고
        ccxt 조회제한에 맞춰 자동으로 모든 데이터 저장

        :param request_time_type: 시간타입 (1d, 1m, 1w..) default : 1d
        :param request_start_time: 데이터조회 시작시간
        :param request_end_time: 데이터조회 종료시간 없으면 현재날짜

        저장되는 데이터 형식
        index = time,
        open	high	low	    close	volume
        ex)
        	        open	high	low	    close	volume
        2017-08-17	4261.48	4485.39	4200.74	4285.08	795.150377
        '''

        self.exchange = ccxt.binance()
        self.exchange_rate_limit_time = float(ccxt_config["ccxt_rate_limit_time"])  # ccxt api 조회제한 회피용 대기 시간
        self.symbol = ccxt_config["symbol"]  # 조회할 심볼명
        self.request_time_type = ccxt_config["time_type"]  # 시간타입 (1d, 15m, 1w, 4h..)
        self.ccxt_limit_cnt = ccxt_config["ccxt_limit_cnt"]  # ccxt api 최대 조회제한 갯수 (default 1000개)

        # 수집 시작일과 종료일 datetime 형식으로 변환
        if request_start_time is None:
            raise ValueError("데이터조회 시작시간 시간이 존재해야 합니다")
        else:
            self.request_start_time = util.TimeUtil.transfer_time_type(request="datetime", data=request_start_time)

        # 종료날짜 없으면 현재날짜 +1일로 요청 (ccxt 데이터 처리 기준때문)
        if request_end_time is None:
            self.request_end_time = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            self.request_end_time = util.TimeUtil.transfer_time_type(request="datetime", data=request_end_time)

        self.df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

    def get_ccxt_data(self):

        # 날짜
        start_time = self.request_start_time
        end_time = self.request_end_time

        time_set = self.__get_time_set(start_time=start_time, end_time=end_time)
        time_interval = time_set["time_interval"]
        times = time_set["times"]
        total_cnt = self.__get_total_cnt(time_interval=time_interval)
        current_cnt = 0     # ccxt에서 현재 수집된 갯수
        loop_cnt = 0

        try:
            while True:
                request_limit = self.__get_limit_cnt(current_cnt=current_cnt, total_cnt=total_cnt)

                df = self.__get_coin_data_df(start_time=start_time, request_limit=request_limit,
                                             time_type=self.request_time_type, ticker=self.symbol)
                current_cnt = len(df) + current_cnt
                time.sleep(self.exchange_rate_limit_time)

                # ccxt에 데이터가 없는 경우가 있어 예외처리
                if len(df) == 0:
                    break

                # 시작시간을 수집한 마지막 데이터의 time_type +n 으로 변경
                start_time = (df.iloc[-1]['datetime']) + times
                df.set_index('datetime', inplace=True)
                self.df = pd.concat([self.df, df])

                # 요청한 시작시간 데이터가 ccxt에 없을경우 시작시간 재조정
                # ex) binance거래소의 BTC/USDT 데이터는 2017-08-17부터 시작인데 2017-01-01요청한 경우
                if loop_cnt == 0 and pd.to_datetime(self.df.iloc[0].name) != self.request_start_time:
                    print("[{}] 요청한 시작시간 데이터가 CCXT에 존재하지 않습니다 시작시간 재조정 : {} -> {}"
                          .format(self.symbol, self.request_start_time, self.df.iloc[0].name))
                    time_set = self.__get_time_set(start_time=start_time, end_time=end_time)
                    time_interval = time_set["time_interval"]
                    total_cnt = self.__get_total_cnt(time_interval=time_interval) + current_cnt

                print(f"[{self.request_time_type}] 현재수행 횟수 / 남은횟수 :: {current_cnt} / {total_cnt}")

                if current_cnt >= total_cnt:
                    break

                loop_cnt = loop_cnt + 1

            print("CCXT 데이터 조회 완료 {} ~ {}".format(self.df.iloc[0].name, self.df.iloc[-1].name))
            return self.df

        except Exception as e:
            print(e)

    def __get_time_set(self, start_time, end_time):
        '''
        요청한 시간타입에 따라 +1 씩 추가하는 로직. (1분씩추가, 1시간씩 추가 1일씩추가..)
        ccxt에 조회제한이 넘는 데이터를 요청할때 자동으로 다음 날짜로 변경해서 요청하게 하려고 만듬
        ex) 2020-01-01로 데이터 수집이 마감되었으면 다음요청시 자동으로 2020-01-02를 조회 시작일로 요청
        '''

        request_time = int(self.request_time_type[:-1])  # 1m 1분, 1시간등 요청 시간의 앞자리 숫자
        request_time_type = self.request_time_type[-1]  # m , h, d 등 요청 시간의 타입

        if request_time_type == 'm':
            times = datetime.timedelta(minutes=request_time)
            time_interval = int((end_time - (start_time-times)).total_seconds() / (60 * request_time))
        elif request_time_type == 'h':
            times = datetime.timedelta(hours=request_time)
            time_interval = int((end_time - (start_time-times)).total_seconds() / (3600 * request_time))
        elif request_time_type == 'd':
            times = datetime.timedelta(days=request_time)
            time_interval = int((end_time - (start_time-times)).total_seconds() / (86400 * request_time))
        elif request_time_type == 'w':
            times = datetime.timedelta(weeks=request_time)
            time_interval = int((end_time - (start_time-times)).total_seconds() / (604800 * request_time))
        elif request_time_type == 'M':
            times = datetime.timedelta(weeks=request_time)
            time_interval = int((end_time - (start_time-times)).total_seconds() / (2592000 * request_time))
        else:
            raise ValueError("요청한 time_type이 설정 조건에 없습니다.")

        # 만약 조회해야할 갯수가 음수면 이전시간을 요청한것이므로 그대로 break
        if time_interval < 0:
            print("요청한 end_date보다 현재시간이 더 최신입니다.")
            sys.exit()

        return {"time_interval": time_interval, "times": times}

    def __get_total_cnt(self, time_interval):
        '''
        ccxt에서 조회해야 할 총 갯수 계산

        :param time_interval: 시작일과 종료일의 차이
        :return:
        '''
        limit_cnt = self.ccxt_limit_cnt  # ccxt에서 1회 요청에 받아올 수 있는 데이터 갯수 (ccxt 조회제한)
        remainder_cnt = time_interval % limit_cnt    # 마지막 회차에 조회할 나머지 갯수. (10500이면 1000씩 10번 조회하고 500을 추가조회해야함)
        repeat_cnt = int(time_interval / limit_cnt)  # ccxt 조회횟수
        total_cnt = (limit_cnt * repeat_cnt) + remainder_cnt

        return total_cnt

    def __get_limit_cnt(self, current_cnt, total_cnt):
        '''
        전체갯수와 CCXT에서 받아온 데이터 갯수 비교해서 CCXT 요청 갯수 재조정

        :return: request_limit
        '''

        # 현재 수집갯수가 0개거나 다음 요청에서 수집해야할 갯수가 ccxt api 최대 조회제한 갯수보다 많으면 조회제한 갯수 리턴
        request_limit = self.ccxt_limit_cnt

        # ccxt api 최대 조회제한 갯수보다 적은 갯수를 요청했으면 total_cnt 갯수로만 조회
        if current_cnt == 0 and total_cnt < self.ccxt_limit_cnt:
            request_limit = total_cnt

        # 마지막 회차면 남은 갯수만큼 리턴
        if not (current_cnt == 0 or total_cnt - current_cnt > self.ccxt_limit_cnt):
            request_limit = total_cnt - current_cnt

        return request_limit

    def __get_coin_data_df(self, start_time, request_limit, time_type, ticker):

        try:
            since = util.TimeUtil.transfer_time_type(request="timestamp", data=start_time)
            btc_ohlcv = self.exchange.fetch_ohlcv(symbol=ticker, timeframe=time_type, since=since, limit=request_limit)
            df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])

            if len(btc_ohlcv) == 0:
                print("CCXT에 데이터 없음 요청한 종료일이 현재시간보다 미래거나 CCXT오류 ticker : " + ticker + " since : " + str(since) + " time_type : "+ time_type)

            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            return df

        except ccxt.BaseError as ccxtException:
            print("ccxt exception : " + str(ccxtException))
        except Exception as e:
            print(e)
