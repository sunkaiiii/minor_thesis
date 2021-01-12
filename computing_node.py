from forward_table import ForwardTable
from uwb_handler import UWBHandler

class EdgeComputingNode:
    def __init__(self):
        self.uwb_handler = UWBHandler()
        self.forward_table = ForwardTable()
    
    def detect_nodes(self):
        self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
        

    def handle_uwb_information_callback(self,uwb_list):
        for node in uwb_list:
            print(node)
        self.forward_table.refresh_table(uwb_list)


if __name__ == '__main__':
    node = EdgeComputingNode()
    node.detect_nodes()
    import time
    time.sleep(30)

