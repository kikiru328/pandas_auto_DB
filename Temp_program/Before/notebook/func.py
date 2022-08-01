global pd
import pandas as pd

######   #######   #####   ######            ##  ###   #####   ### ###  #######  ######   
### ###  ### ###  ### ###  ### ###           ### ###  ### ###  ### ###  ### ###  ### ###  
### ###  ###      ### ###  ### ###           #######  ### ###  ### ###  ###      ### ###  
######   #####    #######  ### ###           #######  #######  ### ###  #####    ######   
### ##   ###      ### ###  ### ###           ### ###  ### ###  ### ###  ###      ### ##   
### ###  ### ###  ### ###  ### ###           ### ###  ### ###   #####   ### ###  ### ###  
### ###  #######  ### ###  ######            ### ###  ### ###    ###    #######  ### ###  
                                                                                          

def read_naver_table(path):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    df = pd.read_excel(path,header=1)
    need_columns = ['상품주문번호','주문번호','배송방법(구매자 요청)','배송방법','택배사','송장번호','발송일','구매자명','수취인명','상품명','상품종류','옵션정보','수량','옵션가격','상품가격','상품별 총 주문금액','배송지','구매자연락처','배송메세지','정산예정금액','수취인연락처1','배송속성','배송희망일','결제일','구매자ID','우편번호']
    columns = df.columns.to_list()
    drop_columns = [x for x in columns if x not in need_columns]
    df = df.drop(drop_columns, axis=1)
    return df


 #####    #####   ###               ######   #######  ##  ###   #####   ##   ##  #######  
### ###  ### ###  ###               ### ###  ### ###  ### ###  ### ###  ### ###  ### ###  
###      ### ###  ###               ### ###  ###      #######  ### ###  #######  ###      
###      ### ###  ###               ######   #####    #######  #######  #######  #####    
###      ### ###  ###               ### ##   ###      ### ###  ### ###  ### ###  ###      
### ###  ### ###  ###  ##           ### ###  ### ###  ### ###  ### ###  ### ###  ### ###  
 #####    #####   #######           ### ###  #######  ### ###  ### ###  ### ###  #######  
                                                                                          

def col_rename(df):
    df['상품종류'] = ''
    df = df['품목주문번호,주문번호,주문자명,수취인명,상품명,상품종류,옵션정보,수량,주소,주문자 연락처,배송메세지,수취인 연락처,주문자 E-Mail,우편번호'.split(',')]
    df = df.rename(columns = {
        '주문번호' : '주문번호',
        '품목주문번호' : '상품주문번호',
        '주문자명' : '구매자명',
        '수취인명' : '수취인명',
        '상품명':'상품명',
        '상품종류':'상품종류',
        '옵션정보':'옵션정보',
        '수량':'수량',
        '주소':'배송지',
        '주문자 연락처':'구매자연락처',
        '배송메세지':'배송메세지',
        '수취인 연락처':'수취인연락처1',
        '주문자 E-Mail':'구매자ID',
        '우편번호':'우편번호'
        }
    )
    
    return df

##  ###  ### ###  ##   ##  ######             #####   ### ###   #####   ##  ###   #####   #######  
### ###  ### ###  ### ###  ### ###           ### ###  ### ###  ### ###  ### ###  ###  ##  ### ###  
#######  ### ###  #######  ### ###           ###      ### ###  ### ###  #######  ###      ###      
#######  ### ###  #######  ######            ###      #######  #######  #######  ### ###  #####    
### ###  ### ###  ### ###  ### ###           ###      ### ###  ### ###  ### ###  ###  ##  ###      
### ###  ### ###  ### ###  ### ###           ### ###  ### ###  ### ###  ### ###  ###  ##  ### ###  
### ###   #####   ### ###  ######             #####   ### ###  ### ###  ### ###   #####   #######  
                                                                                                   

def numbers_change(df):
    
    def numbers(x):
        x = str(x)
        if x.startswith('1') == True:
            return '0' + str(x)[:2] + '-' + str(x)[2:6] + '-' + str(x)[6:]
        else: 
            return '0' + str(x)[:3] + '-' + str(x)[3:7] + '-' + str(x)[7:]
    
    df['구매자연락처'] = df['구매자연락처'].apply(lambda x : numbers(x))
    df['수취인연락처1'] = df['수취인연락처1'].apply(lambda x : numbers(x))
    return df


 #####    ######  ######    ######  ######             #####    #####   ### ###  ##  ###   ######  
###  ##   # ## #  ### ###     ##    ### ###           ### ###  ### ###  ### ###  ### ###   # ## #  
###         ##    ### ###     ##    ### ###           ###      ### ###  ### ###  #######     ##    
 #####      ##    ######      ##    ######            ###      ### ###  ### ###  #######     ##    
     ##     ##    ### ##      ##    ###               ###      ### ###  ### ###  ### ###     ##    
###  ##     ##    ### ###     ##    ###               ### ###  ### ###  ### ###  ### ###     ##    
 #####      ##    ### ###   ######  ###                #####    #####    #####   ### ###     ##    
                                                                                                   

def strip_count(df):
    
    def count(x):
        x = x[:-5]
        return x
    
    df['옵션정보'] = df['옵션정보'].apply(lambda x : count(x))
    return df    





 #####   ### ###           ######    ######  #######   ######            #####   ######   ###       ######   ######  
### ###  ### ###           ### ###     ##    ### ###   # ## #           ###  ##  ### ###  ###         ##     # ## #  
###      ### ###           ### ###     ##    ###         ##             ###      ### ###  ###         ##       ##    
###      ### ###           ### ###     ##    #####       ##              #####   ######   ###         ##       ##    
###      ### ###           ### ###     ##    ###         ##                  ##  ###      ###         ##       ##    
### ###  ### ###           ### ###     ##    ### ###     ##             ###  ##  ###      ###  ##     ##       ##    
 #####    #####            ######    ######  #######     ##              #####   ###      #######   ######     ##    
                                                                                                                     

def curation_diet_split(df):
    def diet_change(x):
        if ' / 하루 식단 수 : ' in x:
            x_ = x.split(' / 하루 식단 수 : ')[0]
            y = x.split(' / 하루 식단 수 : ')[1]
            y = y.replace(' ','')
            return x_ + ' / 하루 식단 수 : ' +  y
        else:
            return x
    df['옵션정보'] = df['옵션정보'].apply(lambda x : diet_change(x))    
    return df

 #####   ### ###           ### ###  ##  ###   #####             #####   ######   ###       ######   ######  
### ###  ### ###           ### ###  ### ###  ### ###           ###  ##  ### ###  ###         ##     # ## #  
###      ### ###           ### ###  #######  ### ###           ###      ### ###  ###         ##       ##    
###      ### ###           ### ###  #######  ### ###            #####   ######   ###         ##       ##    
###      ### ###           ### ###  ### ###  ### ###                ##  ###      ###         ##       ##    
### ###  ### ###           ### ###  ### ###   #####            ###  ##  ###      ###  ##     ##       ##    
 #####    #####             #####   ### ###      ###            #####   ###      #######   ######     ##    
                                                                                                            

def curation_unique_split(df):
    def unique_product_split(x):
        if x == '[Original line]   1일 2식 10일 프로그램':
            return '[Original line] 1일 2식 10일 프로그램'
        else:
            return x
    df['상품명'] = df['상품명'].apply(lambda x : unique_product_split(x))
    return df
    

 #####   ### ###           ######    ######  #######   ######            #####   ##  ###   ######  
### ###  ### ###           ### ###     ##    ### ###   # ## #           ### ###  ### ###   # ## #  
###      ### ###           ### ###     ##    ###         ##             ###      #######     ##    
###      ### ###           ### ###     ##    #####       ##             ###      #######     ##    
###      ### ###           ### ###     ##    ###         ##             ###      ### ###     ##    
### ###  ### ###           ### ###     ##    ### ###     ##             ### ###  ### ###     ##    
 #####    #####            ######    ######  #######     ##              #####   ### ###     ##    
                                                                                                   
    
def curation_diet_count(df):
    df['Temp'] = ''
    for index_, counts in enumerate(df['옵션정보'].to_list()):
        if ' / 하루 식단 수 ' in counts:
            diet_day = counts.split(' / 하루 식단 수 : ')[1].split('일')[0]+'일'
            diet_count = counts.split(' / 하루 식단 수 : ')[1].split('일')[1]
            options = counts.split(' / 하루 식단 수 : ')[0]
            diet_option = diet_day + ' ' + diet_count
            df.loc[index_,'Temp'] = diet_option
            df.loc[index_,'옵션정보'] = options
        else:
            df.loc[index_,'Temp'] = 'x'

    return df


 #####   ### ###            ######   #####    ######   #####   ###                #####   ######    ######           
### ###  ### ###            # ## #  ### ###   # ## #  ### ###  ###               ### ###  ### ###   # ## #           
###      ### ###              ##    ### ###     ##    ### ###  ###               ### ###  ### ###     ##             
###      ### ###              ##    ### ###     ##    #######  ###               ### ###  ######      ##             
###      ### ###              ##    ### ###     ##    ### ###  ###               ### ###  ###         ##             
### ###  ### ###              ##    ### ###     ##    ### ###  ###  ##           ### ###  ###         ##             
 #####    #####               ##     #####      ##    ### ###  #######            #####   ###         ##             
                                                                                                                     
                                                                                                                          
        
def curation_total_option_split(df):
    df['temp2'] = ''
    df['temp3'] = ''
    for index_, products_name in enumerate(df['상품명'].to_list()):
        if '(탄수화물' in products_name:
            product_split_program = products_name.split('프로그램 ')[0].split('[Original line] ')[1] + '프로그램'
            product_name = '[Original line] ' + df.loc[index_,'Temp'] + ' ' + product_split_program 
            df.loc[index_,'상품명'] = product_name        
            product_option_carbon = products_name.split('프로그램 ')[1].split('/')[0].replace('(','')
            product_option_protein = products_name.split('프로그램 ')[1].split('/')[1].replace(')','')
            df.loc[index_, 'temp2'] = product_option_carbon
            df.loc[index_, 'temp3'] = product_option_protein
        else:   
            df.loc[index_, 'temp2'] = 'x'
            df.loc[index_, 'temp3'] = 'x'
    return df
            
            
            
         
######   ###       ######  ### ###            #####   ######   ###       ######   ######  
### ###  ###         ##    ### ###           ###  ##  ### ###  ###         ##     # ## #  
### ###  ###         ##    ### ###           ###      ### ###  ###         ##       ##    
### ###  ###         ##    ### ###            #####   ######   ###         ##       ##    
### ###  ###         ##    ### ###                ##  ###      ###         ##       ##    
### ###  ###  ##     ##     #####            ###  ##  ###      ###  ##     ##       ##    
######   #######   ######    ###              #####   ###      #######   ######     ##    
                     
                     
                                                                                          
def delivery_split(df):
    def split_delivery(x):
        if "공동현관 비밀번호(없을시'없음'작성)" in x:
            return x.replace("공동현관 비밀번호(없을시'없음'작성)","공동현관 출입비밀번호 (없을 시 '없음'작성)")
        else:
            return x
    df['옵션정보'] = df['옵션정보'].apply(lambda x : split_delivery(x))
    return df
    




 #####   ######    ######   ######   #####   ##  ###   #####   
### ###  ### ###   # ## #     ##    ### ###  ### ###  ###  ##  
### ###  ### ###     ##       ##    ### ###  #######  ###      
### ###  ######      ##       ##    ### ###  #######   #####   
### ###  ###         ##       ##    ### ###  ### ###       ##  
### ###  ###         ##       ##    ### ###  ### ###  ###  ##  
 #####   ###         ##     ######   #####   ### ###   #####   
                                                               
    

        
def options(df):    
    for index_, option in enumerate(df['옵션정보'].to_list()):
        
        
        ### 추가 ####
        
        if '단백질' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'단백질 추가: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '탄수화물' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'상품종류'] = '추가구성상품'
        
        ### 메뉴 변경 ###
            
        elif '현미밥만' in option:
            df.loc[index_, '상품명']  = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'    
            
        elif '고구마+현미밥' in option:
            df.loc[index_, '상품명']  = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '콩' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '당근' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '오이' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '기타' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        else:
            df.loc[index_,'상품종류'] = '조합형옵션상품'
            
    return df




#######  ##   ##   #####    ######  ###      
### ###  ### ###  ### ###     ##    ###      
###      #######  ### ###     ##    ###      
#####    #######  #######     ##    ###      
###      ### ###  ### ###     ##    ###      
### ###  ### ###  ### ###     ##    ###  ##  
#######  ### ###  ### ###   ######  #######  
                                             


def E_mail_disguise(df):
    import numpy as np
    for index_, email in enumerate(df['구매자ID'].to_list()):
        if type(email) == float:
            df.loc[index_,'구매자ID'] = '없음'
        else:
            email = email.split('@')[0]
            id = email[:2] + ('*' * len(email[2:]))
            df.loc[index_,'구매자ID'] = id
    return df        











             
             
                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                   
 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                                                                                                                                                                                                                   
 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                   
                                   
                                   
                                   
                                   
                                   
                                                                                                                                                                                                                                                   





######   #######            #####   ######   ###       ######   ######  
### ###  ###  ##           ###  ##  ### ###  ###         ##     # ## #  
### ###  ###               ###      ### ###  ###         ##       ##    
### ###  #####              #####   ######   ###         ##       ##    
### ###  ###                    ##  ###      ###         ##       ##    
### ###  ###               ###  ##  ###      ###  ##     ##       ##    
######   ###                #####   ###      #######   ######     ##    
                                                                        


def DF_SPLIT(df):
    import pandas as pd
    curation_indexes = []
    curation_df = pd.DataFrame(columns = df.columns)
    for index_, temp in enumerate(df['Temp'].to_list()):
        
        if '1일 1식' in temp or '1일 2식' in temp:
            
            insert_curation_df = pd.DataFrame([[ df.loc[index_,x] for x in list(df.columns)]],columns=df.columns)
            curation_df = pd.concat([curation_df, insert_curation_df],ignore_index=True)
            curation_indexes.append(str(index_))
            
        elif temp == 'x':
            pass
    
    for index_ in curation_indexes:
        df = df.drop(int(index_))
    df = df.reset_index(drop=True)
    
    honest_indexes = []  
    honest_df = pd.DataFrame(columns = df.columns)  
    
    for index_, product in enumerate(df['상품명'].to_list()):
        
        if '[Honest Line | 단품] 어니스트라인 (닭고야)' == product:
            insert_honest_df = pd.DataFrame([[ df.loc[index_,x] for x in list(df.columns)]],columns=df.columns)
            honest_df = pd.concat([honest_df,insert_honest_df],ignore_index = True)
            honest_indexes.append(index_)
        else:
            pass
        
    
    for index_ in honest_indexes:
        df = df.drop(int(index_))
    original_df = df.reset_index(drop=True)
    
    honest_df = honest_df.drop(['Temp','temp2','temp3'],axis=1)
    original_df = original_df.drop(['Temp','temp2','temp3'],axis=1)
    
    return curation_df, honest_df, original_df









                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                   
 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                                                                                                                                                                                                                   
 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                
                                                
                                                
                                                
                                                
                                                
                                                
                                                
                                                                                                                                                                                                                                                   
   #############################################################################
   #   #####   ######    ######   #####    ######  ##  ###   #####   ###       #
   #  ### ###  ### ###     ##    ###  ##     ##    ### ###  ### ###  ###       #
   #  ### ###  ### ###     ##    ###         ##    #######  ### ###  ###       #
   #  ### ###  ######      ##    ### ###     ##    #######  #######  ###       #
   #  ### ###  ### ##      ##    ###  ##     ##    ### ###  ### ###  ###       #
   #  ### ###  ### ###     ##    ###  ##     ##    ### ###  ### ###  ###  ##   #
   #   #####   ### ###   ######   #####    ######  ### ###  ### ###  #######   #
   #############################################################################
           


 #####    #####            ######   ######    ######            #####   ### ###   #####   ##  ###   #####   #######  
### ###  ###  ##           ### ###  ### ###   # ## #           ### ###  ### ###  ### ###  ### ###  ###  ##  ### ###  
### ###  ###               ### ###  ### ###     ##             ###      ### ###  ### ###  #######  ###      ###      
### ###  ### ###           ######   ### ###     ##             ###      #######  #######  #######  ### ###  #####    
### ###  ###  ##           ###      ### ###     ##             ###      ### ###  ### ###  ### ###  ###  ##  ###      
### ###  ###  ##           ###      ### ###     ##             ### ###  ### ###  ### ###  ### ###  ###  ##  ### ###  
 #####    #####            ###      ######      ##              #####   ### ###  ### ###  ### ###   #####   #######  
                                                                                                                           



def original_product_change(df):
    for index_, product in enumerate(df['상품명'].to_list()):
        
        ### 단품 ###
        
        if product == '[단품] 맛보기 박스 (랜덤2팩)':
            df.loc[index_,'상품명'] = '윤식단 단품 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질'
        
        ### 정기 1식 ###
        
        elif product == '[Original line] 1일 1식 10일 프로그램':
            df.loc[index_,'상품명'] = '[윤식단] 샐러드 정기 배달 - 1일 1식 10일 프로그램 (2주)'
            
        elif product == '[Original line] 1일 1식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 1식 20일 프로그램 도시락 배달 건강 식단 새벽 구독 저염'
        
        ### 정기 2식 ###
        
        elif product == '[Original line] 1일 2식 10일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 2식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독'
        
        elif product == '[Original line] 1일 2식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 2식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독'    
            
        ### 정기 3식 ###
        
        elif product == '[Original line] 1일 3식 10일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 3식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독'    
        
        elif product == '[Original line] 1일 3식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 3식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독'
            
    return df






######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                                                                                                                                                                                                                   
######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  









    ###########################################################
    #   ### ###   #####   ##  ###  #######   #####    ######  #
    #   ### ###  ### ###  ### ###  ### ###  ###  ##   # ## #  #
    #   ### ###  ### ###  #######  ###      ###         ##    #
    #   #######  ### ###  #######  #####     #####      ##    #
    #   ### ###  ### ###  ### ###  ###           ##     ##    #
    #   ### ###  ### ###  ### ###  ### ###  ###  ##     ##    #
    #   ### ###   #####   ### ###  #######   #####      ##    #
    ###########################################################                                                  
            
            
            
def honest_order_count(df):
    # df['주문팩'] = ''
    df['총수량'] = ''
    for index_, count in enumerate(df['옵션정보'].to_list()):
        if '(4팩)' in count:
            # df.loc[index_,'주문팩'] = 4
            df.loc[index_,'총수량'] = df.loc[index_,'수량'] * 4
        else:
            # df.loc[index_,'주문팩'] = 1
            df.loc[index_,'총수량'] = df.loc[index_,'수량'] * 1
    
    columns = ['상품주문번호', '주문번호', '구매자명', '수취인명', '상품명', '상품종류', '옵션정보', '수량','총수량','배송지',
       '구매자연락처', '배송메세지', '수취인연락처1', '구매자ID', '우편번호']
    
    df = df[columns]
    
    return df











 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  
                                                                                                                                                                                                                                                   
 ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######   ######  






    ################################################################################
    #                                                                              #
    #   #####   ### ###  ######    #####    ######   ######   #####   ##  ###      #
    #  ### ###  ### ###  ### ###  ### ###   # ## #     ##    ### ###  ### ###      #
    #  ###      ### ###  ### ###  ### ###     ##       ##    ### ###  #######      #
    #  ###      ### ###  ######   #######     ##       ##    ### ###  #######      #
    #  ###      ### ###  ### ##   ### ###     ##       ##    ### ###  ### ###      #
    #  ### ###  ### ###  ### ###  ### ###     ##       ##    ### ###  ### ###      #
    #   #####    #####   ### ###  ### ###     ##     ######   #####   ### ###      #
    #                                                                              #
    ################################################################################





def curation_format(df):
    import pandas as pd
    result_df = pd.DataFrame(columns=df.columns)
    for index_, Temp in enumerate(df['Temp'].to_list()):
        
        if df.loc[index_,'Temp'] == '1일 1식':
            count = '(10팩)'
        elif df.loc[index_,'Temp'] == '1일 2식':
            count = '(20팩)'
            
        if df.loc[index_,'temp2'] == '탄수화물100g' and df.loc[index_,'temp3'] == '단백질100g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            result_df = pd.concat([result_df,main],axis=0, ignore_index = True)
        
        elif df.loc[index_,'temp2'] == '탄수화물100g' and df.loc[index_,'temp3'] == '단백질150g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 50g추가{count}'
            append_df = pd.concat([append,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
        
            
        elif df.loc[index_,'temp2'] == '탄수화물100g' and df.loc[index_,'temp3'] == '단백질200g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 100g추가{count}'
            append_df = pd.concat([append,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
        
            
            
        elif df.loc[index_,'temp2'] == '탄수화물150g' and df.loc[index_,'temp3'] == '단백질100g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 50g추가{count}'
            append_df = pd.concat([append,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
            
        elif df.loc[index_,'temp2'] == '탄수화물150g' and df.loc[index_,'temp3'] == '단백질150g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 50g추가{count}'
            scd = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            scd.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 50g추가{count}'
            append_df = pd.concat([fst,scd,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
            
        elif df.loc[index_,'temp2'] == '탄수화물150g' and df.loc[index_,'temp3'] == '단백질200g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 50g추가{count}'
            scd = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            scd.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 100g추가{count}'
            append_df = pd.concat([fst,scd,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
            
            
            
        elif df.loc[index_,'temp2'] == '탄수화물200g' and df.loc[index_,'temp3'] == '단백질100g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            append_df.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 100g추가{count}'
            append_df = pd.concat([fst,scd,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
        
        elif df.loc[index_,'temp2'] == '탄수화물200g' and df.loc[index_,'temp3'] == '단백질150g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 100g추가{count}'
            scd = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            scd.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 50g추가{count}'
            append_df = pd.concat([fst,scd,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
        
        elif df.loc[index_,'temp2'] == '탄수화물200g' and df.loc[index_,'temp3'] == '단백질200g' :
            main = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            fst.loc[index_,'옵션정보'] = f'탄수화물 추가 : 탄수화물 100g추가{count}'
            scd = pd.DataFrame(df.loc[index_, [x for x in list(df.columns)]]).T
            scd.loc[index_,'옵션정보'] = f'단백질 추가 : 단백질 100g추가{count}'
            append_df = pd.concat([fst,scd,main],ignore_index = True,axis=0)
            result_df = pd.concat([result_df,append_df],axis=0, ignore_index = True)
    
    return result_df
                    

def curation_strip(df):
    return df.drop(['Temp','temp2','temp3'],axis=1)




                                                                                          
 ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##  
  ####     ####     ####     ####     ####     ####     ####     ####     ####     ####   
######## ######## ######## ######## ######## ######## ######## ######## ######## ######## 
  ####     ####     ####     ####     ####     ####     ####     ####     ####     ####   
 ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##  
                                  



 ######   #####    ######   #####   ###      
 # ## #  ### ###   # ## #  ### ###  ###      
   ##    ### ###     ##    ### ###  ###      
   ##    ### ###     ##    #######  ###      
   ##    ### ###     ##    ### ###  ###      
   ##    ### ###     ##    ### ###  ###  ##  
   ##     #####      ##    ### ###  #######  
                                             




                                                                                          
 ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##  
  ####     ####     ####     ####     ####     ####     ####     ####     ####     ####   
######## ######## ######## ######## ######## ######## ######## ######## ######## ######## 
  ####     ####     ####     ####     ####     ####     ####     ####     ####     ####   
 ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##   ##  ##  
                                                                                          
global IMWEB_total
def IMWEB_total(df_path:str):
    """

    Args:
        df_path (DataFrame): ImWeb DataFrame path
    """
    df = pd.read_excel(df_path)
    # Main
    df = col_rename(df)
    df = numbers_change(df)
    df = strip_count(df)
    # For split
    df = curation_diet_split(df)
    df = curation_unique_split(df)
    df = curation_diet_count(df)
    df = curation_total_option_split(df)
    # Delivery
    df = delivery_split(df)
    # Email
    df = E_mail_disguise(df)

    # SPLIT 3 DF
    curation_df, honest_df,original_df = DF_SPLIT(df)


    ### HONEST
    honest_df = honest_order_count(honest_df)
    honest_df = options(honest_df)

    ### Original
    original_df = original_product_change(original_df)
    original_df = options(original_df)
    
    ### curation
    curation_df = curation_format(curation_df)
    curation_df = curation_strip(curation_df)
    curation_df = options(curation_df)
    curation_df = original_product_change(curation_df)
    total = pd.concat([curation_df,original_df],axis=0, ignore_index=True)
    
    
    return original_df, honest_df, curation_df, total