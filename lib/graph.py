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
        self.tadj = None
        self.tradj = None

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

    def get_degrees(self, label):
        try:
            u = self.label_to_index[label]
        except KeyError as e:
            raise self.VertexNotFound(e.args[0])
        tin_nbrs = self.tradj[u]
        tout_nbrs = self.tadj[u]
        return (len(self.radj[u]), len(self.adj[u]),
            None if tin_nbrs is None else len(tin_nbrs) - 1,
            None if tout_nbrs is None else len(tout_nbrs) - 1)

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

    def get_tadj(self, uci):
        if self.tadj is None:
            return None
        else:
            try:
                tadju = self.tadj[self.label_to_index[uci]]
                return [self.index_to_label[x] for x in tadju]
            except KeyError as e:
                raise self.VertexNotFound(e.args[0])

    def get_tradj(self, uci):
        if self.tadj is None:
            return None
        else:
            try:
                tradju = self.tradj[self.label_to_index[uci]]
                return [self.index_to_label[x] for x in tradju]
            except KeyError as e:
                raise self.VertexNotFound(e.args[0])

    def transitive_closure(self):
        n = len(self.adj)
        self.tadj = [[] for i in range(n)]
        self.tradj = [[] for i in range(n)]
        visited = None

        def visit(r, u, nbr_arr, tarr):
            if u not in visited:
                visited.add(u)
                tarr.append(u)
                for v in nbr_arr[u]:
                    if v not in visited:
                        visit(r, v, nbr_arr, tarr)

        for r in range(n):
            visited = set()
            visit(r, r, self.adj, self.tadj[r])
            visited = set()
            visit(r, r, self.radj, self.tradj[r])
            if self.topo_order is not None:
                self.tradj[r].sort(key=(lambda x: self.topo_order[x]))

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

    cclist = graph.scc()
    print('SCCs:')
    for cci, vlist in enumerate(cclist):
        print(cci, vlist)
    print('depth:', [graph.get_depth(i) for i in range(n)])
    print('topo_order', [graph.get_topo_order(i) for i in range(n)])
    graph.transitive_closure()
    print('Transitive adjacent:')
    for i in range(n):
        print(str(i) + ':', graph.get_tadj(i))
    print('Transitive reverse adjacent:')
    for i in range(n):
        print(str(i) + ':', graph.get_tradj(i))


if __name__ == '__main__':
    main()
