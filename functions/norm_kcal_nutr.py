import streamlit as st

# ---- Расчёт нормы суточного потребления калорий и нутриентов для собаки

metrics_age_types=["в годах","в месецах"]
gender_types=["Самец", "Самка"]
rep_status_types=["Нет", "Щенность (беременность)", "Период лактации"]
berem_time_types=["первые 4 недедели беременности","последние 5 недель беременности"]
lact_time_types=["1 неделя","2 неделя","3 неделя","4 неделя"]
age_category_types=["puppy","adult","senior"]

activity_level_cat_1 = ["Пассивный (гуляеет на поводке менее 1ч/день)", "Средний1 (1-3ч/день, низкая активность)",
                        "Средний2 (1-3ч/день, высокая активность)", "Активный (3-6ч/день, рабочие собаки, например, овчарки)",
                        "Высокая активность в экстремальных условиях (гонки на собачьих упряжках со скоростью 168 км/день в условиях сильного холода)",
                        "Взрослые, склонные к ожирению"]
activity_level_cat_2 = ["Пассивный", "Средний", "Активный"]


# ---- Расчёт нормы суточного потребления калорий
def kcal_calculate(age_type, expected):
   reproductive_status=st.session_state.select_reproductive_status
   berem_time=st.session_state.show_res_berem_time
   num_pup=st.session_state.show_res_num_pup
   L_time=st.session_state.show_res_lact_time
   weight=st.session_state.weight_sel
   activity_level=st.session_state.activity_level_sel
   age=st.session_state.age_sel
   user_breed=st.session_state.user_breed
    
   formula=""    # --- Вывод формулы, по которой выполнен расчёт калорий
   page=""       # --- Ссылка на страницу онлайн-документа FEDIAF, где была взята формула 

   # --- Коэффициент для расчёта калорий в зависимости от периода лактации
   if L_time==lact_time_types[0]:
      L=0.75
   elif L_time==lact_time_types[1]:
      L=0.95
   elif L_time==lact_time_types[2]:
      L=1.1
   else :
      L=1.2

   # ---- Расчёт калорий с учётом репродуктивного статуса
   # --- Беременность	
   if reproductive_status==rep_status_types[1]:
      if berem_time==berem_time_types[0]:     # --- Расчёт для первых 4 недель беременности
         kcal=132*(weight**0.75)
         formula= r"kcal = 132 \cdot вес^{0.75}  \\  \text{(первые 4 недели беременности)}"
         page = "56"
      else:                                   # --- Расчёт для последних 5 недель беременности
         kcal=132*(weight**0.75) + (26*weight)
         formula= r"kcal = 132 \cdot вес^{0.75} + 26 \cdot вес  \\  \text{(последние 5 недель беременности)}"
         page = "56"

   # --- Лактационный период		
   elif reproductive_status==rep_status_types[2]:
      if num_pup<5:         # --- Расчёт при количестве щенков меньше 5
         kcal=145*(weight**0.75) + 24*num_pup*weight*L
         formula = fr"kcal = 145 \cdot вес^{{0.75}} + 24 \cdot n \cdot вес \cdot L  \\  \text{{n - количество щенков}}  \\  \text{{L = {L} для {L_time}}}"
         page = "56"
      else:                 # --- Расчёт при количестве щенков больше 5
         kcal=145*(weight**0.75) + (96+12*num_pup-4)*weight*L
         formula = fr"kcal = 145 \cdot вес^{{0.75}}  + (96 + 12 \cdot n - 4) \cdot вес \cdot L    \\  \text{{n - количество щенков}}  \\  \text{{L = {L} для {L_time}}}"       
         page = "56"

  # --- При отсутствии репродуктивного статуса
   else:
	  # --- Расчёт калорий для щенков
      if age_type==age_category_types[0]:
         if age<2:                         # --- Щенки до 2 месяцев            
            kcal=25 * weight 
            formula= r"kcal = 25 \cdot вес"
            page = "56"
         elif age>=2 and age <12:          # --- Щенки от 2 месяцев до 1 года
            kcal=(254.1-135*(weight/expected) )*(weight**0.75)
            formula=fr"kcal = \left(254.1 - 135 \cdot \frac{{вес}}{{w}}\right) \cdot вес^{{0.75}}  \\  w = {round(expected,2)}  \text{{кг ;  предположительный вес для породы {user_breed}}}"
            page = "56"
         else:
            kcal=130*(weight**0.75)        # --- Щенки старше 1 года
            formula= r"kcal = 130 \cdot вес^{0.75}"
            page = "54"
			 
	  # --- Расчёт калорий для пожилых собак
      elif age_type==age_category_types[2]:
         if activity_level==activity_level_cat_2[0]:    # --- Пасивные
            kcal=80*(weight**0.75)
            formula= r"kcal = 80  \cdot вес^{0.75}"
            page = "54"
         elif activity_level==activity_level_cat_2[1]:  # --- Среднеактивные
            kcal=95*(weight**0.75)
            formula= r"kcal = 95  \cdot вес^{0.75}"
            page = "54"    
         else:                                          # --- Активные
            kcal=110*(weight**0.75)
            formula= r"kcal = 110  \cdot вес^{0.75}"
            page = "54"
			 
	  # --- Расчёт калорий для взрослых собак
      else:   
         if activity_level==activity_level_cat_1[0]:     # --- Пасивные
            kcal=95*(weight**0.75)
            formula= r"kcal = 95  \cdot вес^{0.75}"
            page = "55"
         elif activity_level==activity_level_cat_1[1]:   # --- Низкоактивные
            kcal=110*(weight**0.75)
            formula= r"kcal = 110  \cdot вес^{0.75}"
            page = "55"
         elif activity_level==activity_level_cat_1[2]:   # --- Среднеактивные
            kcal=125*(weight**0.75)
            formula= r"kcal = 125  \cdot вес^{0.75}"
            page = "55"
         elif activity_level==activity_level_cat_1[3]:   # --- Активные
            kcal=160*(weight**0.75)
            formula= r"kcal = 160  \cdot вес^{0.75}"
            page = "55"
         elif activity_level==activity_level_cat_1[4]:  # --- Очень активные (гонки в собачьей упряжке в экстремальных условиях)
            kcal=860*(weight**0.75)
            formula= r"kcal = 860  \cdot вес^{0.75}"
            page = "55"
         else:                                          # --- Для взрослых собак, склонных к ожирению
            kcal=90*(weight**0.75)
            formula= r"kcal = 90  \cdot вес^{0.75}"
            page = "55"
				
   st.markdown(f"Было рассчитано по формуле")
   st.latex(formula)
   url = "https://europeanpetfood.org/wp-content/uploads/2024/09/FEDIAF-Nutritional-Guidelines_2024.pdf#page=" + page
   st.markdown(f"[Подробнее]({url})")   
   kcal= 0 if kcal<0 else kcal
   return kcal


# ---- Расчёт нормы суточного потребления нутриентов
def nutrient_norm(kkal, age_type_categ,  w, reproductive_status):
   # ---- Для щенков
   if age_type_categ==age_category_types[0]:
      nutrients_per_1000_kcal = {
         "calcium_mg": 3000*kkal/1000,
         "phosphorus_mg": 2500*kkal/1000,
         "magnesium_mg": 100*kkal/1000,
         "sodium_mg": 550*kkal/1000,
         "potassium_mg": 1100*kkal/1000,
         "iron_mg": 22*kkal/1000,
         "copper_mg": 2.7*kkal/1000,
         "zinc_mg": 25*kkal/1000,
         "manganese_mg": 1.4*kkal/1000,

         "vitamin_a_mcg": 378.9*kkal/1000,
         "vitamin_d_mcg": 3.4*kkal/1000,
         "vitamin_e_mg": 7.5*kkal/1000,
         "vitamin_b1_mg": 0.34*kkal/1000,
         "vitamin_b2_mg": 1.32*kkal/1000,
         "vitamin_b3_mg": 4.25*kkal/1000,
         "vitamin_b6_mg": 0.375*kkal/1000,
         "vitamin_b12_mcg": 8.75*kkal/1000,
                         
         "selenium_mcg": 87.5*kkal/1000,
         "choline_mg": 425*kkal/1000,
         "vitamin_b5_mg": 3.75*kkal/1000,
         "linoleic_acid_g": 3.3*kkal/1000,
         "vitamin_b9_mcg": 68*kkal/1000,
         "alpha_linolenic_acid_g": 0.2*kkal/1000,
         "arachidonic_acid_g": 0.08*kkal/1000,
         "epa_g(50-60%) + dha_g(40-50%)": 0.13*kkal/1000,
           
         "iodine_mcg": 220*kkal/1000,
         "Биотин (мкг)": 4*kkal/1000 }
      return nutrients_per_1000_kcal
	   
   # --- Для беременных или в период лактации
   elif reproductive_status==rep_status_types[1] or reproductive_status==rep_status_types[2]:
      nutrients_per_1000_kcal = {
         "calcium_mg": 1900*kkal/1000,
         "phosphorus_mg": 1200*kkal/1000,
         "magnesium_mg": 150*kkal/1000,
         "sodium_mg": 500*kkal/1000,
         "potassium_mg": 900*kkal/1000,
         "iron_mg": 17*kkal/1000,
         "copper_mg": 3.1*kkal/1000,
         "zinc_mg": 24*kkal/1000,
         "manganese_mg": 1.8*kkal/1000,

         "vitamin_a_mcg": 378.9*kkal/1000,
         "vitamin_d_mcg": 3.4*kkal/1000,
         "vitamin_e_mg": 7.5*kkal/1000,
         "vitamin_b1_mg": 0.56*kkal/1000,
         "vitamin_b2_mg": 1.3*kkal/1000,
         "vitamin_b3_mg": 4.25*kkal/1000,
         "vitamin_b6_mg": 0.375*kkal/1000,
         "vitamin_b12_mcg": 8.75*kkal/1000,

         "selenium_mcg": 87.5*kkal/1000,
         "choline_mg": 425*kkal/1000,
         "vitamin_b5_mg": 3.75*kkal/1000,
         "vitamin_b9_mcg": 67.5*kkal/1000,
         "linoleic_acid_g": 3.3*kkal/1000,
         "alpha_linolenic_acid_g": 0.2*kkal/1000,
         "epa_g(50-60%) + dha_g(40-50%)": 0.13*kkal/1000,

         "iodine_mcg": 220*kkal/1000,
         "Биотин": 4*kkal/1000}
      return nutrients_per_1000_kcal

   # --- Для взрослых и пожилых 	
   else:  
      other_for_adult = {
         "calcium_mg": 130*(w**0.75),
         "phosphorus_mg": 100*(w**0.75),
         "magnesium_mg": 19.7*(w**0.75),
         "sodium_mg": 26.2*(w**0.75),
         "potassium_mg": 140*(w**0.75),
         "iron_mg": 1.0*(w**0.75),
         "copper_mg": 0.2*(w**0.75),
         "zinc_mg": 2.0*(w**0.75),
         "manganese_mg": 0.16*(w**0.75),

         "vitamin_a_mcg": 4.175*(w**0.75),
         "vitamin_d_mcg": 0.45*(w**0.75),
         "vitamin_e_mg": 1.0*(w**0.75),
         "vitamin_b1_mg": 0.074*(w**0.75),
         "vitamin_b2_mg": 0.171*(w**0.75),
         "vitamin_b3_mg": 0.57*(w**0.75),
         "vitamin_b6_mg": 0.049*(w**0.75),
         "vitamin_b12_mcg": 1.15*(w**0.75),

         "selenium_mcg": 11.8*(w**0.75),
         "iodine_mcg": 29.6*(w**0.75),
         "vitamin_b5_mg": 0.49*(w**0.75),
         "vitamin_b9_mcg": 8.9*(w**0.75),
         "choline_mg": 56*(w**0.75),
         "linoleic_acid_g": 0.36*(w**0.75),
         "alpha_linolenic_acid_g": 0.014*(w**0.75),
         "epa_g(50-60%) + dha_g(40-50%)": 0.03*(w**0.75) }
      return other_for_adult

	   
