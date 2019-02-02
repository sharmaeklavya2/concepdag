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
        self.depth = None
        self.topo_order = None

    def get_labels(self):
        return self.index_to_label

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

    def get_depth(self, uci):
        if self.depth is None:
            return None
        else:
            try:
                return self.depth[self.label_to_index[uci]]
            except KeyError as e:
                raise self.VertexNotFound(e.args[0])

    def get_topo_order(self, uci):
        if self.topo_order is None:
            return None
        else:
            try:
                return self.topo_order[self.label_to_index[uci]]
            except KeyError as e:
                raise self.VertexNotFound(e.args[0])

    def scc(self):
        n = len(self.index_to_label)
        fintime_order = []
        visited = [False] * n

        def visit1(u):
            if not visited[u]:
                visited[u] = True
                for v in self.adj[u]:
                    if not visited[v]:
                        visit1(v)
                fintime_order.append(u)

        for r in range(n):
            if not visited[r]:
                visit1(r)

        visited = [False] * n
        cc = [-1] * n
        cclist = []
        self.depth = [0] * n

        def visit2(u, cci):
            if not visited[u]:
                visited[u] = True
                cc[u] = cci
                cclist[-1].append(u)
                for v in self.radj[u]:
                    if cc[v] != cc[u] and cc[v] != -1:
                        self.depth[u] = max(self.depth[u], self.depth[v] + 1)
                    if not visited[v]:
                        visit2(v, cci)

        cci = 0
        for r in reversed(fintime_order):
            if not visited[r]:
                cclist.append([])
                visit2(r, cci)
                cci += 1

        self.topo_order = cc
        cclist2 = [[self.index_to_label[u] for u in l] for l in cclist]
        return cclist2


def main():
    n = int(input())
    graph = Graph()
    for i in range(n):
        graph.add_vertex(i)
    try:
        while True:
            u, v = [int(x) for x in input().split()]
            graph.add_edge(u, v)
    except EOFError:
        pass

    print(graph.scc())


if __name__ == '__main__':
    main()
