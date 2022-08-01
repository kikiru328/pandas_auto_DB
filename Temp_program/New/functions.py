import pandas as pd

def apply_pandas(pd):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
def read_naver_table(naver_path):
    df = pd.read_excel(naver_path, header=1)
    need_columns = [
        '상품주문번호','주문번호','배송방법(구매자 요청)','배송방법','택배사','송장번호','발송일',
        '구매자명','수취인명','상품명','상품종류','옵션정보','수량','옵션가격','상품가격',
        '상품별 총 주문금액','배송지','구매자연락처','배송메세지','정산예정금액','수취인연락처1',
        '배송속성','배송희망일','결제일','구매자ID','우편번호']
    columns = df.columns.to_list()
    drop_columns = [x for x in columns if x not in need_columns]
    df = df.drop(drop_columns, axis=1)
    return df    

def read_imweb_table(imweb_path):
    df = pd.read_excel(imweb_path)
    return df
    

def rename_columns(df):
    df['상품종류'] = ''
    df = df['품목주문번호,주문번호,주문자명,수취인명,상품명,상품종류,옵션정보,수량,주소,'\
            '주문자 연락처,배송메세지,수취인 연락처,계정,우편번호'.split(',')]
    df = df.rename(columns = {
        '주문번호' : '주문번호', 
        '품목주문번호' : '상품주문번호',
        '주문자명' : '구매자명',
        '수취인명' : '수취인명',
        '상품명' : '상품명',
        '상품종류' : '상품종류',
        '옵션정보' : '옵션정보',
        '수량' : '수량',
        '주소' : '배송지',
        '주문자 연락처' : '구매자연락처',
        '배송메세지' : '배송메세지',
        '수취인 연락처' : '수취인연락처1',
        '계정' : '구매자ID',
        '우편번호' : '우편번호'
    })
    return df
    
    
def strip_count_option(df):
    df['옵션정보']= df['옵션정보'].apply(lambda x : x[:-5])
    return df

def rename_delivery_option(df):
    def rename_delivery(x):
        if "공동현관 비밀번호(없을시'없음'작성)" in x:
            x = x.replace("공동현관 비밀번호(없을시'없음'작성)",
                         "공동현관 출입비밀번호 (없을 시 '없음'작성)")
            return x
        else:
            return x
    df['옵션정보']= df['옵션정보'].apply(lambda x : rename_delivery(x))
    return df    

def change_product_name_by_option_add(df):
    for index_, option in enumerate(df['옵션정보'].to_list()):
        if '단백질' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'옵션정보'] = f'단백질 추가: {option.split(" : ")[1]}'
            df.loc[index_,'상품종류'] = '추가구성상품'
            
        elif '탄수화물' in option:
            df.loc[index_,'상품명'] = option.split(' : ')[1]
            df.loc[index_,'상품종류'] = '추가구성상품'
    return df

def change_product_name_by_option_remove(df):
    for index_, option in enumerate(df['옵션정보'].to_list()):
        if '현미밥만' in option:
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

def change_product_name_as_naver(df):
    for index_, product in enumerate(df['상품명'].to_list()):
        if product == '[단품] 맛보기 박스 (랜덤2팩)':
            df.loc[index_,'상품명'] = '윤식단 단품 샐러드 도시락 정기배송 다이어트 건강 식단'\
                                    '새벽배송 배달 저염식 단백질'
            
        elif product == '[Original line] 1일 1식 4일 프로그램':
            df.loc[index_,'상품명'] = '[윤식단] 샐러드 정기 배송 - 1일 1식 4일 프로그램'
        
        elif product == '[Original line] 1일 2식 4일 프로그램':
            df.loc[index_,'상품명'] = '[윤식단] 샐러드 정기 배송 - 1일 2식 4일 프로그램'    
            
        elif product == '[Original line] 1일 3식 4일 프로그램':
            df.loc[index_,'상품명'] = '[윤식단] 샐러드 정기 배송 - 1일 3식 4일 프로그램'
            
        elif product == '[Original line] 1일 1식 10일 프로그램':
            df.loc[index_,'상품명'] = '[윤식단] 샐러드 정기 배달 - 1일 1식 10일 프로그램'\
                                    '(2주)' 
            
        elif product == '[Original line] 1일 1식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 1식 20일 프로그램 도시락'\
                                    '배달 건강 식단 새벽 구독 저염'
        
        elif product == '[Original line] 1일 2식 10일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 2식 10일 프로그램 도시락'\
                                    '배달 다이어트 식단 새벽 구독'
                                    
        elif product == '[Original line] 1일 2식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 2식 20일 프로그램 도시락'\
                                    '배달 다이어트 식단 새벽 구독'    
                                    
        elif product == '[Original line] 1일 3식 10일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 3식 10일 프로그램 도시락'\
                                    '배달 다이어트 식단 새벽 구독'    
                                    
        elif product == '[Original line] 1일 3식 20일 프로그램':
            df.loc[index_,'상품명'] = '윤식단 샐러드 정기배송 1일 3식 20일 프로그램 도시락'\
                                    '배달 다이어트 식단 새벽 구독'
    return df

def split_table_for_honest(df):
    honest_dataframe = df[df['상품명'] == '[Honest Line | 단품] 어니스트라인 (닭고야)']
    honest_indexes = honest_dataframe.index
    original_product_dataframe = df.drop(honest_indexes,axis=0)\
        .reset_index(drop=True)
    honest_dataframe = honest_dataframe.reset_index(drop=True)
    return original_product_dataframe, honest_dataframe        

def split_honest_options(df):
    df['상품선택'] = ''
    for index_, option in enumerate(df['옵션정보'].to_list()):
            df.loc[index_,'상품선택'] = option.split(' / 상품선택 : ')[1]
            df.loc[index_,'옵션정보'] = option.split(' / 상품선택 : ')[0]
    return df

def count_honest_products(df):
    df['제조총수량'] = ''
    for index_, option in enumerate(df['옵션정보'].to_list()):
        if '단품' in option:
            df.loc[index_, '제조총수량'] = df.loc[index_, '수량'] * 1
            
        elif '묶음팩' in option:
            df.loc[index_, '제조총수량'] = df.loc[index_, '수량'] * 4
    return df

def resort_honest_columns(df):
    columns = ['상품주문번호', '주문번호', '구매자명', '수취인명', '상품명', '상품종류', 
               '옵션정보', '수량','제조총수량','배송지','구매자연락처', '배송메세지', 
               '수취인연락처1', '구매자ID', '우편번호']
    df = df[columns]
    return df

def resort_original_columns(naver_df, original_product_dataframe):
    add_columns = []
    for col in naver_df.columns.to_list():
        if col not in original_product_dataframe.columns.to_list():
            add_columns.append(col)
        
    for col in add_columns:
        original_product_dataframe[col] = ''        
        
    original_product_dataframe = original_product_dataframe[naver_df.columns]
    return original_product_dataframe


def preprocess_only_for_imweb_columns(original_product_dataframe):
    naver_dataframe_columns = [
        '상품주문번호', '주문번호', '배송방법(구매자 요청)', '배송방법', '택배사', '송장번호',\
        '발송일', '구매자명', '수취인명', '상품명', '상품종류', '옵션정보', '수량', '옵션가격',\
        '상품가격', '상품별 총 주문금액', '배송지', '구매자연락처', '배송메세지', '정산예정금액',\
        '수취인연락처1', '배송속성', '배송희망일', '결제일', '구매자ID', '우편번호'
    ]
    add_columns = []
    for col in naver_dataframe_columns:
        if col not in original_product_dataframe.columns.to_list():
            add_columns.append(col)
    
    for col in add_columns:
        original_product_dataframe[col] = '없음'
        
    original_product_dataframe = original_product_dataframe[naver_dataframe_columns]
    return original_product_dataframe


def concat_imweb_and_naver(naver_df, original_product_dataframe):
    uniformed_dataframe = pd.concat([naver_df, original_product_dataframe]\
        ,axis=0)
    return uniformed_dataframe


def preprocess_only_imweb(pd, iw_path):
    apply_pandas(pd)
    iw_df = read_imweb_table(iw_path)
    iw_df = rename_columns(iw_df)
    iw_df = strip_count_option(iw_df)
    iw_df = rename_delivery_option(iw_df)
    iw_df = change_product_name_by_option_add(iw_df)
    iw_df = change_product_name_by_option_remove(iw_df)
    iw_df = change_product_name_as_naver(iw_df)

    original, honest = split_table_for_honest(iw_df)

    original = preprocess_only_for_imweb_columns(original)
    

    honest = split_honest_options(honest)
    honest = count_honest_products(honest)
    honest = resort_honest_columns(honest)
    return original, honest



def total(pd, iw_path, naver_path):
    apply_pandas(pd)
    naver_df = read_naver_table(naver_path)
    iw_df = read_imweb_table(iw_path)
    iw_df = rename_columns(iw_df)
    iw_df = strip_count_option(iw_df)
    iw_df = rename_delivery_option(iw_df)
    iw_df = change_product_name_by_option_add(iw_df)
    iw_df = change_product_name_by_option_remove(iw_df)
    iw_df = change_product_name_as_naver(iw_df)

    original, honest = split_table_for_honest(iw_df)

    original = resort_original_columns(naver_df, original)
    uniform = concat_imweb_and_naver(naver_df, original)

    honest = split_honest_options(honest)
    honest = count_honest_products(honest)
    honest = resort_honest_columns(honest)
    return uniform, honest