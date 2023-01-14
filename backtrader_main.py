import backtrader as bt
import locale
import pandas
import pandas as pd
from tabulate import tabulate
from config.common_config import backtest_confing
import strategy as strategy_list
from strategy import SmaCross, RsiDivergence, LazyBear
from util.sizer import CustomSizer
from data.ccxt_data import CcxtData
from data.influxdb_data import InfluxdbData
import util

def main():

    try:
        cerebro = bt.Cerebro()
        data_type = backtest_confing["data_type"]         # 백테스트 데이터 타입 선택 1: CCXT에서 바로 조회 2: csv 파일사용 3: influxDB 데이터
        strategy = SmaCross                             # 백테스트 할 전략 등록

        # default : 저장된 데이터 쓰지않고 CCXT에서 바로 시세 조회
        if data_type == 2:
            # csv 파일에 저장된 데이터 사용
            csv_file = util.select_csv_file()
            df = pandas.read_csv(csv_file, index_col=0)
            df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
        elif data_type == 3:
            # influxDB에 저장된 데이터 사용
            df = InfluxdbData(start=backtest_confing["start_time"],
                              end=backtest_confing["end_time"]).get_influxdb_data()
        else:
            # ccxt에서 바로 조회
            # 시간형식 : yyyy-MM-dd HH:mm:ss
            # 시간타입 : 1d, 4h, 15m 등
            df = CcxtData(request_start_time=backtest_confing["start_time"],
                          request_end_time=backtest_confing["end_time"]).get_ccxt_data()

        # 데이터 추가
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        # 백테스트 전략
        cerebro.addstrategy(strategy)

        # 초기자금 & 수수료
        cerebro.broker.setcash(backtest_confing["cash"])
        cerebro.broker.setcommission(commission=backtest_confing["commission"])

        # 초기 투자금
        init_cash = cerebro.broker.getvalue()
        locale.setlocale(locale.LC_ALL, 'ko_KR')  # 숫자 3자리마다 콤마 찍게 설정 1000000 -> 1,000,000

        # analyzers 설정
        cerebro.addanalyzer(util.Analyzer, _name='Analyzer')                # 사용자 정의 analyzer
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)     # 샤프지수
        cerebro.addanalyzer(bt.analyzers.Returns)                           # 연평균 수익률
        cerebro.addanalyzer(bt.analyzers.DrawDown)                          # 최대낙폭 (MDD)

        # sizer 설정
        # cerebro.addsizer(util.CustomSizer)

        # run backtest
        cerebro_run = cerebro.run(tradehistory=True)

        # analyzers 결과 출력
        Analyzer = cerebro_run[0].analyzers
        print(tabulate(Analyzer.Analyzer.get_analysis(), headers="keys", floatfmt=".2f", numalign='left', stralign='left', tablefmt='pretty'))

        mdd = Analyzer.drawdown.get_analysis()['max']['drawdown']
        cagr = Analyzer.returns.get_analysis()['rnorm100']
        sharp = Analyzer.sharperatio.get_analysis()['sharperatio']
        if mdd and cagr and sharp:
            print(f"MDD : {mdd:.2f}, CAGR: {cagr:.2f}, SHARP: {sharp:.2f}")

        # 최종 금액 / 수익률 출력
        final_cash = cerebro.broker.getvalue()
        print('* 초기 투자금 : %s $' % locale.format_string('%d', init_cash, grouping=True))
        print('* 백테스트 후 투자금 : %s $' % locale.format_string('%d', final_cash, grouping=True))
        print("수익률 : ", round(float(final_cash - init_cash) / float(init_cash) * 100.0, 2), "%")

        # 백테스팅 결과 csv 파일 생성
        if backtest_confing["save_result_csv"]:
            df = pd.DataFrame(Analyzer.Analyzer.get_analysis())
            util.save_csv_file(df=df)

        # 차트 그리기 설정. 차트종류, 상승봉 색깔 등
        cerebro.plot(style='candlestick', barup="green", bardown="red")

    except bt.BacktraderError as bte:
        print("BackTrader Exception : " + str(bte))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()