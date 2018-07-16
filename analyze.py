import string
import operator
import requests
from os import path
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
import random

def string_conversion(txt_file):
    """Take a text file in the same folder as frequency.py and conver it into
    a string"""
    with open(txt_file, 'r') as myfile:
        data=myfile.read().replace('\n', ' ')
    return data

def list_conversion(data_string):
    """Take in a string of all of the responses and return a list of all of the responses"""

    data_string = data_string
    c_num = ["0","1","2","3","4","5","6","7","8","9"]
    response_list = []

    response = "" #initialize current reponse string
    count = 0
    while count < len(data_string)-1:
        if data_string[count] in c_num:
            if data_string[count+1] == "/":
                response_list.append(response)
                response = ""
                temp_count = 0 #initialize a new temporary counter
                found = False #set the state of M being found to false
                while found == False: #while M is not found
                    if data_string[count+temp_count] == "M": #if the next character in the data string is M
                        temp_count += 1
                        count += temp_count#add the temporary counter to the main counter
                        found = True #set the found state to true to break the loop
                    temp_count += 1 #add one to the temporary counter
            else:
                response += data_string[count]
                count += 1
        else:
            response += data_string[count]
            count += 1
    return response_list

def convert_to_word_list(response_list):
    """Start with the list of responses where each element is a response and return a list where each element is a nested
    list containing the frequency of a word accross all responses as the first element, and the word as the second"""

    responses = " ".join(response_list)
    responses = responses.lower()
    for c in string.punctuation:
        responses = responses.replace(c,"")
    word_list = responses.split()
    freq_dict = {}
    for word in word_list:
        if word in freq_dict:
            freq_dict[word] += 1
        else:
            freq_dict[word] = 1
    freq_list = []
    for key in freq_dict:
        temp_list = []
        temp_list.append(freq_dict[key])
        temp_list.append(key)
        freq_list.append(temp_list)
    sorted_list = sorted(freq_list, key=lambda entry: entry[0],reverse = True)
    return sorted_list

def filter_list(sorted_list):
    """This takes the sorted list where each element is a nested list where the first element is the number of times a word is used and the second
    is the word itself, and returns a filtered sorted list with all the common words removed"""
    filtered_list = []

    for nested_list in sorted_list:
        if nested_list[1] not in STOPWORDS:
            filtered_list.append(nested_list)

    return filtered_list

def print_n_most_freq(sorted_list, n):
    """This takes the list of nested lists of words along with how many times the word was mentioned and prints out
    the n most frequent words, how frequent each word was, and numbers them based on how frequent each was."""
    temp_list = sorted_list[0:n]
    count = 1
    for word in temp_list:
        print(str(count)+": "+word[1]+", used "+ str(word[0]) + " times")
        count+=1

def get_wc_string(data_string):
    """Starts with a string that is the direct conversion from the text file and returns a string with no capitalization,
    puncuation, or unnecessary headers"""
    c_num = ["0","1","2","3","4","5","6","7","8","9"]
    wc_string = ""

    count = 0
    while count < len(data_string)-1:
        if data_string[count] in c_num:
            if data_string[count+1] == "/":
                temp_count = 0 #initialize a new temporary counter
                found = False #set the state of M being found to false
                while found == False: #while M is not found
                    if data_string[count+temp_count] == "M": #if the next character in the data string is M
                        temp_count += 1
                        count += temp_count#add the temporary counter to the main counter
                        found = True #set the found state to true to break the loop
                    temp_count += 1 #add one to the temporary counter
            else:
                wc_string += data_string[count]
                count += 1
        else:
            wc_string += data_string[count]
            count += 1
    wc_string = wc_string.lower()
    for c in string.punctuation:
        wc_string = wc_string.replace(c,"")
    return wc_string

def generate_wordcloud(responses):
    """Starts with a string of all the words used in the responses and plots the word clouds of that data"""
    wordcloud = WordCloud().generate(responses)
    plt.imshow(wordcloud, interpolation = 'bilinear')
    plt.axis("off")

    wordcloud = WordCloud(max_font_size = 50).generate(responses)
    plt.figure()

    plt.imshow(wordcloud,interpolation='bilinear')
    plt.axis("off")

    plt.show()

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):

    return "hsl(49, 97%, 54%)"

def generate_mask_word_cloud(responses, image):
    """This will generate a word cloud of the reponses in the shape given"""
    d = path.dirname(__file__)

    image_mask = np.array(Image.open(path.join(d,image)))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(background_color="green", max_words=2000, mask=image_mask,stopwords = stopwords,max_font_size = 160)

    wc.generate(responses)
    #wc.to_file(path.join(d,"word_heart.png"))
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
           interpolation="bilinear")
    plt.axis("off")
    plt.show()

def find_sent(sentence_list):
    """This will take a list of sentences as input. It will return the average sentiment expressed accross all of the sentences."""
    total_sentences = len(sentence_list) #the total sentences contained in this list
    total_dict = {'pos':float(0),'neg':float(0),'neu':float(0),'compound':float(0)} #creating a dictionary that will contain all of the totals
    avg_dict = {} #initalize the dictionary to conatin all of the average sentiments

    for sentence in sentence_list: #for every sentence that mentions the target word
        sentiment_dict = analyzer.polarity_scores(sentence) #analyze the sentiment expressed in this sentence
        for sentiment in sentiment_dict: #for every sentiment in the dictionary for sentiment
            total_dict[sentiment] += sentiment_dict[sentiment] #add the value for that sentiment to the total value for that sentiment

    for sentiment in total_dict: #for every sentiment total in the totals dictionary
        avg_sentiment = total_dict[sentiment] / total_sentences #calculate the average value for that sentiment
        avg_dict[sentiment] = avg_sentiment #append the average sentiment into the average dictionary under the corresponding sentiment key

    return avg_dict

def print_sent(avg_sent):
    """This will take the sentiment dictionary containing all of the averages as an input and return the percentage of positive vs negative sentiments expressed"""
    total = avg_sent['pos'] + avg_sent['neg']
    pos_ratio = avg_sent['pos'] / total
    neg_ratio = avg_sent['neg'] / total
    pos_percent = int(pos_ratio * 100)
    neg_percent = int(neg_ratio * 100)

    print("positive ratio: "+str(pos_ratio) + "\n" + "negative ratio: " + str(neg_ratio))
    print("positive percentage: "+str(pos_percent)+"%" + "\n" + "negative percentage: " + str(neg_percent)+"%")

def analyze(questions, images):
    for answers in questions:
        image = images[questions.index(answers)]
        data_string = string_conversion(answers)
        response_list = list_conversion(data_string)
        sorted_list = convert_to_word_list(response_list)
        filtered_list = filter_list(sorted_list)
        avg_sent = find_sent(response_list)
        print_sent(avg_sent)
        print_n_most_freq(filtered_list,20)
        responses = get_wc_string(data_string)
        generate_wordcloud(responses)
        
if __name__ == '__main__':
    questions = 'q3.txt','q4.txt','q6.txt'
    images = 'plus_mask.jpg','greater_mask1.jpg','division_mask.jpg'
    analyze(questions,images)
