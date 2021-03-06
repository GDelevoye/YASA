#!/usr/bin/env python
import random
import re
import time

import yasa

# do we want randomized results to be reproducible?
random.seed(98723432)


def run_aligner(aligner, source, target, pretty=True):
    print aligner
    t0 = time.clock()
    alignment = aligner.align(source, target)
    t1 = time.clock()
    if pretty:
        print "+" * 10, "  Alignment Time = {} ms  ".format((t1 - t0) * 1000), "+" * 10
        print alignment.pretty_print()
        print alignment
        print "+" * 10, "  Alignment Time = {} ms  ".format((t1 - t0) * 1000), "+" * 10
        print
        summary = yasa.ClassifierErrorRate()
        summary.accu_alignment(alignment)
        print(summary)
    else:
        print alignment
    print
    return alignment


def test_non_string_alignment():
    aligner = yasa.LevinshteinAligner(5, 100)
    run_aligner(aligner, [1, 2, 3], [2, 2, 3, 3])


def run_wer_aligner(source, target, pretty=True):
    """
    Test Word Error Rate aligner

    :param source:
    :param target:
    :param pretty:
    :return:
    :rtype: None
    """
    aligner = yasa.LevinshteinAligner(20, 200)
    run_aligner(aligner, source, target, pretty)


def __jumble(tokens):
    for i in xrange(len(tokens) - 1):
        if random.random() < 0.1:
            # only let the sapping take place N tokens apart
            swapx = random.randint(i + 1, min(i + 1 + 5, len(tokens) - 1))
            if swapx < len(tokens):
                swap = tokens[swapx]
                tokens[swapx] = tokens[i]
                tokens[i] = swap


def __announce_test(test_name):
    print "-" * 20
    print test_name
    print "-" * 20


def __load_declaration(n=1):
    """
    Load the declaration of independence repeated n times.
    :param n:
    :return:
    """
    print "Loading declaration...",
    fp = open('declaration.txt')
    text = fp.read()
    fp.close()
    print "Done"
    return text * n


def __del_some(tokens, del_prob=0.1, m_del_prob=0.4):
    new_tokens = []
    for i in xrange(len(tokens)):
        if random.random() > del_prob:
            # match here
            new_tokens.append(tokens[i])
        else:
            # maybe this deletion is a multiple deletion
            while random.random() < m_del_prob:
                i += 1
    return new_tokens


def __get_words(text):
    return re.split("\s+", text)


def __get_chars(text):
    return [c for c in text]


def big_word_test():
    __announce_test("Big Word Test")
    # TODO there is something strange going on here.
    # If you run the big word test with one copy of the declaration everything works fine. But, if you use 2
    # copies the alignment become horrible.

    copies_of_declaration = 3
    text = __load_declaration(copies_of_declaration)
    target = __get_words(text)
    source = __get_words(text)
    source = __del_some(source)
    target = __del_some(target)

    # print "SOURCE"
    # print " ".join(source)
    # print "TARGET"
    # print " ".join(target)

    aligner = yasa.NestedLevinshteinAligner(1, 50)
    run_aligner(aligner, source, target, True)
    # __param_search(source, target, True)


def big_char_test():
    __announce_test("Big Char Test")
    text = __load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    __jumble(source)

    aligner = yasa.LevinshteinAligner(source, target)
    run_aligner(aligner, source, target)
    # __param_search(source, target)


WORD_SOURCE_TARGET_PAIRS = [
    # disproportionately long target
    ("how many chucks could a wood chuck",
     "wood chucks are nice animals -- although they will dig holes in your garden. " +
     "how many chucks could a wood chuck if a wood chuck could chuck wood"),
    # disproportionately long source
    ("wood chucks are nice animals -- although they will dig holes in your garden. " +
     "how many chucks could a wood chuck if a wood chuck could chuck wood",
     "how many chucks could a wood chuck"),
    # this will not align
    ("this is a test", "sailing up wind is hard"),
    # poor alignment
    ("bad alignments are bad", "on the other hand, good alignments are good"),
    # reasonable alignment
    ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable"),
    # reasonable alignment + 1
    ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable right???"),
    # poor-ish alignment
    ("no alignment is better than a horrible one?", "i had a horrible headache"),
    ("this is a little bit tricky", "fishes are a very sticky animal"),
    ("this is very crappy and this is a little bit tricky", "this is a little bit tricky")
]


def default_aligner_tests():
    __announce_test("Default Aligner Tests")

    aligner = yasa.NestedLevinshteinAligner(1, 20)
    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
        run_aligner(aligner, __get_words(source), __get_words(target))


def wer_aligner_tests():
    __announce_test("WER Aligner Tests")

    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
        run_wer_aligner(__get_words(source), __get_words(target))


def get_errors_test():
    __announce_test("Get errors test")

    aligner = yasa.NestedLevinshteinAligner(1, 100)

    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
        source = __get_words(source)
        target = __get_words(target)

        alignment = aligner.align(source, target)
        print alignment
        for node in alignment.errors():
            print node.pretty_print(source, target)


def get_error_counts_test():
    test_error_counts_1()
    test_error_counts_2()


def test_error_counts_1():
    __announce_test("Get error counts test 1")

    source = __get_words("a b b a")
    target = __get_words("a x x i s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)
    print alignment
    for (error, count) in alignment.error_counts():
        print '{}\t{}'.format(error, count)


def test_error_counts_2():
    __announce_test("Get error counts test 2")

    source = __get_words("a b b a")
    target = __get_words("a x x i s s s s s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)
    print alignment
    for (error, count) in alignment.error_counts():
        print '{}\t{}'.format(error, count)


def test_bad_error_key():
    __announce_test('Bad error key')
    source = __get_words("a b b a")
    target = __get_words("a x x i s s s s s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)

    err = yasa.ClassifierErrorRate()
    err.accu_alignment(alignment)

    print(err.as_string(labels=['a', 'b', 'x', 'bad', 'poopy']))


def run_all_tests():
    # known_weirdness()

    default_aligner_tests()
    test_non_string_alignment()
    test_bad_error_key()
    # big_word_test()
    # get_errors_test()
    # get_error_counts_test()


if __name__ == '__main__':
    run_all_tests()
