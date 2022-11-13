import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
from chip_class import Chip

def main():
    #file = input("Select the input you wish to test (without the .def): ")
    file = sys.argv[1]
    c = Chip(file)

    # we create the graph by using pins as nodes
    G = nx.Graph()
    for pin in c.not_connected:
        G.add_node(pin.name, pos = (pin.x, pin.y), color = 'blue')

    method = "fast"     #str(input("Choose fast or slow method: "))

    # we create the path using either the fast or the slow algo
    if (method == "fast"):
        global_distance, standard_dev, mean = c.find_paths_fast_version()


    elif (method == "slow"):
        global_distance, standard_dev, mean = c.find_paths_slow_version()

    # we add driver pins
    for pin_min, pin_plus in zip(c.driver_pins_minus, c.driver_pins_plus):
        G.add_node(pin_plus.name, pos = (pin_plus.x, pin_plus.y), color = 'red')
        G.add_node(pin_min.name, pos = (pin_min.x, pin_min.y), color = 'red')
    # we add edges
    for e in c.graph:
        G.add_edge(e.conn_in.name, e.conn_out.name)

    # plotting the graph
    pos = nx.get_node_attributes(G, 'pos')
    colors = nx.get_node_attributes(G, 'color')
    colors_list = []
    for color in colors.values():
        colors_list.append(color)
    nx.draw(G, pos = pos, node_size = 5, node_color = colors_list)

    # writing the result into a file
    output_file = open(os.getcwd() + "/" + file + "_output.def", "w")
    for e in c.graph:
        output_file.write("- BOGUS NET NAME\n"
                        + "  (  " + e.conn_in.name + " conn_in )\n"
                        + "  (  " + e.conn_out.name + " conn_out )\n;\n")

    output_file.close()

    print('global_distance: ', global_distance)
    print('mean: ', mean)
    print('standard deviation: ', standard_dev)
    
    plt.show()

main()
