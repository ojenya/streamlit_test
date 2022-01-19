import streamlit as st
import pandas as pd
import SessionState
import datetime
from pathlib import Path

#######################################################
# Загрузка пакетов для работы с вопросами теста из файла
import pandas as pd
import os
import re
import numpy as np
from PIL import Image
from IPython.core.display import display

# Пути (надо менять)
PATH_TO_FOLDER = 'C:/Users/Софья/Desktop/адаптивное тестирование/'  # Путь к папке с данными
PATH_TO_PIC = 'C:/Users/Софья/Desktop/адаптивное тестирование/test_pic_full/'  # Путь к папке с картинками
FILE_NAME = 'test_full.xlsx'  # Имя файла с данными
PATH_TO_FILE = PATH_TO_FOLDER + FILE_NAME

# Читаем excel для проверки вопросов
df = pd.read_excel(PATH_TO_FILE, dtype=str, index_col=0)

# Список колонок с вопросами:
list_questions_columns = []
for i in df.columns.tolist():
    list_questions_columns.extend(re.findall('Вариант \d', i))

# Номера правильных ответы:
true_answer = df['Номера правильных ответов']

#Правильные ответы текстом
true_answer_text = df['Правильный ответ']

# Замена пропусков нулями:
for i in list_questions_columns:
    df[i] = df[i].fillna(0)

# Список с индексами вопросов, в которых есть картинка
list_questions_with_pic = df[df['Картинка'] == 'да'].index.tolist()

# Записываем в переменные картинки из папки
files = os.listdir(PATH_TO_PIC)
pics = dict()
lst = [i for i in files if i.startswith('q_')]
for i in lst:
    pic = Image.open(PATH_TO_PIC + i)
    pics.update({int(i[2:-4]): pic})

# генерация банка эл-ов, если пользователь не может предоставить
from catsim.cat import generate_item_bank
# пакет моделирования содержит Симулятор и все абстрактные классы
from catsim.simulation import *
# пакет инициализации содержит различные стратегии начальной оценки квалификации
from catsim.initialization import *
# пакет содержит разные методы выбора элемента из банка
from catsim.selection import *
# пакет оценки содержит различные методы оценки квалификации
from catsim.estimation import *
# кртитерии остановки CAT
from catsim.stopping import *
import catsim.plot as catplot
from catsim.irt import icc

import random

import matplotlib.pyplot as plt

# Задается для всех испытуемых одинаковая способность.
# например, хотим, чтобы все начали с первого уровня
initializer = FixedPointInitializer(-2)

# первоначальный уровень тета (уровень студента), который мы задали ранее
est_theta = initializer.initialize()
print('Examinee initial proficiency:', est_theta)

# достижение максимального количсетва элементов
stopper1 = MaxItemStopper(25)

# достижение минимальной стандартной ошибки оценки (тета)
stopper2 = MinErrorStopper(0.7)

# выбор следующего элемента
selector = RandomesqueSelector(3)

# оценка значений способностей испытуемых, учитывая дихотомический (бинарный) вектор ответа и массив вопросов
estimator = NumericalSearchEstimator(precision=6, dodd=True, verbose=False, method='bounded')

# создаем массив сложости и заполняем его значениями из общего массива q -> q[i][3][0]
b = []
for i in range(1, len(df['Уровень сложности']) + 1):
    b.append(int(df['Уровень сложности'][i]))
b = np.array(b)
# Стандартизуем переменные
b = np.array(b)
b = -2 + (b - b.min()) / (b.max() - b.min()) * 4

# Item Matrix со сложностями вопроса IRT 1
items = irt.normalize_item_bank(numpy.array([b]).T)
#######################################################

# Скрыть разное на странице
hide_menu = """
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: visible;
}

footer:after {
    content:'Тест для проверки уровня грамотности в данных';
    display:block;
    position:relative;
    color:black;
    padding:50
}
</style>    
"""
#Запустить сокрытие всякого на странице
st.markdown(hide_menu, unsafe_allow_html=True)

# список страниц

#option_names = ["main_form", "question_1", "question_2", "question_3", 'last_page']

option_names = ['main_form']
for i in range(1, len(df)+1):
    option_names.append('question_' + str(i))
option_names.append('last_page')

#получить номер первого вопроса
def get_first_quest():
    return selector.select(items=items, administered_items=st.session_state['administr_items'],
                           est_theta=st.session_state['est_theta'])

#функция для получения следующего вопроса. Алгоритм адаптивного тестирования
def get_next_qestion():
    _stop1 = False
    _stop2 = False
    # определяем нужные перемнные
    # список элементов, на которые ответил пользователь
    administered_items = st.session_state['administr_items']
    # овтеты пользователя, храятся в формате верно/неверно
    responses = st.session_state['right_answ']

    # Задается для всех испытуемых одинаковая способность.
    # например, хотим, чтобы все начали с первого уровня
    initializer = st.session_state['initializer']

    # первоначальный уровень тета (уровень студента), который мы задали ранее
    est_theta = st.session_state['est_theta']

    # col_true = 0  # Число правильных ответов
    # kol_vopr = 0

    # Выбор нового объекта
    # Селектор берет матрицу параметров элемента и текущее значение θ ^, чтобы выбрать новый элемент, на который ответит испытуемый.
    # Он использует индексы уже использованных элементов, чтобы игнорировать их.
    # на основании овтета опредляем новое значение тета
    item_index = selector.select(items=items, administered_items=administered_items, est_theta=est_theta)
    # kol_vopr = kol_vopr + 1
    # print()
    # print('Текущий номер вопроса:', kol_vopr)
    print('Номер вопроса из банка:', item_index)
    # print()
    # print(df.iloc[item_index]['Вопрос'])
    # try:
    #     display(pics[item_index + 1])
    # except KeyError:
    #     pass
    # for q in list_questions_columns:
    #     if df.iloc[item_index][q] != 0:
    #         print(df[q].name, df.iloc[item_index][q])
    # print()
    # answer = input('Введите через пробел номера правильных ответов: ')
    # if answer == true_answer[item_index + 1]:
    #     correct = True
    # else:
    #     correct = False
    # print(correct)
    # administered_items.append(item_index)
    # responses.append(correct)
    est_theta = estimator.estimate(items=items, administered_items=administered_items, response_vector=responses,
                                   est_theta=est_theta)
    st.session_state['est_theta'] = est_theta
    # Проверка, следует ли закончить тест
    _stop1 = stopper1.stop(administered_items=items[administered_items], theta=est_theta)
    _stop2 = stopper2.stop(administered_items=items[administered_items], theta=est_theta)
    print('Предполагаемый уровень знаний:', est_theta)
    print('Точность оценки:', irt.see(est_theta, items[administered_items]))
    return [item_index+1, _stop1, _stop2]

#функция для проверки ответа
def check_answ(df_dict_one_funct):
    date_res = pd.DataFrame()
    data_res_a = pd.DataFrame.from_dict(df_dict_one_funct)
    st_ans = ''
    i = 0
    index_ans_many = 0
    index_ans = 0
    print((data_res_a))

    if len(data_res_a.columns)>0 and data_res_a.columns[i] != 'time':
        index_ans = int(data_res_a.columns[i].split('_')[1])
        st.session_state['administr_items'].append(index_ans-1)
        print(index_ans)
        while i < len(data_res_a.columns) and len(data_res_a.columns)>1:
            if data_res_a[data_res_a.columns[i]][0]:
                index_ans_many = int(data_res_a.columns[i].split('_')[2]) + 1
                st_ans = st_ans + str(index_ans_many) + ', '
            i = i + 1
        if st_ans != '':
            st_ans = st_ans.replace(",", "")
            data_res_a[data_res_a.columns] = st_ans[:-1]

        print(data_res_a[data_res_a.columns[0]][0])
        print(true_answer_text.iloc[index_ans - 1])
        if (data_res_a[data_res_a.columns[0]][0] == true_answer_text.iloc[index_ans - 1]):
            st.session_state['right_answ'].append(True)
            print(True)
        else:
            st.session_state['right_answ'].append(False)
            print(False)
        return get_next_qestion()
    pass

#функция для считывания овтета из строки
def read_answ_line(item_index):
    if int(df.iloc[item_index]['Правильных ответов']) == 0:
        df_dict_l ={}
        j="question_"+str(item_index+1)
        question_l = df.iloc[item_index]['Вопрос']
        df_dict_l[j] = [st.text_input(question_l)]
        st.session_state['last_answ'] = df_dict_l
        pass
    pass



# конструкция позволяющая при нажатии кнопки "далее" переходить к следующей вкладке
next = st.button("Далее")
if next:
    #go_to_page = int(st.session_state['next_page'])
    # if st.session_state['option_main_form'] != 1:
    #     read_answ_line(option_names.index(st.session_state["radio_option"])-1)
    result_check_answ = check_answ(st.session_state['last_answ'])
    print(result_check_answ)
    print(st.session_state['administr_items'])
    st.session_state['last_answ'] = {}
    if st.session_state['option_last_form'] == 1:
        st.session_state.radio_option = option_names[option_names.index(st.session_state["radio_option"])]
    elif st.session_state['option_main_form']==1:
        first_quest = get_first_quest()
        print(first_quest)
        st.session_state.radio_option = option_names[first_quest]
    elif result_check_answ[0]<len(option_names):
        if not (result_check_answ[1] or result_check_answ[2]):
            st.session_state.radio_option = option_names[result_check_answ[0]]
        else:
            st.session_state.radio_option = option_names[len(option_names)-1]

# Оформление страниц как списка слева при запуске
option = st.sidebar.radio("Pick an option", option_names , key="radio_option")


# Позволяет сохранить файлы по окончании сессии
session_state = SessionState.get(name='', img=None)


# Структура вопросов
if option == 'main_form':
    df_dict = {}
    df_dict_one = {}
    df_dict['firstname'] = [st.text_input('Введите имя')]
    df_dict['secondname'] = [st.text_input('Введите Фамилию')]
    df_dict['login'] = [st.text_input('Введите рабочий логин, например ivanov.ie')]
    session_state.img = df_dict
    index_next_page = 1
    # st.session_state['next_page'] = index_next_page
    st.session_state['last_answ'] = df_dict_one
    st.session_state['administr_items'] = []
    st.session_state['right_answ'] = []
    st.session_state['est_theta'] = initializer.initialize()
    st.session_state['initializer'] = FixedPointInitializer(-2)
    st.session_state['option_main_form'] = 1
    st.session_state['option_last_form'] = 0
else:
    st.session_state['option_main_form'] = 0

for i, j in enumerate(option_names[1:-1], 0):
    if option == j:
        # #содержит число, которое представляет страницу для перехода
        # index_next_page = st.text_input('Введите число')
        # if (index_next_page != ''):
        #     st.session_state['next_page'] = index_next_page
        df_dict_one = st.session_state['last_answ']
        df_dict = session_state.img
        item_index = i
        question = df.iloc[item_index]['Вопрос']
        answer = []
        for q in list_questions_columns:
            if df.iloc[item_index][q] != 0:
                answer.append(df.iloc[item_index][q])
        answer = tuple(answer)
        if int(df.iloc[item_index]['Правильных ответов']) == 1:
            df_dict[j] = [st.radio(question, answer)]
            session_state.img = df_dict
            df_dict_one[j] = df_dict[j]
            try:
                st.image(pics[item_index + 1])
            except KeyError:
                pass
            #print(df_dict)
        else:
            if int(df.iloc[item_index]['Правильных ответов']) == 0:
                df_dict[j] = [st.text_input(question)]
                session_state.img = df_dict
                df_dict_one[j] = df_dict[j]
                try:
                    st.image(pics[item_index + 1])
                except KeyError:
                    pass
            else:
                df_dict = session_state.img
                st.write(question)
                for a, answ in enumerate(answer, 0):
                    df_dict[j + '_' + str(a)] = [st.checkbox(answ)]
                    df_dict_one[j + '_' + str(a)] = df_dict[j + '_' + str(a)]
                session_state.img = df_dict
                try:
                    st.image(pics[item_index + 1])
                except KeyError:
                    pass
        st.session_state['last_answ'] = df_dict_one


if option == 'last_page':
    st.session_state['option_last_form'] = 1
    df_dict = session_state.img
    st.header('Тест окончен')

    # По нажатии кнопки происходит сохранение
    if (st.button("Отправить результаты")):
        df_dict['time'] = datetime.datetime.now()
        st.text("Ваш тест отправлен!")

        # Проверяем создан ли файл
        # Если нет, создаем
        # Если создан - дописываем
        if Path('C:/Users/Софья/Desktop/адаптивное тестирование/temp.xlsx').is_file():
            df = pd.read_excel('C:/Users/Софья/Desktop/адаптивное тестирование/temp.xlsx')
            df = df.append(pd.DataFrame.from_dict(df_dict))
            df.to_excel('C:/Users/Софья/Desktop/адаптивное тестирование/temp.xlsx', index=False)
        else:
            pd.DataFrame.from_dict(df_dict).to_excel('C:/Users/Софья/Desktop/адаптивное тестирование/temp.xlsx', index=False)

        date_res=pd.DataFrame()
        data_res_a=pd.DataFrame.from_dict(df_dict)
        date_res['firstname'] = [data_res_a['firstname'][0]]
        date_res['secondname'] = [data_res_a['secondname'][0]]
        date_res['login'] = [data_res_a['login'][0]]
        date_res['time'] = [data_res_a['time'][0]]
        print(len(data_res_a.columns))
        print(data_res_a)
        st_ans=''
        i=3
        index_ans_many=0
        index_ans = 0
        while i<len(data_res_a.columns)-2:
            if data_res_a.columns[i]!='time':
                date_res[data_res_a.columns[i]] = [data_res_a.columns[i]]
                date_res[data_res_a.columns[i]][0]=data_res_a[data_res_a.columns[i]][0]
                k=i
                index_ans=int(data_res_a.columns[i].split('_')[1])
                while data_res_a.columns[i].split('_')[1] == data_res_a.columns[i+1].split('_')[1]:
                    if data_res_a[data_res_a.columns[i]][0]:
                        index_ans_many=int(data_res_a.columns[i].split('_')[2])+1
                        st_ans=st_ans+str(index_ans_many)+', '
                    i = i + 1
                if st_ans!='':
                    if data_res_a[data_res_a.columns[i]][0]:
                        index_ans_many = int(data_res_a.columns[i].split('_')[2]) + 1
                        st_ans=st_ans+str(index_ans_many)+', '
                    date_res[data_res_a.columns[k]][0]=st_ans[:-2]
            if (data_res_a[data_res_a.columns[i]][0] == true_answer_text.iloc[index_ans-1]):
                date_res['корректность ответа на вопрос '+ data_res_a.columns[i].split('_')[1]] = True
            else:
                date_res['корректность ответа на вопрос '+ data_res_a.columns[i].split('_')[1]] = False
            st_ans = ''
            i=i+1
        #df.iloc[item_index][q]
        print(date_res)

        # Проверяем создан ли файл
        # Если нет, создаем
        # Если создан - дописываем
        if Path('C:/Users/Софья/Desktop/адаптивное тестирование/result.xlsx').is_file():
            df = pd.read_excel('C:/Users/Софья/Desktop/адаптивное тестирование/result.xlsx')
            df = df.append(pd.DataFrame.from_dict(date_res))
            df.to_excel('C:/Users/Софья/Desktop/адаптивное тестирование/result.xlsx', index=False)
        else:
            pd.DataFrame.from_dict(date_res).to_excel('C:/Users/Софья/Desktop/адаптивное тестирование/result.xlsx',
                                                     index=False)

