backtest_confing =\
    {
        'data_type': 1,                                          # 백테스트 데이터를 어디서 가져올 것인지 선택 1: ccxt에서 바로 조회 2: csv 파일사용 3: influxDB 데이터
        'save_result_csv': True,                                 # 백테스팅 결과를 csv파일로 생성할것인지 여부. True=생성/False=미생성
        'start_time': "2017-01-01 00:00:00",                     # 백테스트 시작시간 (ccxt와 influxDB데이터에서 사용)
        'end_time': "2022-12-31 00:00:00",                       # 백테스트 종료시간 (ccxt와 influxDB데이터에서 사용)
        'cash': 1000000,                                         # 백테스트 초기 자금 설정
        'commission': 0.0004                                     # 백테스트 수수료 설정
    }

ccxt_config =\
    {
        'ccxt_rate_limit_time': 0.2,                             # ccxt api 조회제한 회피용 대기 시간
        'time_type': "1d",                                       # ccxt에서 조회할 시간 타입 1d, 1w, 4h...
        'symbol': "BTC/USDT",                                    # ccxt에서 조회할 심볼
        'ccxt_limit_cnt': 1000,                                  # ccxt api 최대 조회제한 갯수 (default 1000개)
    }