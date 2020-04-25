
from __future__ import print_function
import numpy as np
import json
with open("kickstarter.jsonlist") as f:
    documents = [(x['name'], x['category'], x['text'])
                 for x in json.loads(f.readlines()[0])
                 if len(x['text'].split()) > 50]
    
#To prove I'm not cheating with the magic trick...
np.random.shuffle(documents)

vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7,
                            min_df = 75)
my_matrix = vectorizer.fit_transform([x[2] for x in documents]).transpose()
vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7,
                            min_df = 75)
my_matrix = vectorizer.fit_transform([x[2] for x in documents]).transpose()
print(type(my_matrix))
print(my_matrix.shape)
from scipy.sparse.linalg import svds
u, s, v_trans = svds(my_matrix, k=100)
print(u.shape)
print(s.shape)
print(v_trans.shape)


import matplotlib
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline
plt.plot(s[::-1])
plt.xlabel("Singular value number")
plt.ylabel("Singular value")
plt.show()

words_compressed, _, docs_compressed = svds(my_matrix, k=40)
docs_compressed = docs_compressed.transpose()

print(words_compressed.shape)
print(docs_compressed.shape)

word_to_index = vectorizer.vocabulary_
index_to_word = {i:t for t,i in word_to_index.iteritems()}
print(words_compressed.shape)

from sklearn.preprocessing import normalize
words_compressed = normalize(words_compressed, axis = 1)

def closest_words(word_in, k = 10):
    if word_in not in word_to_index: return "Not in vocab."
    sims = words_compressed.dot(words_compressed[word_to_index[word_in],:])
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

closest_words("nuclear")
print(word_to_index.keys()[:200])
from sklearn.manifold import TSNE
tsne = TSNE(verbose=1)
print(docs_compressed.shape)
#we'll just take the first 5K documents, because TSNE is memory intensive!
subset = docs_compressed[:5000,:]
projected_docs = tsne.fit_transform(subset)
print(projected_docs.shape)

docs_compressed = normalize(docs_compressed, axis = 1)
def closest_projects(project_index_in, k = 5):
    sims = docs_compressed.dot(docs_compressed[project_index_in,:])
    asort = np.argsort(-sims)[:k+1]
    return [(documents[i][0],sims[i]/sims[asort[0]]) for i in asort[1:]]

for i in range(10):
    print(documents[i][0])
    for title, score in closest_projects(i):
        print("{}:{:.3f}".format(title[:40], score))
    print()