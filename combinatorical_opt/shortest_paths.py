import time


class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

        # Set the number of steps it took to get to the node
        if self.parent is not None:
            self.number_of_steps = parent.number_of_steps + 1
        else:
            self.number_of_steps = 0

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.state == other.state
        return False

    def __str__(self):
        return "<Node: row=" + str(self.state[0]) + " col=" + str(self.state[1]) + ">"

    def __repr__(self):
        return self.__str__()


class Frontier:
    def __init__(self):
        self.frontier = []

    def clear(self):
        self.frontier = []

    def push(self, node):
        self.frontier.append(node)

    def empty(self):
        return len(self.frontier) == 0

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)


class StackFrontier(Frontier):
    def __init__(self):
        super().__init__()

    def pop(self):
        if self.empty():
            raise Exception("Frontier Empty")
        return self.frontier.pop()


class QueueFrontier(Frontier):
    def __init__(self):
        super().__init__()

    def pop(self):
        if self.empty():
            raise Exception("Frontier Empty")
        return self.frontier.pop(0)


class PriorityQueueFrontier(QueueFrontier):
    def __init__(self, heuristic_function):
        super().__init__()
        self.heuristic_function = heuristic_function

    def push(self, node):
        if node in self.frontier:
            return
        if self.empty():
            self.frontier.append(node)
        else:
            for i in range(len(self.frontier)):
                if self.heuristic_function(self.frontier[i]) > self.heuristic_function(node):
                    self.frontier = self.frontier[:i] + [node] + self.frontier[i:]
                    return
                elif i == len(self.frontier) - 1:
                    self.frontier.append(node)


class Maze:
    def __init__(self, file_path, algo_type='dfs'):
        self.maze = []
        self.solution = ([], [])
        self.frontier = None
        self.explored = []
        self.solving_time = 0.

        with open(file_path, "r") as f:
            for line in f:
                self.maze.append(list(line))

        for row in range(len(self.maze)):
            for column in range(len(self.maze[row])):
                if self.maze[row][column] == "A":
                    self.start_node = Node((row, column), None, None)
                elif self.maze[row][column] == "B":
                    self.goal_node = Node((row, column), None, None)

        self.print_maze()

        if algo_type == 'dfs':
            self.frontier = StackFrontier()
        elif algo_type == 'bfs':
            self.frontier = QueueFrontier()
        elif algo_type == 'gbfs':
            self.frontier = PriorityQueueFrontier(self.manhattan_distance)
        elif algo_type == 'a*':
            self.frontier = PriorityQueueFrontier(self.a_star)
        else:
            raise Exception("Invalid frontier type")

    def print_maze(self, show_explored=False, show_manhattan=False, show_a_star=False):
        for row in range(len(self.maze)):
            for column in range(len(self.maze[row])):
                if self.maze[row][column] == "A":
                    print("A", sep='', end='')
                elif self.maze[row][column] == "B":
                    print("B", sep='', end='')
                elif self.maze[row][column] == "#":
                    print('\u25A0', sep='', end='')
                elif self.maze[row][column] == " " and show_a_star:
                    for node in self.explored:
                        if node.state == (row, column):
                            print("|",
                                  self.a_star(node),
                                  "|",
                                  sep='', end='')
                            break
                elif self.maze[row][column] == " " and show_manhattan:
                    print("|",
                          self.manhattan_distance(Node((row, column), None, None)),
                          "|",
                          sep='', end='')
                elif show_explored and Node((row, column), None, None) in self.explored:
                    print("e", sep='', end='')
                elif Node((row, column), None, None) in self.solution[1]:
                    print("*", sep='', end='')
                elif self.maze[row][column] == " ":
                    print(" ", sep='', end='')
            print()

    def solve(self):
        time_start = time.time()
        self.calculate_solution()
        time_end = time.time()
        self.solving_time = time_end - time_start

    def calculate_solution(self):
        # The frontier and checked nodes data structures initialization
        self.frontier.clear()
        self.explored = []

        # Push the first node into the frontier, that being the start node of the maze
        self.frontier.push(self.start_node)

        num_of_actions = 0
        print('Solving...')
        while True:
            # If the frontier is empty, there is no solution, raise Exception
            if self.frontier.empty():
                raise Exception("No Solution")

            # Init the explored node as the node returned by the frontier pop method
            explored_node = self.frontier.pop()
            num_of_actions += 1  # increment the number of actions

            # Append the explored node into the checked nodes
            self.explored.append(explored_node)

            # If the explored node is the end node return the solution
            if explored_node == self.goal_node:
                actions = []
                nodes = []

                loop_node = explored_node
                while loop_node is not None:
                    actions.append(loop_node.action)
                    nodes.append(loop_node)

                    loop_node = loop_node.parent
                actions.reverse()
                nodes.reverse()
                self.solution = actions, nodes
                print('frontier', self.frontier.frontier)
                return

            # Push Available Nodes of the explored Node into the frontier
            if 0 != explored_node.state[0] and '#' != self.maze[explored_node.state[0] - 1][
                explored_node.state[1]]:
                # add the row-1 state
                node = Node((explored_node.state[0] - 1, explored_node.state[1]), explored_node, 'u')
                if node not in self.explored:
                    self.frontier.push(node)

            if len(self.maze) - 1 != explored_node.state[0] and '#' != self.maze[explored_node.state[0] + 1][
                explored_node.state[1]]:
                # add the row+1 state
                node = Node((explored_node.state[0] + 1, explored_node.state[1]), explored_node, 'd')
                if node not in self.explored:
                    self.frontier.push(node)

            if 0 != explored_node.state[1] and '#' != self.maze[explored_node.state[0]][
                explored_node.state[1] - 1]:
                # add the col-1 state
                node = Node((explored_node.state[0], explored_node.state[1] - 1), explored_node, 'l')
                if node not in self.explored:
                    self.frontier.push(node)

            if len(self.maze[0]) - 1 != explored_node.state[1] and '#' != self.maze[explored_node.state[0]][
                explored_node.state[1] + 1]:
                # add the col+1 state
                node = Node((explored_node.state[0], explored_node.state[1] + 1), explored_node, 'r')
                if node not in self.explored:
                    self.frontier.push(node)

    def manhattan_distance(self, node):
        return abs(self.goal_node.state[0] - node.state[0]) + abs(self.goal_node.state[1] - node.state[1])

    def a_star(self, node):
        return self.manhattan_distance(node) + node.number_of_steps


if __name__ == "__main__":
    maze = Maze("files/maze3.txt", algo_type='a*')
    maze.solve()
    print('Solution length:', len(maze.solution[0]) - 1)
    print('Explored states length:', len(maze.explored))
    print('Solving time:', maze.solving_time * 1000, 'ms')
    print('Showing Solution:')
    maze.print_maze()
    print('\nExplored states of the Maze:')
    maze.print_maze(show_explored=True)
    # print('Manhattan Distance Visualisation:')
    # maze.print_maze(show_manhattan=True)
    # print('A* Visualisation:')
    # maze.print_maze(show_a_star=True)
