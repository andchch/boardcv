import asyncio
import base64
import os

from telegram.error import BadRequest, InvalidToken

import telegram_integration
import utilities
import streamlit as st

import zulip_integration

models = ['page', 'page-column-sort', 'handwritten', 'table']

if 'res' not in st.session_state:
    st.session_state.res = {}

st.sidebar.success('Выберите страницу')

st.title('Распознавание нескольких файлов')

if not os.path.exists('imgs'):
    os.mkdir('imgs')

# Set the directory for scanning images
local = os.getcwd() + '\\imgs'
st.markdown(f'Сканирование директории `{local}` на наличие файлов для распознавания')

# Button to preview images in the directory
if st.button('Предпросмотр изображений'):
    imgs = utilities.image_grid()  # Get images from the directory
    if len(imgs) == 0:
        st.warning('В папке отсутствуют изображения')

# --- OCR model selection and description ---
col1, col2 = st.columns(2)
with col1:
    selected_model = st.radio('Модель', models, index=2)
with col2:
    st.markdown('''- ***page*** — подходит для изображений с любым количеством строк текста, сверстанного в одну 
    колонку. \n- ***page-column-sort*** — для распознавания многоколоночного текста. \n- ***handwritten*** — для 
    распознавания произвольного сочетания печатного и рукописного текста на русском и английском языках. \n- 
    ***table*** — для распознавания таблиц на русском и английском языках.''')

# --- Recognize text from all images ---
if st.button('Распознать'):
    imgs = utilities.image_grid()  # Get images from the directory
    API_KEY = os.getenv('YANDEX_API_KEY')  # Get API key from environment variable
    with st.spinner('Выполнение...'):
        st.session_state.res = {}
        for img in imgs:
            # Read and encode image data
            f = open(img, 'rb')
            encoded_string = base64.b64encode(f.read())
            img1 = str(encoded_string)[2:-1]
            f.close()

            # Make OCR request and parse response
            ocr_response = utilities.do_ocr_request(img1, selected_model, API_KEY)
            recognized_text = utilities.parse_ocr_response(ocr_response)

            # Store recognized text and credentials in session state
            st.session_state.text = recognized_text[0]
            st.session_state.creds = recognized_text[1]

            # Store results in the dictionary with image path as key
            st.session_state.res[img] = [st.session_state.text, st.session_state.creds['telegram_username']]

            # Send recognized text to Telegram if username found and exists
            if recognized_text[1]['telegram_username'] is None:
                pass  # No Telegram username found
            elif telegram_integration.get_user_id(st.session_state.creds['telegram_username']) is None:
                pass  # Telegram username not found in database
            else:
                st.success('Распознанный текст отправлен в телеграм')
                asyncio.run(telegram_integration.send_message(st.session_state.creds['telegram_username'],
                                                              st.session_state.text))

# --- Send results section ---
st.subheader('Отправка результата')
telegram_tab, zulip_tab = st.tabs(['Telegram', 'Zulip'])
with telegram_tab:
    tg_username = st.text_input(label='Введите телеграм',
                                help='Ввести можно в произвольном формате (@username или username) или ссылкой')
    if st.button('Отправить', key=11):
        with st.spinner('Выполнение...'):
            for img, v in st.session_state.res.items():
                try:
                    asyncio.run(telegram_integration.send_message(tg_username, v[0], img))
                except BadRequest:
                    st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
                except InvalidToken:
                    st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')

with zulip_tab:
    zulip_username = st.text_input(label='Введите ID или канал в Zulip')
    zulip_topic = st.text_input(label='Введите топик в Zulip', help='Игнорируется если в поле выше введен ID '
                                                                    'человека, а не канал')
    if st.button('Отправить', key=33, on_click=utilities.clean_temp_dir):
        with st.spinner('Выполнение...'):
            try:
                zulip_id = int(zulip_username)
                try:
                    for img, v in st.session_state.res.items():
                        zulip_response = zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                                        message=v[0],
                                                                        attachment=img)
                        if zulip_response.get('result') != 'success':
                            st.error(f"Ошибка отправки сообщения!\n{zulip_response.get('msg')}", icon='🚨')
                except Exception as e:
                    st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
            except ValueError:
                try:
                    for img, v in st.session_state.res.items():
                        zulip_response = zulip_integration.send_message(id=zulip_username, topic=zulip_topic,
                                                                        message=v[0],
                                                                        attachment=img)
                        if zulip_response.get('result') != 'success':
                            st.error(f"Ошибка отправки сообщения!\n{zulip_response.get('msg')}", icon='🚨')
                except Exception as e:
                    st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
