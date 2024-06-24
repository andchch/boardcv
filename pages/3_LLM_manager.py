import os
import streamlit as st
import modules.ai_integration as ai_integration


st.title('На этой странице вы можете настроить работу локальной LLM')
if os.getenv('USE_LOCAL') == 'True':
    models = ai_integration.ollama_check()
    if len(models['models']) != 0:
        st.info('Модель уже загружена')
    st.warning('''Размер модели ~4,7Gb. Процесс может быть длительным.
               Во время процесса скачивания/обновления нельзя переходить на другие страницы или обновлять страницу!''', icon="⚠️")
    if st.button('Скачать/обновить модель'):
        with st.spinner('Ожидайте...'):
            ai_integration.ollama_init()
        st.success('Модель успешно загружена/обновлена!', icon="✅")
else:
    st.warning('''Запущен режим работы со сторонними нейросетями''', icon="⚠️")
    