import os


class Brown:
    word_tag_pairs = []
    word_tag_dictionary = {}
    words = []
    word_dictionary = {}  # store all words in a map<word, numOfOccurrences>
    tags = []
    distinct_tags = []
    tag_dictionary = {}  # store all tags in a map<tag, numOfOccurrences>
    transaction_tag_dictionary = {}

    def __init__(self, brown_folder_path):
        print('Studying from the Brown corpus...')
        listing = os.listdir(brown_folder_path)
        for infile in listing:
            with open(brown_folder_path + "/" + infile) as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip():
                        line = "START/START " + line + " END/END"
                        previous_tag = 'START'
                        for word_tag in line.split():
                            self.word_tag_pairs.append(word_tag)
                            if word_tag in self.word_tag_dictionary:
                                self.word_tag_dictionary[word_tag] += 1
                            else:
                                self.word_tag_dictionary[word_tag] = 1

                            split_word_tag = word_tag.rsplit('/', 1)
                            word_temp = split_word_tag[0]
                            tag_temp = split_word_tag[1]
                            self.words.append(word_temp)
                            self.tags.append(tag_temp)

                            transaction_tag = previous_tag + '_' + tag_temp
                            if transaction_tag in self.transaction_tag_dictionary:
                                self.transaction_tag_dictionary[transaction_tag] += 1
                            else:
                                self.transaction_tag_dictionary[transaction_tag] = 1

                            previous_tag = tag_temp

                            if word_temp in self.word_dictionary:
                                self.word_dictionary[word_temp] += 1
                            else:
                                self.word_dictionary[word_temp] = 1

                            if tag_temp in self.tag_dictionary:
                                self.tag_dictionary[tag_temp] += 1
                            else:
                                self.distinct_tags.append(tag_temp)
                                self.tag_dictionary[tag_temp] = 1
            file.close()

        print('done!')

brown = Brown('brown')


def emission_prob(word, tagg):
    word_tag_temp = word + '/' + tagg
    count_word_tag = 0

    if word_tag_temp in brown.word_tag_dictionary.keys():
        count_word_tag = brown.word_tag_dictionary[word_tag_temp]

    count_tag = brown.tag_dictionary[tagg]
    return count_word_tag / count_tag


def transition_prob(tag1, tag0):
    num_of_trans_tag0_tag1 = 0
    transaction_tag_key = tag0 + '_' + tag1
    if transaction_tag_key in brown.transaction_tag_dictionary:
        num_of_trans_tag0_tag1 = brown.transaction_tag_dictionary[transaction_tag_key]
    return num_of_trans_tag0_tag1 / brown.tag_dictionary[tag0]


def get_user_input():
    return input("Enter your sentence ('stop' to exit): ")

distinct_tags = brown.distinct_tags

user_input = get_user_input()

while user_input != 'stop':
    sentence = user_input.split()

    sentence_length = len(sentence)

    print('... analyzing sentence:', sentence)

    viterbi = []
    back_pointer = []

    first_viterbi = {}
    first_back_pointer = {}
    for tag in distinct_tags:
        # don't record anything for the START tag
        if tag == "START":
            continue
        first_viterbi[tag] = transition_prob(tag, 'START') * emission_prob(sentence[0], tag)
        first_back_pointer[tag] = "START"

    viterbi.append(first_viterbi)
    back_pointer.append(first_back_pointer)

    for word_index in range(1, len(sentence)):
        this_viterbi = {}
        this_back_pointer = {}
        prev_viterbi = viterbi[-1]
        for tag in distinct_tags:
            if tag == "START":
                continue
            best_previous = ''
            best_prob = 0.0
            for prev_tag in prev_viterbi.keys():
                prob = prev_viterbi[prev_tag] * transition_prob(tag, prev_tag) * emission_prob(sentence[word_index], tag)
                if prob >= best_prob:
                    best_previous = prev_tag
                    best_prob = prob

            this_viterbi[tag] = prev_viterbi[best_previous] * transition_prob(tag, best_previous) * emission_prob(sentence[word_index], tag)
            this_back_pointer[tag] = best_previous

        viterbi.append(this_viterbi)
        back_pointer.append(this_back_pointer)

    prev_viterbi = viterbi[-1]
    best_previous = max(prev_viterbi.keys(), key=lambda prevtag: prev_viterbi[prevtag] * transition_prob('END', prevtag))

    prob_tag_sequence = prev_viterbi[best_previous] * transition_prob('END', best_previous)

    best_tag_sequence = ['END', best_previous]

    back_pointer.reverse()

    current_best_tag = best_previous
    for bp in back_pointer:
        best_tag_sequence.append(bp[current_best_tag])
        current_best_tag = bp[current_best_tag]

    best_tag_sequence.reverse()

    print("==> The best tag sequence is:", best_tag_sequence)

    user_input = get_user_input()
