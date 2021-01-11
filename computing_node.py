from forward_table import ForwardTable
from uwb_handler import UWBHandler

class EdgeComputingNode:
    def __init__(self):
        self.uwb_handler = UWBHandler()
        self.forward_table = ForwardTable()
    
    def detect_nodes(self):
        self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
        

    def handle_uwb_information_callback(self,uwb_list):
        self.forward_table.refresh_table(uwb_list)

