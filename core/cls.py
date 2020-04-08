
class Recommendation:
    user_id = None
    bio = None
    name = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Person:
    person_id = None
    name = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Message:
    message_id = None
    message_from = None
    match_id = None
    message = None
    sent_date = None
    timestamp = None
    message_to = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Match:
    message_count = None
    match_id = None
    person = None
    messages = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Profile:
    user_id = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))
