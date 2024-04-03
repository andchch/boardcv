import os
import re
import json
import shutil
import requests


tg_username_regex = r'(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(\w{4,})$'
email_regex = r'^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$'


def do_ocr_request(content, model, key):
    payload = {
        'mimeType': 'JPEG',
        'languageCodes': ['en', 'ru'],
        'model': model,
        'content': content
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Api-Key {}'.format(key),
        'x-data-logging-enabled': 'true'
    }

    try:
        response = requests.post(os.getenv('YC_OCR_ENDPOINT'), json=payload, headers=headers)
    except Exception as ex:
        print('Exception during request! {}'.format(str(ex)))
        return None
    if response.status_code != 200:
        print('Daemon return code {}'.format(response.status_code))
        print(response.content)
        return None
    else:
        return json.loads(response.content)


def parse_ocr_response(response_json):
    credentials = {
        'telegram_username': None,
        'email': None
    }
    result = response_json.get('result', {})
    text_annotation = result.get('textAnnotation', {})
    full_text = text_annotation.get('fullText', '')
    if full_text is not None and full_text != '':
        matches = re.findall(tg_username_regex, full_text, re.MULTILINE)
        if len(matches) != 0:
            credentials['telegram_username'] = matches[0]
        matches = re.findall(email_regex, full_text, re.MULTILINE)
        if len(matches) != 0:
            email = ''.join(matches[0])
            credentials['email'] = email

    res = ''
    blocks = text_annotation.get('blocks', [])
    for i, block in enumerate(blocks):
        block_text = ''
        lines = block.get('lines', [])
        for line in lines:
            line_text = line.get('text', '')
            block_text += line_text + "\n"
        res += '\n' + block_text

        for line in lines:
            words = line.get('words', [])
            line_words = []
            for word in words:
                word_text = word.get('text', '')
                line_words.append(word_text)

    return res, credentials


def clean_temp_dir(temp_dir):
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Ошибка удаления %s. Причина: %s' % (file_path, e))
