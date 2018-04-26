"""Predictor
"""
# -*- coding: utf-8 -*-
import string
import json
import random

class Event:
    """Event class."""
    def __init__(self,
                 name,
                 desc,
                 tag,
                ):
        self.name = name
        self.desc = desc
        self.tag = tag

def process_attr(word):
    """Process attribute."""
    html = ['<a>', '<p>', '</p>', '</a>']
    for tag in html:
        word = word.replace(tag, '')
    result = ''
    for char in word:
        if char not in string.punctuation:
            result += char
    return result


class Model:
    """Model class."""
    def __init__(self):
        self.categories = {}
        self.cat_counts = {}
        self.attr_counts = {}
        self.attr_totals = {}
        self.events = self.get_events('code/tagged.txt')
        self.test = []
        self.prep_model()

    def test_model(self):
        """Test model."""
        random.shuffle(self.events)
        self.test = self.events[-500:]
        count = 0
        for i in self.test:
            if self.predict_bayes(i.name) == i.tag:
                count += 1

        # print(float(count) / float(500))

    def prep_model(self):
        """Prepare model."""
        sw = STOP_WORDS_NLTK

        self.categories, self.cat_counts = self.get_categories()
        self.attr_counts = {}
        self.attr_totals = {}
        for cat in self.categories:
            self.attr_counts[cat] = {}
            self.attr_totals[cat] = 0
            for event in self.categories[cat]:
                context = event.desc.split(' ')
                context.extend(event.name.split(' '))
                for word in context:
                    word = word.lower()
                    word = process_attr(word)
                    if word == '' or word in sw or len(word) > 20:
                        continue
                    if word[0] == '<' or word == u'\u2022':
                        continue

                    self.attr_totals[cat] += 1
                    if word in self.attr_counts[cat]:
                        self.attr_counts[cat][word] += 1
                    else:
                        self.attr_counts[cat][word] = 1

    def get_categories(self):
        """Get categories."""
        category_counts = {}
        counts = {}
        for e in self.events:
            for tag in e.tags:
                if tag in category_counts:
                    counts[tag] += 1
                    category_counts[tag].append(e)
                else:
                    category_counts[tag] = [e]
                    counts[tag] = 1

        return (category_counts, counts)

    def get_events(self, file_name):
        """Get events."""
        event_list = []
        f = open(file_name, 'r')
        data = f.read()
        lines = data.split('\n')
        i = 0
        while i < len(lines) - 1:
            if lines[i] == '' or lines[i + 1] == '':
                i += 2
                continue

            event_info = json.loads(lines[i])

            if 'description' in event_info.keys() \
                and event_info['description']:
                desc = event_info['description']
            else:
                i += 3
                continue

            if 'name' not in event_info.keys():
                continue
            ename = event_info['name']
            # eid = lines[i + 1]
            tag = lines[i + 2]
            e = Event(ename, desc, tag)
            e.tags = [tag]
            event_list.append(e)
            i += 3

        f.close()
        return event_list

    def predict_bayes(self, name):
        """Predict using Naive Bayes model."""
        sw = STOP_WORDS_NLTK
        context = name.split(' ')

        # context.extend(event.name.split(' '))

        processed = []
        for word in context:
            word = word.lower()
            word = process_attr(word)
            if word == '' or word in sw or len(word) > 20:
                continue
            if word[0] == '<':
                continue
            processed.append(word)

        probs = {}
        for category in self.cat_counts:
            p_label = float(self.cat_counts[category]) \
                / float(len(self.events))
            prob = p_label
            for attr in processed:
                p_attr = 1
                if attr in self.attr_counts[category]:
                    p_attr = float(self.attr_counts[category][attr]) \
                        / float(self.attr_totals[category])
                else:

                    p_attr = float(1) \
                        / float(self.attr_totals[category])
                prob *= p_attr
            probs[category] = prob

        return max(probs, key=probs.get)

    def get_top_attributes(self, category, num):
        """Get top attributes."""
        sorted_attrs = sorted(self.attr_counts[category].iteritems(),
                              key=lambda (k, v): (v, k))
        return list(i[0] for i in sorted_attrs[-num:])

# Stop words from NLTK
STOP_WORDS_NLTK = set([
    u'all',
    u'just',
    u"don't",
    u'being',
    u'over',
    u'both',
    u'through',
    u'yourselves',
    u'its',
    u'before',
    u'o',
    u'don',
    u'hadn',
    u'herself',
    u'll',
    u'had',
    u'should',
    u'to',
    u'only',
    u'won',
    u'under',
    u'ours',
    u'has',
    u"should've",
    u"haven't",
    u'do',
    u'them',
    u'his',
    u'very',
    u"you've",
    u'they',
    u'not',
    u'during',
    u'now',
    u'him',
    u'nor',
    u"wasn't",
    u'd',
    u'did',
    u'didn',
    u'this',
    u'she',
    u'each',
    u'further',
    u"won't",
    u'where',
    u"mustn't",
    u"isn't",
    u'few',
    u'because',
    u"you'd",
    u'doing',
    u'some',
    u'hasn',
    u"hasn't",
    u'are',
    u'our',
    u'ourselves',
    u'out',
    u'what',
    u'for',
    u"needn't",
    u'below',
    u're',
    u'does',
    u"shouldn't",
    u'above',
    u'between',
    u'mustn',
    u't',
    u'be',
    u'we',
    u'who',
    u"mightn't",
    u"doesn't",
    u'were',
    u'here',
    u'shouldn',
    u'hers',
    u"aren't",
    u'by',
    u'on',
    u'about',
    u'couldn',
    u'of',
    u"wouldn't",
    u'against',
    u's',
    u'isn',
    u'or',
    u'own',
    u'into',
    u'yourself',
    u'down',
    u"hadn't",
    u'mightn',
    u"couldn't",
    u'wasn',
    u'your',
    u"you're",
    u'from',
    u'her',
    u'their',
    u'aren',
    u"it's",
    u'there',
    u'been',
    u'whom',
    u'too',
    u'wouldn',
    u'themselves',
    u'weren',
    u'was',
    u'until',
    u'more',
    u'himself',
    u'that',
    u"didn't",
    u'but',
    u"that'll",
    u'with',
    u'than',
    u'those',
    u'he',
    u'me',
    u'myself',
    u'ma',
    u"weren't",
    u'these',
    u'up',
    u'will',
    u'while',
    u'ain',
    u'can',
    u'theirs',
    u'my',
    u'and',
    u've',
    u'then',
    u'is',
    u'am',
    u'it',
    u'doesn',
    u'an',
    u'as',
    u'itself',
    u'at',
    u'have',
    u'in',
    u'any',
    u'if',
    u'again',
    u'no',
    u'when',
    u'same',
    u'how',
    u'other',
    u'which',
    u'you',
    u"shan't",
    u'shan',
    u'needn',
    u'haven',
    u'after',
    u'most',
    u'such',
    u'why',
    u'a',
    u'off',
    u'i',
    u'm',
    u'yours',
    u"you'll",
    u'so',
    u'y',
    u"she's",
    u'the',
    u'having',
    u'once',
    ])
