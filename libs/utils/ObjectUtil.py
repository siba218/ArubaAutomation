def set_session(obj, type='rest'):
    if type == 'rest' and hasattr(obj, "rest"):
        session_obj = obj.rest
    elif type == 'apigw' and hasattr(obj, "apigw"):
        session_obj = obj.apigw
    elif type == 'ui' and hasattr(obj, 'ui'):
        session_obj = obj.ui
    else:
       session_obj = obj
    return session_obj

def to_json(response):
    try:
        return response.json()
    except:
        return response.text
