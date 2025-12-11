class NoUserInSession(Exception):
    def __init__(self, *args):
        super().__init__(*args)
    
class NoUserInDb(Exception):
    def __init__(self, *args):
        super().__init__(*args)