import zulip


def upload_file(file_path, client):
    """
    Uploads a file to the Zulip server.

    Parameters:
        file_path (str): The path to the file to upload.
        client (zulip.Client): A Zulip client object.

    Returns:
        dict: A dictionary containing information about the uploaded file, including the URI.
    """
    with open(file_path, 'rb') as file:
        result = client.upload_file(file)
    return result


def send_message(**kwargs):
    """
    Sends a message to a Zulip user or stream.

    Parameters:
        **kwargs: Keyword arguments for the message:
            * id (str or int): The ID of the recipient (user ID or stream name).
            * topic (str, optional): The topic of the message (required for streams).
            * message (str): The message content.
            * attachment (str, optional): The path to a file to attach.

    Returns:
        dict: A dictionary containing the result of the send_message request.
    """
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
