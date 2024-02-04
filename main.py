import random as rand
from math import sqrt
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from skspatial.objects import Sphere

CONSTANT_K = 8.99 * (10 ** 9)

# maximum iterations
I_MAX: int = 40

# temperature drop rate per iteration
DROP_RATE: float = 0.5

# initial temperature
T: float = 60.0

# sphere radius
R: int = 100

# number of points
N: int = 20


def generate_random_pos() -> tuple[float, float, float]:
    """Generate a random 3D position vector (x, y, z) for a node."""
    r = np.random.uniform(0, R)
    theta = np.random.uniform(0, np.pi)
    phi = np.random.uniform(0, 2 * np.pi)

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z


def get_random_current() -> int:
    """Generate a random current value within a given range for a node."""
    return rand.randint(1, 10)


def generate_nodes(n: int) -> list[Tuple[Tuple[float, float, float], int]]:
    """Create an array of N nodes, where N is a random number."""
    nodes = []
    for _ in range(n):
        # Generating three random coordinates
        pos = generate_random_pos()

        # Generating a random value for the node
        value = np.random.randint(1, 10) * (10 ** (-4))

        # Adding a tuple (coordinates, value) to the list of nodes
        nodes.append((pos, value))
    return nodes


def get_random_node(nodes: list) -> [[tuple[float, float, float], int], int]:
    """Get a random node from the array of nodes."""
    n = rand.randint(0, len(nodes) - 1)
    return nodes[n], n


def change_node_position(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Change the position of a node by adding a direction vector, e.g., [1, -1, 0] means moving up
    and left in 3 dimensions."""
    x_new = 0
    y_new = 0
    z_new = 0
    while True:
        r = np.random.uniform(0.1, R / 10)
        theta = np.random.uniform(0, np.pi)
        phi = np.random.uniform(0, 2 * np.pi)
        x_new = x + r * np.sin(theta) * np.cos(phi)
        y_new = y + r * np.sin(theta) * np.sin(phi)
        z_new = z + r * np.cos(theta)
        if x_new ** 2 + y_new ** 2 + z_new ** 2 <= R ** 2:
            break

    return x_new, y_new, z_new


def check_energy(energy: float, new_energy: float, temperature: float) -> bool:
    """Check whether we accept new energy state."""
    if abs(energy) > abs(new_energy):
        return True
    elif temperature < 0.95 * T:
        return probability_fun(energy, new_energy, temperature)
    else:
        return False


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


def calculate_energy(nodes: list, ref_node: tuple, n: int) -> float:
    """Calculates the total energy between all nodes and the reference node."""
    energy = 0.0
    ref_node_values, ref_node_charge = ref_node

    for node in nodes:
        if node == nodes[n]:
            continue
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


def extract_points(nodes: list) -> tuple:
    x = []
    y = []
    z = []
    for node in nodes:
        x.append(node[0][0])
        y.append(node[0][1])
        z.append(node[0][2])
    return x, y, z


def system_energy(nodes: list) -> float:
    """Calculate energy of whole system"""
    total_energy = 0.0
    for i in range(len(nodes)):
        total_energy += calculate_energy(nodes, nodes[i], i)
    return total_energy


def main():
    # initial temperature
    temp: float = T

    nodes = generate_nodes(N)

    # List to store energy values for each iteration
    energy_values = [system_energy(nodes)]
    points_pos = [(extract_points(nodes), temp)]

    end_counter = 0
    while temp > 1:
        for i in range(1, I_MAX):
            node, n = get_random_node(nodes)
            init_energy = energy_values[-1]
            new_pos = change_node_position(node[0][0], node[0][1], node[0][2])
            new_node = (new_pos, node[1])
            nodes_copy = nodes.copy()
            nodes_copy[n] = new_node
            new_energy = system_energy(nodes_copy)

            is_better = check_energy(init_energy, new_energy, temp)
            if is_better:
                nodes[n] = new_node
            total_energy = system_energy(nodes)
            energy_values.append(total_energy)
            points_pos.append((extract_points(nodes), temp))

        delta = abs(np.average(energy_values[-I_MAX:]) - energy_values[-1])
        if delta < 0.1:
            end_counter += 1
            if end_counter == 2:
                break
        else:
            end_counter = 0
        temp -= DROP_RATE

    time = range(0, len(energy_values))

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(2, 1, 2)
    sct2, = ax.plot(time, energy_values)
    plt.xlabel('Time')
    plt.ylabel('Energy')
    plt.grid(True)

    ax = fig.add_subplot(2, 1, 1, projection='3d')
    sct, = ax.plot([], [], [], "o", )
    title = ax.set_title("")

    sphere = Sphere([0, 0, 0], radius=R)
    sphere.plot_3d(ax, alpha=0.2)

    def update(ifrm):
        sct.set_data(points_pos[ifrm][0][0], points_pos[ifrm][0][1])
        sct.set_3d_properties(points_pos[ifrm][0][2])
        sct2.set_data(time[:ifrm + 1], energy_values[:ifrm + 1])
        title.set_text('T={:.0f}'.format(points_pos[ifrm][1]))
        return sct, title, sct2

    ax.set_xlim(-R, R)
    ax.set_ylim(-R, R)
    ax.set_zlim(-R, R)
    ani = FuncAnimation(fig, func=update, frames=len(points_pos), interval=1, repeat=False)
    plt.show()


if __name__ == "__main__":
    main()
