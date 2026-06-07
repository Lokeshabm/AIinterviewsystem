"""
Bulk template expansion and generator runner.
Creates parameterized templates across branches and generates many questions.
Run from repo root with venv:

    d:/Desktop/interveiw/.venv/Scripts/python.exe question_generator/bulk_generate.py --count 10000 --outdir question_generator/output_big

"""
import json
import os
import random
import argparse
from uuid import uuid4

BRANCHES = [
    'CSE','ISE','AIML','Data Science','Cyber Security','ECE','EEE','Mechanical','Civil','Chemical','Aerospace','Biotechnology','Industrial','Mechatronics','Robotics','Automobile','Environmental'
]
QTYPES = ['MCQ','TF','NUM','SA','LA','CODE']
SUBJECTS_SAMPLE = {
    'CSE': ['Data Structures','Algorithms','Operating Systems','Databases','Computer Networks'],
    'ECE': ['Circuits','Signals','Digital Design','Communication Systems'],
    'Mechanical': ['Thermodynamics','Mechanics','Fluid Mechanics']
}

# Simple template generators per qtype

def make_template(tid, branch, subject, topic, qtype, difficulty):
    base = {
        'id': tid,
        'branch': branch,
        'subject': subject,
        'topic': topic,
        'qtype': qtype,
        'difficulty': difficulty,
        'params': {}
    }
    if qtype == 'MCQ':
        base['statement_template'] = f'In {topic}, what is the main purpose of {{concept}}?'
        base['params'] = {'concept': {'type': 'choice', 'choices': ['stack','queue','graph','tree','hash table']}}
        base['option_strategy'] = 'concept_options'
    elif qtype == 'TF':
        base['statement_template'] = f'{topic} typically requires understanding of {{concept}}.'
        base['params'] = {'concept': {'type': 'choice', 'choices': ['recursion','concurrency','synchronization','encryption']}}
    elif qtype == 'NUM':
        base['statement_template'] = f'Given values a={{a}} and b={{b}} in {topic}, compute result of a+b.'
        base['params'] = {'a':{'type':'int','min':1,'max':100}, 'b':{'type':'int','min':1,'max':100}}
    elif qtype == 'CODE':
        base['statement_template'] = f'Write a function to solve {{problem}} in {topic}.'
        base['params'] = {'problem':{'type':'choice','choices':['reverse string','binary search','flood fill']}}
    else:
        base['statement_template'] = f'Explain the concept of {{concept}} in {topic}.'
        base['params'] = {'concept':{'type':'choice','choices':['principle','trade-off','method']}}
    return base


def expand_templates(num_templates=200):
    templates = []
    tid = 1
    for branch in BRANCHES:
        subjects = SUBJECTS_SAMPLE.get(branch, [f'{branch} Fundamentals', f'{branch} Applications'])
        for subject in subjects:
            for topic_idx in range(2):
                topic = f'{subject} - Topic {topic_idx+1}'
                for qtype in QTYPES:
                    difficulty = random.choice(['Easy','Medium','Hard','Expert'])
                    templates.append(make_template(f'tpl_{tid:05d}', branch, subject, topic, qtype, difficulty))
                    tid += 1
                    if tid > num_templates:
                        return templates
    return templates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10000)
    parser.add_argument('--outdir', type=str, default='output_big')
    parser.add_argument('--templates', type=int, default=300)
    args = parser.parse_args()

    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, args.outdir), exist_ok=True)

    templates = expand_templates(args.templates)
    templates_path = os.path.join(here, 'templates.generated.json')
    with open(templates_path, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2)

    # Import generator functions by reading generator.py utilities
    from generator import build_question_from_template, canonicalize_text, sha256_text, export_json, export_csv, export_sql, export_mongo

    dedupe = set()
    questions = []
    i = 0
    trials = 0
    max_trials = args.count * 20
    while i < args.count and trials < max_trials:
        trials += 1
        tpl = random.choice(templates)
        q = build_question_from_template(tpl)
        if q['canonical_hash'] in dedupe:
            continue
        dedupe.add(q['canonical_hash'])
        questions.append(q)
        i += 1

    outdir = os.path.join(here, args.outdir)
    export_json(questions, os.path.join(outdir, 'questions.json'))
    export_csv(questions, os.path.join(outdir, 'questions.csv'))
    export_sql(questions, os.path.join(outdir, 'questions.sql'))
    export_mongo(questions, os.path.join(outdir, 'questions.mongo.json'))

    print(f'Generated {len(questions)} questions in {outdir}')

if __name__ == '__main__':
    main()
