#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re
import os

import numpy as np

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer

QUOTATION_REGEX = r'\"(.*?)\"'

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.porter = PorterStemmer()
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.read_data()
      self.movies_count = 0
      self.movie_titles = []

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = 'How can I help you?'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Have a nice day!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      if self.is_turbo == True:
        response = 'processed %s in creative mode!!' % input
      else:
        movie_titles = re.findall(QUOTATION_REGEX, input)
        
        if len(movie_titles) == 0:
          response = 'Sorry. Didn\'t quite get that. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.'
        elif len(movie_titles) > 1:
          response = 'Please tell me about one movie at a time. Go ahead.'
        else:
          match = re.search(QUOTATION_REGEX, input)
          quote_start = match.start(0)
          quote_end = match.end(0)

          input_movie_removed = input[:quote_start] + input[quote_end:]
          movie_title = input[quote_start + 1 : quote_end - 1]

          self.movies_count += 1
          sentiment = 'liked'
          tokens = input_movie_removed.split(' ') #remove movie title before tokenizing
          pos_count = 0.0
          neg_count = 0.0

          for t in tokens:
            print('stem: ' + self.porter.stem(t))
            if t in self.sentiment:
              if self.sentiment[t] == 'pos':
                pos_count += 1.0
              else:
                neg_count += 1.0
            elif self.porter.stem(t) in self.sentiment_stemmed:
              if self.sentiment_stemmed[self.porter.stem(t)] == 'pos':
                pos_count += 1.0
              else:
                neg_count += 1.0

          if pos_count >= neg_count:
            sentiment = 'liked'
            
          else:
            sentiment = 'didn\'t like'
          response = 'So you ' + sentiment + ' \"' + movie_title + '\". Got it. How about another movie?'




        # quote_index = max(input.find('\''), input.find('\"'))
        # if quote_index >= 0:
        #   end_index = max(input.find('\'', quote_index+1), input.find('\"', quote_index+1))
        #   if end_index >= 0:
        #     movie_title = input[quote_index+1 : end_index]
        #     self.movies_count += 1
            
        #     sentiment = 'liked'
        #     tokens = (input[:quote_index] + input[end_index+1:]).split(' ') #remove movie title before tokenizing
        #     pos_count = 0.0
        #     neg_count = 0.0

        #     for t in tokens:
        #       print('stem: ' + self.porter.stem(t))
        #       if t in self.sentiment:
        #         if self.sentiment[t] == 'pos':
        #           pos_count += 1.0
        #         else:
        #           neg_count += 1.0

        #     if pos_count >= neg_count:
        #       sentiment = 'liked'
        #     else:
        #       sentiment = 'didn\'t like'
        #     response = 'So you ' + sentiment + ' \"' + movie_title + '\". Got it. How about another movie?'
          
        #   else:
        #     response = 'You probably forgot to close your quotation marks. Can you say the movie again?'
        
        # else:
        #   if self.movies_count < 5:
        #     response = 'I need to know a bit more about your movie preferences before I can provide you with a recommendation. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.'
        #     # response = 'Sorry. Didn\'t quite get that. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.'
        #   else:
        #     response = 'Ok. That\'s enough for me to make a recommendation.'
        
        # response = 'processed %s in starter mode' % input

      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      self.movie_titles = set(xx for [xx , genre] in self.titles)
      print(self.movie_titles)
      
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)
      self.sentiment_stemmed = dict()

      subdirs = os.listdir('./deps')
      if 'sentiment_stemmed.txt' in subdirs:
        print('Already stemmed...')
        self.sentiment_stemmed = dict(csv.reader(open('./deps/sentiment_stemmed.txt', 'rb')))
      else:
        print('Stemming sentiment lexicon.')
        of = open('./deps/sentiment_stemmed.txt', 'w')
        for k,v in self.sentiment.iteritems():
          k_stem = self.porter.stem(k)
          self.sentiment_stemmed[k_stem] = v
          line = '%s,%s' % (k_stem, v)
          of.write(line)
          of.write('\n')
        of.close()    


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""

      pass


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      pass


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      pass


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
