from ..app import context, AppCtxt
from ..login.window import Login

class TestPlugin:
    def __init__(self):
        context.signals.showing.connect(self.on_open)
    #     context.signals.closing.connect(self.on_open)

    def on_open(self):
        print('login initialized')    

plugin = TestPlugin