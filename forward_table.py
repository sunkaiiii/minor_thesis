from datetime import datetime
from uwb_handler import UWBInformation


class ForwardTable:
    """
    The forward table has records of each devices.
    The name of the device is the ID.
    the table is a map, which contains id and a list.
    The list is the records of the UWB information
    """
    def __init__(self):
        self.max_size = 5000
        self.cloest_nodes = []
        self.table = {}

    def refresh_table(self, nodes: UWBInformation):
        for node in nodes:
            # create list of UWB information if there is a new id found.
            if self.table.get(node.id) is not None:
                record_list = self.table[node.id]
            else:
                record_list = []
            record_list.append(DistanceRecord(node.id, node))
            # according to the record time, let the newest record in the first place.
            record_list.sort(reverse=True, key=lambda x: x.record_time)
            if len(record_list) > self.max_size:
                record_list.pop()
            self.table[node.id] = record_list
        self.__reload_best_device()

    def __reload_best_device(self):
        # find the closest node according to the distance record.
        self.cloest_nodes = sorted(self.table.items(),
                     key=lambda x: x[1][0].uwb_information.distance)
        print(self.cloest_nodes)
    def get_the_best_node(self,except_nodes = []):
        for node in self.cloest_nodes:
            if node[0] not in except_nodes:
                return node[1][0]
        return self.cloest_nodes[1][0]


class DistanceRecord:
    def __init__(self, id, uwb_information: UWBInformation):
        self.id = id
        self.record_time = datetime.now()
        self.uwb_information = uwb_information

    def __str__(self):
        return str(self.id)+","+","+str(self.record_time) + ','+str(self.uwb_information)


if __name__ == '__main__':
    import uwb_handler
    f = ForwardTable()
    node = uwb_handler.UWBInformation(1, 1.123, 1, '', '')
    node2 = uwb_handler.UWBInformation(1, 2.124124, 2, '', '')
    node3 = uwb_handler.UWBInformation(2, 2.43, 100, '', '')
    f.refresh_table([node, node2, node3])
    print(f.get_the_best_node())
    # for n in f.table[1]:
    #     print(n)
