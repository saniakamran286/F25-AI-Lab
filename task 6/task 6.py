import re
import math
import csv
import time
from collections import Counter

# ---------------------------------------------------------------
# Data used in the lab
# ---------------------------------------------------------------
DOCS = {
    'D1': "Examination Rules. Students must arrive thirty minutes before the paper starts and carry their university card. Mobile phones, smart watches and notes are not allowed inside the hall. A student who is late by more than fifteen minutes will not be admitted. Anyone caught copying will receive a zero in that paper and a report will be sent to the disciplinary committee. Students who fall sick during the exam may leave only with the written permission of the invigilator. Result cards are issued within three weeks after the last paper.",
    'D2': "Hostel Policy. Residents must return before ten at night because the gate is locked after that time. Visitors are allowed only in the common room between four and six in the afternoon. Cooking in rooms is not permitted because of fire safety rules. The monthly fee must be paid before the fifth day of each month and a fine of five hundred rupees is added for late payment. Students who want to leave the hostel for good must inform the warden two weeks earlier. Damage to furniture is charged to the room occupants.",
    'D3': "Transport Service. University buses run on six routes from seven in the morning until five in the evening. Every student needs a bus card that must be renewed each semester. Dr. Imran manages the transport office and keeps a record of every complaint. Passengers should show the card to the conductor when boarding. A lost card can be replaced after paying a replacement fee of three hundred rupees. Buses do not run on public holidays or during the summer break unless the office announces a special schedule.",
    'D4': "Scholarship Rules. Students with a semester GPA of at least three point five can apply for the merit scholarship. The application form must reach the finance office before the first week of the semester ends. A family income certificate is required for the need based scholarship. Scholarship holders must keep seventy five percent attendance or the award is cancelled. The committee announces the selected names on the notice board and the university website. Students may apply again every semester.",
    'D5': "Library Services. The library lends three books to each student for fourteen days. A book can be renewed once if no other student has reserved it. A late fine of ten rupees is charged for each day after the due date. Reference books and past papers cannot leave the reading hall. Silence must be kept in all study areas. Group discussion rooms can be booked online for up to two hours. Lost books must be replaced by the borrower or paid for at the current price.",
}

FAQS = [
    ('How do I reset my password?', 'Open the portal and use the Forgot Password link.', 'portal_help.txt'),
    ('Where can I find my timetable?', 'The timetable is posted in the student portal under Academics.', 'portal_help.txt'),
    ('How do I apply for a transcript?', 'Submit the transcript form at the registrar office.', 'registrar.txt'),
    ('When does the library open?', 'The library opens at 8 am on all working days.', 'library.txt'),
    ('How can I contact the help desk?', 'Write to the help desk email or visit the IT room.', 'portal_help.txt'),
]

# question, document that holds the answer, exact evidence phrase
ANSWERABLE = [
    ('When must students reach the exam hall?', 'D1', 'arrive thirty minutes before the paper starts'),
    ('At what time is the hostel gate locked?', 'D2', 'before ten at night'),
    ('What is the fine for paying the hostel fee late?', 'D2', 'five hundred rupees'),
    ('How many books can a student borrow?', 'D5', 'three books'),
    ('What penalty applies for cheating in a paper?', 'D1', 'zero in that paper'),
    ('What is the charge for replacing a lost bus card?', 'D3', 'three hundred rupees'),
    ('Which GPA is needed for the merit scholarship?', 'D4', 'three point five'),
    ('How much is charged every day for a late book?', 'D5', 'ten rupees'),
]
UNANSWERABLE = ["What is tomorrow's weather forecast?", 'Who won the cricket match?']
EVIDENCE = {'D1': 'arrive thirty minutes before the paper starts', 'D2': 'before ten at night',
            'D3': 'three hundred rupees', 'D4': 'three point five', 'D5': 'three books'}


# ---------------------------------------------------------------
# TF-IDF helpers
# ---------------------------------------------------------------
def words_of(text):
    return re.findall(r'\w+', text.lower())


class TfidfIndex:
    def __init__(self, texts):
        self.rows = [words_of(t) for t in texts]
        counts = Counter()
        for row in self.rows:
            counts.update(set(row))
        n = len(texts)
        self.idf = {w: math.log((1 + n) / (1 + c)) + 1 for w, c in counts.items()}
        self.vectors = [self.vectorize(row) for row in self.rows]

    def vectorize(self, row):
        tf = Counter(row)
        vec = {w: tf[w] * self.idf[w] for w in tf if w in self.idf}
        size = math.sqrt(sum(v * v for v in vec.values()))
        return {w: v / size for w, v in vec.items()} if size else {}

    def scores(self, query):
        q = self.vectorize(words_of(query))
        return [sum(v * q.get(w, 0) for w, v in vec.items()) for vec in self.vectors]

    def top(self, query, k=3):
        s = self.scores(query)
        order = sorted(range(len(s)), key=lambda i: -s[i])
        return [(s[i], i) for i in order[:k]]


# ---------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------
def window_chunks(text, size=40, overlap=0):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError('Require size > 0 and 0 <= overlap < size')
    words = text.split()
    step = size - overlap
    result = []
    for start in range(0, len(words), step):
        part = words[start:start + size]
        result.append((start, start + len(part), ' '.join(part)))
        if start + size >= len(words):
            break
    return result


def split_sentences(text):
    text = text.strip()
    return re.split(r'(?<=[.!?])\s+', text) if text else []


def sentence_chunks(text, limit=40):
    result, current, begin, seen = [], [], 0, 0
    for sentence in split_sentences(text):
        words = sentence.split()
        if len(words) > limit:
            if current:
                result.append((begin, seen, ' '.join(current)))
                current = []
            for s, e, t in window_chunks(sentence, limit, 0):
                result.append((seen + s, seen + e, t))
            seen += len(words)
            begin = seen
            continue
        if current and len(current) + len(words) > limit:
            result.append((begin, seen, ' '.join(current)))
            current = []
            begin = seen
        current += words
        seen += len(words)
    if current:
        result.append((begin, seen, ' '.join(current)))
    return result


def build_corpus(strategy):
    corpus = []
    for doc_id, text in DOCS.items():
        if strategy == 'sentence':
            parts = sentence_chunks(text)
        else:
            parts = window_chunks(text, 40, int(strategy))
        for number, (s, e, t) in enumerate(parts):
            first = max(text.find(t), 0)
            corpus.append({'id': doc_id + ':' + str(number), 'doc': doc_id, 'start': s, 'end': e,
                           'text': t, 'chars': (first, first + len(t))})
    return corpus


def repeated_words(corpus):
    total = 0
    for a, b in zip(corpus, corpus[1:]):
        if a['doc'] == b['doc']:
            total += max(0, a['end'] - b['start'])
    return total


# ---------------------------------------------------------------
# TASK 1
# ---------------------------------------------------------------
def task1():
    samples = ['Hello, world!', "She can't come.", 'info@campus.edu', 'CS-601', '',
               'یہ ایک جملہ ہے', 'v2.5 build 4412X']
    for text in samples:
        plain = text.split()
        regex = re.findall(r'\w+', text)
        print('Original:', repr(text))
        print('Whitespace:', plain, len(plain))
        print('Word-like :', regex, len(regex))
    try:
        import tiktoken
        print('Model tokenizer found:', tiktoken.__name__)
    except ImportError:
        print('Model tokenizer not available on this computer')


def faq_bot(question):
    question = question.strip()
    if not question:
        return ['Please enter a question.']
    for q, answer, source in FAQS:
        if q.lower() == question.lower():
            return [answer + ' [source: ' + source + ']']
    index = TfidfIndex([q for q, a, s in FAQS])
    found = [(s, i) for s, i in index.top(question, 2) if s > 0.2]
    if not found:
        return ['No matching FAQ. Please contact the help desk.']
    lines = ['Possible matches; choose or rephrase your question:']
    for score, i in found:
        lines.append(FAQS[i][0] + ' (similarity ' + format(score, '.3f') + ')')
    return lines


def task1_bot():
    for question in ['How do I reset my password?', 'When does the library open?',
                     'password reset help', '', 'volcano geology']:
        print('You:', question)
        for number, line in enumerate(faq_bot(question)):
            print('Bot:' if number == 0 else '   ', line)


# ---------------------------------------------------------------
# TASK 2
# ---------------------------------------------------------------
def task2():
    for doc_id, text in DOCS.items():
        print(doc_id, 'words:', len(text.split()))
    print('Edge case tests:')
    print('empty text ->', window_chunks(''))
    print('short text ->', [(s, e) for s, e, t in window_chunks('one two three four five six seven eight nine ten')])
    try:
        window_chunks('some words here', 5, 5)
    except ValueError as error:
        print('invalid overlap -> ValueError:', error)
    long_sentence = ' '.join(['word'] * 95) + '.'
    print('95 word sentence ->', len(sentence_chunks(long_sentence)), 'chunks, sizes',
          [e - s for s, e, t in sentence_chunks(long_sentence)])
    parts = split_sentences('Dr. Imran keeps a record of every complaint.')
    print('abbreviation split:', repr(parts[0]), '|', repr(parts[1][:20]))

    print('Comparison (40 word budget):')
    for strategy in ['0', '10', 'sentence']:
        corpus = build_corpus(strategy)
        sizes = [c['end'] - c['start'] for c in corpus]
        whole = 0
        for doc_id, phrase in EVIDENCE.items():
            if any(phrase in c['text'].lower() for c in corpus if c['doc'] == doc_id):
                whole += 1
        print('strategy', strategy, '| chunks:', len(corpus), '| avg words:', round(sum(sizes) / len(sizes), 1),
              '| max words:', max(sizes), '| repeated words:', repeated_words(corpus),
              '| evidence kept whole:', whole, 'of 5')

    print('Semantic suggestions (sentence chunks):')
    corpus = build_corpus('sentence')
    index = TfidfIndex([c['text'] for c in corpus])
    for query in ['What should I carry to an exam?', 'How late can I pay the hostel fee?',
                  'Can a bus card be replaced?']:
        score, i = index.top(query, 1)[0]
        print('tfidf |', query, '->', corpus[i]['id'], format(score, '.3f'))
    try:
        from sentence_transformers import SentenceTransformer
        print('embedding: model loaded')
    except ImportError:
        print('embedding: not run (sentence-transformers model not available)')


# ---------------------------------------------------------------
# TASK 3
# ---------------------------------------------------------------
def evaluate(corpus, index, items):
    hits, total_rr = 0, 0
    failed = []
    for question, doc_id, phrase in items:
        top = index.top(question, 3)
        rank = None
        for place, (score, i) in enumerate(top, 1):
            if phrase in corpus[i]['text'].lower():
                rank = place
                break
        if rank:
            hits += 1
            total_rr += 1 / rank
        else:
            failed.append((question, corpus[top[0][1]], top[0][0]))
    return hits / len(items), total_rr / len(items), failed


def task3():
    dev, test = ANSWERABLE[:4], ANSWERABLE[4:]
    results = {}
    log = open('retrieval_log.csv', 'w', newline='', encoding='utf8')
    writer = csv.writer(log)
    writer.writerow(['strategy', 'split', 'question', 'rank', 'chunk_id', 'score', 'start_char', 'end_char'])
    print('Token audit: not run (model not available)')
    for strategy in ['0', '10', 'sentence']:
        started = time.time()
        corpus = build_corpus(strategy)
        index = TfidfIndex([c['text'] for c in corpus])
        d = evaluate(corpus, index, dev)
        t = evaluate(corpus, index, test)
        seconds = round(time.time() - started, 4)
        results[strategy] = (d, t, corpus, index)
        print('Strategy', strategy, '| tfidf | chunks:', len(corpus), '| time:', seconds, 's')
        print('dev  Hit@3 =', round(d[0], 3), ' MRR@3 =', round(d[1], 3))
        print('test Hit@3 =', round(t[0], 3), ' MRR@3 =', round(t[1], 3))
        for name, items in (('dev', dev), ('test', test)):
            for question, doc_id, phrase in items:
                for place, (score, i) in enumerate(index.top(question, 3), 1):
                    c = corpus[i]
                    writer.writerow([strategy, name, question, place, c['id'], round(score, 3), *c['chars']])
    log.close()
    print('Log saved to retrieval_log.csv')

    best = None
    for strategy in ['0', '10', 'sentence']:
        if best is None or results[strategy][0][1] > results[best][0][1]:
            best = strategy
    d, t, corpus, index = results[best]
    print('Selected on dev MRR:', (best, 'tfidf'), '| dev:', (round(d[0], 3), round(d[1], 3)),
          '| held-out test:', (round(t[0], 3), round(t[1], 3)))
    print('Failed answerable queries for selected setting:')
    if not d[2] + t[2]:
        print('none')
    for question, chunk, score in d[2] + t[2]:
        print(question, '| top chunk:', chunk['id'], '| score:', round(score, 3))
        print('top text:', chunk['text'][:80])
    print('Unanswerable queries (top result still returned if score > 0):')
    for question in UNANSWERABLE:
        score, i = index.top(question, 1)[0]
        print(question, '->', corpus[i]['id'], 'score:', round(score, 3))

    return corpus, index


def document_bot(question, corpus, index, choice=None):
    print('Question:', question)
    if not question.strip():
        print('Please enter a question.')
        return
    top = index.top(question, 3)
    print('Candidate evidence; relevance must be checked:')
    for number, (score, i) in enumerate(top, 1):
        c = corpus[i]
        print(number, c['id'], 'score=' + format(score, '.3f'), 'characters', str(c['chars'][0]) + '-' + str(c['chars'][1]))
    if choice:
        print('User chooses', choice)
        c = corpus[top[choice - 1][1]]
        print('Retrieved passage:', c['text'])
        print('Source:', c['doc'], 'characters', c['chars'][0], c['chars'][1])


def main():
    print('=== TASK 1: TOKENS ===')
    task1()
    print('=== TASK 1: FAQ CHATBOT ===')
    task1_bot()
    print('=== TASK 2 ===')
    task2()
    print('=== TASK 3: EVALUATION ===')
    corpus, index = task3()
    print('=== TASK 3: DOCUMENT CHATBOT ===')
    document_bot('What is the fine for late hostel payment?', corpus, index, 1)
    document_bot('', corpus, index)
    document_bot('Who won the cricket match?', corpus, index)


main()
