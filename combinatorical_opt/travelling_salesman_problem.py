import networkx as nx
import matplotlib.pyplot as plt
import random
import math


def lexi_check(path):
    for node in range(len(path)):
        if str(path[node]) > str(path[len(path) - 1 - node]):
            return False
        elif str(path[node]) < str(path[len(path) - 1 - node]):
            return True
    raise Exception('Something went wrong!')

class Node:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.name


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


class Graph:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.best_hams = []
        self.best_hams_bb = []

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

    def is_in_ham(self, edge, which=0):
        try:
            ham = self.best_hams[which]
        except Exception:
            raise Exception('Getting the desired Hamiltonian failed!')
        if ham is None:
            return False
        for node_i in range(len(ham)):
            node_1 = ham[node_i]
            node_2 = ham[(node_i + 1) % len(ham)]
            if (edge.source == node_1 and edge.target == node_2
                    or edge.source == node_2 and edge.target == node_1 and not edge.is_oriented):
                return True
        return False

    def get_neighbour_nodes(self, node):
        neighbours = []
        for edge in self.E:
            if edge.source == node:
                neighbours.append(edge.target)
            elif not edge.is_oriented and edge.target == node:
                neighbours.append(edge.source)
        return neighbours

    def get_min_est(self, path):
        # Should be returning the minimal cost of way we can get going along this path
        # Will be using this for the branch and bound algorithm
        return 0

    def branch_and_bound(self):
        min_cost = float('inf')
        starting_node = self.V[0]

        def branch(visited_nodes, cost=0, current_node=starting_node):
            nonlocal min_cost
            visited_nodes = visited_nodes[:]

            neighbours = self.get_neighbour_nodes(current_node)
            for neighbour in neighbours:
                if neighbour in visited_nodes:
                    continue

                # Here we can be checking if branching is pruned
                # If the minimal cost of this path > minimal hamiltonian found so far -> then prune
                if self.get_min_est(visited_nodes + [neighbour]) <= min_cost:
                    branch(visited_nodes + [neighbour], cost + self.get_cost_between_nodes(current_node, neighbour),
                           neighbour)

            # Base Case
            # Adding new pest paths or returning
            if all(neighbour in visited_nodes for neighbour in neighbours):
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
            cost = self.get_cost(path)
            if cost < min_cost:
                min_cost = cost
                self.best_hams.clear()
                self.best_hams.append(path)
            elif cost == min_cost:
                self.best_hams.append(path)

        if min_cost == float('inf'):
            return None, None
        return min_cost, self.best_hams

    def get_cost(self, path):
        cost = 0
        for node in range(len(path)):
            cost += self.get_cost_between_nodes(path[node], path[(node + 1) % len(path)])
        return cost

    def get_cost_between_nodes(self, node_1, node_2):
        for edge in self.E:
            if edge.source == node_1 and edge.target == node_2 or edge.source == node_2 and edge.target == node_1 and not edge.is_oriented:
                return edge.weight
        return float('inf')


if __name__ == '__main__':
    have_passed = True
    for i in range(100):
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

        # Edges
        edges = []
        for n1 in range(len(nodes)):
            for n2 in range(len(nodes)):
                if n1 < n2:
                    edges.append(Edge(nodes[n1], nodes[n2], random.randint(1, 10)))

        graph = Graph(nodes, edges)
        cost, tsp_result = graph.minimal_hamiltonian_path()
        # print('exhaustive search cost:', cost, 'paths:',  tsp_result)

        bb_result = graph.branch_and_bound()
        # print('tsp result with branch and bound:', bb_result)

        if len(tsp_result) != len(bb_result):
            # print('tsp result is different than bb_result')
            have_passed = False
        for r_1 in tsp_result:
            if r_1 not in bb_result:
                # print('tsp exhaustive result not present in bb_result')
                have_passed = False
    if have_passed:
        print('Passed!')
    else:
        print('Failed!')
