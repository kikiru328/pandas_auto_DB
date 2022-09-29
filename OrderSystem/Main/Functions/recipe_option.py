import pandas as pd
import json

def seperate_dataframe_for_recipe(d_f):
    """_summary_

    Args:
        d_f (_type_): _description_
    """
    
    ### 추가 옵션이 있다면 ###
    for index, additional_option in enumerate(d_f['고객요청옵션'].to_list()):
        if additional_option != 'X':
            d_f.loc[index, '옵션유무'] = 'O'
        else:
            pass
        
    
    subs_df_query = "상품명.str.contains('정기')"
    subs_df = d_f.query(subs_df_query)

    single_df_query = "상품명.str.contains('단품')"
    single_df = d_f.query(single_df_query)

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

class StandardIngredient:
    def prepare_ingredient_standard(standard_df,menu_list):
        recipe_df = pd.DataFrame()
        for index, std_index in enumerate(list(standard_df.index)):
            product = standard_df.loc[std_index, '상품명']
            dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0])
            if dining_count == 1:
                client_recipe = pd.DataFrame()
                for menu_name in menu_list[:2]:
                    with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
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
                    with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
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
                    with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
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
        standard_total_df = standard_total_df.T.groupby(axis=1, level=0).sum()
        return standard_total_df


    def prepare_ingredient_standard_taste(standard_taste_df,menu_list,single_check):
        recipe_df = pd.DataFrame()
        single_menu_list = [menu_name for menu_name, single_popular in zip(menu_list, single_check) if single_popular == True]
        
        for index, std_index in enumerate(standard_taste_df.index):
            product = standard_taste_df.loc[std_index, '상품명']
            # dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0]) 
            client_recipe = pd.DataFrame()
            for menu_name in single_menu_list:
                with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
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
        standard_taste_total_df = standard_taste_total_df.T.groupby(axis=1, level=0).sum()
        return standard_taste_total_df

class OptionIngredient:
    
    def check_menu_list(menu_list,remove_options,additional_option):
        client_menu = menu_list.copy()
        for index, menu_name in enumerate(menu_list):
            with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
                recipe = json.load(recipe_file)
            main_ingredients = []
            for recipe_main in recipe['레시피']['메인재료']:
                for ingredient_name in recipe_main.keys():
                    main_ingredients.append(ingredient_name)      
            removing_main_ingredient = []
            for i in remove_options:
                for j in main_ingredients:
                    if i in j :
                        removing_main_ingredient.append(i)
            if len(removing_main_ingredient) != 0:
                print(f'{menu_name} 제외')
                client_menu.remove(menu_name) 
            else:
                pass
        if len(client_menu) == 5: # 전체가 다 포함 
            client_menu =  client_menu[:4] # 메인 2, 서브1 (2)            
        else: # 전체가 다 포함되지 않을 경우
            client_menu =  client_menu
            
        if additional_option == '메뉴동일': # 메뉴동일일시, 앞 2개는 같아야 함.
            return client_menu[:2]
        else: # 아니면
            return client_menu # 그냥 return
    
    
    def prepare_ingredient_option(option_df,menu_list):
        recipe_df = pd.DataFrame()
        for index, opt_index in enumerate(list(option_df.index)):    
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
            
            # print(menu_list)
            ### ADDITIONAL_OPTION
            # print(product)
            
            additional_option = option_df.loc[opt_index, '고객요청옵션']
            
            # print(additional_option)
            
            client_menu_list = OptionIngredient.check_menu_list(menu_list, remove_options,additional_option)
            
            # print(client_menu_list)
            
            ################ 전 메뉴 제외 ######################
            
            if len(client_menu_list) == 0 :
                # print('#################################################################################################################')
                # print('client_menu_list', len(client_menu_list))
                # print('#################################################################################################################')
                next
            else:
                    
                # print('Dining_count', dining_count)
                
                need_menu_count = dining_count * 2 
                
                # print('need_menu_count',need_menu_count) 
                
                if additional_option == '1팩추가':
                    need_menu_count += 1
                else:
                    pass
                # print('Additional_menu_count', need_menu_count)
                # print('====================')
                while count < need_menu_count:
                    
                    for menu_name in client_menu_list:
                        with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
                            recipe = json.load(recipe_file)
                        
                    
                        if menu_name in client_recipe.index:
                            menu_name = f'{menu_name}_{count}'
                        else:
                            pass
                        
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
                        
                        
                        carbon_ingredients = []
                        for recipe_carbon in recipe['레시피']['탄수화물']:
                            for ingredient_name in recipe_carbon.keys():
                                carbon_ingredients.append(ingredient_name)            
                            
                        if len(recipe['레시피']['탄수화물']) != 0:
                            if '고구마' in carbon_ingredients:
                                for recipe_carbon in recipe['레시피']['탄수화물']: # 탄수화물 딕션
                                    for ingredient_name in recipe_carbon.keys(): # 탄수화물 Key
                                        amount = recipe_carbon[ingredient_name]['양'] # 탄수화물 양
                                        
                                        
                                        if ingredient_name == '고구마':
                                            if add_carbon != 'X': # 탄수화물 추가
                                                add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])
                                                if add_amount == 50:
                                                    if change_carbon_to_rice != 'X': # 현미밥만
                                                        add_ingredient_name = '현미밥'
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 0.5 #고구마 50
                                                        client_recipe.loc[menu_name, add_ingredient_name] = amount #현미밥 100
                                                    else: # 그냥
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 1.5 #고구마 150
                                                        
                                                elif add_amount == 100:
                                                    if change_carbon_to_rice != 'X': # 현미밥만
                                                        add_ingredient_name = '현미밥'
                                                        client_recipe.loc[menu_name, add_ingredient_name] = amount * 2.0 # 현미밥 200
                                                    else:
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 2.0 # 고구마 200
                                                        
                                            else: # 추가 없음                                   
                                                client_recipe.loc[menu_name, ingredient_name] = amount # 고구마 그대로
                                                
                                        else:
                                            client_recipe.loc[menu_name, ingredient_name] = amount
                                            
                                            
                                            
                            else: # 탄수화물은 있음. 고구마가 없음.
                                for recipe_carbon in recipe['레시피']['탄수화물']: # 탄수화물 딕션
                                    for ingredient_name in recipe_carbon.keys(): # 탄수화물 key
                                        amount = recipe_carbon[ingredient_name]['양'] # 탄수화물 양
                                        
                            ############### 애초에 고구마가 없음 ###################
                            
                                        if add_carbon != 'X': #추가가 있으면
                                            add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])
                                            if add_amount == 50:
                                                if change_carbon_to_rice != 'X': #현미밥만
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본 레시피 탄수화물
                                                    
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.05   
                                                else: #그냥
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본 레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.05  
                                                    
                                            elif add_amount == 100:
                                                if change_carbon_to_rice != 'X':  #현미밥만
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본 레시피 탄수화물
                                                    add_ingredient_name = '현미밥'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.1
                                                else: # 그냥
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본 레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.1
                                                    
                                        else: # 추가 없음
                                            client_recipe.loc[menu_name, ingredient_name] = amount                            
                        
                        else: # 탄수화물 없음. 고구마도 없음. > 조회 필요없음. 추가만.
                            if add_carbon != 'X': # 추가가 있으면
                                add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])
                                
                                if add_amount == 50:
                                    if change_carbon_to_rice != 'X': #현미밥만
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.05   
                                    else: #그냥
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.05  
                                            
                                elif add_amount == 100:
                                    if change_carbon_to_rice != 'X': # 현미밥만
                                        add_ingredient_name = '현미밥'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.1
                                    else: # 그냥
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.1                            
                                        
                            else: # 추가가 없으면
                                pass

                        toping_ingredients = []
                        for recipe_toping in recipe['레시피']['토핑재료']:
                            for ingredient_name in recipe_toping.keys():
                                toping_ingredients.append(ingredient_name) 
                                                        
                        after_remove_toping = toping_ingredients.copy()
                        removing_toping_ingredient = []
                        for i in remove_options:
                            for j in toping_ingredients:
                                if i in j : 
                                    removing_toping_ingredient.append(j)  
                        for remove_menu in removing_toping_ingredient:
                            after_remove_toping.remove(remove_menu)

                        for ingredient_name in after_remove_toping:
                            for recipe_toping in recipe['레시피']['토핑재료']:
                                try:
                                    amount = recipe_toping[ingredient_name]['양']
                                    client_recipe.loc[menu_name, ingredient_name] = amount
                                except:
                                    pass
                        
                        
                        client_recipe = client_recipe.fillna(0)
                        count+=1
                        if count == need_menu_count:
                            break
                        
                # display(client_recipe)        
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
        # display(option_total)
        return option_total

    def prepare_ingredient_sw_r(sw_r_df, menu_list,rice_check):
        recipe_df = pd.DataFrame()
        menu_dict_with_rice = {}
        for menu_name, rice in zip(menu_list, rice_check):
            menu_dict_with_rice.update({menu_name:rice})

        # print(menu_dict_with_rice)
        # print('==========================================')

        for index, opt_index in enumerate(sw_r_df.index):
            product = sw_r_df.loc[opt_index, '상품명']
            count = 0
            dining_count = int(product.split('] ')[1].split(' ')[1].split('식')[0])
            client_recipe = pd.DataFrame()            
            remove_option_columns = ['콩제외','당근제외','오이제외','기타','배송메세지']
            remove_options = []
            for rv_col in remove_option_columns:
                if sw_r_df[rv_col][opt_index] != 'X':
                    if '제외' in rv_col:
                        rev = rv_col.split('제외')[0]
                        remove_options.append(rev)    
            add_protein = sw_r_df.loc[opt_index, '단백질추가']
            add_carbon = sw_r_df.loc[opt_index, '탄수화물추가']
            change_carbon_to_rice = sw_r_df.loc[opt_index, '고구마+현미밥'] 
            
            # print(menu_list)
            ### ADDITIONAL_OPTION
            additional_option = sw_r_df.loc[opt_index, '고객요청옵션']
            
            # print(additional_option)
             
            client_menu_list = OptionIngredient.check_menu_list(menu_list, remove_options,additional_option)
            
            # print(client_menu_list)
            
            ################ 전 메뉴 제외 ######################
            
            if len(client_menu_list) == 0 :
                # print('#################################################################################################################')
                # print('client_menu_list', len(client_menu_list))
                # print('#################################################################################################################')
                next
            else:
                
                # print(client_menu_list)
                
                
                
                # print(product)
                # print(client_menu_list)
                # print(add_carbon)
                # print('-----------')
                
                # print('Dining_count', dining_count)
                
                need_menu_count = dining_count * 2
                
                # print('need_menu_count',need_menu_count)
                
                if additional_option == '1팩추가':
                    need_menu_count += 1
                else:
                    pass
                
                # print('Additional_menu_count', need_menu_count)
                # print('==========================')
                
                
                while count < need_menu_count:
                    for menu_name in client_menu_list:
                        with open(f'./menu/{menu_name}.json','r',encoding='utf-8-sig') as recipe_file:
                            recipe = json.load(recipe_file)
                    
                        if menu_name in client_recipe.index:
                            menu_name = f'{menu_name}_{count}'
                        else:
                            pass
                        
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
                                    
                                    
                        # 탄수화물
                        carbon_ingredients = []
                        for recipe_carbon in recipe['레시피']['탄수화물']:
                            for ingredient_name in recipe_carbon.keys():
                                carbon_ingredients.append(ingredient_name) 
                        # print(f'[{menu_name}]' )    
                        # print('탄수화물  carbon_ingredients : ', carbon_ingredients)
                        # 만약 이 메뉴가 현미밥을 주는 메뉴인가


                        if menu_name[-1:].isnumeric() == True:
                            Temp_menu_name = menu_name[:-2]
                        else:
                            Temp_menu_name = menu_name
                            
                        # print('MENU_NAME', menu_name)
                        # print('TEMP_MENU_NAME', Temp_menu_name)    
                        # print(f'이 메뉴가 현미밥을 주는 메뉴인가   {menu_name} : {menu_dict_with_rice[Temp_menu_name]}')                
                        
                        if menu_dict_with_rice[Temp_menu_name] == True: # 현미밥을 주는 메뉴일경우
                            if len(recipe['레시피']['탄수화물']) != 0: # 탄수화물이 있음
                                if '고구마' in carbon_ingredients: # 고구마가 있다.                                        
                                    for recipe_carbon in recipe['레시피']['탄수화물']: #탄수화물 딕션
                                        for ingredient_name in recipe_carbon.keys(): #탄수화물 키
                                            amount = recipe_carbon[ingredient_name]['양']
                                                
                            ############################## 여긴 모두 고구마 + 현미밥 ###############################
                                                
                                                                                
                                            if ingredient_name == '고구마':
                                                if add_carbon != 'X': #탄수화물추가
                                                    add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                                    
                                                    if add_amount == 50:
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 0.5 #고구마 50
                                                        add_ingredient_name = '현미밥'
                                                        client_recipe.loc[menu_name, add_ingredient_name] = amount #현미밥 100
                                                            
                                                    elif add_amount == 100:
                                                        client_recipe.loc[menu_name, ingredient_name] = amount   #고구마 100
                                                        add_ingredient_name = '현미밥'
                                                        client_recipe.loc[menu_name, add_ingredient_name] = amount  # 현미밥 100
                                                        
                                                else: # 추가 없음
                                                    #### 현미밥을 주는 메뉴 >> 현미밥을 준다 <<
                                                    add_ingredient_name = '현미밥'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = amount # 기본 고구마 100
                                                    
                                            else: # 고구마가 아닌 탄수화물 재료
                                                client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물

                                else: # 탄수화물 재료 중에 고구마가 없다.
                                    ###### 현미밥을 주는 메뉴이지만, 다른 탄수화물이 존재한다. >> 현미밥 제공 X <<< ### 
                                    
                                    for recipe_carbon in recipe['레시피']['탄수화물']: #탄수화물 딕션
                                        for ingredient_name in recipe_carbon.keys(): #탄수화물 키
                                            amount = recipe_carbon[ingredient_name]['양']
                                                
                            ############################## 여긴 모두 고구마 + 현미밥 ###############################
                                                                                                
                                            if add_carbon != 'X': #탄수화물추가
                                                add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                                
                                                if add_amount == 50:
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.05 # 고구마 50
                                                            
                                                elif add_amount == 100:
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.1  # 고구마 100
                                                    
                                            else: # 추가 없음
                                                client_recipe.loc[menu_name, ingredient_name] = amount # 기본 고구마 100
                            
                            
                            else: #탄수화물이 없음.
                                ####### 현미밥을 주는 메뉴이지만, 다른 탄수화물도 없다. >>> 현미밥을 제공 X <<< ###
                                ### 조회 필요없음 바로 추가만 ###
                                
                                if add_carbon != 'X': #탄수화물추가
                                    add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                    
                                    if add_amount == 50:
                                        client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.05 # 고구마 50
                                                
                                    elif add_amount == 100:
                                        client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.1  # 고구마 100
                                        
                                else: # 추가 없음
                                    pass
                                        
                                    
                        else: # 그냥 메뉴일경우
                            if len(recipe['레시피']['탄수화물']) != 0: # 탄수화물이 있음
                                if '고구마' in carbon_ingredients: # 고구마가 있다.                                        
                                    for recipe_carbon in recipe['레시피']['탄수화물']: #탄수화물 딕션
                                        for ingredient_name in recipe_carbon.keys(): #탄수화물 키
                                            amount = recipe_carbon[ingredient_name]['양']
                                                
                            ############################## 여긴 모두 고구마 + 현미밥 ###############################
                            ###### 현미밥 안줌  >> 현미밥 제공 X <<< ###                    
                                                                                
                                            if ingredient_name == '고구마':
                                                if add_carbon != 'X': #탄수화물추가
                                                    add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                                    
                                                    if add_amount == 50:
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 1.5 #고구마 150
                                                            
                                                    elif add_amount == 100:
                                                        client_recipe.loc[menu_name, ingredient_name] = amount * 2.0   #고구마 200
                                                        
                                                        
                                                else: # 추가 없음
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본 고구마 100      
                                                    
                                                    
                                            else: # 고구마가 아닌 탄수화물 재료
                                                client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물

                                else: # 탄수화물 재료 중에 고구마가 없다.
                                    ###### 현미밥 안줌 다른 탄수화물이 존재한다. >> 현미밥 제공 X <<< ### 
                                    
                                    for recipe_carbon in recipe['레시피']['탄수화물']: #탄수화물 딕션
                                        for ingredient_name in recipe_carbon.keys(): #탄수화물 키
                                            amount = recipe_carbon[ingredient_name]['양']
                                                
                            ############################## 여긴 모두 고구마 + 현미밥 ###############################
                                                                                                
                                            if add_carbon != 'X': #탄수화물추가
                                                add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                                
                                                if add_amount == 50:
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.05 # 고구마 50
                                                            
                                                elif add_amount == 100:
                                                    client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                                    add_ingredient_name = '고구마'
                                                    client_recipe.loc[menu_name, add_ingredient_name] = 0.1  # 고구마 100
                                                    
                                            else: # 추가 없음
                                                client_recipe.loc[menu_name, ingredient_name] = amount # 기본 고구마 100
                            
                            
                            else: #탄수화물이 없음.
                                ###### 현미밥 안줌 다른 탄수화물이 존재한다. >> 현미밥 제공 X <<< ### 
                                ### 조회 필요없음 바로 추가만 ###
                                
                                if add_carbon != 'X': #탄수화물추가
                                    add_amount = int(add_carbon.split('g')[0].split('탄수화물 ')[1])    
                                    
                                    if add_amount == 50:
                                        client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.05 # 고구마 50
                                                
                                    elif add_amount == 100:
                                        client_recipe.loc[menu_name, ingredient_name] = amount # 기본레시피 탄수화물
                                        add_ingredient_name = '고구마'
                                        client_recipe.loc[menu_name, add_ingredient_name] = 0.1  # 고구마 100
                                        
                                else: # 추가 없음
                                    pass     
                            
                        toping_ingredients = []
                        for recipe_toping in recipe['레시피']['토핑재료']:
                            for ingredient_name in recipe_toping.keys():
                                toping_ingredients.append(ingredient_name) 
                        after_remove_toping = toping_ingredients.copy()
                        removing_toping_ingredient = []
                        for i in remove_options:
                            for j in toping_ingredients:
                                if i in j : 
                                    removing_toping_ingredient.append(j)
                        for remove_menu in removing_toping_ingredient:
                            after_remove_toping.remove(remove_menu)
                            
                            
                        for ingredient_name in after_remove_toping:
                            for recipe_toping in recipe['레시피']['토핑재료']:
                                try:
                                    amount = recipe_toping[ingredient_name]['양']
                                    client_recipe.loc[menu_name, ingredient_name] = amount
                                except:
                                    pass
                            
                        client_recipe = client_recipe.fillna(0)
                        count+=1

                        
                        if count == need_menu_count:
                            break
                    # display(client_recipe)
                    # print('=========================')
                if index == 0:
                    recipe_df = client_recipe
                    recipe_df.index.name = 'MENU_NAME'
                else:
                    client_recipe.index.name = 'MENU_NAME'
                    try:
                        recipe_df = pd.concat([recipe_df, client_recipe],axis=0)
                    except:
                        client_recipe = client_recipe.groupby(axis=1, level=0).sum()
                        recipe_df = pd.concat([recipe_df, client_recipe], axis=0)
                    recipe_df = recipe_df.reset_index(drop=False)
                    recipe_df = recipe_df.set_index('MENU_NAME')
                    recipe_df = recipe_df.fillna(0)
            option_total_df = pd.DataFrame(recipe_df.T.sum(axis='columns').round(3))
            option_total_df = option_total_df.rename(columns = {0:'total'})
            option_total = option_total_df.T.groupby(axis=1, level=0).sum()
            return option_total 
    
    

class HonestIngredient:
    
    def prepare_ingredient_honest(honest_df):
        ############################### 여기는 모두 닭고야 / 어니스트 #####################################
        recipe_df = pd.DataFrame()
        for index, single_index in enumerate(honest_df.index):
            client_recipe = pd.DataFrame()
            # Option _ Pack 수 파악
            single_pack = honest_df.loc[single_index, '단품옵션']
            set_pack = honest_df.loc[single_index, '세트옵션']
            # print('single_pack',single_pack)
            # print('set_pack',set_pack)
            count = 0
            # print(set_pack.split('팩')[0][-1])
            # print(single_pack.split('팩')[0][-1])
            
            try: 
                count += int(single_pack.split('팩')[0][-1])
                count += int(set_pack.split('팩')[0][-1])
                
            except ValueError:
                count = 0
                if single_pack == 'X':
                    count += int(set_pack.split('팩')[0][-1])    
                else:
                    count += int(single_pack.split('팩')[0][-1])

            # print('수량', count)
            with open('./menu/어니스트.json', 'r', encoding ='utf-8-sig') as recipe_file:
                recipe = json.load(recipe_file)
                
            for recipe_main in recipe['레시피']['메인재료']:
                for ingredient_name in recipe_main.keys():
                    amount = recipe_main[ingredient_name]['양']
                    # print(ingredient_name, amount)
                    client_recipe.loc['어니스트', ingredient_name] = amount * count
            # display(client_recipe)
            
            if index == 0 :
                recipe_df = client_recipe
                recipe_df.index.name = 'MENU_NAME'
            else:
                client_recipe.index.name = 'MENU_NAME'
                try:
                    recipe_df = pd.concat([recipe_df, client_recipe], axis=0)
                except:
                    client_recipe = client_recipe.groupby(axis=1, level=0).sum()
                    recipe_df = pd.concat([recipe_df,client_recipe],axis=0)
                    
                    
                    
            recipe_df = recipe_df.reset_index(drop=False)
            recipe_df = recipe_df.set_index('MENU_NAME')
            recipe_df = recipe_df.fillna(0)
            # display(recipe_df)
            # print('-------------------------------------')
        # display(recipe_df)    
        option_total_df = pd.DataFrame(recipe_df.T.sum(axis='columns').round(3))
        option_total_df = option_total_df.rename(columns = {0:'total'})
        option_total = option_total_df.T.groupby(axis=1, level=0).sum()
        return option_total       
        # display(option_total)


class TotalGathering:

    def calculate_each_df(Total_df,menu_list,rice_check,single_check):
        standard_df, standard_taste_df, option_df, sw_r_df, honest_df = seperate_dataframe_for_recipe(d_f = Total_df)
        
        standard_total  = StandardIngredient.prepare_ingredient_standard(standard_df = standard_df,
                                                                         menu_list = menu_list)
        standard_taste_total = StandardIngredient.prepare_ingredient_standard_taste(standard_taste_df = standard_taste_df,
                                                                                    menu_list = menu_list,
                                                                                    single_check = single_check)
        option_total = OptionIngredient.prepare_ingredient_option(option_df = option_df,
                                                                  menu_list = menu_list)
        sw_r_total = OptionIngredient.prepare_ingredient_sw_r(sw_r_df = sw_r_df,
                                                              menu_list = menu_list,
                                                              rice_check = rice_check)
        hon_total = HonestIngredient.prepare_ingredient_honest(honest_df = honest_df)
        
        Total_recipe = pd.concat([standard_total,standard_taste_total,option_total,sw_r_total,hon_total],axis=0)
        
        Total_recipe = Total_recipe.fillna(0)
        Total_recipe = Total_recipe.groupby(axis=0, level=0).sum()
        return Total_recipe