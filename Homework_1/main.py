from itertools import combinations
import json

PATHS = []


def get_shortest_paths(graph):
    global PATHS
    comb = list(combinations(graph.keys(), 2))
    print("Combinations found. length:", len(comb))
    for (start, end) in comb:
        print("Finding shortest paths between", start, "and", end)
        PATHS.append(shortest_paths(graph, start, end))
    print("Shortest paths found. length:", len(PATHS))


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
        print("Finding shortest paths")
        get_shortest_paths(graph)

    for node in graph:
        print("Finding betweenness centrality for node", node)
        nodes[node] = betweenness_centrality(PATHS, node)

    return nodes


def betweenness_centrality(all_paths, node):
    ''' 
    For a given node n, its betweeness centrality is calculated as follows:
      # of shortest paths that pass through n / total # of shortest paths
    '''
    print(f"======{node}======")
    res = 0
    for paths in all_paths:
        paths = [path for path in paths if node !=
                 path[0] and node != path[-1]]
        if len(paths) == 0:
            continue
        res += (len([p for p in paths if node in p]) / len(paths))
    # print("Paths that pass through", node, ":", len(paths))
    return res


def shortest_paths(graph, start, end):
    ''' Find all shortest paths between start and end nodes '''
    paths = []

    def dfs(node, visited: set, path: list = []):
        if node in visited:
            return
        if node == end:
            paths.append(path+[node])
            return

        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor, visited, path+[node])
        visited.remove(node)

    dfs(start, set())
    # print(f"paths from {start} to {end}: {paths}")
    # print(f"paths found: {len(paths)}")
    min_path_length = min([len(path) for path in paths])
    # print(f"min path length: {min_path_length}")
    paths = [path for path in paths if len(path) == min_path_length]
    # print(f"min path length paths: {len(paths)}")
    return paths


def find_closeness_centrality(graph):
    '''
    To find the closeness centrality of a node, we need to calculate the mean length of all shortest paths from the node to all other nodes.
    '''
    if len(PATHS) == 0:
        print("Finding shortest paths")
        get_shortest_paths(graph)
        print(PATHS)
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
        print(paths)
        res += sum([len(path)-1 for path in paths])
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


def read_json(graph: dict):
    with open("input.json", "r", encoding="utf-8") as file:
        obj = json.load(file)
        for edge in obj["edges"]:
            from_node = edge["source"]
            to_node = edge["target"]
            if from_node not in graph:
                graph[from_node] = set()
            if to_node not in graph:
                graph[to_node] = set()
            graph[from_node].add(to_node)
            graph[to_node].add(from_node)


def read_adjacency_list(graph: dict):
    with open("input2.txt", "r", encoding="utf-8") as file:
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

    args = sys.argv
    print(args)
    if len(args) > 1 and args[1] == "--json":
        read_json(graph)
    else:
        read_adjacency_list(graph)

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
            nodes = find_degree_centrality(graph)
            nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
            print_table(nodes)
        elif choice == "2":
            print("Betweenness Centrality:")
            nodes = find_betweenness_centrality(graph)
            nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
            print_table(nodes)
        elif choice == "3":
            print("Closeness Centrality:")
            nodes = find_closeness_centrality(graph)
            nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
            print_table(nodes)
        elif choice == "4":
            print("Clustering Coefficient:")
            nodes = find_clustering_coefficient(graph)
            nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
            print_table(nodes)
        elif choice == "5":
            break
        else:
            print("Invalid choice")


def print_table(data):
    print(f"{'Index':^10}{'Node':^10}{'Value':^10}")
    print('-' * 30)
    for (i, node) in enumerate(data):
        print(f"{i+1:^10}{node[0]:^10}{node[1]:^10}")


if __name__ == "__main__":
    import sys
    main()
