"""
Change tables into uniformed table

Returns:
    .xlsx : uniformed for basic table
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
        '상품주문번호', '주문번호', '배송방법(구매자 요청)', '배송방법', '택배사', 
        '송장번호', '발송일', '구매자명', '수취인명', '상품명', '상품종류', 
        '옵션정보', '수량', '옵션가격', '상품가격', '상품별 총 주문금액', 
        '기본배송지', '상세배송지', '구매자연락처', '배송메세지', '정산예정금액', '수취인연락처1', '배송속성', '배송희망일', '결제일', '구매자ID', '우편번호']
    columns = d_f.columns.to_list()
    drop_columns = [x for x in columns if x not in need_columns]
    d_f = d_f.drop(drop_columns, axis=1)
    d_f = d_f.fillna(' ')
    d_f['배송지'] = d_f['기본배송지'] + ' ' + d_f['상세배송지']
    d_f['플랫폼'] = '네이버'
    return d_f

class change_product:
    
    def read_product_json(path):
        """

        Args:
            path (_type_): 상품명변환.json

        Returns:
            _type_: _description_
        """
        
        import json
        with open(path, 'r', encoding='UTF-8-sig') as product_change_file:
            product_change_json = json.load(product_change_file)
        naver = {}
        naver_product_name = []
        for set_ in product_change_json.get('naver_product_name'):
            naver.update({set_.get('네이버'):set_.get('변환')})
            naver_product_name.append(set_.get('네이버'))
            
            
        imweb = {}
        imweb_product_name = []
        for set_ in product_change_json.get('imweb_product_name'):
            imweb.update({set_.get('자사몰'):set_.get('변환')})
            imweb_product_name.append(set_.get('자사몰'))
        return naver, naver_product_name, imweb, imweb_product_name        
        

    def change_product_name(df,path):
        naver, naver_product_name, imweb, imweb_product_name = change_product.read_product_json(path)
        for order_id, platform_ in zip(df['주문번호'], df['플랫폼']):
            df_index = list(df[df['주문번호'] == order_id].index)
            for index_ in df_index:
                product_str = df.loc[index_, '상품명']
                if platform_ == '네이버':
                    if product_str in naver_product_name:
                        df.loc[index_, '상품명'] = naver.get(product_str)
                    else:
                        pass
                else:
                    if product_str in imweb_product_name:
                        df.loc[index_, '상품명'] = imweb.get(product_str)
                    else:
                        pass
        return df

class change_option:
    
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


    def read_option_json(path):
        """

        Args:
            path (_type_): 옵션정보.json
        """
        import json
        with open(path, 'r', encoding='utf-8') as option_file:
            options_info = json.load(option_file)
        return options_info
    


    def make_dict(options_info, title):
        dict_ = {}
        for col, row in zip(options_info.get(title).get('행'), options_info.get(title).get('열')):
            dict_.update({col:row})
            
        return dict_    


    def make_option_list(options_info, title, opt_list_count):
        list_ = []
        for opt in opt_list_count:
            for opt_row in options_info.get(title).get('행'):
                if opt_row in opt:
                    list_.append(opt)
                else:
                    pass
        return list_
    
    
    def change_func(d_f,option_list, options_info, main_idx, title):
        
        dict_ = change_option.make_dict(options_info, title)

        for col_ in options_info.get(title).get('열'):
            d_f.loc[main_idx, col_] = np.nan
            
        if len(option_list) != 0:
            for opt_ in option_list:
                for row_ in options_info.get(title).get('행'):
                    if row_ in opt_:
                        Col_ = dict_.get(row_)
                        d_f.loc[main_idx, Col_] = opt_
        return d_f


    def change_func_pack(d_f, main_df, order_id, option_list, options_info, main_idx, title):
        dict_ = change_option.make_dict(options_info, title)
        
        for col_ in options_info.get(title).get('열'):
            d_f.loc[main_idx, col_] = np.nan
            
        if len(option_list) != 0:
            box_idx_list = list(main_df[(main_df['주문번호']==order_id) & (main_df['상품명']=='[윤식단][단품] 닭고야/어니스트')].index)
            try:
                for box_idx in box_idx_list:
                    box_idx = box_idx
            except:
                pass
            for opt_ in option_list:
                for row_ in options_info.get(title).get('행'):
                    if row_ in opt_:
                        Col_ = dict_.get(row_)
                        d_f.loc[box_idx, Col_] = opt_
        return d_f


    def split_options_by_product(d_f, path):
        """
        Split product option to add option by customer.
        Args:
            d_f: Args for split_dataframe func
            path: 옵션정보.json
        Returns:
            d_f: resort by customer
        """
        d_f, main_df, option_df = change_option.split_dataframe(d_f)
        options_info = change_option.read_option_json(path)
        
        for order_id in option_df['주문번호'].to_list():
            main_idx = main_df[main_df['주문번호']==order_id].index[0]
            opt_list = list(option_df[option_df['주문번호'] == order_id]['상품명'])
            opt_count = list(option_df[option_df['주문번호'] == order_id]['수량'])
            opt_list_count = []
            for option, count in zip(opt_list, opt_count):
                count_str = ' X ' +str(count)
                opt_list_count.append(option+count_str)
            d_f.loc[main_idx,'옵션유무'] = 'O'

            add = change_option.make_option_list(options_info, '추가', opt_list_count)
            remove = change_option.make_option_list(options_info, '제거', opt_list_count)
            change = change_option.make_option_list(options_info, '변경', opt_list_count)
            pack = change_option.make_option_list(options_info, '팩', opt_list_count)
            etc = change_option.make_option_list(options_info, '기타', opt_list_count)
            
            d_f = change_option.change_func(d_f,add, options_info, main_idx, '추가')
            d_f = change_option.change_func(d_f,remove, options_info, main_idx, '제거')
            d_f = change_option.change_func(d_f,change, options_info, main_idx, '변경')
            d_f = change_option.change_func_pack(d_f,main_df, order_id, pack, options_info, main_idx,'팩')
            d_f = change_option.change_func(d_f,etc, options_info, main_idx, '기타')

            
            d_f = d_f.fillna('X')
            d_f = d_f[d_f['상품종류']=='조합형옵션상품']
        return d_f

class change_delivery_info:
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

def unify_table(p_d, naver_path, product_name_json_file, option_info_json_file):
    """
    Total functions
    Args:
        d_f: uniformed d_f

    Returns:
        d_f: uniformed for customer
    """
    apply_pandas(p_d)
    d_f = read_naver_table(naver_path)
    d_f = change_product.change_product_name(d_f, product_name_json_file)
    d_f = change_option.split_options_by_product(d_f, option_info_json_file)
    d_f = change_delivery_info.split_delivery_options(d_f)
    return d_f
        
    
    