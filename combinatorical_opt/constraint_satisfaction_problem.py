import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    def __init__(self, node, colors):
        self.starting_node = node
        self.constraints = colors
        self.all_nodes = [self.starting_node]
        self.find_all_nodes(self.starting_node)

    def find_all_nodes(self, node):
        for neighbour in node.neighbour_nodes:
            if neighbour not in self.all_nodes:
                self.all_nodes.append(neighbour)
                self.find_all_nodes(neighbour)

    def print_graph(self):
        for node in self.all_nodes:
            print(node, 'connected with:', end=' ')
            for neighbour in node.neighbour_nodes:
                print(neighbour, end=' ')
            print()

    def visualize_graph(self):
        G = nx.DiGraph()  # Use nx.Graph() for an undirected graph
        for node in self.all_nodes:
            for neighbor in node.neighbour_nodes:
                G.add_edge(node, neighbor)

        pos = nx.spring_layout(G)  # Position nodes using the spring layout
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=16,
                font_weight='bold')
        plt.show()

    def backtrack_search(self):
        # Check if the conditions hold, if not return false
        # If everything fine, and there are no nodes with no value return True
        is_unset = False
        for node in self.all_nodes:
            for neighbour in node.neighbour_nodes:
                if node.value == '' or neighbour.value == '':
                    is_unset = True
                    continue
                elif node.value == neighbour.value:
                    return False
        if not is_unset:
            return True

        # Assign new Values in recursive loop
        for node in self.all_nodes:
            if node.value != '':
                continue
            for constraint in self.constraints:
                node.value = constraint
                if self.backtrack_search():
                    return True
                else:
                    node.value = ''
        return False  # Return False if no correct configuration was found


class Node:
    def __init__(self, name='nameless', *neighbour_nodes):
        self.name = name
        self.value = ''
        if len(neighbour_nodes) == 0:
            self.neighbour_nodes = set()
        else:
            self.neighbour_nodes = set(neighbour_nodes)

    def __str__(self):
        if self.value != '':
            return '(' + self.name + ' val:' + self.value + ')'
        else:
            return '(' + self.name + ')'

    def __repr__(self):
        return self.__str__()

    def set_neighbours(self, *neighbour_nodes):
        for neighbour in neighbour_nodes:
            self.neighbour_nodes.add(neighbour)
        for node in self.neighbour_nodes:
            node.neighbour_nodes.add(self)


if __name__ == '__main__':
    node_1 = Node(name='A')
    node_2 = Node(name='B')
    node_3 = Node(name='C')
    node_4 = Node(name='D')
    node_5 = Node(name='E')
    node_6 = Node(name='F')
    node_7 = Node(name='G')
    node_8 = Node(name='H')

    node_1.set_neighbours(node_2, node_4, node_5, node_6, node_7)
    node_2.set_neighbours(node_3, node_4, node_5, node_6, node_7)
    node_3.set_neighbours(node_4, node_5, node_6)
    node_5.set_neighbours(node_4, node_6)
    node_6.set_neighbours(node_7)
    node_8.set_neighbours(node_1, node_2, node_3, node_4, node_5, node_6, node_7)

    graph = Graph(node_1, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
    graph.print_graph()

    # Call the back track search that will assign value to each node
    print('\nWas backtrack Successful:', graph.backtrack_search(), '\n')
    graph.visualize_graph()
