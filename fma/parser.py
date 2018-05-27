import json
import datetime
import copy

cache = {}

def _load_data(filename):
    if filename in cache:
        return cache[filename]
    else:
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
            cache[filename] = data
            return data
        
def get_messages(filename):
    data = _load_data(filename)

    # Copy the stored messages we have
    copied_messages = copy.deepcopy(data['messages'])

    # Convert every message's Unix timestamp to a date
    for message in copied_messages:
        message['date'] = datetime.datetime.fromtimestamp(message['timestamp'])

    # Return a sorted list of messages by time
    return sorted(copied_messages, key=lambda message : message['timestamp'])
