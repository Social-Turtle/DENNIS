import pygame

class Model:
    def __init__(self, f_createModel):
        self.neurons, self.dendrites = f_createModel()

    def update(self):
        for neuron in self.neurons:
            neuron.update()
        for dendrite in self.dendrites:
            dendrite.update()

    def draw(self, screen):
        for neuron in self.neurons:
            neuron.draw(screen)
