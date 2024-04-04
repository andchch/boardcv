import asyncio
import base64
import os

from dotenv import load_dotenv

import telegram_integration
import utilities

dotenv_path = 'cfg/.env'
success = load_dotenv(dotenv_path)
res = {}


async def check():
    image_files, manuscripts = utilities.load_images('imgs/*.jpg')

    view_images = []
    for image_file in image_files:
        if any(manuscript in image_file for manuscript in manuscripts):
            view_images.append(image_file)

    for img in view_images:
        f = open(img, 'rb')
        encoded_string = base64.b64encode(f.read())
        img1 = str(encoded_string)[2:-1]
        f.close()
        try:
            if img not in res.keys():
                ocr_response = utilities.do_ocr_request(img1, 'handwritten', API_KEY)
                recognized_text = utilities.parse_ocr_response(ocr_response)
                text = recognized_text[0]
                creds = recognized_text[1]
                res[img] = [text, creds['telegram_username']]

                if recognized_text[1]['telegram_username'] is None:
                    pass
                elif telegram_integration.get_user_id(creds['telegram_username']) is None:
                    pass
                else:
                    os.remove(img)
                    await telegram_integration.send_message(creds['telegram_username'], text)
        except Exception:
            pass


async def periodic():
    while True:
        await check()
        await asyncio.sleep(DELAY)


def stop():
    task.cancel()


DELAY = int(os.getenv('SCAN_PERIOD'))
API_KEY = os.getenv('YANDEX_API_KEY')

loop = asyncio.get_event_loop()
task = loop.create_task(periodic())

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass
except AttributeError:
    pass
