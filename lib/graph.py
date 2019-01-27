"""
Class which represents a directed graph.

Nodes are addressed by string labels.
First call add_node with labels to add nodes.
Then call add_edge with endpoint labels to add edges.
Then do whatever processing you want.
"""

from collections import OrderedDict


class Graph:

    class VertexNotFound(ValueError):
        pass

    def __init__(self):
        self.label_to_index = {}
        self.index_to_label = []
        self.adj = []
        self.radj = []
        self.edge_labels = {}

    def add_vertex(self, label):
        if label not in self.label_to_index:
            self.label_to_index[label] = len(self.index_to_label)
            self.index_to_label.append(label)
            self.adj.append([])
            self.radj.append([])

    def add_edge(self, label1, label2, edge_label=None):
        self.add_vertex(label1)
        self.add_vertex(label2)
        u = self.label_to_index[label1]
        v = self.label_to_index[label2]
        self.adj[u].append(v)
        self.radj[v].append(u)
        if edge_label is not None:
            self.edge_labels[(u, v)] = edge_label

    def get_radj(self, label):
        try:
            v = self.label_to_index[label]
        except KeyError as e:
            raise self.VertexNotFound(e.args[0])
        res = OrderedDict()
        for u in self.radj[v]:
            res[self.index_to_label[u]] = self.edge_labels.get((u, v))
        return res

    def get_adj(self, label):
        try:
            u = self.label_to_index[label]
        except KeyError as e:
            raise self.VertexNotFound(e.args[0])
        res = OrderedDict()
        for v in self.adj[u]:
            res[self.index_to_label[v]] = self.edge_labels.get((u, v))
        return res
