"""Script to calculate all the manhatt distances and store them in a dictionnary"""
from collections import deque
import pickle

def generate_valid_neighbors(x, y):
    """
    Given x and y coordinates, generate all valid neighbors on the Abalone board.
    A neighbor is considered valid if it exists on the board and shares a side with the current cell.
    """
    # Potential neighbors for all cells
    neighbors = [(x-2, y), (x+2, y)]  # Left and right neighbors
    
    # Additional potential neighbors depending on the row
    if y % 2 == 0:  # For even rows
        neighbors.extend([(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)])
    else:  # For odd rows
        neighbors.extend([(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)])
    
    # Filtering neighbors that are not valid based on the set of valid coordinates
    valid_neighbors = [neighbor for neighbor in neighbors if neighbor in valid_coordinates]
    
    return valid_neighbors

def bfs_shortest_path(start, goal):
    # Initialize the queue with the start position and a count of 0 steps
    queue = deque([(start, 0)])
    # Set to keep track of visited cells
    visited = set()
    visited.add(start)
    
    # Continue until the queue is empty
    while queue:
        current, steps = queue.popleft()
        # Return the number of steps if the goal is reached
        if current == goal:
            return steps
        # Get all valid neighbors
        for neighbor in generate_valid_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, steps + 1))
    
    # If the goal is not reachable, return None
    return None

# We should first create a list of all valid coordinates on the board based on your image.
valid_coordinates = set([
    (4, 0), (3, 1), (2, 2), (1, 3), (0, 4),
    (6, 0), (5, 1), (4, 2), (3, 3), (2, 4), (1, 5),
    (8, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6),
    (10, 0), (9, 1), (8, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7),
    (12, 0), (11, 1), (10, 2), (9, 3), (8, 4), (7, 5), (6, 6), (5, 7), (4, 8),
    (14, 0), (13, 1), (12, 2), (11, 3), (10, 4), (9, 5), (8, 6), (7, 7), (6, 8),
    (16, 0), (15, 1), (14, 2), (13, 3), (12, 4), (11, 5), (10, 6), (9, 7), (8, 8),
    (15, 3), (14, 4), (13, 5), (12, 6), (11,7), (10, 8),
    (16, 4), (15, 5), (14, 6), (13, 7), (12, 8),
])

# Test the new function with the same cells to verify correctness
# Function to precompute all shortest path distances
def precompute_distances(valid_cells):
    distance_table = {}
    for start in valid_cells:
        for goal in valid_cells:
            if start != goal:
                # Use a tuple (start, goal) as the key for the dictionary
                distance_table[(start, goal)] = bfs_shortest_path(start, goal)
    return distance_table

## Now call the precompute function and store the result in 'all_distances'
all_distances = precompute_distances(valid_coordinates)

# Test printing some distances to verify (you can remove or comment this out later)
test_cases = [((11, 5), (10, 8)), ((4, 0), (4, 4)), ((0, 4), (8, 0)), ((7, 3), (9, 5))]
for start, goal in test_cases:
    print(f"Distance from {start} to {goal}: {all_distances[(start, goal)]}")

# Assuming 'all_distances' is your distance table
with open('abalone_distances.pkl', 'wb') as f:
    pickle.dump(all_distances, f)