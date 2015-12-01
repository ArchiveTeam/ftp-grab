import sys
import urllib.request

wpull_hook = globals().get('wpull_hook') # silence code checkers
tries = 0
max_tries = 5

def handle_response(url_info, record_info, response_info):
    global tries
    global max_tries
    response_code = response_info['response_code']
    if 200 <= response_code <= 299:
        tries = 0
        return wpull_hook.actions.NORMAL
    elif response_code in (530, 550):
        tries = 0
        return wpull_hook.actions.FINISH
    else:
        if tries >= max_tries:
            raise Exception('Something went wrong, received status code %d %d times. ABORTING...'%(response_code, max_tries))
        print('You received status code %d. Retrying...'%response_code)
        sys.stdout.flush()
        tries += 1
        return wpull_hook.actions.RETRY

def handle_error(url_info, record_info, error_info):
    global max_tries
    tries = record_info["try_count"]
    if tries >= max_tries - 2:
        try:
            urllib.request.urlopen(url_info["url"])
        except Exception as error:
            error_message = str(error)
            print(error_message)
            sys.stdout.flush()
            if tries >= max_tries:
                if '550' in error_message and 'No such file or directory' in error_message:
                    return wpull_hook.actions.FINISH
                raise Exception('Something went wrong... ABORTING...')
    if tries >= max_tries:
        raise Exception('Something went wrong... ABORTING...')

wpull_hook.callbacks.handle_response = handle_response
wpull_hook.callbacks.handle_error = handle_error