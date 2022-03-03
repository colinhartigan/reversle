import os, json
from typing import *
from tqdm import tqdm

PRINT = False  

def _print(*args):
    if PRINT: print(*args)

def fetch_wordlist(filename):
    with open(os.path.abspath(os.path.join("data", f"{filename}.txt")), "r") as f:
        return f.read().splitlines()

def fetch_frequencies():
    with open(os.path.abspath(os.path.join("data", "frequencies.json")), "r") as f:
        return json.loads(f.read())

def get_next_possible_words(real_word: str, word_list: List[str], guess_types: List[str], previous_word: str=None, previous_guess_types: List[str]=None):
    frequencies = {letter: real_word.count(letter) for letter in real_word}
    words = []

    for word in word_list:
        works = True 
        accepted_indices = [] # indicies that did not fail (0)
        
        for i,letter in enumerate(word):
            # check for basic rules

            #_print(word, letter, real_word[i], guess_types[i])

            if guess_types[i] == "0":
                continue
            if guess_types[i] == "1":
                #_print(word, letter, real_word[i], letter in real_word)
                # letter in word but in wrong position
                if not letter in real_word or real_word[i] == letter:
                    works = False
                    break
            if guess_types[i] == "2":
                if letter != real_word[i]:
                    works = False
                    break

            accepted_indices.append(i)
                    
        if works:
            # basic frequency analysis to make sure the word follows rules for yellow guesses
            accepted_frequencies = {word[i]: 0 for i in accepted_indices}
            for i in accepted_indices:
                accepted_frequencies[word[i]] += 1
            
            for i,v in accepted_frequencies.items():
                if frequencies[i] != v:
                    works = False
                    break

        if works and previous_word is not None and previous_guess_types is not None:
            # if there's a previous guess to compare against to make sure the word follows rules for hard mode
            letters_must_be_used = [previous_word[i] for i, t in enumerate(previous_guess_types) if t == "1" or t == "2"]
            for i,old_letter in enumerate(letters_must_be_used):
                if not old_letter in word:
                    works = False
                    break
            
            # check to make sure the new yellow letters match the old yellow letters
            new_yellows = [word[i] for i, t in enumerate(guess_types) if t == "1" or t == "2"]
            old_yellows = [previous_word[i] for i, t in enumerate(previous_guess_types) if t == "1" or t == "2"]

            for oy in old_yellows:
                try:
                    new_yellows.pop(new_yellows.index(oy))
                except Exception as e:
                    works = False
                    break

            if works:
                _print(f"✅ {previous_word} -> {word}", letters_must_be_used)
        
        if works: words.append(word)

    return words


def sort_guesses(guesses):
    frequences = fetch_frequencies()
    sort = sorted(guesses, key=lambda x: frequences[x], reverse=True)
    return sort

def main():
    valid_words = fetch_wordlist("allowed_words")
    word_schedule = fetch_wordlist("word_schedule")    

    result = '''
Wordle 256 5/6

⬜⬜⬜🟨🟨
⬜⬜🟨🟨🟨
🟨🟩🟨⬜⬜
🟨🟩⬜🟨🟨
🟩🟩🟩🟩🟩
    '''.strip().replace("⬜", "⬛")
    result_split = result.split("\n")
    meta = result_split[0]

    print(f"\n{result}")
    day_num = int(meta[meta.find("Wordle ") + 7:meta.find("/") - 2])

    todays_word = word_schedule[day_num]
    print(" ".join(i for i in todays_word))

    guesses = result_split[2:]

    roots = []

    def next_guess(iter=0, root=None, previous_word=None, previous_guess_types=None):
        # play every possible game (following hard mode rules) that follows the pattern then look for a matching pattern, use that to extrapolate start word
        # LETTERS USED IN GUESS 1 ALSO HAVE TO BE USED IN GUESS 2

        #trees[root]

        _print(f"guess {iter+1} (root: {root} / previous: {previous_word})\n{guesses[iter]}")
        guess_types = [("0" if letter == "⬛" else "1" if letter == "🟨" else "2" if letter == "🟩" else "") for i, letter in enumerate(guesses[iter])]

        word_list = get_next_possible_words(todays_word, valid_words, guess_types, previous_word, previous_guess_types)

        _print(f"possible words ({len(word_list)}) - {word_list}\n")

        if len(word_list) > 1:
            for word in word_list:
                p_root = root if root is not None else word
                success = next_guess(iter+1, p_root, previous_word=word, previous_guess_types=guess_types)
        
        elif iter == len(guesses) or len(word_list) == 1:
            if previous_word == todays_word or (len(word_list) == 1 and word_list[0] == todays_word):
                if not root in roots: roots.append(root)
                return True
            return False

    next_guess()
    print(f"\npossible first guesses ({len(roots)}) {roots}")

    sort_roots = sort_guesses(roots)
    print(f"\nmost likely: {sort_roots}\n")