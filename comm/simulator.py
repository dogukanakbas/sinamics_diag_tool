import random, time

class Simulator:
    def __init__(self):
        self._faults = []
        self._alarms = []

    def inject_fault(self, fid="F30012", comp="Inverter"):
        self._faults = [{"id": fid, "desc": "Simulated fault", "component": comp}]
    def inject_alarm(self, aid="A05010", comp="Fan"):
        self._alarms = [{"id": aid, "desc": "Simulated alarm", "component": comp}]
    def clear(self):
        self._faults.clear()
        self._alarms.clear()

    def read_diagnostics(self):
        # Basit demo: mevcut listeyi döndür
        return {"faults": list(self._faults), "alarms": list(self._alarms)}
