from os import listdir, path
from csv import reader
from string import punctuation
from collections import defaultdict
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import sys

class data():
    def __init__(self):
        self.interview_directory = sys.argv[1]
        print(self.interview_directory)
        self.interview_csvs = list(filter(lambda x: x[-3:] == "csv",listdir("./"+self.interview_directory))) #filter out csv files
        # ^this is a list of all csv files in the same dir as script
        self.num_questions = None
        self.get_num_questions()
        self.notes_list = []
        self.word_frequency_lists = []
        self.filtered_lists = [] #The extended name is filtered_word_frequency_lists
        self.questions_asked = []
        self.stopwords = None
        self.set_stopwords()
        self.extract_all_notes()
        self.extract_questions()
        self.standardize_notes()
        self.sort_words()
        self.filter_words()

    def set_stopwords(self):
        self.stopwords = set(STOPWORDS)
        self.stopwords.add("thing")
        self.stopwords.add("things")
        self.stopwords.add("stuff")
        self.stopwords.add('nono')
        self.stopwords.remove('no')

    def get_num_questions(self):
        """
        This function goes through the csv file and counts how many questions were asked.
        This number is saved as an int in num_questions
        """

        csv_file = self.read_csv(self.interview_csvs[0])
        num_questions = -1 #initialize num_questions at -1 to compensate for header row
        for row in csv_file:
            if row[1] != '':
                num_questions +=1
        self.num_questions = num_questions


    def extract_questions(self):
        """
        This function stores the questions asked in a list called questions_asked
        """
        csv_file = self.read_csv(self.interview_csvs[0])
        for i in range(self.num_questions):
            self.questions_asked.append(csv_file[1+i][1])

    def extract_notes(self,question_num):
        """
        This function stores the notes taken on a given question in notes_list
        question_num (int): indexing starts at 1, this is the question you want notes on

        Returns: None
        """
        all_notes = []

        for csv_file in self.interview_csvs:
            csv_aslist = self.read_csv(csv_file)
            notes = csv_aslist[question_num][2] + csv_aslist[question_num][3]
            all_notes.append(notes)

        self.notes_list.append(all_notes)

    def read_csv(self,file):
        """
        This function opens a csv file and reads its rows into a list of lists,
        each inner list containing all the info for one row
        """
        open_file = open("./"+self.interview_directory+"/"+file, newline='')
        file_reader = reader(open_file)
        file_data = []
        for row in file_reader:
            file_data.append(row)
        return file_data

    def extract_all_notes(self):
        """
        This function iterates through the number of questions asked of interviewees
        and stores the notes taken in notes_list
        num_questions (int): number of quesitons to iterate through
        """
        for counter in range(self.num_questions):
            self.extract_notes(counter+1)

    def standardize_notes(self):
        """
        This function standardizes our notes in notes_list so that we can turn them into word clouds
        """
        for note_list in self.notes_list:
            for note in note_list:
                note.lower()
                for c in punctuation:
                    note = note.replace(c,"")

    def sort_words(self):
        """
        This function finds the most frequent words used in the notes for all the questions
        n (int): number of most frequent words to find
        """
        for note_list in self.notes_list:
            all_notes = " ".join(note_list)
            word_list = all_notes.split()
            freq_dict = defaultdict(int)
            for word in word_list:
                freq_dict[word] += 1
            freq_list = freq_dict.items()
            sorted_list = sorted(freq_list, key=lambda entry: entry[1],reverse = True)
            self.word_frequency_lists.append(sorted_list)

    def filter_words(self):
        """
        This function iterates through the list in word_frequency_lists
        and removes any useless words, i.e. a, and, the, etc.
        """
        for frequency_list in self.word_frequency_lists:
            filtered_freq_list = []
            for frequency_tuple in frequency_list:
                if frequency_tuple[0] not in self.stopwords:
                    filtered_freq_list.append(frequency_tuple)
            self.filtered_lists.append(filtered_freq_list)

    def generate_wordcloud(self):

        """
        This function takes the words and their frequencies and generates a word
        cloud from them
        """

        image_array = np.array(Image.open('olin.jpg'))
        image_colors = ImageColorGenerator(image_array)
        for count,note_list in enumerate(self.notes_list):
            all_notes = " ".join(note_list)
            wordcloud = WordCloud(stopwords=self.stopwords, mask=image_array, background_color="white", color_func=colour_function).generate(all_notes)
            plt.title(self.questions_asked[count])
            plt.imshow(wordcloud.recolor(color_func=image_colors))
            plt.axis('off')
            plt.show()

def colour_function(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(198, 100%, 44%)"

if __name__ == '__main__':
    interview_data = data()
    interview_data.generate_wordcloud()
    # interview_data.generate_wordcloud()

    # print(interview_data.filtered_lists[0])
