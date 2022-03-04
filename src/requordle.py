import os, json

DEBUG = False
_print = lambda *x: print(*x) if DEBUG else None

def fetch_wordlist(filename):
    with open(os.path.abspath(os.path.join("data", f"{filename}.txt")), "r") as f:
        return f.read().splitlines()

def sanitize_input(inp, answers):
    a = [i for i in answers]
    result_lines = inp.split("\n")
    print(inp)

    meta = result_lines[0:4]
    guesses = result_lines[4:]
    split_point = guesses.index('')

    guesses = [guesses[:split_point], guesses[split_point+1:]]
    guesses_halfsplit = [[j.split() for j in i] for i in guesses]

    guesses_sorted = {}

    for v in guesses_halfsplit:
        for i in range(0,2):
            pld = []
            for j in v:
                if j[i] != "⬛⬛⬛⬛⬛":
                    pld.append(j[i])
            guesses_sorted[a.pop(0).lower()] = pld
    
    return meta, guesses_sorted


def get_valid_words(iter, guesses, word_list):
    valid = []

    for word in word_list:
        works = True
        
        _print("\n"+"-"*20)
        for answer,word_guesses in guesses.items():
            
            if iter < len(word_guesses): # check if the solution for a puzzle was already found by this iteration
                _print()

                guess = word_guesses[iter]
                _print(guess)
                _print(f"{word.upper()} -> {answer.upper()}")

                #letter_results = [(word[i], slot) for i,slot in enumerate(guess)]
                simulated_outcome = []
                simulated_blocks = ""

                for index,slot in enumerate(guess):
                    # fill in the guaranteed letters first
                    letter = word[index]

                    if letter == answer[index]:
                        simulated_outcome.append((letter, "🟩"))
                    else:
                        simulated_outcome.append((letter, "🟦")) # temporary placeholder, will be computed next b/c lower importance


                for index,slot in enumerate(guess):
                    # check for everything else
                    letter = word[index]

                    if letter == answer[index]: # greens
                        simulated_outcome[index] = (letter,"🟩")
                    
                    elif letter in answer: # yellows 'n whites
                        if word.count(letter) > 1:
                                
                            expected = answer.count(letter)
                            actual = 0 

                            for i in simulated_outcome:
                                if i[0] == letter and (i[1] == "🟩" or i[1] == "🟨"):
                                    actual += 1
                            if actual < expected:
                                simulated_outcome[index] = (letter,"🟨")
                            else:
                                simulated_outcome[index] = (letter,"⬜")
                        else:
                            simulated_outcome[index] = (letter,"🟨")
                    
                    elif not letter in answer: # whites
                        simulated_outcome[index] = (letter,"⬜")

                _print(simulated_outcome)
                simulated_blocks = "".join([i[1] for i in simulated_outcome])
                if not simulated_blocks == guess:
                    works = False

        if works:
            _print("WORKS!")
            valid.append(word)

    return valid




def main(answers):
    word_list = fetch_wordlist("test_wordlist" if DEBUG else "allowed_words")

    result = '''
Daily Quordle #38
3️⃣7️⃣
9️⃣8️⃣
quordle.com
⬜🟨⬜🟩🟩 🟨🟨⬜⬜🟨
⬜⬜🟩🟩🟩 ⬜🟩🟨⬜🟨
🟩🟩🟩🟩🟩 ⬜⬜🟨⬜🟨
⬛⬛⬛⬛⬛ 🟨🟩⬜⬜🟨
⬛⬛⬛⬛⬛ ⬜🟨🟨🟩🟩
⬛⬛⬛⬛⬛ 🟨⬜🟩🟩🟩
⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩

⬜⬜🟨🟨🟩 ⬜🟨⬜⬜🟨
🟨⬜⬜🟨🟩 ⬜🟨🟨⬜⬜
⬜⬜⬜🟨🟩 ⬜🟨🟨⬜🟨
⬜🟨⬜⬜⬜ 🟨🟨⬜⬜⬜
⬜⬜🟨⬜⬜ 🟩⬜🟩⬜🟩
🟨🟨⬜⬜⬜ 🟨⬜⬜⬜🟩
⬜🟨⬜⬜⬜ 🟨🟨⬜⬜🟩
⬜⬜🟨⬜⬜ 🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛
    '''.strip()

    meta, guesses = sanitize_input(result, answers)
    _, longest_word_guesses = max(guesses.items(), key = lambda x: len(set(x[1])))

    calculated_guesses = []
    def next(iter=0, tree=[], guesses={}):
        valid_words = get_valid_words(iter, guesses, word_list)
        calculated_guesses.append(valid_words)

    if not DEBUG:
        for i in range(len(longest_word_guesses)):
            next(iter=i,guesses=guesses)

    else:
        next(iter=5, guesses=guesses)

    print_output(calculated_guesses)

def print_output(answers):
    print("\n====== possible guesses ======")
    for i,v in enumerate(answers):
        print(f"{i+1}: " + "; ".join(j for j in v))