import mysql.connector
import json
import os
import networkx as nx


connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="set_local",
)
cursor = connection.cursor()

# query = """SELECT DISTINCT author as count FROM (
# 	SELECT author FROM sbf_comment
# 	UNION
# 	SELECT author FROM sbf_suggestion
# ) AS all_users;"""
# cursor.execute(query)

# users = list(map(lambda x: str(x[0]).strip(), cursor.fetchall()))
# unique = set()

# for user in users:
#     if user not in unique:
#         unique.add(user)
#     else:
#         print(f"Duplicate: {user}")

# print(len(unique))

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

cursor.close()


# Convert {user: [commentsId]} to {commentId: user}
comments_user_reverse = {}
for user, comments in user_comments.items():
    for comment in comments:
        comments_user_reverse[comment] = user

suggestions_user_reverse = {}
for user, suggestions in user_suggestions.items():
    for suggestion in suggestions:
        suggestions_user_reverse[suggestion] = user


G = nx.DiGraph()

count = 0
for suggestion, comments in suggestion_comments.items():
    # count += 1
    # Create node in graph
    suggestion_author = suggestions_user_reverse[suggestion]
    # if not G.has_node(suggestion_author):
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

    # if count == 4:
    #     break

nx.write_gexf(G, "suggestions_comments.gexf")
