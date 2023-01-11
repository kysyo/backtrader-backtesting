import backtrader as bt
import math

# 포지션 크기 조절
class CustomSizer(bt.Sizer):
    params = (('risk', 0.5),)   # 진입시 전체 자산 %

    def _getsizing(self, comminfo, cash, data, isbuy):

        # long / short 구분
        if isbuy == True:
            size = math.floor((cash * self.p.risk) / data[0])
        else:
            size = math.floor((cash * self.p.risk) / data[0]) * -1

        return size