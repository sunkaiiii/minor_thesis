import computing_node
import receiver_node

class EdgeComputingHandler:
    def __init__(self):
        self.computing_node = computing_node.EdgeComputingNode()
        self.receiver = receiver_node.ReceiverTaskHandler()
    
    def start_receving_task(self):
        self.receiver.start_service()
    
    def stop_receving_task(self):
        self.receiver.stop_service()

if __name__ == "__main__":
    handler = EdgeComputingHandler()
    handler.start_receving_task()
    import time
    time.sleep(4)
    handler.stop_receving_task()
    time.sleep(2)