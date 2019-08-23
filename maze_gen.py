# -*- coding: utf-8 -*-
from random import choice
import networkx as nx
from setch import Setch #set with random choice
import numpy as np

def gen_maze(DIM):
    """
    Maze generator.
    """
    G = nx.grid_graph(DIM)
    tree = nx.Graph()
    old_node = choice(list(G))
    tree.add_node(old_node)
    all_neighbors = Setch(*G.neighbors(old_node))
    while tree.order() < G.order():
        neighbors = [node for node in G.neighbors(old_node)\
                     if node not in tree]
        try:
            new_node = choice(neighbors)
            neighbors.remove(new_node)
        except IndexError: #Dead-end
            new_node = all_neighbors.choose()
            nodes_in_tree, neighbors = [], []
            for node in G.neighbors(new_node):
                (nodes_in_tree if node in tree else neighbors).append(node)
            old_node = choice(nodes_in_tree)
        all_neighbors.remove(new_node)
        tree.add_edge(old_node, new_node)
        all_neighbors += neighbors
        old_node = new_node
    return tree

def maze_to_array(maze, DIM, start="top_left", end="bottom_right"):
    """
    Cells in the maze will be of dimension size * size.

    'start'/'end' parameters can be one of:
        'top_left', 'top_right',
        'bottom_left', 'bottom_right'
    """
    #Check that position options are valid.
    pos_options = ["top_left", "top_right", "bottom_left", "bottom_right"]
    if not all([pos in pos_options for pos in [start, end]]):
        raise ValueError("'start, end' arguments invalid.")

    maze_copy = maze.copy() #copy, so we don't ruin the maze as we remove edges
    nodes = list(maze_copy)
    maze_array = np.full([2 * i + 1 for i in DIM[::-1]], 0, dtype=np.float32)
    for node in nodes:
        node_x, node_y = (2 * i + 1 for i in node)
        maze_array[node_x: node_x + 1, node_y: node_y + 1] = 1
        for neighbor in list(maze_copy.neighbors(node)):
            path_x, path_y = (i + j + 1 for i, j in zip(node, neighbor))
            maze_array[path_x: path_x + 1, path_y: path_y + 1] = 1
            maze_copy.remove_edge(node, neighbor) #Don't add redundant cells

    #Create start and finish cells
    positions = {"top"   : slice(1, 2),
                 "bottom": slice(2 * DIM[1] - 1, 2 * DIM[1]),
                 "left"  : slice(0, 1),
                 "right" : slice(2 * DIM[0], 2 * DIM[0] + 1)
                 }
    #Parse
    y_start, x_start, y_end, x_end = start.split("_") + end.split("_")
    y_start, x_start = positions[y_start], positions[x_start]
    y_end, x_end = positions[y_end], positions[x_end]
    #Broadcast cells
    maze_array[y_start, x_start] = 1
    maze_array[y_end, x_end] = 1

    return maze_array
