import time
import pygame
from colors import *
from pygame.math import Vector2
import math

class Neuron:
    def __init__(self, position, radius, active_color=BLUE):
        # List of incoming dendrites (connections from other neurons)
        self.dendrites = []
        # List of sensory input functions (return True if input is active)
        self.sensory_inputs = []
        # List of output functions to call when neuron fires
        self.target_outputs = []
        self.position = Vector2(position)
        self.radius = radius
        self.active_color = active_color
        self.last_print_time = 0
        self.print_interval = 1
        self.last_fired_time = 0
        # List of dendrites this neuron connects to (downstream)
        self.downstream_dendrites = []
        self.last_checked_firing = False

    def update(self):
        # Store firing state for this frame
        self._firing = any(f() for f in self.sensory_inputs) or any(d.firing for d in self.dendrites)
        if self._firing:
            self.last_fired_time = time.time()
            for f_targetOutput in self.target_outputs:
                f_targetOutput()
            # Reset all incoming dendrites after firing
            for dendrite in self.dendrites:
                dendrite.reset()
            

    def throttled_print(self, *args, **kwargs):
        now = time.time()
        if now - self.last_print_time > self.print_interval:
            print(*args, **kwargs)
            self.last_print_time = now

    def draw(self, screen):
        color = self.get_current_color()
        if self.is_inhibitory:
            # Draw as a circle for inhibitory neurons
            pygame.draw.circle(screen, color, self.position, self.radius)
        else:
            # Draw as a triangle for regular neurons
            x, y = self.position.x, self.position.y
            r = self.radius/1.2
            points = [
                (x, y - r),         # Top point
                (x - r, y + r),     # Bottom left
                (x + r, y + r),     # Bottom right
            ]
            pygame.draw.polygon(screen, color, points)

        if (pygame.mouse.get_pos() - self.position).length_squared() <= self.radius**2:
            for dendrite in self.dendrites:
                dendrite.draw(screen)
            for dendrite in self.downstream_dendrites:
                dendrite.draw(screen, upstream_display_connection=self)

    def get_current_color(self):
        linger_time = 0.1
        if (time.time() - self.last_fired_time) < linger_time:
            return self.active_color
        else:
            return interpolate_color(WHITE, self.active_color, 0.25)
        
    @property
    def is_firing(self):
        return getattr(self, '_firing', False)
    
    @property
    def is_inhibitory(self):
        # Returns True if this neuron is an inhibitor on any dendrite
        return any(self in dendrite.inhibitors for dendrite in self.downstream_dendrites)
