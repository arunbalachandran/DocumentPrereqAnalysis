from stemming.porter2 import stem
from stop_words import get_stop_words

match_strength = .8

phrase_length = 10

stopwords = get_stop_words('en')

def process_text(text):
    words = text.split()
    words_processed_1 = [ (stem(w.lower()), i) for i,w in enumerate(words) if w.lower() not in stopwords]
    max_wp = len(words_processed_1)
    words_processed_2 = [words_processed_1[k:k+phrase_length] for k in range(max_wp-phrase_length)]
    words_processed = [(set([q[0]for q in p]) ,p[0][1], p[-1][1]) for p in words_processed_2]
    return (words_processed, words)

def process_query(query):
    querywordset = set([stem(i.lower()) for i in query.split() if i.lower() not in stopwords])
    return querywordset

def search(text, query):
    words_processed, words = process_text(text)
    querywordset = process_query(query)
    #print('query', querywordset)
    matches = False
    match_factor = int(round(len(querywordset)*match_strength))
    for wordset, i, j in words_processed:
        #print(wordset,i,j)
        if len(wordset & querywordset) >= match_factor:
            matches = True
            # print(" ".join(words[i:j+1]))
    return matches

# search("temp_file.txt", "High Resolution Classifier")
