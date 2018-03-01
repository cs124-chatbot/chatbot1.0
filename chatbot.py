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
from operator import itemgetter

import numpy as np

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer


#############################################################################
# Constants
#############################################################################

QUOTATION_REGEX = r'\"(.*?)\"'
ACTUAL_YEAR_REGEX = r'\([1-2][0-9]{3}\)'
YEAR_REGEX = r'\((.*?)\)'

MIN_NUM_MOVIES_NEEDED = 5
# Binarize Constants
UPPER_THRESHOLD = 3.1
LOWER_THRESHOLD = 2.9

#############################################################################
# THE CLASS
#############################################################################

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.porter = PorterStemmer()
      self.movie_titles = []
      self.no_year_titles = []
      self.name = 'Movie Bot'
      self.is_turbo = is_turbo
      self.read_data()
      self.binarize()
      self.negation_lexicon = set(self.readFile('deps/negation.txt'))
      self.movie_inputs = {}
      self.recommend_flag = 0
      self.recommended_movies = []
      self.mag_u_count = 0
      self.mag_v_count = 0
      self.bad_input_count = 0
      self.genres_input = {}
      self.carryover = ()

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = 'The name\'s Bot. James--, I mean, Movie Bot. I\'m here to give you recommendations on what movies to watch. So go ahead, tell me about a movie that you\'ve seen.'

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

    def removeYear(self, title):
      title_wo_year = re.sub(ACTUAL_YEAR_REGEX, '', title)
      return title_wo_year.strip()

    #def readVagueInput(self, s):

<<<<<<< HEAD
    # def noYearProcess(self, movie_title):
    #   print movie_title
      
    #   pass  
=======
    def noYearProcess(self, movie_title):
      print movie_title

      pass
>>>>>>> 7b0eb7716af8ed3d755c195e76b0718d4579c2a0

    def segmentWords(self, s):
      """
       * Splits lines on whitespace for file reading
      """
      return s.split()

    def getMovieYear(self, title):
      paren_matches = re.findall(YEAR_REGEX, title)
      year = ''
      if len(paren_matches) >= 1:
        year = paren_matches[len(paren_matches) - 1]
      return year

    def getGenresList(self, title):
      movie_index = self.movie_titles.index(title)
      movie_obj = self.titles[movie_index]
      genre_obj = movie_obj[1]
      genresList = genre_obj.split('|')
      return genresList

    def reverse_convert_article(self, raw_title):
      readable_title = raw_title
      if raw_title == "Valachi Papers,The (1972)":
        return "The Valachi Papers (1972)"
      indexParen = raw_title.find('(')
      if indexParen != -1:
        commaChunk = (raw_title[:indexParen])[-6:]
        indexComma = commaChunk.find(',')
        if indexComma != -1:
          article = commaChunk[indexComma + 1:].strip()
          if article == 'The' or article == 'A' or article == 'An':
            readable_title = article + " " + raw_title[: indexParen - (6 - indexComma)] + ' ' + raw_title[indexParen:]
      return readable_title


    def convert_article(self, s):
      #find ( using rfind if not append to the end if s[0:2] is the if cant find, add
      if len(s) >= 3:
        article = s[0:3].lower()
        if article == 'the':
            article = 'The'
            s = s[3:]
        elif article[0:2] == 'a ':
            article = 'A'
            s = s[2:]
        elif article == 'an ':
            article ='An'
            s = s[2:]
        if article == 'The' or article == 'A' or article == 'An':
          indexParen = s.find('(')
          if indexParen != -1:
            s = s[0: indexParen - 1] + ', ' + article + ' ' + s[indexParen:]
          else:
            s += ', ' + article + ' '
      return s.strip()

    def convert_foreignArticle(self, s):
      if len(s) >= 3:
        foreignList = set(['i', 'de', ' das', ' les', 'las', "l'", 'un', 'det', 'der', 'die', 'den', 'une', 'el', 'en', 'il', 'le', 'la', 'lo', 'los', 'un'])
        for article in foreignList:
          if article in s.lower() and s.lower().find(article) == 0:
            s = s[len(article):]
            s += ', ' + article.capitalize() + ' '
            break
      return s.strip()

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
        print "TURBO MODE ACTIVATED"
        # Old response = 'processed %s in creative mode!!' % input
        # Find movie(s) mentioned by user
        movies_mentioned = re.findall(QUOTATION_REGEX, input)
        if self.carryover:
          curr_title = self.carryover[0][0][0]
          if ':next' in input:
            self.carryover = ()
            return "Okay! We can forget about " + curr_title + "! What other movies have you seen?"
   
          matched_movie = ''
          year_matches = re.findall('[1-2][0-9]{3}', input)
          if len(year_matches) >= 1:
            year = year_matches[len(year_matches) - 1]
            for title, date in self.carryover[0]:
              if year == date:
                matched_movie = "%s (%s)" % (title, date)           
            if matched_movie == '':
              return "Ah geez, this is embarassing. I don't think there was a movie called " + curr_title + " released in " + year + ". Maybe you're mistaken . . .could you try again? If it\'s easier you could also just tell me what number it was chronologically! Also, if you're tired of talking about " + curr_title + ", just tell me :next to move on."
          
          elif len(input.strip()) == 1 and input != '0':
            num_match = re.findall('[0-9]', input) 
            if len(num_match) >= 1:
              num = int(num_match[0])
              if len(self.carryover[0]) >= num:
                title = self.carryover[0][num-1][0]
                date = self.carryover[0][num-1][1]
                matched_movie = "%s (%s)" % (title, date)
              else: 
                return "Hmmm . . . there aren'y that many movies called " + curr_title + ". There were only " + str(len(self.carryover[0])) + ". Would you mind telling me which one it was again? If it's easier you can also let me know what year it the movie was released! Otherwise, if you want to forget about it just tell me :next to move on."
          
          else:
            return "Sorry, I was not emotionally prepared for that response! Could you try telling me the year the movie you're talking about was released or what number it was chronolgically? Alternatively, tell me :next , and we can move on from " + curr_title + "."
          
          if self.carryover[1] >= 0:
            sentiment = 'liked'
          else:
            sentiment = 'didn\'t like'

          response = 'Oh I see! You ' + sentiment + ' \"' + matched_movie + '\". Thanks for bearing with me. Let\'s continue! Tell me about more movies you\'ve seen.'
          self.carryover = ()
          movie_title = matched_movie

        elif self.recommend_flag > 0 and self.recommend_flag <= 9 and input != ':no':
          response = ("I suggest you watch \"%s.\"\nWould you like another recommendation? (If not, enter :no. Enter :quit to exit)") % (self.reverse_convert_article(self.recommended_movies[(9 - self.recommend_flag)][0]))
          self.recommend_flag += 1
        elif self.recommend_flag == 10:
          response = "I gave you 10 recommendations already! Did you watch all of them already? I can make more recommendations, but you'll have to update me on your preferences."
          self.movie_inputs = {}
          self.recommended_movies = []
          self.recommend_flag = 0
        elif len(movies_mentioned) == 0:
          if self.bad_input_count == 2:
            response = "Listen. I know you're probably trying to break me. But I'm unbreakable!\nBy the way, \"Unbreakable (2000)\" is a good choice if you're into Drama or Sci-Fi. Tell me about another movie."
            self.bad_input_count += 1
          elif self.bad_input_count > 2:
            response = "Be nice and tell me about a movie that you've watched. I've got places to go! \nSpeaking of which... \"Going Places (Valseuses, Les) (1974)\" is not bad."
            self.bad_input_count += 1
          elif input == ':no':
            self.movie_inputs = {}
            self.recommended_movies = []
            self.recommend_flag = 0
            possible_responses = [
              'OK. Tell me more about movies that you\'ve watched. (enter :quit to exit)',
              'Sure. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes. (enter :quit to exit)',
              'So, tell me about another movie. (enter :quit to exit)'
            ]
            response = possible_responses[random.randint(0, len(possible_responses) - 1)]
            self.bad_input_count += 1
          elif len(self.movie_inputs) < MIN_NUM_MOVIES_NEEDED:
            possible_responses = [
              'I need to know a bit more about your movie preferences before I can provide you with a recommendation. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.',
              'Sorry. Didn\'t quite get that. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.',
              'I know I\'m supposed to be a smart bot... but in order for me to make good recommendations, I need you to tell me a few more movies that you\'ve seen. Thanks!'
            ]
            response = possible_responses[random.randint(0, len(possible_responses) - 1)]
            self.bad_input_count += 1
          else:
            self.bad_input_count = 0
            text = 'Ok. That\'s enough for me to make a recommendation.'
            #print self.movie_inputs
            preference_vec = []
            for title in self.movie_titles:
              if title in self.movie_inputs:
                preference_vec.append(self.movie_inputs[title])
              else:
                preference_vec.append(0)
            #print preference_vec
            self.recommended_movies = self.recommend(preference_vec)
            response = ("%s\nI suggest you watch \"%s.\"\nWould you like another recommendation? (If not, enter :no. Enter :quit to exit)") % (text, self.reverse_convert_article(self.recommended_movies[9][0]))
            self.recommend_flag = 1

        # More than 1 movied mentioned in the same input
        elif len(movies_mentioned) > 1:
          response = 'Please tell me about one movie at a time. Go ahead.'
          self.bad_input_count = 0
        # 1 Movie Mentioned
        else:
          self.bad_input_count = 0
          # Search for movie title in quotes
          match = re.search(QUOTATION_REGEX, input)
          quote_start = match.start(0)
          quote_end = match.end(0)
          movie_title = input[quote_start + 1 : quote_end - 1]
          input_movie_removed = input[:quote_start] + input[quote_end:]

          movie_found = False
          readable_title = movie_title
          # Check to see if movie title is known
          if self.getMovieYear(movie_title) is '':
            results = []

            converted_title_noyr = self.convert_article(movie_title)

            #loop through non-year movie title list
            for title, year in self.no_year_titles:
              if movie_title == title:
                movie_found = True
                results.append((title, year))
              elif converted_title_noyr == title:
                movie_found = True
                results.append((converted_title_noyr, year))
              elif movie_title == 'The Valachi Papers':
                movie_found = True
                results.append(('Valachi Papers,The', '1972'))
              '''
              alternate_title = '(a.k.a. ' + movie_title.lower() + ')'
              paren_title = '(' + movie_title.lower() + ')'
              converted_paren_title = '(' + self.convert_article(movie_title).lower() + ')'
              converted_alt_title = '(a.k.a. ' + self.convert_article(alternate_title).lower() + ')'
              converted_foreign_title = '(' + self.convert_foreignArticle(movie_title).lower() + ')'

              lower_title = title.lower()
              #   if ',' in title and '(' in title:
              #     startIndex = title.find('(')
              #     closingIndex = title.find(')')
              #     newStr = title[startIndex + 1:closingIndex]
              #     if ',' in newStr:
              #       newStr = newStr[newStr.find(',') + 1:]
              #       setofArticles.append(newStr)
              if alternate_title in lower_title or converted_alt_title in lower_title:
                movie_found = True
                movie_title = title
                results.append((title, year))
              elif paren_title in lower_title or converted_paren_title in lower_title or converted_foreign_title in lower_title:
                movie_found = True
                movie_title = title
                results.append((title, year))
            '''
            if len(results) == 1:
              movie_title = "%s (%s)" % (results[0][0], results[0][1])
              print movie_title
              print ' ---- ---- ----'
<<<<<<< HEAD
            elif len(results) > 1: 
              results = sorted(results, key=itemgetter(1))
              movie_found = True
              self.carryover = (results, 0)
              #return "Looks like there are multiple movies called " + movie_title + ". Can you please tell me that again with the year of the movie you were talking about? Thanks!"
=======
            elif len(results) > 1:
              movie_found = False
              return "Looks like there are multiple movies called " + movie_title + ". Can you please tell me that again with the year of the movie you were talking about? Thanks!"
>>>>>>> 7b0eb7716af8ed3d755c195e76b0718d4579c2a0


          elif movie_title in self.movie_titles:
            movie_found = True
          elif self.convert_article(movie_title) in self.movie_titles:
            movie_title = self.convert_article(movie_title)
            movie_found = True
          elif movie_title == 'The Valachi Papers (1972)' or movie_title == 'The Valachi Papers': # special case for article without a space
            movie_title = 'Valachi Papers,The (1972)'
            movie_found = True

          setofArticles = []
          if not movie_found:
            alternate_title = '(a.k.a. ' + movie_title.lower() + ')'
            paren_title = '(' + movie_title.lower() + ')'
            converted_paren_title = '(' + self.convert_article(movie_title).lower() + ')'
            converted_alt_title = '(a.k.a. ' + self.convert_article(alternate_title).lower() + ')'
            converted_foreign_title = '(' + self.convert_foreignArticle(movie_title).lower() + ')'

            for title in self.movie_titles:
              lower_title = title.lower()
              lower_title = re.sub(ACTUAL_YEAR_REGEX, '', lower_title)
            #   if ',' in title and '(' in title:
            #     startIndex = title.find('(')
            #     closingIndex = title.find(')')
            #     newStr = title[startIndex + 1:closingIndex]
            #     if ',' in newStr:
            #       newStr = newStr[newStr.find(',') + 1:]
            #       setofArticles.append(newStr)
              if alternate_title in lower_title or converted_alt_title in lower_title:
                movie_found = True
                movie_title = title
                break
              elif paren_title in lower_title or converted_paren_title in lower_title or converted_foreign_title in lower_title:
                movie_found = True
                movie_title = title
                break
          # print set(setofArticles)

          if movie_found:

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Creative
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # print self.getMovieYear(movie_title)
            # print self.getGenresList(movie_title)
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            tokens = input_movie_removed.split(' ') #remove movie title before tokenizing
            #self.movies_count += 1
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
              if t.strip() in ['but', ',but', ', but']:
                sentiment_counter = 0

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

            if sentiment_counter > 0:
              sentiment = 'liked'
              # for g in self.getGenresList(movie_title):
              #   self.genres_input[g] = self.genres_input.get(g, 0) + 1
            elif sentiment_counter < 0:
              sentiment = 'didn\'t like'
              for g in self.getGenresList(movie_title):
                self.genres_input[g] = self.genres_input.get(g, 0) - 1

            else:
              return 'Sorry, didn\'t quite get whether you liked \"' + readable_title + '\". Can you elaborate on what you thought of \"' + movie_title + '\"?'

            if self.carryover:
              self.carryover = (self.carryover[0], sentiment_counter)
              num_options = len(self.carryover[0])
              ex_date = self.carryover[0][1][1]
              return "Woah! Hold the phone! Looks like there are " + str(num_options) + " movies called " + movie_title + ". Which one are you talking about? You can tell me the year the movie was released or let me know which number it was chronologically. For example, if you were talking about the second movie called " + movie_title + ", which was released in " + ex_date + ", just tell me 2 or " + ex_date + "."

            like_genre = ''
            dislike_genre = ''
            for genre, count in self.genres_input.iteritems():
              if count > 2:
                like_genre = genre
              if count < -2:
                dislike_genre = genre

            if len(like_genre) > 0:
              print("Wow! You seem to really like movies in the " + like_genre + " genre!")
            if len(dislike_genre) > 0:
              print("Interesting. You seem to really dislike movies in the " + dislike_genre + " genre.")

            response = 'So you ' + sentiment + ' \"' + readable_title + '\". Got it. How about another movie?'

            if sentiment_counter == 0:
              self.movie_inputs[movie_title] = 1.0
            else:
              self.movie_inputs[movie_title] = (float(sentiment_counter / abs(sentiment_counter)))
          else:
            response = 'Sorry, I don\'t recognize that movie. How about we try another movie?'

      # -----------------------------------------
      # STANDARD MODE
      # DO NOT CHANGE BELOW FOR CREATIVE MODE
      # CREATIVE MODE ABOVE THIS LINE
      # -----------------------------------------

      else:
        # Find movie(s) mentioned by user
        movies_mentioned = re.findall(QUOTATION_REGEX, input)
        if self.recommend_flag > 0 and self.recommend_flag <= 9 and input != ':no':
          response = ("I suggest you watch \"%s.\"\nWould you like another recommendation? (If not, enter :no. Enter :quit to exit)") % (self.reverse_convert_article(self.recommended_movies[(9 - self.recommend_flag)][0]))
          self.recommend_flag += 1
        elif self.recommend_flag == 10:
          response = "I gave you 10 recommendations already! Did you watch all of them already? I can make more recommendations, but you'll have to update me on your preferences."
          self.movie_inputs = {}
          self.recommended_movies = []
          self.recommend_flag = 0
        elif len(movies_mentioned) == 0:
          if self.bad_input_count == 2:
            response = "Listen. I know you're probably trying to break me. But I'm unbreakable!\nBy the way, \"Unbreakable (2000)\" is a good choice if you're into Drama or Sci-Fi. Tell me about another movie."
            self.bad_input_count += 1
          elif self.bad_input_count > 2:
            response = "Be nice and tell me about a movie that you've watched. I've got places to go! \nSpeaking of which... \"Going Places (Valseuses, Les) (1974)\" is not bad."
            self.bad_input_count += 1
          elif input == ':no':
            self.movie_inputs = {}
            self.recommended_movies = []
            self.recommend_flag = 0
            possible_responses = [
              'OK. Tell me more about movies that you\'ve watched. (enter :quit to exit)',
              'Sure. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes. (enter :quit to exit)',
              'So, tell me about another movie. (enter :quit to exit)'
            ]
            response = possible_responses[random.randint(0, len(possible_responses) - 1)]
            self.bad_input_count += 1
          elif len(self.movie_inputs) < MIN_NUM_MOVIES_NEEDED:
            possible_responses = [
              'I need to know a bit more about your movie preferences before I can provide you with a recommendation. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.',
              'Sorry. Didn\'t quite get that. Tell me about a movie that you\'ve seen. Make sure it\'s in quotes.',
              'I know I\'m supposed to be a smart bot... but in order for me to make good recommendations, I need you to tell me a few more movies that you\'ve seen. Thanks!'
            ]
            response = possible_responses[random.randint(0, len(possible_responses) - 1)]
            self.bad_input_count += 1
          else:
            self.bad_input_count = 0
            text = 'Ok. That\'s enough for me to make a recommendation.'
            #print self.movie_inputs
            preference_vec = []
            for title in self.movie_titles:
              if title in self.movie_inputs:
                preference_vec.append(self.movie_inputs[title])
              else:
                preference_vec.append(0)
            #print preference_vec
            self.recommended_movies = self.recommend(preference_vec)
            response = ("%s\nI suggest you watch \"%s.\"\nWould you like another recommendation? (If not, enter :no. Enter :quit to exit)") % (text, self.reverse_convert_article(self.recommended_movies[9][0]))
            self.recommend_flag = 1

        # More than 1 movied mentioned in the same input
        elif len(movies_mentioned) > 1:
          response = 'Please tell me about one movie at a time. Go ahead.'
          self.bad_input_count = 0
        # 1 Movie Mentioned
        else:
          self.bad_input_count = 0
          # Search for movie title in quotes
          match = re.search(QUOTATION_REGEX, input)
          quote_start = match.start(0)
          quote_end = match.end(0)
          movie_title = input[quote_start + 1 : quote_end - 1]
          input_movie_removed = input[:quote_start] + input[quote_end:]

          movie_found = False
          readable_title = movie_title
          # Check to see if movie title is known
          if movie_title in self.movie_titles:
            movie_found = True
          elif self.convert_article(movie_title) in self.movie_titles:
            movie_title = self.convert_article(movie_title)
            movie_found = True
          elif movie_title == 'The Valachi Papers (1972)': # special case for article without a space
            movie_title = 'Valachi Papers,The (1972)'
            movie_found = True

          if movie_found:

            tokens = input_movie_removed.split(' ') #remove movie title before tokenizing
            #self.movies_count += 1
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
              if t.strip() in ['but', ',but', ', but']:
                sentiment_counter = 0

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

            if sentiment_counter > 0:
              sentiment = 'liked'
            elif sentiment_counter < 0:
              sentiment = 'didn\'t like'

            else:
              return 'Sorry, didn\'t quite get whether you liked \"' + readable_title + '\". Can you elaborate on what you thought of \"' + movie_title + '\"?'

            response = 'So you ' + sentiment + ' \"' + readable_title + '\". Got it. How about another movie?'

            if sentiment_counter == 0:
              self.movie_inputs[movie_title] = 1.0
            else:
              self.movie_inputs[movie_title] = (float(sentiment_counter / abs(sentiment_counter)))
          else:
            response = 'Sorry, I don\'t recognize that movie. How about we try another movie?'

      # print self.movie_inputs
      # print self.recommend_flag
      # print self.genres_input
      #############################################################################
      # return statement for both Turbo and Standard bots
      #############################################################################

      return response


    def minDistance(title1, title2):
      len1 = len(title1)
      len2 = len(title2)
      distMatrix = []
      for i in range(0, len2 + 1):
        listNum = []
        for j in range(0, len1 + 1):
            listNum.append(0)
        distMatrix.append(listNum)
      #distMatrix = [[0] * (len1 + 1)] * (len2 + 1)
      print distMatrix
      for row in xrange(0, len2 + 1):
        for col in xrange(0, len1 + 1):
          print title1[col - 1]
          print title2[row - 1]
          if row == 0:
            distMatrix[row][col] = col
          elif col == 0:
            distMatrix[row][col] = row
          elif title1[col-1] == title2[row-1]:
            print 'inside'
            distMatrix[row][col] = distMatrix[row-1][col-1]
          else:
            distMatrix[row][col] = 1 + min(distMatrix[row][col-1], distMatrix[row-1][col],distMatrix[row-1][col-1])
      return distMatrix[len2][len1]

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
      #if self.is_turbo == True:
      for title in self.movie_titles:
        title_wo_yr = self.removeYear(title)
        year = self.getMovieYear(title)
        self.no_year_titles.append((title_wo_yr, year))

      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)

      self.sentiment_stemmed = dict()
      subdirs = os.listdir('deps')
      if 'sentiment_stemmed.txt' in subdirs:
        #print('Sentiment lexicon already stemmed...')
        self.sentiment_stemmed = dict(csv.reader(open('./deps/sentiment_stemmed.txt', 'rb')))
      else:
        #print('Stemming sentiment lexicon.')
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
          rating = 0.0
          if raw_rating >= UPPER_THRESHOLD:
            rating = 1.0
          elif raw_rating <= LOWER_THRESHOLD and raw_rating > 0:
            rating = -1.0
          else:
             rating = 0.0
          self.bin_ratings[row][col] = rating


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      # Cosine similarity
      cos = 0
      mag_u = np.linalg.norm(u)
      mag_v = np.linalg.norm(v)
      dot_prod = np.dot(u,v)
      mag_prod = mag_u * mag_v
      if mag_prod != 0:
        cos = dot_prod / mag_prod
      return cos

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      # count = 0
      suggestions = []
      # loopCt = 0
      for i, movie_vec in enumerate(self.bin_ratings):
        predicted_rating = 0
        if self.movie_titles[i] in self.movie_inputs:
          continue

        for title, rating in self.movie_inputs.iteritems():
          index = self.movie_titles.index(title)
          rating_vec = self.bin_ratings[index]
          #print 'Test:'
          #print index
          #print title
          #print self.bin_ratings[index]
          #print self.ratings[index]

          # print 'rating_vec: %s' % (rating_vec)
          # print 'movie_vec: %s' % (movie_vec)
          # print

          similarity = self.distance(rating_vec, movie_vec)
          #if similarity >= 0: # solve for RuntimeError?
          predicted_rating += (rating * similarity)

        if len(suggestions) < 10:
          suggestions.append((self.movie_titles[i], predicted_rating))
          suggestions = sorted(suggestions, key=itemgetter(1))
          # count += 1
        elif predicted_rating >= suggestions[0][1]:
          suggestions[0] = (self.movie_titles[i], predicted_rating)
          suggestions = sorted(suggestions, key=itemgetter(1))
          # count += 1
        # loopCt += 1

      # print 'loopCt: %s' % (loopCt)
      # print "COUNT = %s" % (count)
      # print(self.mag_u_count)
      # print(self.mag_v_count)
      return suggestions


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
      Hello, I'd like to introduce you to Movie Bot. Movie Bot is not your everyday movie recommendation system.
      This virtual cinephile hit their head as a child and sometimes gets confused that they are a
      British secret agent. Nevertheless, Movie Bot will help you will all your movie recommendation needs.

      Movie Bot exists in two modes.
      1. Standard Mode:
      In Movie Bot's standard mode, they will ask you about your movie preferences.
      After you give at least 5 unique movie preferences, specifically formatted to the standard mode
      Movie Bot's liking, Movie Bot will give you up to 10 movie recommendation.
      In standard mode Movie Bot needs you to talk about movies in the format "Movie Title (YYYY)".

      2. Creative Mode:
      In creative mode, Movie Bot drinks 10 red bulls and gets their wings (enhanced capabilities).
      Movie Bot's enhanced capabilities are:
        1.
        2.
        3.

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
