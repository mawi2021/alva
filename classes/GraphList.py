from classes.Graph import Graph
from classes.GraphAncestor import GraphAncestor

class GraphList():
    
    def __init__(self, root, data):
        super(GraphList, self).__init__()
        self.root = root
        self.data = data
        self.list = []
    def addGraph(self, id):
        graph = Graph(self.root, self.data, id)
        self.list.append(graph)
        return graph
    def addGraphAncestor(self, idList, lineList, minYear, maxYear):
        graph = GraphAncestor(self.root, self.data, idList, lineList, minYear, maxYear)
        self.list.append(graph)
        return graph
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
    def close(self):
        for graph in self.list:
            graph.close()
            self.list.remove(graph)