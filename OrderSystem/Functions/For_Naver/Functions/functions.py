import pandas as pd

def apply_pandas(pd):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    

def read_imweb_table(imweb_path):
    df = pd.read_excel(imweb_path)
    return df
    

def rename_columns(df):
    df['상품종류'] = ''
    
    df = df[
        '품목주문번호,주문번호,배송방법,택배사,송장번호,발송일,주문자명,수취인명,상품명,상품종류,옵션정보,수량,상품별 금액,최종결제금액,주소,주문자 연락처,배송메세지,수취인 연락처,결제일,상품번호,우편번호,계정'.split(',')]

    df = df.rename(columns = {
        '품목주문번호' : '상품주문번호',
        '주문번호' : '주문번호',
        '배송방법' : '배송방법',
        '택배사' : '택배사',
        '송장번호' : '송장번호',
        '발송일' : '발송일', 
        '주문자명' : '구매자명',
        '수취인명' : '수취인명',
        '상품명' : '상품명',
        '옵션정보' : '옵션정보',
        '수량' : '수량',
        '최종결제금액' : '상품별 총 주문금액',
        '주소' : '배송지',
        '주문자 연락처' : '구매자연락처',
        '배송메세지' : '배송메세지',
        '수취인 연락처' : '수취인연락처1',
        '결제일' : '결제일',
        '계정' : '구매자ID',
        '우편번호' : '우편번호'
    })
    
    df['상품주문번호'] = df['상품주문번호'].astype(str)
    df['주문번호'] = df['주문번호'].astype(str)
    return df
    

def seperate_delivery(df):
    for index, imweb_deliv in enumerate(df.배송지):
        try:
            basic_deliv = imweb_deliv.split(') ')[0]+')'
            detail_deliv = imweb_deliv.split(') ')[1]
            df.loc[index, '기본배송지'] = basic_deliv
            df.loc[index, '상세배송지'] = detail_deliv
        except:
            basic_deliv = imweb_deliv
            df.loc[index, '기본배송지'] = basic_deliv
        
    df = df.drop(columns = '배송지', axis=1)
    return df


def order_other_columns(df):
    naver_cols = [
    '상품주문번호', '주문번호', '배송방법(구매자 요청)', '배송방법', '택배사',
    '송장번호', '발송일', '구매자명', '수취인명', '상품명', '상품종류', '옵션정보',
    '수량', '옵션가격', '상품가격', '상품별 총 주문금액', '기본배송지', '상세배송지',
    '구매자연락처', '배송메세지', '정산예정금액', '수취인연락처1', '배송속성',
    '배송희망일', '결제일', '구매자ID', '우편번호', '상품번호', '옵션관리코드']
    for naver_col in naver_cols:
        if naver_col not in df:
            df[naver_col] = ''
            
    df = df[naver_cols]
    return df

    
def strip_count_option(df):
    df['옵션정보']= df['옵션정보'].apply(lambda x : x[:-5])
    return df


def rename_delivery_option(df):
    def rename_delivery(x):
        if "공동현관 비밀번호(없을시'없음'작성)" in x:
            x = x.replace("공동현관 비밀번호(없을시'없음'작성) :",
                         "공동현관 출입비밀번호 (없을 시 '없음'작성):")
            return x
        else:
            return x
    df['옵션정보']= df['옵션정보'].apply(lambda x : rename_delivery(x))
    return df    


def rename_delivery_option2(df):
    def rename_delivery2(x):
        if "배송방법 선택" in x:
            x = x.replace("배송방법 선택 :", "배송방법 선택:")
            return x
        else:
            return x
    df['옵션정보'] = df['옵션정보'].apply(lambda x : rename_delivery2(x))
    return df


def change_option(df,path):
    
    def read_option_json(path):
        """
        Args:
            path (_type_): 옵션정보.json
        """
        import json
        with open(path, 'r', encoding='utf-8') as option_file:
            options_info = json.load(option_file)
        return options_info
    
    options_info = read_option_json(path)
    
    def make_dict(options_info, title):
        dict_ = {}
        for col, row in zip(options_info.get(title).get('열'), options_info.get(title).get('행')):
            dict_.update({row:col})
            
        return dict_   

    def change_option_func(options_info, title, index_, option, df):
        if title == '추가':
            dict_ = make_dict(options_info, title)
            for key_ in dict_.keys():
                if key_ in option:
                    df.loc[index_, '상품명'] = option.split(' : ')[1]
                    df.loc[index_, '옵션정보'] = f'{dict_.get(key_)}: {option.split(" : ")[1]}'
                    df.loc[index_, '상품종류'] = '추가구성상품'
                    
        else:
            dict_ = make_dict(options_info, title)
            for key_ in dict_.keys():
                if key_ in option:
                    df.loc[index_, '상품명'] = option.split(' : ')[1]
                    df.loc[index_, '옵션정보'] = f'메뉴 변경 요청: {option.split(" : ")[1]}'
                    df.loc[index_, '상품종류'] = '추가구성상품'
                    
        return df       
     
    for index_, option in enumerate(df['옵션정보'].to_list()):        
        df = change_option_func(options_info, '추가', index_, option, df)
        df = change_option_func(options_info, '변경', index_, option, df)
        df = change_option_func(options_info, '제거', index_, option, df)
        df = change_option_func(options_info, '기타', index_, option, df)
    return df

def change_type(df):
    def type_fill(x):
        if x == '':
            return '조합형옵션상품'
        else:
            return x
        
    df['상품종류'] = df['상품종류'].apply(lambda x : type_fill(x))
    return df

def change_order_id(df):
    for purchase_name in list(df.구매자명.unique()):
        dfx = df[df['구매자명']==purchase_name]
        if len(dfx) > 1:
            x = []
            for type in list(dfx.상품종류):
                if type == '조합형옵션상품':
                    x.append(type)
                    
            if len(x) > 1:
                index_ = dfx.index.to_list()
                p_index_ = dfx[dfx['상품종류']=='조합형옵션상품'].index.to_list()
                
                for ind, p in enumerate(p_index_):
                    if ind == 0:
                        change_list = index_[index_.index(p)+1:]
                
                for change_ind in change_list:
                    order_id = str(int(df.loc[change_ind, '주문번호']) + 1)
                    df.loc[change_ind, '주문번호'] = order_id
    return df


# def change_product_name(df,path):
#     def read_product_json(path):
#         import json
#         with open(path, 'r', encoding='UTF-8-sig') as product_change_file:
#             product_change_json = json.load(product_change_file)
            
#         imweb = {}
#         imweb_product_name = []
#         for set_ in product_change_json.get('imweb_product_name'):
#             imweb.update({set_.get('자사몰'):set_.get('변환')})
#             imweb_product_name.append(set_.get('자사몰'))
#         return imweb, imweb_product_name

#     imweb, imweb_product_name = read_product_json(path)
#     for order_id in df['주문번호']:
#         df_index = list(df[df['주문번호'] == order_id].index)
#         for index_ in df_index:
#             product_str = df.loc[index_, '상품명']
#             if product_str in imweb_product_name:
#                 df.loc[index_, '상품명'] = imweb.get(product_str)
#             else:
#                 pass
#     return df

def change_rows_by_format(df):
    for index_ in df.index:     
        df.loc[index_,'배송방법(구매자 요청)'] = '직접전달'
        df.loc[index_,'배송방법'] = '직접전달' 
        df.loc[index_,'배송속성'] = '일반배송'
    
    # df['우편번호'] = df['우편번호'].astype(str)
    # df['상품번호'] = df['상품번호'].astype(str)   
    
    # def change_numb(x):
    #     if str(x).startswith('1'):
    #         pn = '0' + str(x)
    #         f_pn = pn[:3] + '-' + pn[3:7] + '-' + pn[7:]
    #     else:
    #         pn = '0' + str(x)
    #         f_pn = pn[:4] + '-' + pn[4:8] + '-' + pn[8:]
    #     return f_pn
    
    # df['구매자연락처'] = df['구매자연락처'].apply(lambda x : change_numb(x))
    # df['수취인연락처1'] = df['수취인연락처1'].apply(lambda x : change_numb(x))
    return df


class honest:
    def split_table_for_honest(df):
        honest_dataframe = df[df['상품명'] == '[Honest Line | 단품] 어니스트라인 (닭고야)']
        honest_indexes = honest_dataframe.index
        original_product_dataframe = df.drop(honest_indexes,axis=0)\
            .reset_index(drop=True)
        honest_dataframe = honest_dataframe.reset_index(drop=True)
        
        def split_honest_select_option(df):
            df['상품선택'] = ''
            for index_, option in enumerate(df['옵션정보'].to_list()):
                    df.loc[index_,'상품선택'] = option.split(' / 상품선택 : ')[1].split(' / ')[0]
                    df.loc[index_,'옵션정보'] = option.split(' / 상품선택 : ')[0] + ' / ' + '배송방법' + option.split(' / 배송방법')[1]
            # df = df.drop(columns = '상품선택',axis=1)
            return df
        honest_dataframe = split_honest_select_option(honest_dataframe)
        
        return original_product_dataframe, honest_dataframe        
    
    def read_option_json(path):
        """
        Args:
            path (_type_): 옵션정보.json
        """
        import json
        with open(path, 'r', encoding='utf-8') as option_file:
            options_info = json.load(option_file)
        return options_info
    

    def honest_option_information(df, honest_options_json_file):
        dfo, dfh = honest.split_table_for_honest(df)
        honest_options_info = honest.read_option_json(honest_options_json_file)

        def make_dict_honest(options_info, title):
            dict_ = {}
            for col, row in zip(options_info.get(title).get('변환'), options_info.get(title).get('옵션')):
                dict_.update({row:col}) 
            return dict_   

        dict_ = make_dict_honest(honest_options_info, '어니스트')
        
        return dfo, dfh, honest_options_info, dict_
    
    
    def add_honest_options(df,honest_options_json_file):
        dfo, dfh, honest_options_info, dict_ = honest.honest_option_information(df,honest_options_json_file)
        
        import pandas as pd
        temp_df = pd.DataFrame(columns = dfh.columns)
        for index_, (order_id, pack_option) in enumerate(zip(dfh.주문번호.to_list(), dfh.상품선택.to_list())):
            og = dfh[dfh['주문번호']==order_id]
            temp = dfh[dfh['주문번호'] == order_id]
            ind = temp.index[0]
            for key_ in dict_.keys():
                if index_ == 0 :
                    if key_ in pack_option:
                        temp.loc[ind, '상품명'] = dict_[key_]
                        temp.loc[ind, '옵션정보'] = f'어니스트: {dict_[key_]}'
                        temp_concat = pd.concat([temp,og], axis=0, ignore_index=True)
                        temp_concat = temp_concat.drop('상품선택', axis=1)
                        temp_df = temp_concat.copy()
                    else:
                        og = og.drop('상품선택', axis=1)
                        temp_df = og.copy()
                else:
                    if key_ in pack_option:
                        temp.loc[ind, '상품명'] = dict_[key_]
                        temp.loc[ind, '옵션정보'] = f'어니스트: {dict_[key_]}'
                        temp_concat = pd.concat([temp,og], axis=0, ignore_index=True)
                        temp_concat = temp_concat.drop('상품선택', axis=1)
                        temp_df = pd.concat([temp_df,temp_concat],axis=0, ignore_index=True)
                    else:
                        og = og.drop('상품선택', axis=1)
                        temp_df = pd.concat([temp_df,og],axis=0,ignore_index=True)
                        
        df_ = pd.concat([dfo, temp_df], axis=0, ignore_index=True)
        return df_


def get_folder_path():
    from datetime import datetime as dt
    import os
    folder_name = './' + dt.today().strftime('%Y-%m-%d_%H')
    os.makedirs(folder_name, exist_ok=True)

    og_file_path = f'{folder_name}/자사몰_오리지널_변환.xlsx'
    ho_file_path = f'{folder_name}/자사몰_어니스트_변환.xlsx'
    return og_file_path, ho_file_path


def reformation_columns(df):
    re_df = df.copy()
    re_df['배송지'] = re_df['기본배송지'] + ' ' + re_df['상세배송지']
    re_df = re_df.drop(columns = '기본배송지', axis=1)
    re_df = re_df.drop(columns = '상세배송지', axis=1)
    return re_df


def reformation_other_columns(df):
    import numpy as np
    naver_cols = [
    '상품주문번호', '주문번호', '배송방법(구매자 요청)', '배송방법', '택배사', '송장번호', '발송일', '구매자명',
       '수취인명', '상품명', '상품종류', '옵션정보', '수량', '옵션가격', '상품가격', '상품별 총 주문금액',
       '배송지', '구매자연락처', '배송메세지', '정산예정금액', '수취인연락처1', '배송속성', '배송희망일', '결제일',
       '구매자ID', '우편번호']
    for naver_col in naver_cols:
        if naver_col not in df:
            df[naver_col] = np.nan
            
    df = df[naver_cols]

           
    return df


def preprocessing(imweb_path, option_path, product_path, honest_options_json_file):
    imweb_df = read_imweb_table(imweb_path)
    imweb_df = rename_columns(imweb_df)
    imweb_order = seperate_delivery(imweb_df)
    imweb_order = order_other_columns(imweb_order)
    imweb_order = strip_count_option(imweb_order)
    imweb_order = rename_delivery_option(imweb_order)
    imweb_order = rename_delivery_option2(imweb_order)
    imweb_order = change_option(imweb_order,option_path)
    
    imweb_order = change_type(imweb_order)
    imweb_order = change_order_id(imweb_order)
    # imweb_order = change_product_name(imweb_order, product_path)
    imweb_order = change_rows_by_format(imweb_order)
    imweb_order = honest.add_honest_options(imweb_order,honest_options_json_file)
    # imweb_reformation = reformation_columns(imweb_order)
    # honest_reformation = reformation_columns(honest_order)
    # imweb_reformation = reformation_other_columns(imweb_reformation)
    # honest_reformation = reformation_other_columns(honest_reformation)
    
    # imweb_upload = imweb_reformation.copy()
    # honest_upload = honest_reformation.copy()
    
    return imweb_order
# , imweb_reformation, imweb_upload, honest_order, honest_reformation, honest_upload

# def Save_functions(imweb_order, imweb_reformation, imweb_upload, honest_order, honest_reformation, honest_upload):
#     from datetime import datetime as dt
#     import pandas as pd
#     import os
#     import shutil

#     folder_name = './'+'output/'+ dt.today().strftime('%Y-%m-%d_%H')
#     dt_str = str(dt.today().strftime('%Y-%m-%d_%H'))
#     os.makedirs(folder_name, exist_ok=True)

#     og_file_path = f'{folder_name}/자사몰_오리지널_변환.xlsx'
#     ho_file_path = f'{folder_name}/자사몰_어니스트_변환.xlsx'
    

#     imweb_order.to_excel(og_file_path,encoding='utf-8-sig',index=0,sheet_name='주문서')
#     honest_order.to_excel(ho_file_path,encoding='utf-8-sig',index=0,sheet_name='주문서')

    
#     zipfile = shutil.make_archive(f'./output/{dt_str}_변환완료','zip',folder_name)
#     shutil.rmtree(folder_name)
    
#     return zipfile

def total(imweb_path,option_path,product_path,honest_options_json_file):
    imweb_order = preprocessing(imweb_path, option_path, product_path,honest_options_json_file)
    # zipfile = Save_functions(imweb_order, imweb_reformation, imweb_upload, honest_order, honest_reformation, honest_upload)
    return imweb_order
    