import time

start_time = time.time()  # Record program start time

class EnergyTracker:
    def __init__(self):
        self.synapse_events = []
        self.dendrite_fires = []

    def log_synapse_flip(self, dendrite_id, synapse_index, turned_on):
        """Track polarization flips of synapses. Takes dendrite_id, 
        synapse_index, and whether or not new_value == True"""
        self.synapse_events.append((dendrite_id, synapse_index, turned_on))

    def log_dendrite_fire(self, dendrite_id, n):
        """Log a dendrite firing event
        with its ID for debugging, and n for energy consumption."""
        self.dendrite_fires.append((dendrite_id, n))

    def reset(self):
        """Kill everything and start over!"""
        self.synapse_events.clear()
        self.dendrite_fires.clear()

energy_tracker = EnergyTracker()
