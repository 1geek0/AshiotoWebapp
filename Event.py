class Event:
    def __init__(self, name, gates, time_start, time_end):
        self.name = name
        self.gates = gates
        self.time_start = time_start
        self.time_end = time_end
        self.number_gates = len(self.gates)
    
    