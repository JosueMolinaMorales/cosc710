import mysql.connector
import json
import os
import networkx as nx
import random


def main():
    # Connect to database
    print("connecting to database...", end="")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="set_local",
    )
    cursor = connection.cursor()
    print("done")

    # Get suggestions and comments
    print("getting suggestions...", end="")
    user_suggestions = {}
    query_suggestions = """SELECT author, suggestionId from sbf_suggestion order by author;"""
    cursor.execute(query_suggestions)

    suggestions = cursor.fetchall()
    suggestion_comments = {}
    for suggestion in suggestions:
        user, suggestion_id = suggestion
        user = user.strip()
        suggestion_id = str(suggestion_id).strip()
        if user not in user_suggestions:
            user_suggestions[user] = []
        user_suggestions[user].append(suggestion_id)

        suggestion_comments[suggestion_id] = []
    print("done.")

    print("getting comments...", end="")
    query_comments = """SELECT author, commentId, suggestionId from sbf_comment order by author;"""
    cursor.execute(query_comments)

    user_comments = {}
    comments = cursor.fetchall()

    for comment in comments:
        user, comment_id, suggestion_id = comment
        user = user.strip()
        comment_id = str(comment_id).strip()
        suggestion_id = str(suggestion_id).strip()
        if user not in user_comments:
            user_comments[user] = []
        user_comments[user].append(comment_id)

        suggestion_comments[suggestion_id].append(comment_id)
    print("done.")
    cursor.close()

    print("mapping user comments...", end="")
    # Convert {user: [commentsId]} to {commentId: user}
    comments_user_reverse = {}
    for user, comments in user_comments.items():
        for comment in comments:
            comments_user_reverse[comment] = user
    print("done.")
    print("mapping user suggestions...", end="")
    suggestions_user_reverse = {}
    for user, suggestions in user_suggestions.items():
        for suggestion in suggestions:
            suggestions_user_reverse[suggestion] = user
    print("done.")

    print("creating graph...", end="")
    G = nx.DiGraph()

    keys = list(suggestion_comments.keys())
    keys.sort(key=lambda x: len(suggestion_comments[x]), reverse=True)
    print(keys[0], len(suggestion_comments[keys[0]]))
    count = 0
    for suggestion in keys:
        comments = suggestion_comments[suggestion]
        count += 1
        # Create node in graph
        suggestion_author = suggestions_user_reverse[suggestion]
        # if not G.has_node(suggestion_author):
        # Suggestion has no commnets, would be a node with no degree
        if len(comments) == 0:
            continue
        G.add_node(suggestion_author)
        for comment in comments:
            # Check to see if edge already exists between u and v, if so
            # increment the weight by one
            # if not, add the edge
            comment_author = comments_user_reverse[comment]
            # if not G.has_node(comment_author):
            G.add_node(comment_author)
            if G.has_edge(suggestion_author, comment_author):
                G[suggestion_author][comment_author]["weight"] += 1
            else:
                G.add_edge(suggestion_author, comment_author, weight=1)

        if count == 100:
            break

    nx.write_gexf(G, "suggestions_comments.gexf")
    print("done.")

    # Print report of graph
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)

    print(f"Num of edges {num_edges}")
    print(f"Num of nodes: {num_nodes}")

    print("finding betweenness_centrality of graph G...", end="")
    res = nx.betweenness_centrality(G)
    print("done.")
    print(res)


if __name__ == "__main__":
    main()
