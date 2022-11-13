# CHIP CHIP

## Introduction

The goal of this challenge was to minimize the average length of chains that connected pins in a chip, while also trying to minimize the standard deviation of the lengths of the different chains.

## Implementation

We decided to approach this problem by modelling it by considering a graph, where the nodes are pins and the edges are the cables that run between connected pins. What we want to minimize is the average sum of the costs / distances of the edges of the connected components. We implemented 2 strategies for this, which use different criteria and have different runtimes.

## Strategy 1

The first strategy that was implemented works by trying to minimize the sum of the lengths of the chains. This method first connects each input driver with an output driver. Then, at each iteration, the algorithm connects one pin (node) to a path / chain. To do so, we need to remove an edge from a chain, and add two new edges: from the new pin to each of the 2 pins from the edge we removed. The algorithm chooses the pin and edge that minimizes the added length of the chain.

This strategy gives a good global average but has complexity O(n^3). Additionally, it doesn't quite match the criteria of trying to minimize the average length, just the global one. Therefore, it works well on smaller test cases (no larger than 1000), but it takes too long for larger cases.

## Strategy 2

Our second strategy, which has complexity O(nlogn), has less accuracy when it comes to minimizing the global sum of lengths / distances, but it can be used for much larger test cases.

This method splits the y-axis into 32 different intervals. Each interval is associated to a driver pin (0 to 15 are input drivers, 16 to 31 are output). We group the intervals in pairs so that each input driver is associated with one output driver (0 with 16, 1 with 17 and so on). The chains that we create take all the nodes from a pair of intervals. From the input interval, we connect them by ordering them by x-coordinate (visually going from left to right). Then we connect the node with the largest x-coordinate to the node with the largest x-coordinate in the output interval. We then connect the nodes in the output interval again ordered by x-coordinate, until we reach the output driver.
 
 ## Run it yourself
 
 In order to run the python code you should first download the repository and download the requierements:
 ```
 git clone https://github.com/paulaesquerra/funcions_numerables_datathon.git
 cd funcions_numerables_datathon
 pip3 install -r requirements.txt

 ```
 Then you can run:
 ```
 python3 main.py [input_file]
 ```
 When executed it will show you total path distance, the mean and the standard desviation, as well as the 
