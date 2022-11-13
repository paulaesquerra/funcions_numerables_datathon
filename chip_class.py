from typing import List, Tuple
import numpy as np


class Pin:
    """Pins in the chip."""
    def __init__(self, name: str, x: int, y: int):
        self.name: str = name
        self.x: int = x
        self.y: int = y

    def __str__(self):
        return self.name + " " + str(self.x) + " " + str(self.y)


class Edge:
    """Edges where the weights are the Manhattan distance."""
    def __init__(self, conn_in: Pin, conn_out: Pin, i:int = 0):
        self.conn_in: Pin = conn_in
        self.conn_out: Pin = conn_out
        self.dist: int = abs(conn_in.x - conn_out.x) + abs(conn_in.y - conn_out.y)
        self.i=i

    def __str__(self):
        return self.conn_in.name + " " + self.conn_out.name


def obx(p:Pin) -> int:
    """Returns x-coordinate of the pin."""
    return p.x

def oby(p:Pin) -> int:
    """Returns y-coordinate of the pin."""
    return p.y


class Chip:
    """The Chip class creates a graph that represents the connections between pins."""

    def __init__(self, test):
        """Variables initialized:
            self.not_connected: list that contains the pins that are not yet connected.
            self.driver_pins_plus: list with input pins.
            self.driver_pins_minus: list with output pins.
            self._max_y: max y-coordinate of the pins (used for the fast implementation).
            self._min_y: min y-coordinate of the pins (used for the fast implementation).
            self.graphs: list that stores the edges added to the chip.
            self._intervals: splits the y axis into 32 different intervals (used for the fast implementation).
        """
        self.not_connected: List[Pin] = []
        self.driver_pins_plus: List[Pin] = []
        self.driver_pins_minus: List[Pin] = []
        self._max_y: int =-1
        self._min_y: int =-1
        self.graph: List[Edge] = []
        self._read(test)
        y_0=self._min_y
        ymax=self._max_y
        self._intervals: List[int] = []
        for i in range(33):
            self._intervals.append(y_0+i*(ymax-y_0)/32)
        self._intervals[0] = y_0-1

    def _read(self, test: str) -> None:
        """Reads data from the given file and stores it in the not_connected and driver_pins lists.

        Args:
            test: string with filename.
        """
        document = []
        with open(test, "r") as file:
            for line in file:
                document.append(str(line).split())

        data_section = False
        for i in range(len(document)):
            line = document[i]

            if len(line) > 0:
                if line[0] == "-":
                    data_section = True
                    line3 = document[i+2]
                    dp = Pin(line[1], int(line3[3]), int(line3[4]))
                    if line[7] == "INPUT":
                        self.driver_pins_plus.append(dp)
                    else:
                        self.driver_pins_minus.append(dp)

                elif line[0] != "+" and data_section:
                    p = Pin(line[0], int(line[5]), int(line[6]))
                    self.not_connected.append(p)
                    if p.y < self._min_y or self._min_y == -1:
                        self._min_y = p.y
                    if p.y>self._max_y or self._max_y == -1:
                        self._max_y = p.y

    def _statistics(self, sample: List[int]) -> Tuple[int, int]:
        """Computes metrics for the fast method.

        Args:
            sample: list with the lengths of every chain.

        Returns:
            standard_dev: standard deviation.
            mean.
        """
        mean=sum(sample)/len(sample)
        deviations = [(x - mean) ** 2 for x in sample]
        standard_dev = np.sqrt(sum(deviations)/(len(sample)-1))
        return standard_dev, mean

    def _add_edge(self, a: Pin, b: Pin, global_distance: int, partial_distance: List[int], i: int) -> None:
        """Adds an edge to the graph and updates parameters.

        Args:
            a: conn_in pin.
            b: conn_out pin.
            global_distance: total length of all the chains.
            partial_distance: list with the length of every chain.
            i: index of the current interval.

        Returns:
            global_distance: updated total length.
        """
        e=Edge(a, b)
        self.graph.append(e)
        global_distance += e.dist
        partial_distance[i] +=e.dist
        return global_distance

    def find_paths_fast_version(self):
        """Faster algorithm, O(nlogn).

        This method splits the y-axis into 32 different intervals. Each interval is associated to a driver pin
        (0 to 15 are input drivers, 16 to 31 are output). We group the intervals in pairs so that each input driver
        is associated with one output driver (0 with 16, 1 with 17 and so on). The chains that we create take all the
        nodes from a pair of intervals. From the input interval, we connect them by ordering them by x-coordinate
        (visually going from left to right). Then we connect the node with the largest x-coordinate to the node with the
        largest x-coordinate in the output interval. We then connect the nodes in the output interval again ordered by
        x-coordinate, until we reach the output driver.

        Returns:
            global_distance: total length of the chains.
            standard_dev: standard deviation of the lengths of the chains.
            mean: mean value of the lengths of the cahins.
        """
        global_distance = 0
        partial_distance = [0]*16
        self.driver_pins_plus.sort(key=oby) #in
        self.driver_pins_minus.sort(key=oby) #out
        selection = []

        for i in range(32):
            selection.append([])
        for node in self.not_connected:
            for i in range(32):
                if node.y > self._intervals[i] and self._intervals[i+1] >= node.y:
                    selection[i].append(node)
        for i in range(32):
            selection[i].sort(key=obx) #sorts pins from nearest to furthest.

        for i in range(16):
            act_sel = selection[i]
            global_distance = self._add_edge(self.driver_pins_plus[i],act_sel[0], global_distance, partial_distance, i)

            for j in range(len(act_sel)-1):
                global_distance = self._add_edge(act_sel[j], act_sel[j+1], global_distance, partial_distance, i)
            next_sel = selection[16+i]
            global_distance = self._add_edge(act_sel[-1], next_sel[-1], global_distance, partial_distance, i)

            for j in range(len(next_sel)-1):
                global_distance = self._add_edge(next_sel[j+1],next_sel[j], global_distance, partial_distance, i)
            global_distance = self._add_edge(next_sel[0],self.driver_pins_minus[i], global_distance, partial_distance, i)

        standard_dev, mean= self._statistics(partial_distance)
        return global_distance, standard_dev, mean

    def _min_edge(self, node: Pin)->Edge:
        """Finds best edge to remove from the chain.

        Args:
            node: new pin that we have to add.

        Returns:
            answer: the optimal edge to remove, that is, if we remove this edge and replace it by 2 edges
                connected to the new node, the added length is minimized.
        """
        first = True
        minim = 0
        answer = self.graph[0]
        for edge in self.graph:
            edge1 = Edge(edge.conn_in, node)
            edge2 = Edge(edge.conn_out, node)
            dist = edge1.dist + edge2.dist - edge.dist
            if dist < minim or first:
                first = False
                minim = dist
                answer = edge
        return answer

    def find_paths_slow_version(self) -> int:
        """Slower but more accurate algorithm, O(n^3).

        This method first connects each input driver with an output driver. Then, at each iteration, the algorithm
        connects one pin (node) to a path / chain. To do so, we need to remove an edge from a chain, and add two new
        edges: from the new pin to each of the 2 pins from the edge we removed. The algorithm chooses the pin and edge
        that minimizes the added length of the chain.

        Returns:
            global_distance: total length of the chains.
            standard_dev: standard deviation of the lengths of the chains.
            mean: mean value of the lengths of the cahins.
        """
        global_distance = 0
        partial_distance = [0]*16

        for i in range(len(self.driver_pins_plus)):
            pin_plus = self.driver_pins_plus[i]
            pin_minus = self.driver_pins_minus[i]
            edge = Edge(pin_plus, pin_minus, i)
            self.graph.append(edge)
            global_distance += edge.dist
            partial_distance[i] += edge.dist

        while (len(self.not_connected) > 0):
            first = True
            minim = 0
            old_node = None
            old_edge = None
            for node in self.not_connected:
                deleted_edge = self._min_edge(node)
                if first or minim > deleted_edge.dist:
                    first = False
                    minim = deleted_edge.dist
                    old_edge = deleted_edge
                    old_node = node

            self.not_connected.remove(old_node)
            self.graph.remove(old_edge)
            global_distance -= old_edge.dist
            i=old_edge.i
            partial_distance[i] -= old_edge.dist
            edge1 = Edge(old_edge.conn_in,old_node,i)
            edge2 = Edge(old_node,old_edge.conn_out, i)
            self.graph.append(edge1)
            global_distance += edge1.dist
            partial_distance[i] += edge1.dist
            self.graph.append(edge2)
            global_distance += edge2.dist
            partial_distance[i] += edge2.dist
        standard_dev, mean= self._statistics(partial_distance)
        return global_distance, standard_dev, mean
