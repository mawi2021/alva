from classes.Graph import Graph

class GraphList():
    
    def __init__(self, root):
        super(GraphList, self).__init__()
        self.root = root
        self.list = []
        
    def addGraph(self,id):
        graph = Graph(self.root)
        if id != "":
            graph.setPerson(id)
        self.list.append(graph)
        graph.show()
        
    def setPerson(self, id):
        if id == "":
            return
        
        for graph in self.list:
            graph.setPerson(id)
            
    def update(self):
        for graph in self.list:
            graph.update()
            
    def clear(self):
        for graph in self.list:
            graph.clearGraph()
            
# :TODO: Fenster schließen