import streamlit as st
from dotenv import load_dotenv

st.sidebar.success('Выберите страницу')

st.title('''Визуальный анализ фото с доски Проект № 27 🤗''')
st.write('''Этот сервис предоставляет возможность провести анализ изображений доски и извлечь текст из них.
            Полученные данные можно отправить на почту, в Telegram или Zulip, 
            а также скачать в формате текстового файла.''')

dotenv_path = 'cfg/.env'
success = load_dotenv(dotenv_path)
if not success:
    st.error('Ошибка загрузки .env файла!', icon='🚨')
