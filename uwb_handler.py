class UWBHandler:
    def detect_nodes(self,callback):
        detect_info = []
        callback(detect_info)


class UWBInformation:
    def __init__(self):
        self.id = ""
        self.distance = -1


