from itertools import combinations


def find_degree_centrality(graph):
    degree_centrality = {}
    for node in graph:
        degree_centrality[node] = len(graph[node])
    return degree_centrality


def find_betweenness_centrality(graph):
    nodes = {}
    for node in graph:
        nodes[node] = betweenness_centrality(graph, node)

    return nodes


def betweenness_centrality(graph, node):
    ''' 
    For a given node n, its betweeness centrality is calculated as follows:
      # of shortest paths that pass through n / total # of shortest paths
    '''
    res = 0
    c = list(combinations(graph.keys(), 2))
    for (start, end) in c:
        if start == node or end == node:
            continue
        paths = shortest_paths(graph, start, end)
        res += (len([path for path in paths if node in path]) / len(paths))
    return res


def shortest_paths(graph, start, end):
    ''' Find all shortest paths between start and end nodes '''
    paths = []

    def dfs(node, visited):
        if node in visited:
            return
        if node == end:
            paths.append(visited + [node])
            return

        visited.append(node)
        for neighbor in graph[node]:
            dfs(neighbor, visited.copy())
        visited.remove(node)

    dfs(start, [])

    min_path_length = min([len(path) for path in paths])
    paths = [path for path in paths if len(path) == min_path_length]

    return paths


def find_closeness_centrality(graph):
    '''
    To find the closeness centrality of a node, we need to calculate the mean length of all shortest paths from the node to all other nodes.
    '''
    cc = {}
    for node in graph:
        cc[node] = closeness_centrality(graph, node)
    return cc


def closeness_centrality(graph, node):
    res = 0
    for end in graph.keys():
        if node == end:
            continue
        paths = shortest_paths(graph, node, end)
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


def main():
    # Read the file
    graph = {}

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
    main()
