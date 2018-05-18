import threading

from mpd import MPDClient


class SoundDriver(object):
    def __init__(self):
        self.access_lock = threading.RLock()
        self.client = None
        self._init()
        
    def _init(self):
        self.client = MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self.client.connect('localhost', 6600)
        
        status = self.client.status()
        self.current_volume = status['volume']
        
    def cleanup(self):
        self.access_lock.acquire()
        
        self.client.close()
        self.client.disconnect()
        self.client = None
        
        self.access_lock.release()

    def get_volume(self):
        return self.current_volume

    def change_volume(self, delta):
        self.access_lock.acquire()
        
        self.current_volume += delta

        if self.current_volume < 0:
            self.current_volume = 0
        if self.current_volume > 100:
            self.current_volume = 100
            
        self.client.setvol(self.current_volume)

        self.access_lock.release()

    def play(self, uri):
        self.access_lock.acquire()
        
        self.client.clear()
        self.client.add(uri)
        self.client.play(0)
        
        self.access_lock.release()
        
    def stop(self):
        self.access_lock.acquire()
        
        self.client.stop()
        
        self.access_lock.release()
