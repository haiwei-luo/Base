# from jellyfish import soundex, metaphone, nysiis, match_rating_codex,\
#     levenshtein_distance, damerau_levenshtein_distance, hamming_distance,\
#     jaro_similarity

import jellyfish as jf

from itertools import groupby
import pandas as pd
import numpy as np


available_names  = ["adel", "angel", "axel", "charlie", "jane", "jules", "morgan", "paris", "robin", "simone"]
available_single_drinks = ["cola", "milk",]
available_double_drinks = ["iced", "tea", "pack", "juice", "orange", "red", "wine", "tropical"]
double_drinks_dict = {"iced" : "iced tea", 
                        "tea": "iced tea", 
                        "pack" : "juice pack",
                        "orange" : "orange juice",
                        "red" : "red wine",
                        "wine" : "red wine",
                        "tropical" : "tropical juice",
                        # "juice": ["orange juice", "tropical juice", "juice pack"],
                        }
available_drinks = list(set(available_single_drinks).union(set(available_double_drinks)))


def speech_recovery(sentence):
    sentence_list = sentence.split()
    print(f"final name: {handle_name(sentence_list)}")
    print(f"final drink: {handle_drink(sentence_list)}")
    

def handle_name(sentence_list):
    result = handle_similar_spelt(sentence_list, available_names, 1)
    if result != "":
        print(f"name (spelt): {result}")
        return result
    else:
        result = handle_similar_sound(sentence_list, available_names, 1)
        print(f"name (sound): {result}")
    
    return result
        


def handle_drink(sentence_list):
    result = infer_second_drink(sentence_list)
    if result != "":
        return result
    result = handle_similar_spelt(sentence_list, available_drinks, 1)
    if result != "":
        print(f"drink (spelt): {result}")
    else:
        result = handle_similar_sound(sentence_list, available_drinks, 0)
        print(f"drink (sound): {result}")
    
    if result == "":
        return ""

    if result in available_single_drinks:
        print(f"final attempt drink: {result}")
        return result
    else:
        sentence_list.append(result)
        return infer_second_drink(sentence_list)

        

def infer_second_drink(sentence_list):
    for input_word in sentence_list:
        if input_word == "juice":
            choices = ["pack", "orange", "tropical"]
            closest_word =  handle_closest_spelt(sentence_list, choices)
            if closest_word == "pack":
                return "juice pack"
            elif closest_word == "orange":
                return "orange juice"
            else:
                return "tropical juice"
        for available_word in available_double_drinks:
            if input_word == available_word:
                return double_drinks_dict[input_word]
    return ""


def handle_similar_spelt(sentence_list, available_words, distance_threshold):
    for input_word in sentence_list:
        for available_word in available_words:
            distance = get_damerau_levenshtein_distance(input_word, available_word)
            if distance <= distance_threshold:
                return available_word
    return ""


def handle_similar_sound(sentence_list, available_words, distance_threshold):
    for input_word in sentence_list:
        for available_word in available_words:
            distance = get_levenshtein_soundex_distance(input_word, available_word)
            if distance <= distance_threshold:
                print(input_word)
                return available_word
    return ""

def handle_closest_spelt(sentence_list, choices):
    closest_distance = get_damerau_levenshtein_distance(sentence_list[0], choices[0])
    closest_word = choices[0]
    for input_word in sentence_list:
        for available_word in choices:
            distance = get_damerau_levenshtein_distance(input_word, available_word)
            if distance < closest_distance:
                closest_distance = distance
                closest_word = available_word
    return closest_word

def get_damerau_levenshtein_distance(word_1, word_2):
    return jf.damerau_levenshtein_distance(word_1, word_2)

def get_levenshtein_soundex_distance(word_1, word_2):
    soundex_word_1 = jf.soundex(word_1)
    soundex_word_2 = jf.soundex(word_2)
    return jf.levenshtein_distance(soundex_word_1, soundex_word_2)

# print(get_damerau_levenshtein_distance("juice", "shoes"))
# print(get_levenshtein_soundex_distance("juice", "shoes"))


# print(jf.levenshtein_distance(jf.metaphone("my"), jf.metaphone("tea")))

# print(jf.soundex("juice"), jf.soundex("shoes"))

# print(jf.levenshtein_distance(jf.soundex("jane"), jf.soundex("jaydon")))

# available_names  = ["adel", "angel", "axel", "charlie", "jane", "jules", "morgan", "paris", "robin", "simone"]
# available_single_drinks = ["cola", "milk",]
# available_double_drinks = ["iced", "tea", "juice", "pack", "orange", "red", "wine", "tropical"]
# double_drinks_dict = {"iced" : "iced tea", 
#                         "tea": "iced tea", 
#                         "pack" : "juice pack",
#                         "orange" : "orange juice",
#                         "red" : "red wine",
#                         "wine" : "red wine",
#                         "tropical" : "tropical juice",
#                         "juice": ["orange juice", "tropical juice", "juice pack"],
#                         }

# available_names_and_drinks = list(set(available_names).union(set(available_single_drinks)).union(set(available_double_drinks)))

# sentence = "my name is axl and my favourite drink is orange shoes"

# dataList = set(sentence.split()).union(set(available_names_and_drinks))


if __name__ == "__main__":
    sentence = "my name is jay and my favourite drink is mill"
    speech_recovery(sentence)
    print("======")
    sentence = "my name is jayne and my favourite drink is orang juice"
    speech_recovery(sentence)
    print("======")
    sentence = "my name is axl and my favourite drink is tropical ef"
    speech_recovery(sentence)
    print("======")
    sentence = "my name is axl and my favourite drink is orange juice juice"
    speech_recovery(sentence)
    print("======")