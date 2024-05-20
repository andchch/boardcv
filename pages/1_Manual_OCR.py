import os
import base64
import asyncio
import streamlit as st
from telegram.error import BadRequest, InvalidToken
import urllib3
import modules.utilities as utilities
import modules.telegram_integration as telegram_integration
import modules.zulip_integration as zulip_integration
import modules.ai_integration as ai_integration
import modules.local_ocr as local_ocr

urllib3.disable_warnings()

models = ['page', 'page-column-sort', 'handwritten', 'table']

st.sidebar.success('Выберите страницу')

st.title('Распознавание текста на фотографии')

uploaded_file = st.file_uploader(label='Выберите файл на устройстве для распознавания текста', type=['jpg', 'png'])

# Save uploaded file to a temporary directory
try:
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with open('temp/' + uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.getbuffer())
        filepath = 'temp/' + uploaded_file.name
except AttributeError:
    pass

# Initialize session state variables for recognized text and credentials
if 'text' not in st.session_state:
    st.session_state.text = ''

if 'creds' not in st.session_state:
    st.session_state.creds = {
        'telegram_username': '',
        'email': ''
    }

# --- Process uploaded file ---
if uploaded_file is not None:
    st.image(uploaded_file, caption='Загруженное изображение', use_column_width=True)

    # --- OCR model selection and description ---
    col1, col2 = st.columns(2)
    with col1:
        selected_model = st.radio('Модель', models, index=2)
    with col2:
        st.markdown('''- ***page*** — подходит для изображений с любым количеством строк текста, сверстанного в одну колонку.
        \n- ***page-column-sort*** — для распознавания многоколоночного текста.
        \n- ***handwritten*** — для распознавания произвольного сочетания печатного и рукописного текста на русском и английском языках.
        \n- ***table*** — для распознавания таблиц на русском и английском языках.''')

    # Recognize text on button click
    if st.button('Распознать'):
        st.session_state.text = ''
        st.session_state.creds = {
            'telegram_username': '',
            'email': ''
        }
        utilities.clean_temp_dir()

        # Get API key and encode image data
        API_KEY = os.getenv('YANDEX_API_KEY')
        encoded_string = base64.b64encode(uploaded_file.getvalue())
        img = str(encoded_string)[2:-1]

        # Make OCR request and parse response
        if os.getenv('USE_LOCAL') == 'True':
            recognized_text = local_ocr.recognize_text(uploaded_file.name)
        else:
            ocr_response = utilities.do_ocr_request(img, selected_model, API_KEY)
            recognized_text = utilities.parse_ocr_response(ocr_response)

        # Store recognized text and credentials in session state
        st.session_state.text = recognized_text[0]
        st.session_state.creds = recognized_text[1]

        st.subheader('Результат распознавания:')
        st.write(recognized_text[0])

        # Check for Telegram username and send message
        if recognized_text[1]['telegram_username'] is None:
            st.toast('На изображении не найден телеграм', icon='😢')
        elif telegram_integration.get_user_id(st.session_state.creds['telegram_username']) is None:
            st.toast('Распознанный телеграм не найден в БД.\nПроверьте правильность распознавания или внесите '
                     'телеграм в бота', icon='😢')
        else:
            st.success('Распознанный текст отправлен в телеграм')
            asyncio.run(telegram_integration.send_message(st.session_state.creds['telegram_username'],
                                                          st.session_state.text))

    gpt_context = st.text_input(label='Введите контекст для GPT. Оставьте пустым если не хотите использовать',
                                help='Нейросеть будет использовать этот контекст при обработке распознанного текста')
    # --- Send results section ---
    st.subheader('Отправка результата')
    telegram_tab, zulip_tab = st.tabs(['Telegram', 'Zulip'])
    with telegram_tab:
        tg_username = st.text_input(label='Введите телеграм', value=st.session_state.creds['telegram_username'],
                                    help='Ввести можно в произвольном формате (@username или username) или ссылкой')
        attach_img = st.toggle(label='Приложить загруженное изображение', value=True, key=1)
        if st.button('Отправить', key=11):
            try:
                if attach_img:
                    asyncio.run(telegram_integration.send_message(tg_username, st.session_state.text, filepath))
                    if gpt_context != '':
                        gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                        asyncio.run(telegram_integration.send_message(tg_username, gpt_response))
                else:
                    asyncio.run(telegram_integration.send_message(tg_username, st.session_state.text))
                    if gpt_context != '':
                        gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                        asyncio.run(telegram_integration.send_message(tg_username, gpt_response))
            except BadRequest:
                st.error(f'Ошибка выполнения!\nПользователь не найден', icon='🚨')
            except InvalidToken:
                st.error(f'Ошибка выполнения!\nНеверный телеграм токен', icon='🚨')

    with zulip_tab:
        zulip_username = st.text_input(label='Введите ID или канал в Zulip')
        zulip_topic = st.text_input(label='Введите топик в Zulip', help='Игнорируется если в поле выше введен ID '
                                                                        'человека, а не канал')
        attach_img = st.toggle(label='Приложить загруженное изображение', value=True, key=3)
        if st.button('Отправить', key=33, on_click=utilities.clean_temp_dir):
            try:
                zulip_id = int(zulip_username)  # Try parsing as user ID
                try:
                    if attach_img:
                        zulip_response = zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                                        message=st.session_state.text,
                                                                        attachment=filepath)
                        if gpt_context != '':
                            gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                            zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                           message=gpt_response)
                    else:
                        zulip_response = zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                                        message=st.session_state.text)
                        if gpt_context != '':
                            print(gpt_context)
                            gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                            print(gpt_response)
                            zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                           message=gpt_response)

                        # Check for Zulip API success
                        if zulip_response.get('result') != 'success':
                            st.error(f"Ошибка отправки сообщения!\n{zulip_response.get('msg')}", icon='🚨')
                except Exception as e:
                    st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
            except ValueError:  # If not a user ID, assume stream name
                try:
                    if attach_img:
                        zulip_response = zulip_integration.send_message(id=zulip_username, topic=zulip_topic,
                                                                        message=st.session_state.text,
                                                                        attachment=filepath)
                        if gpt_context != '':
                            gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                            zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                           message=gpt_response)
                    else:
                        zulip_response = zulip_integration.send_message(id=zulip_username, topic=zulip_topic,
                                                                        message=st.session_state.text)
                        if gpt_context != '':
                            gpt_response = ai_integration.ask_gpt(st.session_state.text, gpt_context)
                            zulip_integration.send_message(id=zulip_id, topic=zulip_topic,
                                                           message=gpt_response)

                        # Check for Zulip API success
                        if zulip_response.get('result') != 'success':
                            st.error(f"Ошибка отправки сообщения!\n{zulip_response.get('msg')}", icon='🚨')
                except Exception as e:
                    st.error(f'Ошибка выполнения!\n{e}', icon='🚨')
