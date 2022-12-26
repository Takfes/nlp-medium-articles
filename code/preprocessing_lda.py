import pandas as pd

import re
import string
import time

import spacy
from spacy.language import Language
from spacy.lang.en.stop_words import STOP_WORDS

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import gensim
from gensim import corpora
from gensim import models
from gensim.corpora.dictionary import Dictionary
from gensim.parsing.preprocessing import STOPWORDS

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.decomposition import NMF, LatentDirichletAllocation

# Load dataset
df = pd.read_pickle('articles.pkl')

# Raw texts list
texts = df.text.tolist()

# Custom preprocessing

# Clean texts
def custom_cleaner(text):
    return re.sub(r'http\S+', '', text).replace('\n\n',' ').replace('\n','').lower().strip()

clean_texts = [custom_cleaner(x) for x in texts]

# Remove punctuation
RE_PUNCTUATION = '|'.join([re.escape(x) for x in string.punctuation])
no_punct_texts = [re.sub(RE_PUNCTUATION,'',x) for x in clean_texts]

# Apply Tokenization
tokenized_texts = [word_tokenize(x) for x in no_punct_texts]

# Remove StopWords
stopwords = set(STOPWORDS)
no_stopwords_texts = [[token for token in doc if token not in stopwords] for doc in tokenized_texts]

# Apply Lemmatizer
lemmatizer = WordNetLemmatizer()
lemmatized_texts = [[lemmatizer.lemmatize(token) for token in doc] for doc in no_stopwords_texts]

# Un-tokenize
custom_proc_texts = [' '.join(doc) for doc in lemmatized_texts] 

# Custom preprocessing function
def text_preprocessing(raw:list) -> list:
    RE_PUNCTUATION = '|'.join([re.escape(x) for x in string.punctuation])
    no_punct_texts = [re.sub(RE_PUNCTUATION,'',x) for x in clean_texts]
    # Apply Tokenization
    tokenized_texts = [word_tokenize(x) for x in no_punct_texts]
    # Remove StopWords
    stopwords = set(STOPWORDS)
    no_stopwords_texts = [[token for token in doc if token not in stopwords] for doc in tokenized_texts]
    # Apply Lemmatizer
    lemmatizer = WordNetLemmatizer()
    lemmatized_texts = [[lemmatizer.lemmatize(token) for token in doc] for doc in no_stopwords_texts]
    return lemmatized_texts

custom_processed_texts = text_preprocessing(clean_texts)

# Spacy preprocessing

nlp = spacy.load("en_core_web_lg", disable=["tok2vec", "attribute_ruler"])
# nlp.pipe_names # nlp.pipeline # nlp.components # nlp.component_names # nlp.disabled
print(nlp.pipe_names)

# Add custom component in the pipeline
# https://medium.com/neurotech-africa/understanding-spacy-process-pipelines-fe90890800e4
@Language.component("remove_stopwords")
def remove_stopwords(doc):
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc

nlp.add_pipe('remove_stopwords', last=True)
print(nlp.pipe_names)

proc_texts = nlp.pipe(clean_texts, batch_size=20)
processed_texts = list(proc_texts)

# processed_texts and custom_processed_texts are list of lists
# we might want to untokenize them if are to be used with Count-Vectorizer of TF-IDF
processed_texts_utkn = [' '.join(x) for x in processed_texts]
custom_processed_texts_utkn = [' '.join(x) for x in custom_processed_texts]

# CountVectorizer
tf = CountVectorizer(max_df=0.95, min_df=3,stop_words='english')
tf_data = tf.fit_transform(custom_processed_texts_utkn)
print(tf_data.shape)

# TF-IDF Transformer
tfidf = TfidfVectorizer()
tfidf_data = tfidf.fit_transform(custom_processed_texts_utkn)
print(tfidf_data.shape)

# Latent Dirichlet Allocation - sklearn
n_topics = 30
lda_data = tf_data # tfidf_data
transformer = tf # tfidf

lda = LatentDirichletAllocation(n_components=n_topics, max_iter=500,
                                learning_method='online',
                                random_state=1990,
                                n_jobs=-1)

start = time.time()
lda.fit(lda_data)
end = time.time()
print(f'{(end-start):.2f}')

# LDA results
def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        topic_sum = topic.sum()
        print("Topic #%d:" % topic_idx)
        print(" + ".join(["%0.3f*'%s'" % (topic[i] / topic_sum, feature_names[i])
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()

print("Topics in LDA model:")
tf_feature_names = transformer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words=8)