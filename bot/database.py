class ContexManager:
    def __init__(self):
        self.context = dict()

    def add_message(self, user_id, message):
        if user_id not in self.context:
            self.context[user_id] = message
        else:
            self.context[user_id] = self.context[user_id] + message

    def contex_message(self, user_id):
        return self.context[user_id]

    def clear(self, user_id):
        if user_id in self.context:
            self.context[user_id] = ""


class Work_AI_dict:
    def __init__(self):
        self.context = dict()

    def add_message(self, user_id, Work_Ai):
        self.context[user_id] = Work_Ai

    def Work_Ai_message(self, user_id):
        return self.context[user_id]


class Work_weather:
    def __init__(self):
        self.context = dict()

    def add_message(self, user_id , Work_weather):
        self.context[user_id] = Work_weather

    def Work_weather_message(self, user_id):
        return self.context[user_id]
