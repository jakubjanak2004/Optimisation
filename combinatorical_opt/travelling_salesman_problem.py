import networkx as nx
import matplotlib.pyplot as plt
import random
import time


def lexi_check(path):
    for node in range(len(path)):
        if str(path[node]) > str(path[len(path) - 1 - node]):
            return False
        elif str(path[node]) < str(path[len(path) - 1 - node]):
            return True
    raise Exception('Something went wrong!')


def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)


class Node:

    def __init__(self, name):
        self.name = name
        self.edges = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    # defining comparison operators
    def __lt__(self, other):
        if isinstance(other, Node):
            return self.name < other.name
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.name > other.name
        return NotImplemented

    def add_edge(self, e):
        for e_i in range(len(self.edges)):
            if self.edges[e_i] > e:
                self.edges = self.edges[:e_i] + [e] + self.edges[e_i:]
                return
        self.edges.append(e)


class Edge:

    def __init__(self, source, target, weight, is_oriented=False):
        self.source = source
        self.target = target
        self.weight = weight
        self.is_oriented = is_oriented

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "< " + str(self.source) + " -- " + str(self.target) + " w: " + str(self.weight) + ">"

    def __lt__(self, other):
        if isinstance(other, Edge):
            return self.weight < other.weight
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Edge):
            return self.weight > other.weight
        return NotImplemented


class Graph:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.best_hams = []
        self.best_hams_bb = []
        self.states_explored = 0
        self.num_of_pruned = 0

        for e in self.E:
            e.source.add_edge(e)
            e.target.add_edge(e)

    def paint_graph(self, only_hem=False, which_hem=0):
        G = nx.DiGraph()

        for node in self.V:
            G.add_node(node)
        for edge in self.E:
            if self.is_in_ham(edge, which=which_hem):
                G.add_edge(edge.source, edge.target, weight=edge.weight, color='red')
                if not edge.is_oriented:
                    G.add_edge(edge.target, edge.source, weight=edge.weight, color='red')
            elif not only_hem:
                G.add_edge(edge.source, edge.target, weight=edge.weight, color='gray')
                if not edge.is_oriented:
                    G.add_edge(edge.target, edge.source, weight=edge.weight, color='gray')

        # Position nodes using the spring layout
        pos = nx.spring_layout(G)

        # Draw the nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=400)

        # Get the edge colors from the graph attributes
        edge_colors = [G[u][v]['color'] for u, v in G.edges]

        # Draw the edges with colors based on the edge attributes
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

        # Draw the labels for nodes
        nx.draw_networkx_labels(G, pos, font_size=10)

        # Extract the edge weights and draw them as labels
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # Show the plot
        plt.show()

    def is_in_ham(self, e, which=0):
        try:
            ham = self.best_hams[which]
        except Exception:
            raise Exception('Getting the desired Hamiltonian failed!')
        if ham is None:
            return False
        for node_i in range(len(ham)):
            node_1 = ham[node_i]
            node_2 = ham[(node_i + 1) % len(ham)]
            if (e.source == node_1 and e.target == node_2
                    or e.source == node_2 and e.target == node_1 and not e.is_oriented):
                return True
        return False

    def get_neighbour_nodes(self, node):
        neighbours = []
        for edge in node.edges:
            if edge.source == node:
                neighbours.append(edge.target)
            elif not edge.is_oriented and edge.target == node:
                neighbours.append(edge.source)
        return neighbours

    def get_min_est(self, path):
        # returns the minimal cost a path can achieve
        cost = self.get_cost_of_sub_path(path)

        for node in self.V:
            if node not in path[:-1]:
                cost += node.edges[0].weight

        return cost

    def mst_lower_bound(self, path):
        cost = self.get_cost_of_sub_path(path)

        subgraph_nodes = [path[0]]
        if path[-1] not in subgraph_nodes:
            subgraph_nodes.append(path[-1])

        for node in self.V:
            if node not in path:
                subgraph_nodes.append(node)

        def mst_cost(subgraph):
            subG = nx.Graph()

            for n in subgraph:
                subG.add_node(n)

            for e in self.E:
                if e.source in subgraph and e.target in subgraph:
                    subG.add_edge(e.source, e.target, weight=e.weight)

            mst = nx.minimum_spanning_tree(subG, weight='weight')

            return mst.size(weight='weight')

        return cost + mst_cost(subgraph_nodes)

    def branch_and_bound(self):
        min_cost = float('inf')
        starting_node = self.V[0]
        self.states_explored = 0

        def branch(visited_nodes, cost=0, current_node=starting_node):
            # print('visited nodes', visited_nodes)
            nonlocal min_cost
            visited_nodes = visited_nodes[:]

            neighbours = self.get_neighbour_nodes(current_node)
            for neighbour in neighbours:
                if neighbour in visited_nodes:
                    continue

                # Here we can be checking if branching is pruned
                # If the minimal cost of this path > minimal hamiltonian found so far -> then prune
                if self.get_min_est(visited_nodes + [neighbour]) <= min_cost:
                    branch((visited_nodes + [neighbour])[:],
                           cost + self.get_cost_between_nodes(current_node, neighbour),
                           neighbour)
                else:
                    # print('pruning', visited_nodes + [neighbour])
                    if len(visited_nodes) <= len(self.V) - 2:
                        self.num_of_pruned += 1
                    else:
                        self.states_explored += 1

            # Base Case
            # Adding new best paths or returning
            if all(neighbour in visited_nodes for neighbour in neighbours):
                self.states_explored += 1
                cost += self.get_cost_between_nodes(visited_nodes[-1], starting_node)
                if cost < min_cost:
                    min_cost = cost
                    self.best_hams_bb.clear()
                elif cost > min_cost:
                    return
                if lexi_check(visited_nodes + [starting_node]):
                    self.best_hams_bb.append(visited_nodes)

        #  Start the recursive branching algo
        branch(visited_nodes=[starting_node])

        return self.best_hams_bb

    def minimal_hamiltonian_path(self):
        all_hams = []
        starting_node = self.V[0]
        other_nodes = self.V[1:]

        def permute(arr, l, r):
            if l == r:
                if lexi_check(arr):
                    all_hams.append(arr)
            else:
                for j in range(l, r + 1):
                    # Swap elements at index l and i
                    arr[l], arr[j] = arr[j], arr[l]

                    # Recurse for the next position
                    permute(arr[:], l + 1, r)

        permute(other_nodes, 0, len(other_nodes) - 1)

        # Handling cycles in permutations
        for i in range(len(all_hams)):
            all_hams[i] = [starting_node] + all_hams[i]

        min_cost = float('inf')
        for path in all_hams:
            cost = self.get_cost_of_path(path)
            if cost < min_cost:
                min_cost = cost
                self.best_hams.clear()
                self.best_hams.append(path)
            elif cost == min_cost:
                self.best_hams.append(path)

        if min_cost == float('inf'):
            return None, None
        return min_cost, self.best_hams

    def get_cost_of_sub_path(self, sub_path):
        cost = 0
        for node in range(len(sub_path) - 1):
            cost += self.get_cost_between_nodes(sub_path[node], sub_path[node + 1])
        return cost

    def get_cost_of_path(self, path):
        cost = 0
        for node in range(len(path)):
            cost += self.get_cost_between_nodes(path[node], path[(node + 1) % len(path)])
        return cost

    def get_cost_between_nodes(self, node_1, node_2):
        for e in node_1.edges:
            if e.source == node_1 and e.target == node_2 or e.source == node_2 and e.target == node_1 and not e.is_oriented:
                return e.weight
        return float('inf')


def test(number_of_nodes=4, number_of_tests=10):
    for t in range(number_of_tests):
        n = []
        for i in range(number_of_nodes):
            n.append(Node(str(i)))

        e = []
        for n1 in range(len(n)):
            for n2 in range(len(n)):
                if n1 < n2:
                    edge = Edge(n[n1], n[n2], random.randint(1, 10))
                    e.append(edge)

        g = Graph(n, e)
        c, tsp_res = g.minimal_hamiltonian_path()
        bb_res = g.branch_and_bound()

        was_fine = True
        if len(tsp_res) != len(bb_res):
            was_fine = False
        for res in tsp_res:
            if res not in bb_res:
                was_fine = False
        if not was_fine:
            raise Exception('TSP results are not equal -> Test Failed!')
    print('Test Passed')


if __name__ == '__main__':
    # Testing the branch and bound:
    # test(6, 100)

    # Nodes
    # Adding nodes increase the computing complexity quickly
    # The complexity is O(n!)
    nodes = []
    nodes.append(Node('A'))
    nodes.append(Node('B'))
    nodes.append(Node('C'))
    nodes.append(Node('D'))
    nodes.append(Node('E'))
    nodes.append(Node('F'))
    nodes.append(Node('G'))
    nodes.append(Node('H'))
    nodes.append(Node('I'))
    nodes.append(Node('J'))
    nodes.append(Node('K'))
    nodes.append(Node('L'))
    nodes.append(Node('M'))
    nodes.append(Node('N'))
    nodes.append(Node('O'))  # 15th node
    # nodes.append(Node('P'))
    # nodes.append(Node('Q'))
    # nodes.append(Node('R'))
    # nodes.append(Node('S'))
    # nodes.append(Node('T'))
    # nodes.append(Node('U'))
    # nodes.append(Node('V'))
    # nodes.append(Node('W'))
    # nodes.append(Node('X'))
    # nodes.append(Node('Y'))
    # nodes.append(Node('Z'))
    # nodes.append(Node('AA'))
    # nodes.append(Node('AB'))
    # nodes.append(Node('AC'))
    # nodes.append(Node('AD')) # 30th Node

    # Edges
    edges = []
    counter = 1
    for n1 in range(len(nodes)):
        for n2 in range(len(nodes)):
            if n1 < n2:
                edge = Edge(nodes[n1], nodes[n2], random.randint(1, 10))  # random.randint(1, 10) or counter
                edges.append(edge)
                counter += 1

    graph = Graph(nodes, edges)

    print('starting the branch and bound')
    start = time.time()
    bb_result = graph.branch_and_bound()
    end = time.time()
    print('num of states explored:', graph.states_explored)
    print('num of pruned branches:', graph.num_of_pruned)
    print('compared to worst case: ', str(len(nodes) - 1) + '! =', fact(len(nodes) - 1))
    print('calculation took:', (end - start), 'seconds')
    print('cost of path', graph.get_cost_of_path(bb_result[0]))
