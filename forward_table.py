from datetime import datetime
class ForwardTable:
    def __init__(self):
        self.max_size = 5000
        self.best_id = None
        self.table = {}

    def refresh_table(self,nodes):
        for node in nodes:
            if self.table.get(node.id) is not None:
                record_list = self.table[node.id]
            else:
                record_list = []
            record_list.append(DistanceRecord(node.id,node.distance))
            record_list.sort(reverse=True,key=lambda x:x.record_time)
            if len(record_list) > self.max_size:
                record_list.pop()
            self.table[node.id] = record_list
        
        self.__reload_best_id()

    def __reload_best_id(self):
        cloest = min(self.table.items(),key=lambda x: x[1][0].distance)
        self.best_id = cloest[0]
    def get_the_best_node(self):
        return self.best_id
            


class DistanceRecord:
    def __init__(self,id,distance):
        self.id = id
        self.distance = distance
        self.record_time = datetime.now()
    def __str__(self):
        return str(self.id)+","+str(self.distance)+","+str(self.record_time)

if __name__ == '__main__':
    import uwb_handler
    f = ForwardTable()
    node = uwb_handler.UWBInformation(1,1.123,1)
    node2=uwb_handler.UWBInformation(1,2.124124,2)
    node3= uwb_handler.UWBInformation(2,1.03,100)
    f.refresh_table([node,node2,node3])
    # for n in f.table[1]:
    #     print(n)
    

