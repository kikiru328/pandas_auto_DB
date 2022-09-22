"""
Functions for uniformization smartstore excel and imweb

Returns:
    excel : uniformized excel
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
    
    
def read_imweb_table(imweb_path):
    """
    Read Imweb excel.
    Args:
        imweb_path: imweb path

    Returns:
        dataframe: imweb_df
    """
    d_f = pd.read_excel(imweb_path)
    return d_f


def rename_columns(d_f):
    """
    Redefine Imweb columns same as naver smartstore excel
    Args:
        d_f: After read_imweb_table func.

    Returns:
        d_f: preprocessing imweb df
    """
    d_f['상품종류'] = ''
    d_f = d_f['품목주문번호,주문번호,주문자명,수취인명,상품명,상품종류,옵션정보,수량,주소,'
              '주문자 연락처,배송메세지,수취인 연락처,계정,우편번호'.split(',')]
    d_f = d_f.rename(columns={
        '주문번호': '주문번호',
        '품목주문번호': '상품주문번호',
        '주문자명': '구매자명',
        '수취인명': '수취인명',
        '상품명': '상품명',
        '상품종류': '상품종류',
        '옵션정보': '옵션정보',
        '수량': '수량',
        '주소': '배송지',
        '주문자 연락처': '구매자연락처',
        '배송메세지': '배송메세지',
        '수취인 연락처': '수취인연락처1',
        '계정': '구매자ID',
        '우편번호': '우편번호'
    })
    return d_f


def strip_count_option(d_f):
    """
    Delete count in option
    Args:
        d_f: After imweb_table rename_columns func.

    Returns:
        d_f: Stripped imweb df
    """
    d_f['옵션정보'] = d_f['옵션정보'].apply(lambda x: x[:-5])
    return d_f


def rename_delivery_option(d_f):
    """
    Split delivery option in imweb table
    Args:
        d_f: After strip_count_option imweb func.
    Returns:
        d_f: Renamed imweb df
    """
    def rename_delivery(dev_opt):
        if "공동현관 비밀번호(없을시'없음'작성)" in dev_opt:
            dev_opt = dev_opt.replace("공동현관 비밀번호(없을시'없음'작성)",
                                      "공동현관 출입비밀번호 (없을 시 '없음'작성)")
            return dev_opt
        return dev_opt
    d_f['옵션정보'] = rename_delivery(d_f['옵션정보'])
    return d_f


def change_product_name_by_option_add(d_f):
    """
    Change imweb table customer add option.
    Args:
        d_f: After rename_delivery_option.

    Returns:
        d_f: Seperate option imweb df
    """
    for index_, option in enumerate(d_f['옵션정보'].to_list()):
        if '단백질' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'단백질 추가: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '탄수화물' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '상품종류'] = '추가구성상품'
        else:
            d_f.loc[index_, '상품종류'] = '조합형옵션상품'
    return d_f


def change_product_name_by_option_remove(d_f):
    """
    Change product name by option in imweb df
    Args:
        d_f: After chnage_product_name_by_option_add imweb func.

    Returns:
        d_f: changed product name imweb df
    """
    for index_, option in enumerate(d_f['옵션정보'].to_list()):
        if '현미밥만' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '고구마+현미밥' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '콩' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '당근' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '오이' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'

        elif '기타' in option:
            d_f.loc[index_, '상품명'] = option.split(' : ')[1]
            d_f.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
            d_f.loc[index_, '상품종류'] = '추가구성상품'
    return d_f


def change_product_name_as_naver(d_f):
    """
    Change product name same as naver excel
    Args:
        d_f: After change_product_name_by_option_remove imweb func

    Returns:
        d_f: Changed product name same as naver imweb df
    """
    for index_, product in enumerate(d_f['상품명'].to_list()):
        if product == '[Original line] 1일 1식 4일 프로그램':
            d_f.loc[index_, '상품명'] = '[윤식단][정기] 1일 1식 4일'

        elif product == '[Original line] 1일 1식 10일 프로그램':
            d_f.loc[index_, '상품명'] = '[윤식단] 샐러드 정기 배달 - 1일 1식 10일 프로그램'\
                ' (2주)'

        elif product == '[Original line] 1일 1식 20일 프로그램':
            d_f.loc[index_, '상품명'] = '윤식단 샐러드 정기배송 1일 1식 20일 프로그램 도시락'\
                ' 배달 건강 식단 새벽 구독 저염'

        elif product == '[Original line] 1일 2식 10일 프로그램':
            d_f.loc[index_, '상품명'] = '윤식단 샐러드 정기배송 1일 2식 10일 프로그램 도시락'\
                ' 배달 다이어트 식단 새벽 구독'

        elif product == '[Original line] 1일 2식 20일 프로그램':
            d_f.loc[index_, '상품명'] = '윤식단 샐러드 정기배송 1일 2식 20일 프로그램 도시락'\
                ' 배달 다이어트 식단 새벽 구독'

        elif product == '[Original line] 1일 3식 10일 프로그램':
            d_f.loc[index_, '상품명'] = '윤식단 샐러드 정기배송 1일 3식 10일 프로그램 도시락'\
                ' 배달 다이어트 식단 새벽 구독'

        elif product == '[Original line] 1일 3식 20일 프로그램':
            d_f.loc[index_, '상품명'] = '윤식단 샐러드 정기배송 1일 3식 20일 프로그램 도시락'\
                ' 배달 다이어트 식단 새벽 구독'
        
        elif product == '[단품] 맛보기 박스 (랜덤2팩)':
            d_f.loc[index_, '상품명'] = '윤식단 단품 샐러드 도시락 정기배송 다이어트 건강 식단'\
                '새벽배송 배달 저염식 단백질'

        elif product == '[Honest Line | 단품] 어니스트라인 (닭고야)':
            d_f.loc[index_, '상품명'] = '[윤식단 단품] 닭고야 샐러드 도시락 정기배송 다이어트'\
                ' 건강 식단 새벽배송 배달 저염식 단백질 바프식단 바디프로필식단'
    return d_f


def split_table_for_honest(d_f):
    """
    Split table for make honest sepeate table
    Args:
        d_f: After change_product_name_as_naver imweb func.

    Returns:
        d_f: Splitted honest df and original
    """
    honest_dataframe = d_f[d_f['상품명'] == '[윤식단 단품] 닭고야 샐러드 도시락 정기배송'\
        ' 다이어트 건강 식단 새벽배송 배달 저염식 단백질 바프식단 바디프로필식단']
    honest_indexes = honest_dataframe.index
    original_product_dataframe = d_f.drop(honest_indexes, axis=0)\
        .reset_index(drop=True)
    honest_dataframe = honest_dataframe.reset_index(drop=True)
    return original_product_dataframe, honest_dataframe


def duplicate_honest_product_and_option(d_f):
    """
    Duplicate honest rows like original line
    Args:
        d_f: only honest dataframe

    Returns:
        return_df: duplicated dataframe
    """
    d_f['sets'] = ''
    import pandas as pd
    for index, option in enumerate(d_f['옵션정보'].to_list()):
        if '상품선택' in option:
            d_f.loc[index, 'sets'] = option.split('상품선택 : ')[1].split(' / ')[0]
            d_f.loc[index, '옵션정보'] = option.split('상품선택 : ')[0]\
                +option.split('상품선택 : ')[1].split(' / ')[1]
    result_df = pd.DataFrame(columns=d_f.columns)
    
    for index, option in enumerate(d_f['sets'].to_list()):
        main = pd.DataFrame(d_f.loc[index, [x for x in list(d_f.columns)]]).T
        main.loc[index, '상품종류'] = '조합형옵션상품'
        append = pd.DataFrame(d_f.loc[index, [x for x in list(d_f.columns)]]).T
        append.loc[index, '상품명'] = option
        append.loc[index, '옵션정보'] = f"어니스트: {option}"
        append.loc[index, '상품종류'] = '추가구성상품'
        append_df = pd.concat([append,main],ignore_index=True, axis=0)
        result_df = pd.concat([result_df,append_df],axis=0, ignore_index=True)
        
    for order_id in list(result_df.주문번호.unique()):
        if len( result_df[(result_df['주문번호']==order_id) & (result_df['상품명']\
            =='[윤식단 단품] 닭고야 샐러드 도시락 정기배송 다이어트 건강 식단 새벽배송 배달 저염식'\
                ' 단백질 바프식단 바디프로필식단')]) == 1:
            pass
        else:
            indexes = result_df[(result_df['주문번호']==order_id) & 
                                (result_df['상품명']=='[윤식단 단품] 닭고야 샐러드 도시락'\
                                    ' 정기배송 다이어트 건강 식단 새벽배송 배달 저염식 단백질'\
                                        ' 바프식단 바디프로필식단')].index.to_list()
            result_df = result_df.drop(indexes[:-1],axis=0)

    result_df = result_df.drop('sets', axis=1)
    result_df = result_df.reset_index(drop=True)
    return result_df
        
        

def unify_imweb_dataframes(original_df, honest_df):
    """
    Unify original_dataframe and honest_dataframe
    Args:
        original_df: Splited original line dataframe
        honest_df: duplicated result_df

    Returns:
        d_f: Imweb uniformed table
    """
    total_df = pd.concat([original_df, honest_df], axis=0, \
        ignore_index=True)
    total_df['플랫폼'] = '자사몰'
    return total_df

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


def total_unify_dataframes(naver_df, total_df):
    """
    Total Uniform functions
    Args:
        naver_df: Naver smartstore table
        total_df: Imweb uniformed table

    Returns:
        d_f: Total uniformed table
    """
    total = pd.concat([naver_df, total_df], axis=0, \
        ignore_index=True)
    total = total.fillna('X')
    return total                    


def total_uniform(p_d, iw_path, naver_path):
    """
    For whole functions
    Args:
        p_d: pandas
        iw_path: imweb excel path
        naver_path: naver excel path

    Returns:
        d_f: Total uniformed table
    """
    apply_pandas(pd)
    imweb_df = read_imweb_table(iw_path)
    imweb_df = rename_columns(imweb_df)
    imweb_df = strip_count_option(imweb_df)
    imweb_df = rename_delivery_option(imweb_df)
    imweb_df = change_product_name_by_option_add(imweb_df)
    imweb_df = change_product_name_by_option_remove(imweb_df)
    imweb_df = change_product_name_as_naver(imweb_df)
    original_df, honest_df = split_table_for_honest(imweb_df)
    honest_df = duplicate_honest_product_and_option(honest_df)
    imweb_df = unify_imweb_dataframes(original_df, honest_df)
    naver_df = read_naver_table(naver_path)
    total_df = total_uniform(naver_df, imweb_df)
    return total_df