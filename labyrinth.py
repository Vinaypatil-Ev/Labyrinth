# -*- coding: utf-8 -*
from random import choice
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.core.window import Window
import numpy as np
import networkx as nx
from maze_gen import gen_maze, maze_to_array

PLAYER_COLOR = np.array([.5, .5, 1], dtype=np.float32)

class Display(Widget):
    def __init__(self, **kwargs):
        super(Display, self).__init__(**kwargs)
        self.level = 0
        self._new_level()
        self.bind(size=self._update_rect, pos=self._update_rect)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _blit(self):
        maze_stack = np.dstack([self.maze_array]*3)
        maze_stack[tuple(self.player_loc)] = PLAYER_COLOR
        self.texture.blit_buffer(maze_stack[::-1].tobytes(), bufferfmt='float')
        self.canvas.ask_update()

    def _new_level(self):
        self.level += 1
        self.maze_dim = [10 * self.level] * 2
        self.grid, self.maze = gen_maze(self.maze_dim)
        self.player_loc, self.maze_array = maze_to_array(self.maze,\
                                                         self.maze_dim)
        self.texture = Texture.create(size=self.maze_array.T.shape)
        self.texture.mag_filter = 'nearest'
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos,\
                                  size=(self.width, self.height))
        self._blit()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        directions = {   'up' : (-1,  0),
                       'left' : ( 0, -1),
                      'right' : ( 0,  1),
                       'down' : ( 1,  0)}

        if keycode[1] not in directions:
            return True

        new_loc = self.player_loc + np.array(directions[keycode[1]])
        #Check if we're in-bounds and no walls are in our way
        if all(new_loc >= 0) and self.maze_array[tuple(new_loc)]:

            #Check if we've completed maze
            if any(new_loc == 2 * np.array(self.maze_dim)):
                self._new_level()
                return True

            #Move player
            self.player_loc = new_loc
            for _ in range(self.level): #More changes as we increase levels
                self._labyrinth_change()
            self._blit()
        return True

    def _labyrinth_change(self):
        if np.random.random() > .3: #30% chance to change maze after a move
            return

        #Find a wall to remove -- equivalently, add an edge to our maze's tree
        while True:
            random_node = choice(list(self.maze))
            neighbors = [node for node in self.grid.neighbors(random_node)\
                         if node not in self.maze.neighbors(random_node)]
            if neighbors:
                neighbor = choice(neighbors)
                break

        #Adding an edge to a tree creates a cycle
        self.maze.add_edge(random_node, neighbor)
        #So we can remove any edge from that cycle to get back to a tree
        new_wall = choice(nx.find_cycle(self.maze, random_node))
        #Removing an edge == adding a wall
        self.maze.remove_edge(*new_wall)
        #Our underlying graph is a tree again -- the maze is still solvable.

        removed_wall_loc = (i + j + 1 for i, j in zip(random_node, neighbor))
        new_wall_loc = (i + j + 1 for i, j  in zip(*new_wall))
        self.maze_array[tuple(removed_wall_loc)] = 1
        self.maze_array[tuple(new_wall_loc)] = 0


class Labyrinth(App):
    def build(self):
        return Display()

if __name__ == '__main__':
    Labyrinth().run()
