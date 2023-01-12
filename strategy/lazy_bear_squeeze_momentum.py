import backtrader as bt
from datetime import datetime, timedelta

'''
@author LazyBear 
https://www.tradingview.com/v/4IneGo8h/

Tradingview에서 좋아요를 가장 많이 받은 지표 백테스트
1. 검은색 십자가에서 -> 회색십자가로 변경되면 진입. (is_volatility 값이 변동성이 커질때 진입)
2. 모멘텀값에 따라 진입 self.val이 0보다 크면 long, 아니면 short
3. 모멘텀이 바뀌면 포지션 종료  
'''

class LazyBear(bt.Strategy):
    params = dict(
        length=20,
        mult=2.0,
        lengthKC=20,
        multKC=1.5,
        size_rate=0.5
    )

    def __init__(self):

        # BB 계산
        self.basis = bt.indicators.SMA(self.datas[0].close, period=self.p.length)
        self.dev = bt.indicators.StdDev(self.datas[0].close, period=self.p.length) * self.p.multKC
        self.upper_bb = self.basis + self.dev
        self.lower_bb = self.basis - self.dev

        # KC 계산
        self.ma = bt.indicators.SMA(self.datas[0].close, period=self.p.lengthKC)
        self.range_1 = bt.indicators.TR(self.datas[0])
        self.rangema = bt.indicators.SMA(self.range_1, period=self.p.lengthKC)
        self.upper_kc = self.ma + (self.rangema * self.p.multKC)
        self.lower_kc = self.ma - (self.rangema * self.p.multKC)
        self.highest_kc = bt.Max(self.datas[0].high[0], self.p.lengthKC)
        self.lowest_kc = bt.Min(self.datas[0].low[0], self.p.lengthKC)

        # Sqz 계산
        self.sqz_on = bt.And(self.lower_bb > self.lower_kc, self.upper_bb < self.upper_kc)
        self.sqz_off = bt.And(self.lower_bb < self.lower_kc, self.upper_bb > self.upper_kc)
        self.no_sqz = bt.And(self.sqz_on == False, self.sqz_off == False)

        # 포지션 사이즈 계산
        self.size = ((self.broker.getvalue() * self.p.size_rate) / self.datas[0].close)

        # 회귀분석
        self.m1 = (self.highest_kc + self.lowest_kc) / 2
        self.val = bt.talib.LINEARREG(self.datas[0].close - ((self.m1 + self.basis) / 2), self.p.lengthKC)

        self.is_volatility = bt.And(self.no_sqz == False, self.sqz_on == False)  # true 변동성이 큼, false 변동성이작음
        self.is_long_cond = self.val > 0                                         # true면 long, false면 short

    def next(self):

        if not self.is_volatility[-1] and self.is_volatility:
            isVolaStart = True
        else:
            isVolaStart = False

        # long 포지션보유중인데 지표가 음수면 포지션 종료
        # short 포지션 보유중인데 지표가 양수면 포지션 종료
        if self.position.size > 0 and self.val < 0:
            self.close()
        elif self.position.size < 0 and self.val > 0:
            self.close()

        # 포지션 없을경우
        if not self.position:
            # long
            # 변동성 증가하며 회귀분석 결과 Long 신호면 진입
            if isVolaStart and self.is_long_cond:
                self.buy(data=self.datas[0], price=self.datas[0].open, size=self.size)
            # short
            # 변동성 증가하며 회귀분석 결과 Short 신호면 진입
            elif isVolaStart and not self.is_long_cond:
                self.sell(data=self.datas[0], price=self.datas[0].open, size=self.size)