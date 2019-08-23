# -*- coding: utf-8 -*
from random import choice
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.core.window import Window
import numpy as np
import networkx as nx
import maze_gen

CELL_SIZE = 5
PLAYER_COLOR = (.5, .5, 1)
PLAYER_CELL = np.dstack([np.full([CELL_SIZE, CELL_SIZE], i, dtype=np.float32)\
                         for i in PLAYER_COLOR])

class Display(Widget):
    def __init__(self, **kwargs):
        super(Display, self).__init__(**kwargs)
        self.maze_dim = [0, 0]
        self.level = 0
        self.new_level()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'left', 'right', 'down']:

            positions = {'up' : np.array([0, -1]),
                         'left' : np.array([-1, 0]),
                         'right' : np.array([1, 0]),
                         'down' : np.array([0, 1])}

            new_location = self.player_loc + positions[keycode[1]]

            #Check if we've completed maze
            if all(new_location == 2 * np.array(self.maze_dim)\
                                   + np.array([-1, -2])):
                self.new_level()
                return True

            maze_loc = self.maze_loc(new_location)
            #Check if we're in-bounds and no walls are in our way
            if all((0 <= i < j\
                   for i, j in zip(maze_loc, self.maze_array.shape))) and\
               self.maze_array[maze_loc]:
                self.player_loc = new_location
                for i in range(self.level): #More changes as we increase levels
                    self.labyrinth_change()
                maze_stack = np.dstack([self.maze_array]*3)
                maze_stack[self.loc_to_slices(self.player_loc)] = PLAYER_CELL
                self.texture.blit_buffer(maze_stack[::-1].tobytes(),\
                                         bufferfmt='float')
                self.canvas.ask_update()
        return True

    def new_level(self):
        self.maze_dim = [self.maze_dim[0] + 10, self.maze_dim[1] + 10]
        self.level += 1
        #Reset variables
        self.grid = nx.grid_graph(self.maze_dim)
        self.maze = maze_gen.gen_maze(self.maze_dim)
        self.maze_array = maze_gen.maze_to_array(self.maze,\
                                                 self.maze_dim,\
                                                 CELL_SIZE)
        self.player_loc = np.array([-1, 0])
        self.texture = Texture.create(size=self.maze_array.T.shape)
        self.texture.mag_filter = 'nearest'
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos,\
                                  size=(self.width, self.height))
        self.bind(size=self._update_rect, pos=self._update_rect)

        #Draw new maze
        maze_stack = np.dstack([self.maze_array]*3)
        maze_stack[self.loc_to_slices(self.player_loc)] = PLAYER_CELL
        self.texture.blit_buffer(maze_stack[::-1].tobytes(),\
                                 bufferfmt='float')
        self.canvas.ask_update()


    def labyrinth_change(self):
        if np.random.random() > .3: #30% chance to change maze after a move
            return

        #Find a wall to remove (adding edges removes walls)
        while True:
            random_node = choice(list(self.maze))
            neighbors = [node\
                         for node in self.grid.neighbors(random_node)\
                         if node not in self.maze.neighbors(random_node)]
            if len(neighbors) > 0:
                new_neighbor = choice(neighbors)
                break

        #Adding an edge to a tree creates a cycle
        self.maze.add_edge(random_node, new_neighbor)
        #So we can remove any edge from that cycle to get back to a tree
        walls_we_can_add = list(nx.find_cycle(self.maze, random_node))
        added_wall = choice(walls_we_can_add)
        self.maze.remove_edge(*added_wall)
        #Our underlying graph is a tree again -- the maze is still solvable.

        removed_wall_loc = (i + j for i, j in zip(random_node, new_neighbor))
        added_wall_loc = (i + j for i, j  in zip(*added_wall))
        self.maze_array[self.loc_to_slices(removed_wall_loc, False)] = 1
        self.maze_array[self.loc_to_slices(added_wall_loc, False)] = 0

    def maze_loc(self, loc):
        scale_x, scale_y = (CELL_SIZE * (i + 1) for i in loc)
        return scale_y, scale_x

    def loc_to_slices(self, loc, invert=True):
        scale_x, scale_y = (CELL_SIZE * (i + 1) for i in loc)
        x_slice, y_slice =  (slice(i, i + CELL_SIZE) for i in [scale_x, scale_y])
        return (y_slice, x_slice) if invert else (x_slice, y_slice)


class Labyrinth(App):

    def build(self):
        return Display()

if __name__ == '__main__':
    Labyrinth().run()
