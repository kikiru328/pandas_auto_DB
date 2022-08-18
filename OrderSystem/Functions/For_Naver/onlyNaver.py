"""
Make Same Format table for Naver smartstore

Returns:
    excel : uniformized excel file
"""
import pandas as pd
import numpy as np


def apply_pandas(p_d):
    """
    Set options for printing pandas
    Args:
        p_d : pandas option
    """
    p_d.set_option('display.max_rows', None)
    p_d.set_option('display.max_columns', None)
    p_d.set_option('display.width', None)
    p_d.set_option('display.max_colwidth', None)

def read_naver_table(naver_path):
    """
    Read Naver smartstore excel.
    delete header, reset columns
    Args:
        naver_path: naver_file path

    Returns:
        dataframe: naver_df
    """
    d_f = pd.read_excel(naver_path, header=1)
    need_columns = [
        '상품주문번호', '주문번호', '배송방법(구매자 요청)', '배송방법', '택배사', '송장번호',
        '발송일', '구매자명', '수취인명', '상품명', '상품종류', '옵션정보', '수량', '옵션가격',
        '상품가격', '상품별 총 주문금액', '배송지', '구매자연락처', '배송메세지', '정산예정금액',
        '수취인연락처1', '배송속성', '배송희망일', '결제일', '구매자ID', '우편번호']
    columns = d_f.columns.to_list()
    drop_columns = [x for x in columns if x not in need_columns]
    d_f = d_f.drop(drop_columns, axis=1)
    d_f['플랫폼'] = '네이버'
    return d_f


def change_product_name_list(product_name):
    """
    Change product name for uniformed\
    Args:
        product_name (str): product name

    Returns:
        product_name (str): changed product name
    """
    if '1일 1식 4일' in product_name:
        return '[윤식단][정기] 1일 1식 4일'
    elif product_name == '[윤식단] 샐러드 정기 배달 - 1일 1식 10일 프로그램 (2주)':
        return '[윤식단][정기] 1일 1식 10일'
    elif product_name == '윤식단 샐러드 정기배송 1일 1식 20일 프로그램 도시락 배달 건강 식단 새벽 구독 저염':
        return '[윤식단][정기] 1일 1식 20일'
    elif product_name == '윤식단 샐러드 정기배송 1일 2식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 2식 10일'
    elif product_name == '윤식단 샐러드 정기배송 1일 2식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 2식 20일'
    elif product_name ==  '윤식단 샐러드 정기배송 1일 3식 10일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 3식 10일'
    elif product_name ==  '윤식단 샐러드 정기배송 1일 3식 20일 프로그램 도시락 배달 다이어트 식단 새벽 구독':
        return '[윤식단][정기] 1일 3식 20일'
    elif product_name ==  '윤식단 단품 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질':
        return '[윤식단][단품] 윤식단/오리지널'
        # return '[윤식단][정기] 1일 2식 1일'
    elif product_name == '[윤식단 단품] 닭고야 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질 바프식단 바디프로필식단':
        return '[윤식단][단품] 닭고야/어니스트'
    else:
        return  product_name


def change_product_name_by_list(d_f):
    """
    product name for list
    Args:
        d_f: main df

    Returns:
        d_f: changed product name dataframe
    """
    d_f['상품명'] = d_f['상품명'].apply(lambda x : change_product_name_list(x))
    return d_f


def split_dataframe(d_f):
    """
    Split Dataframe uniformed dataframe to main & option
    Args:
        d_f: uniformed df

    Returns:
        d_f: unifomed df
        main_df: seperated main df
        option_df: sepearted option df
    """
    main_df = d_f[d_f['상품종류']=='조합형옵션상품']
    option_df = d_f[d_f['상품종류']=='추가구성상품']
    return d_f, main_df, option_df


def subs_add_options(add,d_f,main_idx):
    if len(add) == 0:
        for add_col in ['단백질추가', '탄수화물추가']:
            d_f.loc[main_idx, add_col] = np.nan
    else:
        for add_opt in add:
            if '단백질' in add_opt:
                d_f.loc[main_idx, '단백질추가'] = add_opt
            elif '탄수화물' in add_opt:
                d_f.loc[main_idx, '탄수화물추가'] = add_opt
    return d_f
                        

def subs_remove_options(change, d_f, main_idx):
    if len(change) == 0:
        for opt_col in ['고구마+현미밥', '현미밥만', '콩제외', '당근제외', '오이제외', '기타']:
            d_f.loc[main_idx, opt_col] = np.nan
    else:
        for change_opt in change:
            if '+' in change_opt:
                d_f.loc[main_idx, '고구마+현미밥'] = change_opt
            elif '현미밥만' in change_opt:
                d_f.loc[main_idx, '현미밥만'] = change_opt
            elif '콩' in change_opt:
                d_f.loc[main_idx, '콩제외'] = change_opt
            elif '당근' in change_opt:
                d_f.loc[main_idx, '당근제외'] = change_opt
            elif '오이' in change_opt:
                d_f.loc[main_idx, '오이제외'] = change_opt
            elif '기타' in change_opt:
                d_f.loc[main_idx, '기타'] = change_opt
    return d_f


def simple_select_options(pack, d_f, order_id, main_df, main_idx):
    if len(pack) == 0:
        d_f.loc[main_idx, '단품옵션'] = np.nan
        d_f.loc[main_idx, '세트옵션'] = np.nan
    else:
        box_idx = main_df[(main_df['주문번호']==order_id) 
                          & (main_df['상품명']==
                             '[윤식단][단품] 닭고야/어니스트')].index[0]
        
        for p_opt in pack:
            if '세트' in p_opt:
                d_f.loc[box_idx, f'세트옵션'] = p_opt
            elif '단품' in p_opt:
                d_f.loc[box_idx, f'단품옵션'] = p_opt
    return d_f
                
                                                
def split_product_options(d_f):
    """
    Split product option to add option by customer.
    Args:
        d_f: Args for split_dataframe func

    Returns:
        d_f: resort by customer
        
    > 2022.08.16
        상품명 (정기/단품) 에 따라 옵션이 다르게 들어가야된다.
        장바구니 시 주문번호가 전체 동일하기 때문에
        단품 옵션이 정기 옵션에 들어가거나 그 반대도 생긴다.
        opt_list의 내용이 main_df의 상품에 따라 들어가게 **
    
    """
    d_f, main_df, option_df = split_dataframe(d_f)
    for order_id in option_df['주문번호'].to_list():
        main_idx = main_df[main_df['주문번호']==order_id].index[0]
        opt_list = list(option_df[option_df['주문번호'] == order_id]['상품명'])
        d_f.loc[main_idx,'옵션유무'] = 'O'
        add = []
        change = []
        pack = []
        for opt in opt_list:
            if '단백질' in opt:
                add.append(opt)
            elif '탄수화물' in opt:
                add.append(opt)    
            elif '팩' in opt:
                pack.append(opt)
            else:
                change.append(opt)
                
        d_f = subs_add_options(add,d_f,main_idx)
        d_f = subs_remove_options(change,d_f,main_idx)
        d_f = simple_select_options(pack,d_f,order_id,main_df,main_idx)
        d_f = d_f.fillna('X')
        d_f = d_f[d_f['상품종류']=='조합형옵션상품']
    return d_f


def split_delivery_options(d_f):
    """
    Split delivery option for simplify
    Args:
        d_f: main df

    Returns:
        d_f: main df
    """
    for order_id in d_f['상품주문번호']:
        idx = d_f[d_f['상품주문번호']==order_id].index[0]
        opt = d_f.loc[idx, '옵션정보']
        for split_opt in opt.split(' / '):
            if split_opt.startswith('공동현관'):
                d_f.loc[idx, '공동현관 출입비밀번호'] = split_opt.split(': ')[1]
            elif split_opt.startswith('배송방법'):
                d_f.loc[idx, '배송방법 고객선택'] = split_opt.split(': ')[1][:4]
            elif split_opt.startswith('상품선택'):
                d_f.loc[idx, '단품옵션'] = split_opt.split(': ')[1]
    return d_f


def resort_new_columns(d_f):
    """
    Resort new columns for uniform
    Args:
        d_f: main df

    Returns:
        d_f: resort columns df
    """
    new_col =[
    '상품주문번호','주문번호','플랫폼',
    '구매자명','구매자ID','구매자연락처','결제일',
    '상품명','상품종류','수량','단품옵션','세트옵션','옵션유무',
    '단백질추가','탄수화물추가','고구마+현미밥','현미밥만','콩제외','당근제외','오이제외','기타',
    '옵션정보','상품가격','옵션가격','상품별 총 주문금액','정산예정금액',
    '수취인명','수취인연락처1', '배송지', '우편번호',
    '배송방법(구매자 요청)','배송방법 고객선택','배송방법','배송속성','택배사','송장번호','발송일',
    '배송희망일', '공동현관 출입비밀번호','배송메세지']
    d_f = d_f[new_col]
    return d_f


def total_uniformize(p_d, naver_path):
    """
    Total functions
    Args:
        d_f: uniformed d_f

    Returns:
        d_f: uniformed for customer
    """
    apply_pandas(p_d)
    d_f = read_naver_table(naver_path)
    d_f = split_product_options(d_f)
    d_f = change_product_name_by_list(d_f)
    d_f = split_delivery_options(d_f)
    d_f = resort_new_columns(d_f)
    return d_f

