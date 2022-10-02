
from .basepage import BasePage

class Post(BasePage):
    def __init__(self, input_path):
        super().__init__(input_path)

    def __str__(self):
        if self.date:
            return "Post on {}: {}".format(self.date.isoformat(), self.title)
        else:
            return "Post: {}".format(self.title)

