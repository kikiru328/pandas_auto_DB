import pandas as pd
import json

def seperate_dataframe_for_recipe(d_f):
    """_summary_

    Args:
        d_f (_type_): _description_
    """
    subs_df_query = "상품명.str.contains('정기')"
    subs_df = df.query(subs_df_query)

    single_df_query = "상품명.str.contains('단품')"
    single_df = df.query(single_df_query)

    # seperate subs_df by options
    standard_df = subs_df[
        (subs_df['옵션유무'] == 'X')
        & (subs_df['상품명'] != '[윤식단][정기] 1일 2식 1일')
    ]

    standard_taste_df = subs_df[
        (subs_df['옵션유무'] == 'X')
        & (subs_df['상품명'] == '[윤식단][정기] 1일 2식 1일')
    ]
    ## same as 1일 1식

    option_df = subs_df[
        (subs_df['옵션유무'] != 'X')
        & (subs_df['고구마+현미밥'] == 'X')
    ]
    sw_r_df = subs_df[
        (subs_df['옵션유무'] != 'X')
        & (subs_df['고구마+현미밥'] != 'X')
    ]
    return standard_df, standard_taste_df, option_df, sw_r_df, single_df


def prepare_ingredient_standard(standard_df,menu_list):
    recipe_df = pd.DataFrame()
    for index, std_index in enumerate(standard_df.index):
        product = standard_df.loc[std_index, '상품명']
        dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0])
        if dining_count == 1:
            client_recipe = pd.DataFrame()
            for menu_name in menu_list[:2]:
                with open(f'./menu/{menu_name}.json','r') as recipe_file:
                    recipe = json.load(recipe_file)
                for type in ['메인재료','탄수화물','토핑재료']:
                    for ingredients in recipe['레시피'][type]:
                        for ingredient_name in ingredients.keys():
                            amount = ingredients[ingredient_name]['양']
                            client_recipe.loc[menu_name, ingredient_name] = amount
                client_recipe = client_recipe.fillna(0)
            if index == 0:
                recipe_df = client_recipe
            else:
                recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
                recipe_df = recipe_df.fillna(0)
                
        elif dining_count == 2:
            client_recipe = pd.DataFrame()
            for menu_name in menu_list[:4]:
                with open(f'./menu/{menu_name}.json','r') as recipe_file:
                    recipe = json.load(recipe_file)
                for type in ['메인재료','탄수화물','토핑재료']:
                    for ingredients in recipe['레시피'][type]:
                        for ingredient_name in ingredients.keys():
                            amount = ingredients[ingredient_name]['양']
                            client_recipe.loc[menu_name, ingredient_name] = amount
                client_recipe = client_recipe.fillna(0)
            if index == 0:
                recipe_df = client_recipe
            else:
                recipe_df = pd.concat([recipe_df,client_recipe],axis=0)     
                recipe_df = recipe_df.fillna(0)
        
        elif dining_count ==3 :
            client_recipe = pd.DataFrame()
            menu_by_condition = sorted(menu_list[:4] + menu_list[:2])
            for menu_name in menu_by_condition:
                with open(f'./menu/{menu_name}.json','r') as recipe_file:
                    recipe = json.load(recipe_file)
                for type in ['메인재료','탄수화물','토핑재료']:
                    for ingredients in recipe['레시피'][type]:
                        for ingredient_name in ingredients.keys():
                            amount = ingredients[ingredient_name]['양']
                            if menu_name in client_recipe.index:
                                client_recipe.loc[f'{menu_name}_1', ingredient_name] = amount
                            else:
                                client_recipe.loc[menu_name, ingredient_name] = amount
                client_recipe = client_recipe.fillna(0)
            if index == 0:
                recipe_df = client_recipe
            else:
                recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
                recipe_df = recipe_df.fillna(0)
                        
    standard_total_df = pd.DataFrame(recipe_df.T.sum(axis='columns').round(3))
    standard_total_df = standard_total_df.rename(columns = {0:'total'})
    return standard_total_df


def prepare_ingredient_standard_taste(standard_taste_df,menu_list):
    recipe_df = pd.DataFrame()
    for index, std_index in enumerate(standard_taste_df.index):
        product = standard_taste_df.loc[std_index, '상품명']
        dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0]) 
        client_recipe = pd.DataFrame()
        for menu_name in menu_list[:2]:
            with open(f'./menu/{menu_name}.json','r') as recipe_file:
                recipe = json.load(recipe_file)
            for type in ['메인재료','탄수화물','토핑재료']:
                for ingredients in recipe['레시피'][type]:
                    for ingredient_name in ingredients.keys():
                        amount = ingredients[ingredient_name]['양']
                        client_recipe.loc[menu_name, ingredient_name] = amount
            client_recipe = client_recipe.fillna(0)
        if index == 0:
            recipe_df = client_recipe
        else:
            recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
            recipe_df = recipe_df.fillna(0)
                
    standard_taste_total_df = pd.DataFrame(recipe_df.T.sum(axis='columns').round(3))
    standard_taste_total_df = standard_taste_total_df.rename(columns = {0:'total'})
    return standard_taste_total_df


def prepare_ingredient_option(option_df,menu_list):
    recipe_df = pd.DataFrame()
    for index, opt_index in enumerate(option_df.index):
        product = option_df.loc[opt_index, '상품명']
        dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0])
        count = 0
        client_recipe = pd.DataFrame()
        
        
        remove_option_columns = ['콩제외','당근제외','오이제외','기타','배송메세지']
        remove_options = []
        for rv_col in remove_option_columns:
            if option_df[rv_col][opt_index] != 'X':
                if '제외' in rv_col:
                    rev = rv_col.split('제외')[0]
                    remove_options.append(rev)
        
        
        add_protein = option_df.loc[opt_index, '단백질추가']
        add_carbon = option_df.loc[opt_index, '탄수화물추가']
        
        change_carbon_to_rice = option_df.loc[opt_index, '현미밥만']
        while count < dining_count * 2:
            for menu_name in menu_list:
                with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
                    recipe = json.load(recipe_file)
                    
                if menu_name in client_recipe.index:
                    menu_name = f'{menu_name}_1'
                else:
                    pass

                main_ingredients = []
                toping_ingredients = []
                carbon_ingredients = []
                
                for recipe_main in recipe['레시피']['메인재료']:
                    for ingredient_name in recipe_main.keys():
                        main_ingredients.append(ingredient_name)
                
                for recipe_toping in recipe['레시피']['토핑재료']:
                    for ingredient_name in recipe_toping.keys():
                        toping_ingredients.append(ingredient_name) 

                for recipe_carbon in recipe['레시피']['탄수화물']:
                    for ingredient_name in recipe_carbon.keys():
                        carbon_ingredients.append(ingredient_name)           


                removing_main_ingredient = []
                for i in remove_options:
                    for j in main_ingredients:
                        if i in j :
                            removing_main_ingredient.append(i)
                
                after_remove_toping = toping_ingredients.copy()
                removing_toping_ingredient = []
                for i in remove_options:
                    for j in toping_ingredients:
                        if i in j : 
                            removing_toping_ingredient.append(j)
                
                for remove_menu in removing_toping_ingredient:
                    after_remove_toping.remove(remove_menu)
                
                if len(removing_main_ingredient) != 0:
                    pass
                else:
                    for recipe_main in recipe['레시피']['메인재료']:
                        for ingredient_name in recipe_main.keys():
                            amount = recipe_main[ingredient_name]['양']
                            if add_protein != 'X':
                                add_amount = int(add_protein.split('g')[0].split('단백질 ')[1])
                                if add_amount == 50:
                                    client_recipe.loc[menu_name, ingredient_name] = amount * 1.5
                                elif add_amount == 100:
                                    client_recipe.loc[menu_name, ingredient_name] = amount * 2.0
                            else:
                                client_recipe.loc[menu_name, ingredient_name] = amount
                    
                    for recipe_carbon in recipe['레시피']['탄수화물']:
                        for ingredient_name in recipe_carbon.keys():
                            amount = recipe_carbon[ingredient_name]['양']
                            if add_carbon != 'X':
                                add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])
                                if add_amount == 50:
                                    client_recipe.loc[menu_name, ingredient_name] = amount * 1.5
                                elif add_amount == 100:
                                    client_recipe.loc[menu_name, ingredient_name] = amount * 2.0
                            else:
                                client_recipe.loc[menu_name, ingredient_name] = amount
                                
                            if (ingredient_name == '고구마') and (change_carbon_to_rice != 'X'):
                                change_ingredient_name = '현미밥'
                                client_recipe = client_recipe.rename(columns = {'고구마':'현미밥'})
                            else:
                                pass
                    
                    for ingredient_name in after_remove_toping:
                        for recipe_toping in recipe['레시피']['토핑재료']:
                            try:
                                amount = recipe_toping[ingredient_name]['양']
                                client_recipe.loc[menu_name, ingredient_name] = amount
                            except:
                                pass
                    
                    client_recipe = client_recipe.fillna(0)
                    count+=1
                
                if count == dining_count * 2:
                    break
        
        if index == 0:
            recipe_df = client_recipe
            recipe_df.index.name = 'MENU_NAME'
        else:
            client_recipe.index.name = 'MENU_NAME' 
            try:
                recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
            except:
                client_recipe = client_recipe.groupby(axis=1, level=0).sum()
                recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
            recipe_df = recipe_df.reset_index(drop=False)
            recipe_df = recipe_df.set_index('MENU_NAME')
            recipe_df = recipe_df.fillna(0)
    option_total_df = pd.DataFrame(recipe_df.T.sum(axis='columns').round(3))
    option_total_df = option_total_df.rename(columns = {0:'total'})
    option_total = option_total_df.T.groupby(axis=1, level=0).sum()
    return option_total


