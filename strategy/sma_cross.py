import backtrader as bt
from datetime import datetime, timedelta
import math

class SmaCross(bt.Strategy):
    '''
    단기 이동평균선과 장기 이동평균선의 cross over, under에 따라 포지션 결정하는 전략
    cross over : Long position
    cross under : Short position

    롱 포지션 보유인데 cross under 출현하거나
    숏 포지션 보유인데 cross over 출현하는등 서로 반대되는 신호 출현시 롱, 숏 같은 비율로 스위칭
    '''
    params = dict(
        sma_fast_period=10,     # 단기 sma 기간
        sma_slow_period=30,     # 장기 sma 기간
        size_percents=0.5       # 전체 자산 대비 투입자금 비율
    )

    def __init__(self):
        self.slow_sma = bt.indicators.SMA(self.datas[0], period=self.p.sma_slow_period)
        self.fast_sma = bt.indicators.SMA(self.datas[0], period=self.p.sma_fast_period)

        # 0보다 크면 cross over, 작으면 cross under
        self.cross = bt.ind.CrossOver(self.fast_sma, self.slow_sma)

    def next(self):
        # 진입 사이즈 = (보유 전체 자산 * 사이즈 진입비율) / 종가
        size = math.floor((self.broker.getvalue() * self.p.size_percents) / self.datas[0].close)

        # 현재 가진 포지션이 존재하는 경우
        if self.position:
            # long 포지션 -> short 포지션 스위칭
            if self.position.size > 0 and self.cross < 0:
                self.close()
                self.sell(data=self.datas[0], price=self.datas[0].open, size=size)

            # short 포지션 -> long 포지션 스위칭
            elif self.position.size < 0 and self.cross > 0:
                self.close()
                self.buy(data=self.datas[0], price=self.datas[0].open, size=size)

        # 포지션 없을경우
        else:
            if self.cross > 0:
                self.buy(data=self.datas[0], price=self.datas[0].open, size=size)

            elif self.cross < 0:
                self.sell(data=self.datas[0], price=self.datas[0].open, size=size)