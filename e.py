#!/usr/bin/env python
# coding: utf-8

from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import speech_recognition as sr
from selenium import webdriver
import time
import pyttsx3

# initializing the voice engine        
engine = pyttsx3.init()

# function for reading the file and doing all the preprocessing
def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []

    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop() 
    
    return sentences

#function for checking similar sentences and processing

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


#final function for generating the summary

def generate_summary(file_name, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences =  read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(top_n):
      summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    print("Summarize Text: \n", " ".join(summarize_text))
    summary=(" ".join(summarize_text))

    #speech engine for speaking out the summary
    engine.say(summary)
    engine.runAndWait()
    

# let's begin

#for opening the file and for storing the recognition text
f=open("input.txt","w")

#working with the recogniser
r=sr.Recognizer()

#initializing the speech engine
engine = pyttsx3.init()

#Recogniser
with sr.Microphone() as source:
    print('Speak Anything:')
    audio=r.listen(source)
    
    try:
        text=r.recognize_google(audio)
        print('You said:{}'.format(text))
        # writing the recognised text to the file
        f.write(text)
        f.close()

        # working for puncting the recognised text and storing in a file
        file= open('input.txt',encoding='utf8')
        text= file.read().strip()
        text=text.replace('\n','')
        chromedriver="C:\\New folder\\chromedriver.exe"
        driver=webdriver.Chrome(chromedriver)
        driver.get("http://bark.phon.ioc.ee/punctuator")
        elem = driver.find_element_by_id("input-text")
        elem.send_keys(text)
        elem=driver.find_element_by_id("punctuate-btn")
        elem.click() 
        time.sleep(5) 
        elem=driver.find_element_by_id("output-text")
        a=(elem.text)

        # finally writting the punctuated text to a file for generating the summary
        f = open('output.txt', 'w+')
        f.write(a) 
        f.close()
    except:
        print('Sorry could not recognize your voice')

#finally callling the generate summary function for summarization

# You can change the summarised line to be any value from 2-n
        
generate_summary( "output.txt",2)

