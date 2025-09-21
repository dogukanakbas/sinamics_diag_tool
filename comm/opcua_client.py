# OPC UA üzerinden S7-1500 köprüsünden alarm/fault okuma örneği
# Not: Bu örnek; TIA Portal'da expose ettiğiniz UA nodelarına göre düzenlenmelidir.
from opcua import Client

class OPCUAClient:
    def __init__(self, endpoint="opc.tcp://192.168.0.10:4840", nodes=None):
        self.endpoint = endpoint
        self.nodes = nodes or {
            "fault_list": "ns=3;s=\"DriveDiag\".\"FaultsJSON\"",
            "alarm_list": "ns=3;s=\"DriveDiag\".\"AlarmsJSON\"",
        }
        self.client = None

    def connect(self):
        if self.client: return
        self.client = Client(self.endpoint)
        self.client.connect()

    def read_diagnostics(self):
        try:
            self.connect()
            fault_json = self.client.get_node(self.nodes["fault_list"]).get_value()
            alarm_json = self.client.get_node(self.nodes["alarm_list"]).get_value()
        except Exception as e:
            return {"faults":[{"id":"COMM","desc":str(e)}], "alarms":[]}

        import json
        faults = json.loads(fault_json) if fault_json else []
        alarms = json.loads(alarm_json) if alarm_json else []
        return {"faults": faults, "alarms": alarms}
