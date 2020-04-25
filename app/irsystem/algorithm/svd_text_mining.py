
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