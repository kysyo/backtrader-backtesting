import backtrader as bt
import math

# 포지션 크기 조절
class CustomSizer(bt.Sizer):
    params = (('risk', 0.5),)   # 진입시 전체 자산 %

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if not position:
            # long / short 구분
            if isbuy == True:
                size = round((cash * self.p.risk) / data[0], 2)
            else:
                size = round((cash * self.p.risk) / data[0], 2) * -1
        else:
            size = position.size

        return size