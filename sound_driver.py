class SoundDriver(object):
    def __init__(self):
        self.current_volume = 50

    def get_volume(self):
        return self.current_volume

    def change_volume(self, delta):
        self.current_volume += delta

        if self.current_volume < 0:
            self.current_volume = 0
        if self.current_volume > 100:
            self.current_volume = 100
