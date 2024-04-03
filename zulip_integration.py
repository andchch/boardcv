import zulip


def upload_file(file_path, client):
    with open(file_path, 'rb') as file:
        result = client.upload_file(file)
    return result


def send_message(**kwargs):
    client = zulip.Client(config_file='cfg/zuliprc')
    request = {}
    msg = kwargs['message']
    if type(kwargs['id']) == str:
        request['type'] = 'stream'
        request['to'] = kwargs['id']
        request['topic'] = kwargs['topic']
        if 'attachment' in kwargs:
            img = upload_file(kwargs['attachment'], client)
            msg = f"[Изображение]({img['uri']})\n" + msg
            request['content'] = msg
        else:
            request['content'] = msg
    elif type(kwargs['id']) == int:
        request['type'] = 'private'
        request['to'] = [kwargs['id']]
        if 'attachment' in kwargs:
            img = upload_file(kwargs['attachment'], client)
            msg = f"[Изображение]({img['uri']})\n" + msg
            request['content'] = msg
        else:
            request['content'] = msg

    result = client.send_message(request)
    return result
