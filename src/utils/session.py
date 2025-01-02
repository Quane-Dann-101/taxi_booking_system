class Session:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance.user_id = None
            cls._instance.user_type = None
            cls._instance.username = None
            cls._instance.email = None
            cls._instance.full_data = None
        return cls._instance

    def create_session(self, user_data, user_type):
        self.user_id = user_data[0]
        self.user_type = user_type
        self.email = user_data[3]
        self.username = user_data[1]
        self.full_data = user_data

    def clear_session(self):
        self.user_id = None
        self.user_type = None
        self.username = None
        self.email = None
        self.full_data = None

    def is_authenticated(self):
        return self.user_id is not None

current_session = Session()
