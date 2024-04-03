import os
import base64
import asyncio
import streamlit as st
from telegram.error import BadRequest, InvalidToken
import urllib3
import utilities
import telegram_integration
import zulip_integration

urllib3.disable_warnings()


models = ['page', 'page-column-sort', 'handwritten', 'table']

st.sidebar.success('Выберите страницу')

st.title('Распознавание текста на фотографии')

uploaded_file = st.file_uploader(label='Выберите файл на устройстве для распознавания текста', type=['jpg', 'png'])
try:
    with open('temp/' + uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.getbuffer())
        filepath = 'temp/' + uploaded_file.name
except AttributeError:
    pass

if 'text' not in st.session_state:
    st.session_state.text = ''

if 'creds' not in st.session_state:
    st.session_state.creds = {}

if uploaded_file is not None:
    st.image(uploaded_file, caption='Загруженное изображение', use_column_width=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_model = st.radio('Модель', models, index=2)
    with col2:
        st.markdown('''- ***page*** — подходит для изображений с любым количеством строк текста, сверстанного в одну колонку.
        \n- ***page-column-sort*** — для распознавания многоколоночного текста.
        \n- ***handwritten*** — для распознавания произвольного сочетания печатного и рукописного текста на русском и английском языках.
        \n- ***table*** — для распознавания таблиц на русском и английском языках.''')

    if st.button('Распознать'):
        API_KEY = os.getenv('YANDEX_API_KEY')

        encoded_string = base64.b64encode(uploaded_file.getvalue())
        img = str(encoded_string)[2:-1]
        ocr_response = utilities.do_ocr_request(img, selected_model, API_KEY)
        recognized_text = utilities.parse_ocr_response(ocr_response)
        st.session_state.text = recognized_text[0]
        st.session_state.creds = recognized_text[1]

        st.subheader('Результат распознавания:')
        st.write(recognized_text[0])
        if recognized_text[1]['telegram_username'] is None:
            st.toast('На изображении не найден телеграм', icon='😢')
        elif telegram_integration.get_user_id(st.session_state.creds['telegram_username']) is None:
            st.toast('Распознанный телеграм не найден в БД.\nПроверьте правильность распознавания или внесите '
                     'телеграм в бота', icon='😢')
        else:
            st.success('Распознанный текст отправлен в телеграм')

st.subheader('Отправка результата')
telegram_tab, email_tab, zulip_tab = st.tabs(['Telegram', 'Email', 'Zulip'])
with telegram_tab:
    tg_username = st.text_input(label='Введите телеграм', value=st.session_state.creds['telegram_username'],
                                help='''Ввести можно в произвольном формате (@username или username) или ссылкой''')
    attach_img = st.toggle(label='Приложить загруженное изображение', value=True, key=1)
    if st.button('Отправить', key=11):
        try:
            asyncio.run(telegram_integration.send_message(tg_username, st.session_state.text))
        except BadRequest:
            st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
        except InvalidToken:
            st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')

with email_tab:
    target_email = st.text_input(label='Введите Email')
    attach_img = st.toggle(label='Приложить загруженное изображение', value=True, key=2)
    if st.button('Отправить', key=22):
        try:
            asyncio.run(telegram_integration.send_message(tg_username, 'recognized_text[0]'))
        except BadRequest:
            st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
        except InvalidToken:
            st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')

with zulip_tab:
    zulip_username = st.text_input(label='Введите ID или канал в Zulip')
    zulip_topic = st.text_input(label='Введите топик в Zulip')
    attach_img = st.toggle(label='Приложить загруженное изображение', value=True, key=3)
    if st.button('Отправить', key=33):
        try:
            zulip_id = int(zulip_username)
            try:
                if attach_img:
                    zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                   message='ocr_response', attachment=filepath)
                else:
                    zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                   message='ocr_response')
            except Exception as e:
                st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
        except ValueError:
            try:
                if attach_img:
                    zulip_integration.send_message(id=zulip_username, topic=zulip_topic,
                                                   message='ocr_response', attachment=filepath)
                else:
                    zulip_integration.send_message(id=zulip_username, topic=zulip_topic,
                                                   message='ocr_response')
            except Exception as e:
                st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
        utilities.clean_temp_dir('temp')
