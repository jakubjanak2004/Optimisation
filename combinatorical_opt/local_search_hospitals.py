import copy
import random


class Space:
    def __init__(self):
        self.houses = []
        self.hospitals = []

    def __str__(self):
        return "<Space | Houses: " + str(self.houses) + " | Hospitals:" + str(self.hospitals) + ">"

    def __repr__(self):
        return self.__str__()

    def print_city(self):
        rows = max(max([e[0] for e in self.houses]), max(e[0] for e in self.hospitals))
        columns = max(max(e[1] for e in self.houses), max(e[1] for e in self.hospitals))

        for row in range(rows + 1):
            for column in range(columns + 1):
                if (row, column) in self.houses:
                    print('P', end='')
                elif (row, column) in self.hospitals:
                    print('H', end='')
                else:
                    print('-', end='')
            print()

    def add_house(self, row, column):
        self.houses.append((row, column))

    def add_hospital(self, row, column):
        self.hospitals.append((row, column))

    def manhattan_distance_from_nearest_hospital(self, row, column):
        shortest_manhattan = float('inf')
        for hospital in self.hospitals:
            manhattan = abs(hospital[0] - row) + abs(hospital[1] - column)
            if manhattan < shortest_manhattan:
                shortest_manhattan = manhattan
        return shortest_manhattan

    def cost(self):
        cost = 0
        for house in self.houses:
            cost += self.manhattan_distance_from_nearest_hospital(house[0], house[1])
        return cost

    def hill_climb(self, algo_type='steepest'):
        def find_best_neighbor():
            current_cost = self.cost()
            better_neighbors = []
            inner_space = Space()
            inner_space.houses = copy.deepcopy(self.houses)
            inner_space.hospitals = copy.deepcopy(self.hospitals)
            for i in range(len(inner_space.hospitals)):
                inner_space.hospitals[i] = inner_space.hospitals[i][0] - 1, inner_space.hospitals[i][1]
                if inner_space.hospitals[i] in inner_space.houses:
                    pass
                elif inner_space.cost() < current_cost:
                    better_neighbors.append((inner_space.cost(), i, -1, 0))
                inner_space.hospitals = copy.deepcopy(self.hospitals)

                inner_space.hospitals[i] = inner_space.hospitals[i][0] + 1, inner_space.hospitals[i][1]
                if inner_space.hospitals[i] in inner_space.houses:
                    pass
                elif inner_space.cost() < current_cost:
                    better_neighbors.append((inner_space.cost(), i, 1, 0))
                inner_space.hospitals = copy.deepcopy(self.hospitals)

                inner_space.hospitals[i] = inner_space.hospitals[i][0], inner_space.hospitals[i][1] - 1
                if inner_space.hospitals[i] in inner_space.houses:
                    pass
                elif inner_space.cost() < current_cost:
                    better_neighbors.append((inner_space.cost(), i, 0, -1))
                inner_space.hospitals = copy.deepcopy(self.hospitals)

                inner_space.hospitals[i] = inner_space.hospitals[i][0], inner_space.hospitals[i][1] + 1
                if inner_space.hospitals[i] in inner_space.houses:
                    pass
                elif inner_space.cost() < current_cost:
                    better_neighbors.append((inner_space.cost(), i, 0, 1))
                inner_space.hospitals = copy.deepcopy(self.hospitals)

            best_neighbor_cost = float('inf')
            best_neighbor_of_hospital = None
            if algo_type == 'steepest':
                for neighbor in better_neighbors:
                    if neighbor[0] < best_neighbor_cost:
                        best_neighbor_cost = neighbor[0]
                        best_neighbor_of_hospital = neighbor
            elif algo_type == 'stochastic':
                if len(better_neighbors) == 0:
                    return None
                best_neighbor_of_hospital = random.choice(better_neighbors)

            return best_neighbor_of_hospital

        best_neighbor = find_best_neighbor()
        while best_neighbor is not None:
            self.hospitals[best_neighbor[1]] = (self.hospitals[best_neighbor[1]][0] + best_neighbor[2]), \
                (self.hospitals[best_neighbor[1]][1] + best_neighbor[3])
            best_neighbor = find_best_neighbor()

    def random_restarts(self, num_of_hospitals, num_of_restarts):
        self.hospitals = []
        opt_results = []

        for _ in range(num_of_restarts):
            while len(self.hospitals) < num_of_hospitals:
                row = random.randint(0, max([e[0] for e in self.houses]))
                column = random.randint(0, max(e[1] for e in self.houses))
                if (row, column) not in self.hospitals and (row, column) not in self.houses:
                    self.hospitals.append((row, column))

            self.hill_climb()
            opt_results.append((self.cost(), self.hospitals))
            print('Optimised to:', self.cost())
            self.hospitals = []

        min_cost = float('inf')
        min_hospitals_placement = None
        for result in opt_results:
            if result[0] < min_cost:
                min_cost = result[0]
                min_hospitals_placement = result[1]

        self.hospitals = min_hospitals_placement


if __name__ == '__main__':
    space = Space()
    space.add_house(1, 1)
    space.add_house(5, 8)
    space.add_house(8, 10)
    space.add_house(0, 10)
    # Generate the hospitals positions randomly
    space.add_hospital(3, 4)
    space.add_hospital(8, 9)
    space.print_city()
    print('Initial Cost', space.cost())
    space.hill_climb(algo_type='steepest')
    # space.random_restarts(2, 50)
    print('Cost After Optimisation', space.cost())
    space.print_city()
