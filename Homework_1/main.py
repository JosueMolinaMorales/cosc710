from collections import deque
import json
import threading

PATHS = []


def get_shortest_paths(graph):
    global PATHS
    pairs = []
    keys = list(graph.keys())
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            pairs.append((keys[i], keys[j]))
    print(f"Finding shortest paths for {len(pairs)} pairs")

    # Break the pairs into chunks to run in parallel
    chunk_size = 10_000
    chunks = [pairs[i:i+chunk_size] for i in range(0, len(pairs), chunk_size)]
    print(f"Running {len(chunks)} chunks")

    # Run paths finding for each chunk

    def find_paths(graph, pairs, paths):
        for pair in pairs:
            paths.append(bfs_shortest_paths(graph, pair[0], pair[1]))

    threads = []
    for (i, chunk) in enumerate(chunks):
        print(f"Running chunk {i+1}/{len(chunks)}")
        thread = threading.Thread(
            target=find_paths, args=(graph, chunk, PATHS))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
        print(f"Thread {thread} finished")


def find_degree_centrality(graph):
    degree_centrality = {}
    for node in graph:
        degree_centrality[node] = len(graph[node])
    return degree_centrality


def find_betweenness_centrality(graph):
    nodes = {}
    # Start by find the shortest paths between all nodes
    # Then, for each node, find the number of shortest paths that pass through it
    if len(PATHS) == 0:
        get_shortest_paths(graph)

    for node in graph:
        nodes[node] = betweenness_centrality(PATHS, node)

    return nodes


def betweenness_centrality(all_paths, node):
    ''' 
    For a given node n, its betweeness centrality is calculated as follows:
      # of shortest paths that pass through n / total # of shortest paths
    '''
    res = 0
    for paths in all_paths:
        paths = [path for path in paths if node !=
                 path[0] and node != path[-1]]
        if len(paths) == 0:
            continue
        res += (len([p for p in paths if node in p]) / len(paths))
    return res


def bfs_shortest_paths(graph, start, end):
    # Check if start and end nodes are valid
    if start not in graph or end not in graph:
        raise ValueError("Invalid start or end node")

    # Initialize a queue for BFS
    queue = deque([(start, [start])])

    # Initialize a set to keep track of visited nodes
    visited = set()

    # Initialize the minimum path length
    min_path_length = float('inf')

    # Initialize a list to store all shortest paths
    shortest_paths = []

    while queue:
        current_node, path = queue.popleft()

        # Mark the current node as visited
        visited.add(current_node)

        # Check if the current node is the destination
        if current_node == end:
            # Update minimum path length
            min_path_length = min(min_path_length, len(path))
            # Add the path to the list if it is a shortest path
            if len(path) == min_path_length:
                shortest_paths.append(path)
            continue

        # Enqueue neighbors of the current node
        for neighbor in graph[current_node]:
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return shortest_paths


def find_closeness_centrality(graph):
    '''
    To find the closeness centrality of a node, we need to calculate the mean length of all shortest paths from the node to all other nodes.
    '''
    if len(PATHS) == 0:
        get_shortest_paths(graph)
    cc = {}
    for node in graph:
        cc[node] = closeness_centrality(graph, node, PATHS)
    return cc


def closeness_centrality(graph, node, all_paths):
    res = 0
    # Get all paths that start or end with the node
    paths = []
    for paths in all_paths:
        paths = [path for path in paths if node == path[0] or node == path[-1]]
        if len(paths) == 0:
            continue
        res += len(paths[0]) - 1
    return round(1 / (res / (len(graph.keys())-1)), 2)


def find_clustering_coefficient(graph):
    cc = {}
    for node in graph:
        cc[node] = clustering_coefficient(graph, node)
    return cc


def clustering_coefficient(graph, node):
    '''
    A node's clustering coefficient is the number of closed triples in the node's neighborhood
    over the total number of triples in the neighborhood.
    '''
    neighbors = [n for n in graph[node]]
    if len(neighbors) == 1:  # if node has only one neighbor
        return 0.0

    existing_connections = sum(
        [1 for i in neighbors for j in neighbors if i != j and j in graph[i]])
    possible_connections = len(neighbors) * (len(neighbors) - 1)

    return round(existing_connections / possible_connections, 2)


def read_json(graph: dict, file: str):
    with open(file, "r", encoding="utf-8") as file:
        obj = json.load(file)
        nodes = dict()
        for node in obj["nodes"]:
            nodes[node["key"]] = node["attributes"]["label"]

        for edge in obj["edges"]:
            from_node = edge["source"]
            to_node = edge["target"]
            if from_node not in graph:
                graph[from_node] = set()
            if to_node not in graph:
                graph[to_node] = set()
            graph[from_node].add(to_node)
            graph[to_node].add(from_node)
        return nodes


def read_adjacency_list(graph: dict, file: str):
    with open(file, "r", encoding="utf-8") as file:
        '''
        Format of input file:
        {Node} - [Node1, Node2, ...]

        Example:
        1 - 2, 3, 4, 5
        2 - 1, 3, 4, 5
        '''
        try:
            lines = file.readlines()
            for line in lines:
                line = line.strip().split(" - ")
                node = int(line[0])
                connections = set(map(int, line[1].split(", ")))
                graph[node] = connections

                # Add reverse connections, since the graph is undirected
                for connection in connections:
                    if connection not in graph:
                        graph[connection] = set()
                    graph[connection].add(node)
        except:
            print("Invalid input file format")
            print("Example format: 1 - 2, 3, 4, 5")
            return


def main():
    # Read the file
    graph = {}
    nodes = {}

    args = sys.argv
    if len(args) < 2:
        print("Usage: python main.py <input_file>")
        return
    elif args[1].endswith(".json"):
        nodes = read_json(graph, args[1])
    elif args[1].endswith(".txt"):
        read_adjacency_list(graph, args[1])
        nodes = {node: str(node) for node in graph}
    else:
        print("Invalid input file format: must be .json or .txt")
        return

    print("Finding shortest paths...")
    get_shortest_paths(graph)
    print("Shortest paths found")

    # Main loop
    while True:
        print("======================================================")
        print('''Choose a centrality measure to sort the nodes by:
    1. Degree
    2. Betweenness
    3. Closeness
    4. Clustering Coefficient
    5. Exit''')
        choice = input(">>> ")
        if choice == "1":
            print("Degree Centrality:")
            dc = find_degree_centrality(graph)
            dc = sorted(dc.items(), key=lambda x: x[1], reverse=True)
            print_table(dc, nodes)
        elif choice == "2":
            print("Betweenness Centrality:")
            bc = find_betweenness_centrality(graph)
            bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)
            print_table(bc, nodes)
        elif choice == "3":
            print("Closeness Centrality:")
            cc = find_closeness_centrality(graph)
            cc = sorted(cc.items(), key=lambda x: x[1], reverse=True)
            print_table(cc, nodes)
        elif choice == "4":
            print("Clustering Coefficient:")
            cc = find_clustering_coefficient(graph)
            cc = sorted(cc.items(), key=lambda x: x[1], reverse=True)
            print_table(cc, nodes)
        elif choice == "5":
            break
        else:
            print("Invalid choice")


def print_table(data, node_names):
    print(f"{'Index':^10}{'Node':^10}{'Value':^10}")
    print('-' * 30)
    for (i, node) in enumerate(data):
        print(f"{i+1:^10}{node_names[node[0]]:^10}{node[1]:^10}")


if __name__ == "__main__":
    import sys
    main()
