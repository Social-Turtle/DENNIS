import pygame
from pygame.math import Vector2
import math
import time
import energy_modelling
from energy_modelling import energy_tracker

class Dendrite:
    def __init__(self, neuron, self_timeout=.25):
        """
        Create a dendrite connected to a neuron.
        neuron: Neuron object this dendrite feeds into.
        """
        self.connections = []  # Excitatory input neurons
        self.inhibitors = []  # Inhibitory input neurons
        self.synapse_states = []  # Track the current state of each synapse ** IS 0 or n the synapse closest to the neuron?**
        self.last_active_time = 0  # Last time a state of synapse_states changed
        self.timeout = self_timeout  # Length of inactivity before reset
        self.neuron = neuron  # Neuron this dendrite feeds into
        self.last_print_time = 0 
        self.print_interval = 0.1
        neuron.dendrites.append(self)

    def synapse(self, neuron, inhibitory=False):
        """
        Connect a neuron to this dendrite.
        If inhibitory=True, neuron is an inhibitor.
        """
        neuron.downstream_dendrites.append(self)
        if inhibitory:
            self.inhibitors.append(neuron)
        else:
            self.connections.append(neuron)

    def update(self):
        """
        Propagate spikes along the synapse chain.
        If a spike is detected at the start, propagate it down the chain.
        Reset all synapses if no activity for self.timeout seconds.
        """
        n = len(self.connections)
        if len(self.synapse_states) != n:
            self.synapse_states = [False] * n

        # Check for inhibitory input
        for inhibitor in self.inhibitors:
            if hasattr(inhibitor, "is_firing") and inhibitor.is_firing:
                self.synapse_states = [False] * n
                self.last_active_time = time.time()
                return

        any_spike = False

        # Work from farthest to closest to neuron
        for i in range(n):
            parent = self.connections[i]
            if hasattr(parent, "is_firing") and parent.is_firing:
                any_spike = True
                if i == 0:
                    # If the first in the tree, set its state directly
                    self.synapse_states[0] = parent.is_firing
                else:
                    # Otherwise, propagate the state from the previous synapse
                    self.synapse_states[i] = parent.is_firing and self.synapse_states[i-1]

        if any_spike:
            self.last_active_time = time.time()

        # Reset if timeout exceeded
        if time.time() - self.last_active_time > self.timeout:
            self.synapse_states = [False] * n


    @property
    def firing(self):
        # Dendrite is "firing" if the last synapse in the chain is high
        return len(self.synapse_states) > 0 and self.synapse_states[-1]


    def reset(self):
        """Immediately reset all synapse states to False."""
        self.synapse_states = [False] * len(self.synapse_states)
        self.last_active_time = time.time()

    def throttled_print(self, *args, **kwargs):
        # Slowed print to avoid flooding the console during debugging
        now = time.time()
        if now - self.last_print_time > self.print_interval:
            print(*args, **kwargs)
            self.last_print_time = now

    def draw(self, screen, upstream_display_connection=None):
        #Drawing tools
        average_connection_position = Vector2(0, 0)
        for connection in self.connections:
            average_connection_position += connection.position
        for inhibitor in self.inhibitors:
            average_connection_position += inhibitor.position

        n_totalConnections = len(self.connections) + len(self.inhibitors)
        average_connection_position /= n_totalConnections
        dir_to_connections = (average_connection_position - self.neuron.position).normalize()

        def calculate_connection_position(f):
            connection_position = self.neuron.position + \
                                  dir_to_connections * self.neuron.radius * (6 - (4 * f))
            return connection_position

        def draw_line(neuron, f):
            connection_position = calculate_connection_position(f)
            pygame.draw.line(screen, neuron.get_current_color(),
                             connection_position, neuron.position, width=4)

        def draw_curved_line(neuron, f):
            connection_position = calculate_connection_position(f)
            displacement = (connection_position - neuron.position)
            distance = displacement.length()
            radius = distance * 3 / 2
            midpoint = (connection_position + neuron.position) / 2
            distance_to_center = math.sqrt(radius**2 - (distance/2)**2)
            normal = Vector2(-displacement.y, displacement.x).normalize()
            center = midpoint + distance_to_center * normal
            bounds = pygame.Rect(center.x - radius,
                                 center.y - radius,
                                 2 * radius,
                                 2 * radius)
            angle1 = (connection_position - center).angle_to(Vector2(1, 0))
            angle2 = (neuron.position - center).angle_to(Vector2(1, 0))
            pygame.draw.arc(screen, neuron.get_current_color(),
                            bounds, math.radians(angle1), math.radians(angle2), width=1)

        if upstream_display_connection is None:
            i = 0
            for connection in self.connections:
                draw_curved_line(connection, i/n_totalConnections)
                i = i + 1
            for inhibitor in self.inhibitors:
                draw_curved_line(inhibitor, i/n_totalConnections)
                i = i + 1
        else:
            draw_curved_line(upstream_display_connection, 0)

        draw_line(self.neuron, 0)
