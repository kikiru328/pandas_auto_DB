"""
Add delivery date into uniformed table
Returns:
    .xlsx : uniformed for basic table with delivery date
"""
import pandas as pd
import numpy as np
import requests
import datetime as dt
import json
from pandas import json_normalize

def read_uniformed_dataframe(unify_form_path):
    d_f = pd.read_excel(unify_form_path)
    return d_f


def holiday_df(holiday_json_path,custom_holiday):
    with open(holiday_json_path, 'r') as api_key:
        key = json.load(api_key)
    api_key = key['holiday_api_key']

    today_year = dt.datetime.today().year
    key = api_key
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=50&solYear=' + str(today_year) + '&ServiceKey=' + str(key)
    response = requests.get(url)
    if response.status_code == 200:
        json_ob = json.loads(response.text)
        holidays_data = json_ob['response']['body']['items']['item']
        dataframe = json_normalize(holidays_data)
        
    def change_date(x):
        hx = dt.datetime.strptime(str(x), '%Y%m%d')
        hx = hx.strftime('%Y-%m-%d-%A')
        return hx 
    
    dataframe['locdate'] = dataframe['locdate'].apply(lambda x : change_date(x))
    dataframe = dataframe.drop(columns=["dateKind","isHoliday","seq"])
    
    def custom_change_date(x):
        hx = x.strftime('%Y-%m-%d-%A')
        return hx
    
    custom_delivery_schedule = pd.read_excel(custom_holiday)
    custom_delivery_schedule['locdate'] = custom_delivery_schedule['locdate'].apply(lambda x : custom_change_date(x))
    dataframe = pd.concat([dataframe, custom_delivery_schedule],axis=0,ignore_index=True)
    dataframe = dataframe.sort_values('locdate')
    return dataframe

class get_delivery_start_date_each:
    
    def get_dawn_delivery_start_date(pay_time, holiday_dataframe):
        """
        True : 17시 이후 > 다음 요일 배송 시스템으로 적용
        False : 17시 이전 > 현재 요일 배송 시스템으로 적용

        Args:
            check_time: datetime timestamp
            holiday_dataframe: holiday dataframe
        Returns:
            _type_: bool. True/False
        """
        day = pay_time.weekday()      
        dawn_holiday_query_str = "dateName == ['설날', '추석', '영업휴일']"
        holiday_list = holiday_dataframe.query(dawn_holiday_query_str).locdate.to_list() # 설날 / 추석 연휴 (대체공휴일 제외)
        
        def mon_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  #이번주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 월요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 수요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A') # 이번주 목요일
                if delivery_start not in holiday_list: pass
                else:
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 화요일
                        
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 목요일    
                        i += 1
            return delivery_start
                    
                
        def tue_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  # 이번주 목요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:  delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 화요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 목요일    
                        
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A') # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else:
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 수요일
                            
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            
            return delivery_start                 
                
                
        def wed_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break                    
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일                                
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            
            return delivery_start    


        def thu_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break                    
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일                                
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                                
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            
            return delivery_start  
        
                    
        def fri_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break                    
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일                                
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            
            return delivery_start  
        
                        
        def sat_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            
            return delivery_start  

                            
        def sun_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: 
                            if i ==0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                        i += 1
            
            return delivery_start                                               

        
        if day == 0:
            return mon_payment(pay_time, holiday_list)
        elif day == 1:
            return tue_payment(pay_time, holiday_list)
        elif day == 2:
            return wed_payment(pay_time, holiday_list)
        elif day == 3:
            return thu_payment(pay_time, holiday_list)
        elif day == 4:
            return fri_payment(pay_time, holiday_list)
        elif day == 5:
            return sat_payment(pay_time, holiday_list)
        elif day == 6:
            return sun_payment(pay_time, holiday_list)
        
        
    def get_normal_delivery_start_date(pay_time, holiday_dataframe):
        """
        True : 17시 이후 > 다음 요일 배송 시스템으로 적용
        False : 17시 이전 > 현재 요일 배송 시스템으로 적용

        Args:
            check_time: datetime timestamp
            holiday_dataframe: holiday datafram
        Returns:
            _type_: bool. True/False
        """
        day = pay_time.weekday()
        holiday_list = holiday_dataframe.locdate.to_list() # 전체
        
        def add_list(holiday_list):
            add_ = []
            for holiday in holiday_list:
                # print(holiday)
                holiday = dt.datetime.strptime(holiday, '%Y-%m-%d-%A')
                # print(holiday)
                holiday_1 = (holiday + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                add_.append(holiday_1)
            add_holiday_list = sorted(list(set(holiday_list + add_)))    
            return add_holiday_list

        holiday_list = add_list(holiday_list) # 전체 + 전체_+1일 
        
        
        # day_deliv 
        def mon_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  # 이번주 목요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 화요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 목요일                   
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  # 이번주 목요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 화요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 목요일    
                        i += 1
            return delivery_start   
                    
                
        def tue_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  # 이번주 목요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 화요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 목요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else:
                                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일
                        i += 1
            return delivery_start                     
                
                
        def wed_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일
                            
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            return delivery_start    


        def thu_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일
                            
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            return delivery_start  
        
                    
        def fri_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일
                            
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            return delivery_start  
        
                        
        def sat_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일
                            
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
            return delivery_start  

                            
        def sun_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 화요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 목요일

                        if delivery_start not in holiday_list: break
                        
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 화요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 목요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: 
                            if i == 0 :
                                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') # 다다음주 화요일
                            else:
                                delivery_start = (pay_time + dt.timedelta(days=1-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') # 다다음주 화요일    
                        if delivery_start not in holiday_list: break                    
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 목요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=3-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 목요일    
                        i += 1
            return delivery_start                                                 

        
        if day == 0:
            return mon_payment(pay_time, holiday_list)
        elif day == 1:
            return tue_payment(pay_time, holiday_list)
        elif day == 2:
            return wed_payment(pay_time, holiday_list)
        elif day == 3:
            return thu_payment(pay_time, holiday_list)
        elif day == 4:
            return fri_payment(pay_time, holiday_list)
        elif day == 5:
            return sat_payment(pay_time, holiday_list)
        elif day == 6:
            return sun_payment(pay_time, holiday_list)
        
        
    def get_direct_delivery_start_date(pay_time, holiday_dataframe):
        """
        True : 17시 이후 > 다음 요일 배송 시스템으로 적용
        False : 17시 이전 > 현재 요일 배송 시스템으로 적용

        Args:
            check_time: datetime timestamp
            holiday_dataframe: holiday datafram
        Returns:
            _type_: bool. True/False
        """
        day = pay_time.weekday()
        holiday_list = holiday_dataframe.locdate.to_list() # 전체
        
        def add_list(holiday_list):
            add_ = []
            for holiday in holiday_list:
                # print(holiday)
                holiday = dt.datetime.strptime(holiday, '%Y-%m-%d-%A')
                # print(holiday)
                holiday_1 = (holiday + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                add_.append(holiday_1)
            add_holiday_list = sorted(list(set(holiday_list + add_)))    
            return add_holiday_list

        holiday_list = add_list(holiday_list) # 전체 + 전체_+1일 

        # day_deliv 
        def mon_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=0)).strftime('%Y-%m-%d-%A')  # 이번주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 월요일

                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') #다음주 수요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A') # 다음주 수요일                        
                        
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            return delivery_start    
                    
                
        def tue_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:  delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            return delivery_start                 
                
                
        def wed_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:  delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            return delivery_start 


        def thu_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:  delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            return delivery_start 
        
                    
        def fri_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else:  delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list:  pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
            return delivery_start 
        
                        
        def sat_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 월요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+1)).strftime('%Y-%m-%d-%A') # 다음주 수요일

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 월요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: 
                            if i == 0: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일    

                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 수요일  
                        i += 1
            return delivery_start    

                            
        def sun_payment(pay_time, holiday_list):
            after5 = dt.datetime(pay_time.year, pay_time.month, pay_time.day, 17, 5, 0)
            if pay_time < after5: 
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: 
                            if i == 0: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                                
                        if delivery_start not in holiday_list: break
                        else:
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                        i += 1
                                
            else: # 5시 이후 결제
                delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=1)).strftime('%Y-%m-%d-%A')  # 다음주 수요일
                if delivery_start not in holiday_list: pass
                else: # 공휴일일 경우
                    i = 0
                    while True: 
                        if delivery_start not in holiday_list: break
                        else: 
                            if i == 0: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                            else: delivery_start = (pay_time + dt.timedelta(days=0-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') # 다다음주 월요일
                                
                        if delivery_start not in holiday_list:  break
                        else:                        
                            if i == 0 : delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=2)).strftime('%Y-%m-%d-%A') #다다음주 수요일    
                            else: delivery_start = (pay_time + dt.timedelta(days=2-pay_time.weekday(), weeks=i+2)).strftime('%Y-%m-%d-%A') #다다음주 수요일
                        i += 1
            return delivery_start                                                  

        
        if day == 0:
            return mon_payment(pay_time, holiday_list)
        elif day == 1:
            return tue_payment(pay_time, holiday_list)
        elif day == 2:
            return wed_payment(pay_time, holiday_list)
        elif day == 3:
            return thu_payment(pay_time, holiday_list)
        elif day == 4:
            return fri_payment(pay_time, holiday_list)
        elif day == 5:
            return sat_payment(pay_time, holiday_list)
        elif day == 6:
            return sun_payment(pay_time, holiday_list)
        
        
    def get_deliv_start_date(d_f,holiday_dataframe):
        for pay_day, deliv_selection in zip(d_f.결제일.to_list(), d_f['배송방법 고객선택'].to_list()):
            if deliv_selection == '새벽배송':
                delivery_start = get_delivery_start_date_each.get_dawn_delivery_start_date(pay_day, holiday_dataframe)
                for index in d_f[d_f['결제일']==pay_day].index:
                    d_f.loc[index, '배송시작일'] = delivery_start
            elif deliv_selection == '일반배송':
                delivery_start = get_delivery_start_date_each.get_normal_delivery_start_date(pay_day, holiday_dataframe)
                for index in d_f[d_f['결제일']==pay_day].index:
                    d_f.loc[index, '배송시작일'] = delivery_start
            elif deliv_selection == '직접배송':
                delivery_start = get_delivery_start_date_each.get_direct_delivery_start_date(pay_day, holiday_dataframe)
                for index in d_f[d_f['결제일']==pay_day].index:
                    d_f.loc[index, '배송시작일'] = delivery_start
        return d_f


class get_delivery_schedule:
    
    def get_direct_delivery_schedule(product, deliv_start, holiday_dataframe):
        holiday_list = holiday_dataframe.locdate.to_list() # 대체공휴일 포함 
        def add_list(holiday_list):
            add_ = []
            for holiday in holiday_list:
                # print(holiday)
                holiday = dt.datetime.strptime(holiday, '%Y-%m-%d-%A')
                # print(holiday)
                holiday_1 = (holiday + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                add_.append(holiday_1)
            add_holiday_list = sorted(list(set(holiday_list + add_)))    
            return add_holiday_list

        holiday_list = add_list(holiday_list) # 전체 + 전체_+1일 
        deliv_list = []
        deliv_start = dt.datetime.strptime(deliv_start, '%Y-%m-%d-%A')

        if product == '[윤식단][정기] 1일 2식 1일':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A')) # Add delivery start date
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
            
        elif product == '[윤식단][단품] 닭고야/어니스트':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A')) # Add delivery start date
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                    
        else:
            days = int(product[-3:-1])
            i = 0
            while len(deliv_list) < days: # Condition 
                if len(deliv_list) == 0: # For start
                    deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A'))  # Append delivery start days
                    
                    if deliv_start.weekday() == 0: # if monday start
                        add_day = (deliv_start + dt.timedelta(days=2-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # this week wednesday delivery 
                        
                        if add_day in holiday_list:
                            i += 1 # Pass
                        else:
                            deliv_list.append(add_day) # add Wednesday
                            i += 1
                            
                    else: # not start on tuesday
                        i += 1
                        
                else: # start on Wednesday
                    add_day = (deliv_start + dt.timedelta(days=0-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # next week monday delivery
                    if add_day in holiday_list:
                        pass
                    else:
                        deliv_list.append(add_day) # add monday
                        
                    if len(deliv_list) == days:  # Break while loop
                        break
                    
                    add_day = (deliv_start + dt.timedelta(days=2-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # next week wednesday delivery
                    if add_day in holiday_list:
                        i += 1
                    else:
                        deliv_list.append(add_day) # add thursday
                        i += 1          
            last_deliv_day = deliv_list[-1]
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
        return deliv_list, last_deliv_day, end_subs_day


    def get_normal_delivery_schedule(product, deliv_start, holiday_dataframe):
        holiday_list = holiday_dataframe.locdate.to_list() # 대체공휴일 포함 
        def add_list(holiday_list):
            add_ = []
            for holiday in holiday_list:
                # print(holiday)
                holiday = dt.datetime.strptime(holiday, '%Y-%m-%d-%A')
                # print(holiday)
                holiday_1 = (holiday + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                add_.append(holiday_1)
            add_holiday_list = sorted(list(set(holiday_list + add_)))    
            return add_holiday_list

        holiday_list = add_list(holiday_list) # 전체 + 전체_+1일 
        deliv_list = []
        deliv_start = dt.datetime.strptime(deliv_start, '%Y-%m-%d-%A')

        if product == '[윤식단][정기] 1일 2식 1일':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A')) # Add delivery start date
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
            
        elif product == '[윤식단][단품] 닭고야/어니스트':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A')) # Add delivery start date
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')        
        else:
            days = int(product[-3:-1])
            i = 0
            while len(deliv_list) < days: # Condition 
                if len(deliv_list) == 0: # For start
                    deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A'))  # Append delivery start days
                    if deliv_start.weekday() == 1: # if tuesday start
                        add_day = (deliv_start + dt.timedelta(days=3-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # this week thursday delivery 
                        if add_day in holiday_list:
                            i += 1 # Pass
                        else:
                            deliv_list.append(add_day) # add thursday
                            i += 1
                    else: # not start on tuesday
                        i += 1
                        
                else: # start on Thursday
                    add_day = (deliv_start + dt.timedelta(days=1-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # next week tuesday delivery
                    # print(add_day)
                    if add_day in holiday_list:
                        pass
                    else:
                        deliv_list.append(add_day) # add tuesday
                        
                    if len(deliv_list) == days:  # Break while loop
                        break
                    
                    add_day = (deliv_start + dt.timedelta(days=3-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A') # next week thursday delivery
                    if add_day in holiday_list:
                        i += 1
                    else:
                        deliv_list.append(add_day) # add thursday
                        i += 1          
                        
            last_deliv_day = deliv_list[-1]
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
        return deliv_list, last_deliv_day, end_subs_day    


    def get_dawn_delivery_schedule(product, deliv_start,holiday_dataframe):    
        dawn_holiday_query_str = "dateName == ['설날', '추석', '영업휴일']"
        holiday_list = holiday_dataframe.query(dawn_holiday_query_str).locdate.to_list() # 설날 / 추석 연휴 (대체공휴일 제외)
        deliv_list = []
        deliv_start = dt.datetime.strptime(deliv_start, '%Y-%m-%d-%A')
        
        if product == '[윤식단][정기] 1일 2식 1일':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A'))
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
        elif product == '[윤식단][단품] 닭고야/어니스트':
            deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A')) # Add delivery start date
            last_deliv_day = deliv_start.strftime('%Y-%m-%d-%A')
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')        
        else:
            days = int(product[-3:-1])
            i = 0
            while len(deliv_list) < days:
                if len(deliv_list) == 0:
                    deliv_list.append(deliv_start.strftime('%Y-%m-%d-%A'))  # Append delivery start days
                    if deliv_start.weekday() == 0: # if monday starts 
                        add_day = (deliv_start + dt.timedelta(days=2-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        if add_day in holiday_list:
                            i += 1 # Pass
                        else:
                            deliv_list.append(add_day) # add Wednesday
                            i += 1
                        
                    elif deliv_start.weekday() == 1: # if tuesday starts
                        add_day = (deliv_start + dt.timedelta(days=3-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        if add_day in holiday_list:
                            i += 1 # Pass
                        else:
                            deliv_list.append(add_day) # add Thursday
                            i += 1
                            
                    else: # not start on monday and tuesday (on wendesday, thuresday)
                        i += 1
                        
                else:
                    if (deliv_start.weekday() == 0) or (deliv_start.weekday() == 2):
                        add_day = (deliv_start + dt.timedelta(days=0-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        # print(add_day)
                        if add_day in holiday_list:
                            pass
                        else:
                            deliv_list.append(add_day) # add Monday

                        if len(deliv_list) == days:  # Break while loop
                            break
                        
                        add_day = (deliv_start + dt.timedelta(days=2-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        if add_day in holiday_list:
                            i += 1
                        else:
                            deliv_list.append(add_day) # add Wednesday
                            i += 1
                        
                    elif (deliv_start.weekday() == 1) or (deliv_start.weekday() == 3):
                        add_day = (deliv_start + dt.timedelta(days=1-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        if add_day in holiday_list:
                            pass
                        else:
                            deliv_list.append(add_day) # add Tuesday
                        if len(deliv_list) == days:  # Break while loop
                            break
                        
                        add_day = (deliv_start + dt.timedelta(days=3-deliv_start.weekday(), weeks=i)).strftime('%Y-%m-%d-%A')
                        if add_day in holiday_list:
                            i += 1
                        else:
                            deliv_list.append(add_day) # add Thursday
                            i += 1               
                        
            last_deliv_day = deliv_list[-1]
            last_deliv_day_timstamp = dt.datetime.strptime(last_deliv_day, '%Y-%m-%d-%A')
            end_subs_day = (last_deliv_day_timstamp + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
        return deliv_list, last_deliv_day, end_subs_day


    def get_total_delivery_schedule(d_f,holiday_json_path, custom_holiday):
        
        holiday_dataframe = holiday_df(holiday_json_path, custom_holiday)
        d_f = get_delivery_start_date_each.get_deliv_start_date(d_f,holiday_dataframe)
        for order_id, product, deliv_start, deliv_selection in zip(d_f.주문번호, d_f.상품명, d_f.배송시작일, d_f['배송방법 고객선택']):
            for index in d_f[(d_f['주문번호']==order_id) & (d_f['상품명']==product)].index:
                if deliv_selection == '새벽배송':
                    deliv_list, last_deliv_day, end_subs_day = get_delivery_schedule.get_dawn_delivery_schedule(product, deliv_start, holiday_dataframe)    
                elif deliv_selection == '일반배송':
                    deliv_list, last_deliv_day, end_subs_day = get_delivery_schedule.get_normal_delivery_schedule(product, deliv_start, holiday_dataframe)    
                elif deliv_selection == '직접배송':
                    deliv_list, last_deliv_day, end_subs_day = get_delivery_schedule.get_direct_delivery_schedule(product, deliv_start, holiday_dataframe)    
                d_f.at[index, '배송일자리스트'] = str(deliv_list)
                d_f.loc[index, '마지막배송일'] = last_deliv_day
                d_f.loc[index, '식단종료일'] = end_subs_day                
        return d_f


class get_schedule:
        
    def get_direct_normal_delivery_holiday(holiday_dataframe):
        import datetime as dt
        import pandas as pd
        holiday_list = holiday_dataframe.locdate.to_list() # 대체공휴일 포함 
        def add_list(holiday_list):
            add_ = []
            for holiday in holiday_list:
                holiday = dt.datetime.strptime(holiday, '%Y-%m-%d-%A')
                holiday_1 = (holiday + dt.timedelta(days=1)).strftime('%Y-%m-%d-%A')
                add_.append(holiday_1)
            add_holiday_list = holiday_list + add_    
            return add_holiday_list
        holiday_list = list(add_list(holiday_list))

        df = pd.DataFrame(columns = holiday_dataframe.columns)
        for i, date in enumerate(sorted(holiday_list)):
            if i == 0 :
                df = holiday_dataframe[holiday_dataframe['locdate']==date]
            else:               
                if len(holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list()) > 1:
                    datename = ''
                    for i in range(0,len(holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list())):
                        datename = datename + holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list()[i] +','
                    datename = datename[:-1]
                    index_ = holiday_dataframe[holiday_dataframe['locdate']==date].index[0]
                    add_df = holiday_dataframe[holiday_dataframe['locdate']==date].loc[[index_]]
                    add_df['dateName'] = datename
                    df = pd.concat([df,add_df],axis=0, ignore_index=True)
                elif len(holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list()) == 0:
                    temp_df = pd.DataFrame({'dateName':'배송사휴일','locdate':date}, index=[0])
                    df = pd.concat([df,temp_df],axis=0, ignore_index=True)
                else: # 1개
                    df = pd.concat([df, holiday_dataframe[holiday_dataframe['locdate']==date]],axis=0, ignore_index=True)            
                    if len(df[df['locdate']==date]) > 1:
                        for i in range(0, len(df[df['locdate']==date].dateName.to_list())):
                            datename = df[df['locdate']==date].dateName.to_list()[i] + ',' + '배송사휴일'
                        index_ = df[df['locdate']==date].index[0]
                        drop_index_ = df[df['locdate']==date].index[1]
                        add_df = df[df['locdate']==date].loc[[index_]]
                        add_df['dateName'] = datename
                        df = pd.concat([df,add_df],axis=0, ignore_index=True)
        df = df.sort_values('locdate').reset_index(drop=True)
        df = df.drop_duplicates(subset='locdate', keep='last', ignore_index=True)
        df_copy = df.copy()
        return df, df_copy


    def get_dawn_delivery_holiday(holiday_dataframe):
        import datetime as dt
        import pandas as pd
        dawn_holiday_query_str = "dateName == ['설날', '추석', '영업휴일']"
        holiday_list = list(set(holiday_dataframe.query(dawn_holiday_query_str).locdate.to_list())) # 설날 / 추석 연휴 (대체공휴일 제외)
        df = pd.DataFrame(columns = holiday_dataframe.columns)
        for i, date in enumerate(sorted(holiday_list)):
            if i == 0 :
                df = holiday_dataframe[holiday_dataframe['locdate']==date]
            else:
                if len(holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list()) != 1:
                    datename = ''
                    for i in range(0,len(holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list())):
                        datename = datename + holiday_dataframe[holiday_dataframe['locdate']==date].dateName.to_list()[i] +','
                    datename = datename[:-1]
                    index_ = holiday_dataframe[holiday_dataframe['locdate']==date].index[0]
                    add_df = holiday_dataframe[holiday_dataframe['locdate']==date].loc[[index_]]
                    add_df['dateName'] = datename
                    df = pd.concat([df,add_df],axis=0, ignore_index=True)
                else:
                    df = pd.concat([df, holiday_dataframe[holiday_dataframe['locdate']==date]],axis=0, ignore_index=True)
        df = df.sort_values('locdate').reset_index(drop=True)
        return df
    
    def get_delivery_schedule_each(holiday_json_path, custom_holiday_path):
        holiday_dataframe = holiday_df(holiday_json_path,custom_holiday_path)
        direct, normal = get_schedule.get_direct_normal_delivery_holiday(holiday_dataframe)
        dawn = get_schedule.get_dawn_delivery_holiday(holiday_dataframe)
        return direct,normal,dawn
    