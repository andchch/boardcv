import asyncio
import os

import streamlit as st
from telegram.error import BadRequest, InvalidToken

import telegram_integration

st.sidebar.success('Выберите страницу')

st.title('Распознавание нескольких файлов')

local = os.getcwd() + '\\imgs'
st.markdown(f'Сканирование директории `{local}` на наличие файлов для распознавания')

st.button('Просканировать директорию')

#st.write('типа появились изображения')

st.button('Распознать')

with st.expander('Результаты распознавания'):
    st.write('resul 1')

st.subheader('Отправка результата\nСКРЫТЬ ДО ЗАГРУЗКИ ФОТО')
telegram_tab, email_tab, zulip_tab, local_tab = st.tabs(['Telegram', 'Email', 'Zulip', 'Скачать'])
with telegram_tab:
    tg_username = st.text_input(label='Введите свой телеграм в произвольном формате!!!!!!!!!!!!!!')
    st.toggle(label='Приложить загруженное изображение', key=1)
    if st.button('Отправить'):
        try:
            asyncio.run(telegram_integration.send_message(tg_username, 'ТЕКСТ ДЛЯ ОТПРАВКИ'))
        except BadRequest:
            st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
        except InvalidToken:
            st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')
with email_tab:
    target_email = st.text_input(label='Введите свой email!!!!!!!!!!!!!!')
    st.toggle(label='Приложить загруженное изображение', key=2)
    if st.button('Отправить', key=151):
        try:
            asyncio.run(telegram_integration.send_message(tg_username, 'ТЕКСТ ДЛЯ ОТПРАВКИ'))
        except BadRequest:
            st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
        except InvalidToken:
            st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')
with zulip_tab:
    zulip_username = st.text_input(label='Введите свой zulip в произвольном формате!!!!!!!!!!!!!!')
    st.toggle(label='Приложить загруженное изображение',key=3)
    if st.button('Отправить', key=4684):
        try:
            asyncio.run(telegram_integration.send_message(tg_username, 'ТЕКСТ ДЛЯ ОТПРАВКИ'))
        except BadRequest:
            st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
        except InvalidToken:
            st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')
with local_tab:
    st.write('Скачать файл в формате .txt')
    st.download_button('Скачать', data='test.txt')