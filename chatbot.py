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
import random

import numpy as np

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer

QUOTATION_REGEX = r'\"(.*?)\"'
MIN_NUM_MOVIES_NEEDED = 5
# Binarize Constants
UPPER_THRESHOLD = 3.1
LOWER_THRESHOLD = 2.9

'''
TODO: Feb 22, 2018
Sentiment:
1) count pos and neg words
2) if prev_word in [not, neither, nor, n't, ...]
   then negate curr_word
4) only count words after 'but', 'although', 'however', ...
'''

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.porter = PorterStemmer()
      self.movie_titles = []
      self.name = 'Movie Bot'
      self.is_turbo = is_turbo
      self.read_data()
      self.binarize()
      self.negation_lexicon = set(self.readFile('deps/negation.txt'))
      self.movies_count = 0
      self.movie_inputs = {}

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = 'The name\'s Bot. Movie Bot. I\'m here to give you recommendations on what movies to watch. So go ahead, tell me about a movie that you\'ve seen.'

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
    def readFile(self, fileName):
      """
       * Code for reading a file.  you probably don't want to modify anything here,
       * unless you don't like the way we segment files.
      """
      contents = []
      f = open(fileName)
      for line in f:
        contents.append(line.decode('utf-8'))
      f.close()
      result = self.segmentWords('\n'.join(contents))
      return result

    def segmentWords(self, s):
      """
       * Splits lines on whitespace for file reading
      """
      return s.split()

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
        # Find movie(s) mentioned by user
        movies_mentioned = re.findall(QUOTATION_REGEX, input)

        if len(movies_mentioned) == 0:
            if self.movies_count < MIN_NUM_MOVIES_NEEDED:
              possible_responses = [
                'I need to know a bit more about your movie preferences before I can provide you with a recommendation. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.',
                'Sorry. Didn\'t quite get that. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.'
              ]
              response = possible_responses[random.randint(0, len(possible_responses) - 1)]
            else:
              response = 'Ok. That\'s enough for me to make a recommendation.' 
              print self.movie_inputs

              preference_vec = []
              for title in self.movie_titles:
                if title in self.movie_inputs:
                  preference_vec.append(self.movie_inputs[title])
                else:
                  preference_vec.append(0)
              print preference_vec
              recommended_movie = self.recommend(preference_vec)
              response = ("I suggest you watch \"%s.\"") % (recommended_movie)

        # More than 1 movied mentioned in the same input
        elif len(movies_mentioned) > 1:
          response = 'Please tell me about one movie at a time. Go ahead.'

        else:
          # Search for movie title in quotes
          match = re.search(QUOTATION_REGEX, input)
          quote_start = match.start(0)
          quote_end = match.end(0)

          input_movie_removed = input[:quote_start] + input[quote_end:]
          movie_title = input[quote_start + 1 : quote_end - 1]
          
          # Check to see if movie title is known
          if movie_title in self.movie_titles:
            tokens = input_movie_removed.split(' ') #remove movie title before tokenizing
            self.movies_count += 1
            sentiment = 'liked'
            sentiment_counter = 0
            prev_word = ''
            curr_word = ''
            negation_flag = False

            for t in tokens:
              prev_word = curr_word
              curr_word = t
              if prev_word in self.negation_lexicon:
                negation_flag = True

              t_stem = self.porter.stem(t)
              if t in self.sentiment:
                if self.sentiment[t] == 'pos':
                  if negation_flag:
                    sentiment_counter -= 1
                  else:
                    sentiment_counter += 1
                else:
                  if negation_flag:
                    sentiment_counter += 1
                  else:
                    sentiment_counter -= 1

              elif t_stem in self.sentiment_stemmed:
                if self.sentiment_stemmed[t_stem] == 'pos':
                  if negation_flag:
                    sentiment_counter -= 1
                  else:
                    sentiment_counter += 1
                else:
                  if negation_flag:
                    sentiment_counter += 1
                  else:
                    sentiment_counter -= 1
            # print(sentiment_counter)

            if sentiment_counter >= 0:
              sentiment = 'liked'
            else:
              sentiment = 'didn\'t like'

            response = 'So you ' + sentiment + ' \"' + movie_title + '\". Got it. How about another movie?'
            
            if sentiment_counter == 0: 
              self.movie_inputs[movie_title] = 1
            else:
              self.movie_inputs[movie_title] = (sentiment_counter / abs(sentiment_counter))

          else:
            response = 'Sorry, I don\'t recognize that movie. How about we try another movie?'

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
      self.movie_titles = [xx for [xx , genre] in self.titles]

      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)

      self.sentiment_stemmed = dict()
      subdirs = os.listdir('deps')
      if 'sentiment_stemmed.txt' in subdirs:
        print('Sentiment lexicon already stemmed...')
        self.sentiment_stemmed = dict(csv.reader(open('./deps/sentiment_stemmed.txt', 'rb')))
      else:
        print('Stemming sentiment lexicon.')
        of = open('deps/sentiment_stemmed.txt', 'w')
        for k,v in self.sentiment.iteritems():
          k_stem = self.porter.stem(k)
          self.sentiment_stemmed[k_stem] = v
          line = '%s,%s' % (k_stem, v)
          of.write(line)
          of.write('\n')
        of.close()


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      num_rows = len(self.ratings)
      num_cols = len(self.ratings[0])

      self.bin_ratings = np.zeros((num_rows, num_cols))
      for row in xrange(num_rows):
        for col in xrange(num_cols):
          raw_rating = self.ratings[row][col]
          rating = 0
          if raw_rating >= UPPER_THRESHOLD:
            rating = 1
          elif raw_rating <= LOWER_THRESHOLD and raw_rating > 0: 
            rating = -1
          else:
             rating = 0
          self.bin_ratings[row][col] = rating


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure
      # Cosine similarity 
      mag_u = np.linalg.norm(u)
      mag_v = np.linalg.norm(v)
      dot_prod = np.dot(u,v)
      cos = float(dot_prod) /(mag_u * mag_v)
      return cos


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      recommendations = []
      max_rate = 0
      suggestion = ''
      for i, movie_vec in enumerate(self.bin_ratings):
        predicted_rating = 0

        for title, rating in self.movie_inputs.iteritems():
          index = self.movie_titles.index(title)
          rating_vec = self.bin_ratings[index]

          if i == index:
            print title

          similarity = self.distance(rating_vec, movie_vec)
          if similarity >= 0:
            predicted_rating += (rating * similarity)
          
          recommendations.append(predicted_rating)

        if predicted_rating > max_rate:        
          max_rate = predicted_rating
          suggestion = self.movie_titles[i]
      
      return suggestion
      


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
