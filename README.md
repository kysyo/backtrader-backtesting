# Backtrader Backtesting
An example of a trading strategy tester using Backtrader

## Installation


```
make init
source venv/bin/activate
```

Installing dependencies
```
make install
```

## Results

![alt text](result/backtesting_result.png "backtesting_result_png")

```
[BTC/USDT] 요청한 시작시간 데이터가 CCXT에 존재하지 않습니다 시작시간 재조정 : 2017-01-01 00:00:00 -> 2017-08-17 00:00:00
[1d] 현재수행 횟수 / 남은횟수 :: 772 / 1963
[1d] 현재수행 횟수 / 남은횟수 :: 1772 / 1963
[1d] 현재수행 횟수 / 남은횟수 :: 1963 / 1963
CCXT 데이터 조회 완료 2017-08-17 00:00:00 ~ 2022-12-31 00:00:00
* 스타트 금액 : 1,000,000 $

MDD : 43.25, CAGR: 29.03, SHARP: 0.79
* 최종 금액 : 7,281,494 $
수익률 :  628.1494641728002 %

```
