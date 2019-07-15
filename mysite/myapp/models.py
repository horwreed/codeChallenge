from django.db import models

class Signal():
    def __init__(self, date, value):
        self.date = date
        self.value = value

    def get_date(self):
        return self.date

    def get_value(self):
        return self.value

