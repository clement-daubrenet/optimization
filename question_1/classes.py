import numpy


class InputFile:
    """
    A class dealing with an input file. The input file looks like:
    [Zearth x coordinate] [Zearth y coordinate] [Zearth z coordinate]
    [number of stations n]
    [station_1 x coordinate] [station_1 y coordinate] [station_1 z coordinate]
    [station_2 x coordinate] [station_2 y coordinate] [station_2 z coordinate]
    [station_n x coordinate] [station_n y coordinate] [station_n z coordinate]
    e.g:
    2.00 2.00 2.00
    3
    0.00 0.00 2.00
    0.00 2.00 2.00
    2.00 0.00 0.00
    """
    def __init__(self, filename):
        """
        Setting the file name.
        :param str filename: The full file name in the working directory.
        e.g: 'input.dat'
        """
        self.filename = filename

    def parse_file(self):
        """
        Parsing the whole file to return the whole map of stations.
        :return obj map: the map instance of all the stations in the universe.
        """
        with open(self.filename, 'r') as stations_file:
            stations_map = self._parse_header(stations_file)
            stations_map = self._parse_body(stations_map, stations_file)
        return stations_map

    @staticmethod
    def _parse_header(stations_file):
        """
        Parsing and validating the file header containing specific information.
        :param obj stations_file: the file instance.
        :return obj map: the updated map with the header data.
        """
        zearth_line = InputLine(stations_file.readline())
        zearth_position = zearth_line.parse_station()
        count_line = InputLine(stations_file.readline())
        count = count_line.parse_count()
        return Map(zearth_position=zearth_position, stations_count=count)

    @staticmethod
    def _parse_body(stations_map, stations_file):
        """
        Parsing the body containing the list of stations excluding planets.
        :param obj stations_map: the current map to be updated.
        :param obj stations_file: the file instance.
        :return obj map: the updated map with the body data.
        :return:
        """
        for line in stations_file.readlines():
            input_line = InputLine(line)
            stations_map.stations.append(Station(input_line.parse_station()))
        return stations_map


class InputLine:
    """
    A class dealing with an input line. An input line can be 2 things:
    - A station coordinate line.
    n.b:[station x coordinate] [station y coordinate] [station z coordinate]
    e.g: 2.00 2.00 2.00
    - A stations count line.
    n.b: [number of stations n]
    e.g: 3
    We perform validations based on the constraints imposed by the size of
    the universe, the maximum of stations and the format of the input.
    """
    def __init__(self, line):
        """
        Declaring the line to parse.
        :param str line: The line to parse.
        e.g: 2.00 2.00 2.00
        """
        self.line = line

    def parse_station(self, maximum=500):
        """
        Parsing a station line containing its coordinates.
        We perform some sanity checks on the data (type, maximum value, etc.).
        :param int maximum: A value specifying the maximum for the coordinates
        (for x, y and z) in absolute value
        e.g: if maximum=500, the following station line will raise an error:
        20000, 1, 1
        :return obj station: the station instance.
        """
        station = self.line.strip('\n').split(' ')
        if len(station) != 3:
            return Exception('The position {} is not at the right format'
                             .format(station))
        try:
            values = float(station[0]), float(station[1]), float(station[2])
        except ValueError:
            raise Exception('The station {} is not containing floats only'
                            .format(station))
        for value in values:
            if abs(value) > maximum:
                raise Exception('A coordinate ({}) is above the maximum in '
                                'absolute value ({})'
                                .format(str(value), str(maximum)))
        return station

    def parse_count(self, maximum=15000):
        """
        Parsing the stations count.
        :param maximum: maximum of stations allowed in the universe.
        e.g: if maximum=150000, the following count line will raise an error:
        200000
        :retur obj station: the station instance.
        """
        try:
            count = float(self.line.strip('\n'))
        except ValueError:
            raise Exception('The count line is not a numerical value')
        if count > maximum:
            raise Exception('The stations count {} is above the maximum ({})'
                            .format(str(count), str(maximum)))
        return count


class Map:
    """
    A representation of the universe map as a collection of stations.
    n.b: we also add the Earth and Zearth on the map.
    """
    def __init__(self, zearth_position, stations_count):
        """
        Initializing the list of stations on the map.
        :param zearth_position: the position of the destination (Zearth)
        e.g: (2,3,4)
        :param stations_count: the stations count on the map.
        e.g: 150
        """
        self.stations = []
        self.stations_count = stations_count
        self.earth_position = numpy.array((0, 0, 0))
        self.zearth_position = numpy.array((float(zearth_position[0]),
                                            float(zearth_position[1]),
                                            float(zearth_position[2])))

    def __add__(self, station):
        """
        Adding a station on the map.
        :param station: A new station instance.
        :return:
        """
        self.stations.append(station)

    def __iter__(self):
        """
        Iterating stations of the map.
        :return iterator: an iterator on the stations.
        """
        return iter(self.stations)

    def is_valid(self):
        """
        Checking if the number of stations is matching the one specified
        in the input file.
        :return boolean: True if they are matching, False if not.
        """
        return len(self.stations) == int(self.stations_count)


class Station:
    """
    A representation of a teleportation station.
    """
    def __init__(self, position):
        self.position = numpy.array((float(position[0]),
                                     float(position[1]),
                                     float(position[2])))

    def get_closest_station(self, stations_map):
        """
        Getting the closest station from this station on the map.
        :param obj stations_map: Instance of the full map of stations.
        :return tuple (closest_station, dmin): closest station with distance.
        """
        closest_station = None
        dmin = float("inf")
        for station in stations_map:
            distance = self.get_distance_to(station)
            if distance < dmin:
                dmin = distance
                closest_station = station
        return closest_station, dmin

    def get_distance_to(self, station):
        """
        Euclidian distance between this station and another station.
        n.b: We use a simple Euclidian formula to calculate it.
        Let's keep special relativity length contraction out of this story ;-)
        :param obj station: the other station.
        :return float distance: the Euclidian distance to the other station.
        """
        return numpy.linalg.norm(self.position - station.position)


class Path:
    """
    A class dealing with the path to follow.
    """
    def __init__(self, stations_map):
        """
        Initialization of the path with whole map.
        :param stations_map: Instance of the full map of stations.
        """
        self.stations_map = stations_map

    def get_longest_teleportation(self):
        """
        Getting what the question asks for: the longest station-station
        trip among the safest ones leading to Zearth.
        n.b: We use a classical Nearest Neighbors (NN) algorithm.
        We start from the Earth, try to find the closest station, and repeat
        the process again and again until Zearth is reached. Among all the
        station-station trips on the way to Zearth, we keep the longest one.
        :return float max_teleport_distance: the longest distance among the
        safest trips rounded to 2 decimal places.
        """
        path = [Station((0, 0, 0))]
        max_teleport_distance = 0
        while len(self.stations_map.stations) >= 1:
            current_station = path[-1]
            closest, distance = \
                current_station.get_closest_station(self.stations_map)
            path.append(closest)
            self.stations_map.stations.remove(closest)
            if distance > max_teleport_distance:
                max_teleport_distance = distance
            if (closest.position == self.stations_map.zearth_position).any():
                break
        return f'{max_teleport_distance:.2f}'
