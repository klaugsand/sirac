class ModelContainer(object):
    def __init__(self):
        self.models = {}

    def add_model(self, name, model):
        self.models[name] = model

    def get_model(self, name):
        model = None

        if name in self.models:
            model = self.models[name]

        return model
