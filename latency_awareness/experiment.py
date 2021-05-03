from datetime import datetime
from edge_nodes import EdgeNode
import csv


class ExperimentHandler:
    def __init__(self, sort_strategy):
        self.experiment_name = 'latency_' + datetime.now().strftime('%Y_%m_%d%H_%M_%S')
        self.log_file = open(self.experiment_name + '.csv', 'w', newline='')
        self.spamwriter = csv.writer(self.log_file, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        self.sort_strategy = sort_strategy

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spamwriter = None
        self.log_file.close()

    def start_experiment(self):
        edge_node = EdgeNode(self.log_file,sort_strategy=self.sort_strategy)
        self.spamwriter.writerow(['start time', str(datetime.now())])
        edge_node.start()
        edge_node.join()
        self.spamwriter.writerow(['finish time', str(datetime.now())])



if __name__ == '__main__':
    for i in range(0,3):
        for i in range(0,10):
            experiment = ExperimentHandler()
            print(experiment.experiment_name)
            experiment.start_experiment()
