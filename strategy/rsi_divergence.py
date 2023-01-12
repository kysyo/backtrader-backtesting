import backtrader as bt
import math

class RsiDivergence(bt.Strategy):
    '''
    현재 종가가 이전 종가보다 낮고 RSI가 설정된 과매수보다 높으면 롱 포지션 진입.
    현재 종가가 이전 종가보다 높고 RSI가 설정된 과매도보다 낮으면 숏 포지션 진입.

    포지션 보유중인데 서로 반대되는 신호 출현시 롱, 숏 같은 비율로 스위칭
    '''
    params = dict(
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
        size_percents=0.5,       # 전체 자산 대비 투입자금 비율
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

    def __is_long(self):
        return True if self.data.close[0] < self.data.close[-1] and self.rsi[0] > self.p.rsi_overbought else False

    def __is_short(self):
        return True if self.data.close[0] > self.data.close[-1] and self.rsi[0] < self.p.rsi_oversold else False

    def next(self):
        # 진입 사이즈 = (보유 전체 자산 * 사이즈 진입비율) / 종가
        size = math.floor((self.broker.getvalue() * self.p.size_percents) / self.datas[0].close)

        # 현재 가진 포지션이 존재하는 경우
        if self.position:
            # long 포지션 -> short 포지션 스위칭
            if self.position.size > 0 and self.__is_short():
                self.close()
                self.sell(data=self.datas[0], price=self.datas[0].open, size=size)

            # short 포지션 -> long 포지션 스위칭
            elif self.position.size < 0 and self.__is_long():
                self.close()
                self.buy(data=self.datas[0], price=self.datas[0].open, size=size)

        # 포지션 없을경우
        else:
            if self.__is_short():
                self.sell(data=self.datas[0], price=self.datas[0].open, size=size)

            elif self.__is_long():
                self.buy(data=self.datas[0], price=self.datas[0].open, size=size)


