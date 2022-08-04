def split_dataframe(df):
    main_df = df[df['상품종류']=='조합형옵션상품']
    option_df = df[df['상품종류']=='추가구성상품']
    return df, main_df, option_df
    
def split_product_options(df):
    import numpy as np
    
    df, main_df, option_df = split_dataframe(df)
    
    for order_id in option_df['주문번호'].to_list():
        main_idx = main_df[main_df['주문번호']==order_id].index[0]
        opt_list = list(option_df[option_df['주문번호'] == order_id]['상품명'])
        
        df.loc[main_idx,'옵션유무'] = 'O'
        
        add = []
        change = []
        pack = []
        
        for opt in opt_list:
            if '추가' in opt:
                add.append(opt)
            elif '세트' in opt:
                pack.append(opt)
            else:
                change.append(opt)


        if len(add) == 0:
            for add_col in ['단백질추가', '탄수화물추가']:
                df.loc[main_idx, add_col] = np.nan
        else:
            for add_opt in add:
                if '단백질' in add_opt:
                    df.loc[main_idx, '단백질추가'] = add_opt
                elif '탄수화물' in add_opt:
                    df.loc[main_idx, f'탄수화물추가'] = add_opt
            
            
        if len(change) == 0:
            for opt_col in ['고구마+현미밥', '현미밥만', '콩제외', '당근제외', '오이제외', '기타']:
                df.loc[main_idx, opt_col] = np.nan
        else:
            for change_opt in change:
                # print(change_opt)
                if '+' in change_opt:
                    df.loc[main_idx, '고구마+현미밥'] = change_opt
                elif '현미밥만' in change_opt:
                    df.loc[main_idx, f'현미밥만'] = change_opt
                elif '콩' in change_opt:
                    df.loc[main_idx, f'콩제외'] = change_opt
                elif '당근' in change_opt:
                    df.loc[main_idx, f'당근제외'] = change_opt
                elif '오이' in change_opt:
                    df.loc[main_idx, f'오이제외'] = change_opt     
                elif '기타' in change_opt:
                    df.loc[main_idx, f'기타'] = change_opt                           
                # test.loc[main_idx, f'옵션_{i+1}'] = change_opt      
        if len(pack) == 0:
            df.loc[main_idx, '단품옵션'] = np.nan
        else:
            for p_opt in pack:
                df.loc[main_idx, '단품옵션'] = p_opt
                
    df = df.fillna('X')
    df = df[df['상품종류']=='조합형옵션상품']            
    return df


def change_product_name_list(x):
    if '1일 1식 4일' in x:
        return '[윤식단][정기] 1일 1식 4일'
    
    elif x == '[윤식단] 샐러드 정기 배달 - 1일 1식 10일 프로그램 (2주)':
        return '[윤식단][정기] 1일 1식 10일'
    
    elif x == '윤식단 샐러드 정기배송 1일 1식 20일 프로그램 도시락 배달 건강 식단 새벽 구독 저염':
        return '[윤식단][정기] 1일 1식 20일'
    
    elif x == '윤식단 샐러드 정기배송 1일 2식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 2식 10일'
    
    elif x == '윤식단 샐러드 정기배송 1일 2식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 2식 20일'        
    
    elif x ==  '윤식단 샐러드 정기배송 1일 3식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 3식 10일'
    
    elif x ==  '윤식단 샐러드 정기배송 1일 3식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 3식 20일'                
    
    elif x ==  '윤식단 단품 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질':
        return '[윤식단][단품] 윤식단/오리지널'
    
    elif x == '[윤식단 단품] 닭고야 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질 바프식단 바디프로필식단':
        return '[윤식단][단품] 닭고야/어니스트'
    else:
        return  x 
    
def change_product_name_by_list(df):
    df['상품명'] = df['상품명'].apply(lambda x : change_product_name_list(x))
    return df


def split_delivery_options(df):
    for order_id in df['상품주문번호']:
        idx = df[df['상품주문번호']==order_id].index[0]
        opt = df.loc[idx, '옵션정보']

        for split_opt in opt.split(' / '):
            if split_opt.startswith('공동현관'):
                df.loc[idx, '공동현관 출입비밀번호'] = split_opt.split(': ')[1]
            elif split_opt.startswith('배송방법'):
                df.loc[idx, '배송방법 고객선택'] = split_opt.split(': ')[1]
            elif split_opt.startswith('상품선택'):
                df.loc[idx, '단품옵션'] = split_opt.split(': ')[1]
    return df


def resort_new_columns(df):
    new_col =[
    '상품주문번호','주문번호','플랫폼',
    '구매자명','구매자ID','구매자연락처','결제일',
    '상품명','상품종류','수량','단품옵션','옵션유무',
    '단백질추가','탄수화물추가','고구마+현미밥','현미밥만','콩제외','당근제외','오이제외','기타','옵션정보',
    '상품가격','옵션가격','상품별 총 주문금액','정산예정금액',
    '수취인명','수취인연락처1', '배송지', '우편번호',
    '배송방법(구매자 요청)','배송방법 고객선택','배송방법','배송속성','택배사','송장번호','발송일','배송희망일',
    '공동현관 출입비밀번호','배송메세지']
    
    df = df[new_col]
    return df


def total(df):
    df = split_product_options(df)
    df = change_product_name_by_list(df)
    df = split_delivery_options(df)
    df = resort_new_columns(df)
    return df    