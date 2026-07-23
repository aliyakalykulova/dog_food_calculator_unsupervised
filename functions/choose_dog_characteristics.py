import streamlit as st

# ---- Ввод характеристик собаки пользователем: возраст, вес, пол, репродуктивный статус, уровень активности, порода, заболевание

metrics_age_types=["в годах","в месецах"]
gender_types=["Самец", "Самка"]
rep_status_types=["Нет", "Щенность (беременность)", "Период лактации"]
berem_time_types=["первые 4 недедели беременности","последние 5 недель беременности"]
lact_time_types=["1 неделя","2 неделя","3 неделя","4 неделя"]
age_category_types=["puppy","adult","senior"]
size_types=["small",  "medium",  "large"]
activity_level_cat_1 = ["Пассивный (гуляеет на поводке менее 1ч/день)", "Средний1 (1-3ч/день, низкая активность)",
                        "Средний2 (1-3ч/день, высокая активность)", "Активный (3-6ч/день, рабочие собаки, например, овчарки)",
                        "Высокая активность в экстремальных условиях (гонки на собачьих упряжках со скоростью 168 км/день в условиях сильного холода)",
                        "Взрослые, склонные к ожирению"]
activity_level_cat_2 = ["Пассивный", "Средний", "Активный"]

# ---- Определение категории размера породы на основе стандартного веса собаки
def size_category(df):
   w = (df["min_weight"].iloc[0] + df["max_weight"].iloc[0]) / 2  
   if w <= 10:
      return size_types[0],w    # --- Категория "small"
   elif w <= 25:
      return size_types[1],w    # --- Категория "medium"
   else :
      return size_types[2],w    # --- Категория "large"

# ---- Определение возрастной категории на основе возраста и категории размера породы
def age_type_category(size_categ, age ,age_metric):
   # --- Перевод единицы измерения возраста из лет в месяцы
   if age_metric==metrics_age_types[0]:     
      age=age*12
     
   # --- Для мелких пород собак  
   if size_categ==size_types[0]:
      if age>=1*12 and age<=8*12:       # --- Категория "щенок"
         return age_category_types[1]
      elif age<1*12:                    # --- Категория "взрослый"
         return age_category_types[0]
      elif age>8*12:                    # --- Категория "пожилой"
         return age_category_types[2]
        
   # --- Для средних пород собак       
   elif size_categ==size_types[2]:
      if age>=15 and age<=7*12  :       # --- Категория "щенок"
         return age_category_types[1]   
      elif age<15:                      # --- Категория "взрослый" 
         return age_category_types[0]
      elif age>7*12:                    # --- Категория "пожилой"
         return age_category_types[2]
        
   # --- Для крупных пород собак             
   else:
      if age<=6*12 and age>=24:         # --- Категория "щенок"
         return age_category_types[1]
      elif age<24:                      # --- Категория "взрослый" 
         return age_category_types[0]
      elif age>6*12:                    # --- Категория "пожилой"
         return age_category_types[2]
               
# ---- Интерфейс выбора характеристик собаки
def choose_dog_characteristics(disease_df):
   st.set_page_config(page_title="Рекомендации по питанию собак", layout="centered")
   st.header("Рекомендации по питанию собак")
   col1, col0 ,col2, col3 = st.columns([3,1, 3, 2]) 
   with col1:
      weight = st.number_input("Вес собаки (в кг)", min_value=0.0, step=0.1)   # --- Ввод веса собаки
   with col2:
      age = st.number_input("Возраст собаки", min_value=0, step=1)             # --- Ввод возраста собаки
   with col3:
      age_metric=st.selectbox("Измерение возроста", metrics_age_types)         # --- Выбор единицы измерения возраста
   gender = st.selectbox("Пол собаки", gender_types)                           # --- Выбор пола собаки

   # --- При изменении пола собаки сбрасываются рассчитанные рекомендации к корму и репродуктивный статус
   if gender != st.session_state.select_gender:
      st.session_state.select_gender = gender
      st.session_state.show_result_1 = False
      st.session_state.show_result_2 = False
      st.session_state.select_reproductive_status = False
      st.session_state.show_res_berem_time = False
      st.session_state.show_res_num_pup = False
      st.session_state.show_res_lact_time = False

   # --- Если пол собаки "самка", отображается инструмент выбора репродуктивного статуса
   if st.session_state.select_gender == gender_types[1]:
      col1, col2 = st.columns([1, 20])  
      with col2:
         reproductive_status = st.selectbox( "Репродуктивный статус", rep_status_types)  # --- Ввод репродуктивного статуса собаки
        
      # --- При изменении репродуктивного статуса сбрасываются рассчитанные рекомендации к корму
      if reproductive_status != st.session_state.select_reproductive_status:
         st.session_state.select_reproductive_status = reproductive_status
         st.session_state.show_result_1 = False
         st.session_state.show_result_2 = False

   # --- Если репродуктивный статус "беременность" и пол "самка", отображается инструмент ввода срока беременности
   if st.session_state.select_reproductive_status==rep_status_types[1] and st.session_state.select_gender == gender_types[1]:
      col1, col2 = st.columns([3, 20])  
      with col2:            
         berem_time=st.selectbox("Срок беременности", berem_time_types)  # --- Ввод срока беременности
        
        # --- При изменении срока беременности сбрасываются рассчитанные рекомендации к корму
         if berem_time != st.session_state.show_res_berem_time:
            st.session_state.show_res_berem_time = berem_time
            st.session_state.show_result_1 = False
            st.session_state.show_result_2 = False 

   # --- Если репродуктивный статус "период лактации" и пол "самка", отображается инструмент ввода характеристик лактации
   elif st.session_state.select_reproductive_status==rep_status_types[2] and st.session_state.select_gender == gender_types[1]:
      col1, col2 = st.columns([3, 20])  
      with col2:  
         lact_time=st.selectbox("Лактационный период", lact_time_types)       # --- Ввод периода лактации 
         num_pup=st.number_input("Количесвто щенков", min_value=0, step=1)    # --- Ввод количества щенков

         # --- При изменении характеристик лактации сбрасываются рассчитанные рекомендации к корму
         if lact_time != st.session_state.show_res_lact_time or num_pup!=st.session_state.show_res_num_pup:
            st.session_state.show_res_lact_time = lact_time
            st.session_state.show_res_num_pup = num_pup
            st.session_state.show_result_1 = False
            st.session_state.show_result_2 = False 
              
   st.sidebar.title("🐶 Smart Dog Diet Advisor")
   st.sidebar.write("Select breed + disorder → get personalized food suggestions")
   st.sidebar.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=80)   
  
   breed_list = sorted(disease_df["name_breed"].unique())
   user_breed = st.selectbox("Порода собаки:", breed_list)   # --- Ввод породы собаки
   breed_size, avg_wight = size_category(disease_df[disease_df["name_breed"] == user_breed])  # --- Присвоение категории размера породы
   age_type_categ = age_type_category(breed_size, age ,age_metric)     # --- Присвоение возрастной категории

   # --- При изменении возраста, единицы измерения возраста или веса сбрасываются рассчитанные рекомендации к корму
   if age!=st.session_state.age_sel or age_metric!=st.session_state.age_metric or weight != st.session_state.weight_sel:
      st.session_state.age_sel=age
      st.session_state.age_metric=age_metric
      st.session_state.weight_sel=weight
      st.session_state.show_result_1 = False
      st.session_state.show_result_2 = False

   # --- При возрастной категории "взрослый" отображается инструмент ввода уровня активности (вариант 1)
   if age_type_categ==age_category_types[1]:
      activity_level_1 = st.selectbox("Уровень активности", activity_level_cat_1)
     
   # --- При возрастной категории "пожилой" отображается инструмент ввода уровня активности (вариант 2) 
   elif age_type_categ==age_category_types[2]:
      activity_level_2 = st.selectbox("Уровень активности",activity_level_cat_2)

  # --- При изменении уровня активности сбрасываются рассчитанные рекомендации к корму
   if age_type_categ==age_category_types[1]:
      if activity_level_1!=st.session_state.activity_level_sel:
         st.session_state.activity_level_sel=activity_level_1
         st.session_state.show_result_1 = False
         st.session_state.show_result_2 = False
   if age_type_categ==age_category_types[2]:
      if  activity_level_2!=st.session_state.activity_level_sel:
         st.session_state.activity_level_sel=activity_level_2
         st.session_state.show_result_1 = False
         st.session_state.show_result_2 = False
          
   return user_breed, breed_size, avg_wight, age_type_categ
