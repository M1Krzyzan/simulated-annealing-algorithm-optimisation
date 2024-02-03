import random as rand
from math import sqrt
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

CONSTANT_K = 8.99 * (10 ** 9)

# maximum iterations
I_MAX: int = 100

# temperature drop rate per iteration
DROP_RATE: float = 0.01

# initial temperature
T: int = 100

# List to store energy values for each iteration
energy_values = []


def generate_random_pos() -> tuple[int, int, int]:
    """Generate a random 3D position vector (x, y, z) for a node."""
    x = rand.randint(1, 1000)
    y = rand.randint(1, 1000)
    z = rand.randint(1, 1000)
    return x, y, z


def get_random_current() -> int:
    """Generate a random current value within a given range for a node."""
    return rand.randint(1, 10)


def generate_nodes(n: int) -> list[Tuple[Tuple[int, int, int], int]]:
    """Create an array of N nodes, where N is a random number."""
    nodes = []
    for _ in range(n):
        # Generating three random coordinates
        x = np.random.randint(-100, 100)
        y = np.random.randint(-100, 100)
        z = np.random.randint(-100, 100)

        # Generating a random value for the node
        value = np.random.randint(-100, 100) * (10 ** (-9))

        # Adding a tuple (coordinates, value) to the list of nodes
        nodes.append(((x, y, z), value))
    return nodes


def get_random_node(nodes: list) -> [[tuple[int, int, int], int], int]:
    """Get a random node from the array of nodes."""
    n = rand.randint(0, len(nodes) - 1)
    return nodes[n], n


def change_node_position(x: int, y: int, z: int) -> Tuple[int, int, int]:
    """Change the position of a node by adding a direction vector, e.g., [1, -1, 0] means moving up
    and left in 3 dimensions."""
    x += np.random.uniform(-1, 1)
    y += np.random.uniform(-1, 1)
    z += np.random.uniform(-1, 1)

    return x, y, z


def check_energy(energy: float, new_energy: float, temperature: float) -> bool:
    """Check whether we accept new energy state."""
    if energy < new_energy:
        return True
    else:
        return probability_fun(energy, new_energy, temperature)


def calculate_distance(node_values: tuple, ref_node_values: tuple) -> float:
    """Calculates the distance between two nodes."""
    distance_x = (node_values[0] - ref_node_values[0]) ** 2
    distance_y = (node_values[1] - ref_node_values[1]) ** 2
    distance_z = (node_values[2] - ref_node_values[2]) ** 2

    return sqrt(distance_x + distance_y + distance_z)


def calculate_energy_between_nodes(node_values: tuple, node_charge: float, ref_node_values: tuple,
                                   ref_node_charge: float) -> float:
    """Calculates the energy between two nodes."""
    try:
        distance = calculate_distance(node_values, ref_node_values)
        return CONSTANT_K * node_charge * ref_node_charge / distance
    except ZeroDivisionError:
        return 0.0


def calculate_energy(nodes: list, ref_node: tuple) -> float:
    """Calculates the total energy between all nodes and the reference node."""
    energy = 0.0
    ref_node_values, ref_node_charge = ref_node

    for node in nodes:
        node_values, node_charge = node
        energy += calculate_energy_between_nodes(node_values, node_charge, ref_node_values,
                                                 ref_node_charge)

    return energy


def probability_fun(current_energy: float, new_energy: float, temperature: float) -> bool:
    """Function that returns the probability of accepting a new state."""
    decision_factor = np.random.rand()
    probability_value = np.exp((current_energy - new_energy) / temperature)

    if decision_factor < probability_value:
        return True
    else:
        return False


def system_energy():
    """Calculate energy of whole system"""
    return


def main():
    # initial temperature
    temp: int = T

    # nodes = generate_nodes(10)
    # for i in range(1, I_MAX):
    #     if temp <= 0:
    #         break
    #     node, n = get_random_node(nodes)
    #     init_energy = calculate_energy(nodes, node)
    #     new_pos = change_node_position(node[0][0], node[0][1], node[0][2])
    #     new_node = (new_pos, node[1])
    #     new_energy = calculate_energy(nodes, new_node)
    #
    #     is_better = check_energy(init_energy, new_energy, temp)
    #     if is_better:
    #         nodes[n] = new_node
    #     temp -= DROP_RATE
    nodes = generate_nodes(10)
    while temp > 0:
        for i in range(1, I_MAX):
            node, n = get_random_node(nodes)
            init_energy = calculate_energy(nodes, node)
            new_pos = change_node_position(node[0][0], node[0][1], node[0][2])
            new_node = (new_pos, node[1])
            new_energy = calculate_energy(nodes, new_node)

            is_better = check_energy(init_energy, new_energy, temp)
            if is_better:
                nodes[n] = new_node
        try:
            energy_values.append(nodes[n][1])
        except UnboundLocalError:
            pass
        temp -= DROP_RATE
    print(energy_values[-1])
    print(np.max(energy_values))
    print(np.min(energy_values))
    print(np.average(energy_values))
    energy_values_reduced = energy_values[::20]
    plt.plot(range(0, len(energy_values), 20), energy_values_reduced, marker='o', linestyle='-')
    plt.xlabel('Iterations')
    plt.ylabel('Energy')
    plt.title('Energy change over iterations')
    plt.grid(True)
    plt.scatter(len(energy_values) - 1, energy_values[-1], color='red')
    plt.show()


if __name__ == "__main__":
    main()
