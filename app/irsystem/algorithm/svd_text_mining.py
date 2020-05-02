from __future__ import print_function
import numpy as np
from flask import jsonify

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.manifold import TSNE

from scipy.sparse.linalg import svds

from app.database import database
from app.spotify import spotify
from collections import defaultdict
import time

db_songs = {}

def get_comments(): 
    songs = database.find_reddit_songs()
    print("got songs from db")
    reddit_obj = []
    """
    for song in songs: 
        song_id = song["id"]
        reddit_comments = ""
        for comment in song["comments"]:
            reddit_comments += comment["text"]
        reddit_obj.append({"song_id": song_id, "comment": reddit_comments})
    """
    done = 0
    idx_to_id = {}
    for song in songs: 
        song_id = song["id"]
        db_songs[song_id] = {
            "name": song["name"],
            "artists": list(map(lambda a: a["name"], song["artists"])),
            "images": song["album"]["images"],
            "id": song["id"]
        }
        reddit_comments = " ".join(list(map(lambda c: c["text"], song["comments"])))
        # for comment in songs[i]["comments"]:
        #     reddit_comments += comment["text"]
        reddit_obj.append({"song_id": song_id, "comment": reddit_comments})
        idx_to_id[done] = song_id
        done += 1
        print(done)
    return (reddit_obj, idx_to_id)


def svd():
    print("running svd")
    redditcomments, idx_to_id = get_comments()
    print("got comments")
    documents = [(x['song_id'], x['comment']) for x in redditcomments]
    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df = 1)
    my_matrix = vectorizer.fit_transform([x[1] for x in documents]).transpose()
    print(type(my_matrix))
    print(my_matrix.shape)
    u, s, v_trans = svds(my_matrix)
    print(u.shape)
    print(s.shape)
    print(v_trans.shape)
    words_compressed, _, docs_compressed = svds(my_matrix, k=40)
    docs_compressed = docs_compressed.transpose()
    print(words_compressed.shape)
    print(docs_compressed.shape)

    word_to_index = vectorizer.vocabulary_
    print ("")
    print ("")
    #print (word_to_index)
    print ("")
    print ("")


    index_to_word = {i:t for t,i in word_to_index.items()}
    print(words_compressed.shape)
    print(list(word_to_index.keys())[:200])
    # from sklearn.manifold import TSNE
    from MulticoreTSNE import MulticoreTSNE as TSNE
    print("Running TSNE")
    #tsne = TSNE()
    print(docs_compressed.shape)
    #we'll just take the first 5K documents, because TSNE is memory intensive!
    subset = docs_compressed[:5000,:]
    projected_docs = TSNE(n_jobs=8).fit_transform(subset)
    print(projected_docs.shape)

    docs_compressed = normalize(docs_compressed, axis = 1)

    def closest_projects(project_index_in, k = 5):
        sims = docs_compressed.dot(docs_compressed[project_index_in,:])
        asort = np.argsort(-sims)[:k+1]
        return [(documents[i][0],sims[i]/sims[asort[0]]) for i in asort[1:]]
    
    scores = defaultdict(int)
    for i in idx_to_id:
        similar = []
        for title, score in closest_projects(i, 30):
            similar.append({"id": title, "score": score})
        database.put_sim_songs(idx_to_id[i], similar)
        print(i)

    # for i in range(0, 1000):
    #     # song = documents[i][0]
    #     for title, score in closest_projects(i):
    #         scores[title] += score
    #         # print("{}:{:.3f}".format(title[:40], score))
    # top = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[0:10]
    # top_named = list(map(lambda k: db_songs[k], top))
    # print(top_named)
    return "done"


    """
    def weightings_list_input_songs(input_song_indexes):
        output = []
        for song_index in input_song_ids:
            closest_songs = closet_songs(song_index)
            output.append(closest_songs)
        return (output)

    def compile_weightings_in_dictionary(weightings_list):
        dic = {}
        for ranking_list in weightings_list:
            for ranking_tuple in ranking_list:
                songid = ranking_tuple[0]
                if songid not in dic:
                    dic(songid) = ranking_tuple[1]
                else:
                    dic(songid) += ranking_tuple[1]
    """

    return documents


    
# #To prove I'm not cheating with the magic trick...
# np.random.shuffle(documents)

# import matplotlib
# import numpy as np
# import matplotlib.pyplot as plt
# plt.plot(s[::-1])
# plt.xlabel("Singular value number")
# plt.ylabel("Singular value")
# plt.show()



