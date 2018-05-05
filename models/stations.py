import jsonpickle
import logging


class Stations(object):
    def __init__(self):
        self.stations_file = './data/stations.json'

        self.stations = []
        self.station_sel = -1

        self.read_stations_file()

    def read_stations_file(self):
        try:
            with open(self.stations_file, 'r') as stations_file:
                json_str = stations_file.read()
                obj = jsonpickle.decode(json_str)
                self.stations = obj
        except EnvironmentError as ex:
            logging.error("Stations.read_stations_file: failed to read file %s", self.stations_file)
        except ValueError as ex:
            logging.error("Stations.read_stations_file: failed to parse file %s", self.stations_file)

    def write_stations_file(self):
        try:
            with open(self.stations_file, 'w') as stations_file:
                json_str = jsonpickle.encode(self.stations)
                stations_file.write(json_str)
        except EnvironmentError as ex:
            logging.error("Stations.write_stations_file: failed to write file %s", self.stations_file)

    def add_station(self, station, update_sel=False):
        self.stations.append(station)
        self.write_stations_file()

        if update_sel is True:
            self.set_station_sel(self.get_station_count() - 1)

    def delete_station(self, index):
        if (index >= 0) and (index < len(self.stations)):
            self.stations.pop(index)
            self.write_stations_file()

    def set_station_sel(self, index):
        if (index >= 0) and (index < len(self.stations)):
            self.station_sel = index

    def get_station_sel(self):
        return self.station_sel

    def get_stations(self):
        return self.stations

    def get_station_count(self):
        return len(self.stations)

    def get_station_index(self, name):
        index = -1

        for pos in range(0, self.get_station_count()):
            if self.stations[pos].name == name:
                index = pos
                break

        return index
