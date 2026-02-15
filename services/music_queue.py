from collections import deque

# one queue per chat
queues = {}

def get_queue(chat_id):
    if chat_id not in queues:
        queues[chat_id] = deque()
    return queues[chat_id]

def add_song(chat_id, song):
    queue = get_queue(chat_id)
    queue.append(song)

def pop_from_queue(chat_id):
    queue = get_queue(chat_id)
    if queue:
        return queue.popleft()
    return None

def clear_queue(chat_id):
    queues.pop(chat_id, None)

def list_queue(chat_id):
    queue = get_queue(chat_id)
    return list(queue)