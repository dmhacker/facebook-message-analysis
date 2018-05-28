import json
import copy

cache = {}

def _load_messages(filename):
    if filename in cache:
        return cache[filename]
    else:
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
            cache[filename] = data
            return data
        
def get_messages(filename, copy_from_cache=True):
    data = _load_messages(filename)

    # Copy the stored messages we have
    copied_messages = data['messages']
    if copy_from_cache:
        copied_messages = copy.deepcopy(data['messages'])

    # Return a sorted list of messages by time
    return sorted(copied_messages, key=lambda message : message['timestamp'])
