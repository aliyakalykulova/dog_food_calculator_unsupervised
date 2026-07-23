import streamlit as st

# ---- Данные переменные используются для проверки: при изменении данных пользователем текущие параметры сбрасываются
# ---- Например: при изменении характеристик собаки сбрасываются рассчитанные рекомендации (калории, ингредиенты, количество нутриентов)
# ---- При изменении параметров корма сбрасывается рассчитанная рецептура (перерасчёт выполняется с учётом новых параметров)

def init_global():
   if "show_result_1" not in st.session_state: 
      st.session_state.show_result_1 = False      # --- Отображение рекомендаций после нажатия кнопки расчёта рекомендаций
   if "show_result_2" not in st.session_state:
      st.session_state.show_result_2 = False      # --- Отображение финальной рецептуры после нажатия кнопки расчёта рецептуры

   if "age_sel" not in st.session_state:
      st.session_state.age_sel = None           # --- Возраст собаки
   if "age_metr_sel" not in st.session_state:
      st.session_state.age_metr_sel = None     # --- Единица измерения возраста (месяцы / годы)
   if "weight_sel" not in st.session_state:
      st.session_state.weight_sel = None       # ---  Вес собаки (кг)
   if "activity_level_sel" not in st.session_state:
      st.session_state.activity_level_sel = None    # --- Уровень активности собаки
   if "select_gender" not in st.session_state:
      st.session_state.select_gender = None             # --- Пол собаки (самец/самка)
	   
   if "select_reproductive_status" not in st.session_state:
      st.session_state.select_reproductive_status = None   # --- Репродуктивный статус (нет, беременность, лактация)
   if "show_res_berem_time" not in st.session_state:
      st.session_state.show_res_berem_time = None       # --- Срок беременности
   if "show_res_lact_time" not in st.session_state:
      st.session_state.show_res_lact_time = None       # --- Срок лактации
   if "show_res_num_pup" not in st.session_state:
      st.session_state.show_res_num_pup = None          # --- Количество щенков 
	
   if "user_breed" not in st.session_state: 
      st.session_state.user_breed = None        # --- Порода собаки
   if "disorder" not in st.session_state:
      st.session_state.disorder = None        # --- Заболевание 
		
   if "kkal_sel" not in st.session_state:
      st.session_state.kkal_sel = None         # --- Суточная потребность в калориях
				
   if "prev_ingr_ranges" not in st.session_state:
      st.session_state.prev_ingr_ranges = []     # --- Соотношение ингредиентов
   if "prev_nutr_ranges" not in st.session_state:
      st.session_state.prev_nutr_ranges = {}     # --- Соотношение нутриентов
	   
   if "selected_ingredients" not in st.session_state:
      st.session_state.selected_ingredients = set()         # --- Список ингредиентов
   if st.session_state.show_result_1 == False: 
      st.session_state.selected_ingredients = set()
		
