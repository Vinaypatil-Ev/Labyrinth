# -*- coding: utf-8 -*-
from random import choice
import numpy as np
import networkx as nx
from setch import Setch #set with random choice


def gen_maze(dim):
    """
    Maze generator.
    """
    G = nx.grid_graph(dim)
    tree = nx.Graph()
    old_node = choice(list(G))
    tree.add_node(old_node)
    all_neighbors = Setch(*G.neighbors(old_node))
    while tree.order() < G.order():
        neighbors = [node for node in G.neighbors(old_node)\
                     if node not in tree]
        if neighbors:
            new_node = choice(neighbors)
            neighbors.remove(new_node)
        else: #Dead-end
            new_node = all_neighbors.choose()
            nodes_in_tree, neighbors = [], []
            for node in G.neighbors(new_node):
                (nodes_in_tree if node in tree else neighbors).append(node)
            old_node = choice(nodes_in_tree)
        all_neighbors.remove(new_node)
        tree.add_edge(old_node, new_node)
        all_neighbors += neighbors
        old_node = new_node
    return G, tree

def maze_to_array(maze, dim):
    maze_copy = maze.copy() #copy, so we don't ruin the maze as we remove edges
    nodes = list(maze_copy)
    maze_array = np.full([2 * i + 1 for i in dim[::-1]], 0, dtype=np.float32)
    for node in nodes:
        node_x, node_y = (2 * i + 1 for i in node)
        maze_array[node_x: node_x + 1, node_y: node_y + 1] = 1
        for neighbor in list(maze_copy.neighbors(node)):
            path_x, path_y = (i + j + 1 for i, j in zip(node, neighbor))
            maze_array[path_x: path_x + 1, path_y: path_y + 1] = 1
            maze_copy.remove_edge(node, neighbor) #Don't add redundant cells

    #Randomly place start and finish cells on opposite sides
    flip = round(np.random.random())
    random_pos1 = 2 * np.random.randint(0, dim[flip]) + 1
    random_pos2 = 2 * np.random.randint(0, dim[flip]) + 1
    length = 2 * dim[not flip]
    start = (slice(random_pos1, random_pos1 + 1), slice(0, 1))
    finish = (slice(random_pos2, random_pos2 + 1), slice(length, length + 1))
    #Broadcast cells
    maze_array[start if flip else start[::-1]] = 1
    maze_array[finish if flip else finish[::-1]] = 1
    start_coord = (random_pos1, 0)
    return start_coord if flip else start_coord[::-1], maze_array
