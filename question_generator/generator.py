import argparse
import json
import os
import random
import csv
import uuid
import hashlib
from datetime import datetime

# Minimal reference generator
# Usage: python generator.py --count 100 --outdir ./output


def canonicalize_text(text):
    # normalize whitespace and lowercase; preserve numeric and keyword variation for uniqueness
    t = " ".join(text.split())
    return t.strip().lower()


def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_mcq_options(strategy, params=None):
    params = params or {}
    if strategy == 'logn_options':
        opts = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)']
        correct = 'O(log n)'
        random.shuffle(opts)
        return opts, correct

    if strategy == 'concept_options' and params:
        concept = params.get('concept', '').lower()
        return generate_concept_options(concept)

    if strategy == 'numeric_addition' and params:
        a = params.get('a', 1)
        b = params.get('b', 2)
        return generate_numeric_options(a, b)

    if strategy == 'formula_options' and params:
        return generate_formula_options(params)

    if params and 'concept' in params:
        return generate_concept_options(params.get('concept', '').lower())

    # fallback options: use generic distractors based on correct value when available
    if correct_value:
        return generate_fallback_mcq_options(correct_value)

    return (['A', 'B', 'C', 'D'], 'A')


def generate_concept_options(concept):
    mapping = {
        'stack': {
            'correct': 'Store elements and remove them in LIFO order.',
            'distractors': [
                'Store elements and remove them in FIFO order.',
                'Store key-value pairs for fast lookup.',
                'Organize nodes in a hierarchical structure.'
            ]
        },
        'queue': {
            'correct': 'Store elements and remove them in FIFO order.',
            'distractors': [
                'Store elements and remove them in LIFO order.',
                'Store key-value pairs for fast lookup.',
                'Organize nodes in a hierarchical structure.'
            ]
        },
        'graph': {
            'correct': 'Represent objects and the relationships between them using nodes and edges.',
            'distractors': [
                'Store a sequence of values in contiguous memory.',
                'Sort data in ascending or descending order.',
                'Encode hierarchical parent-child relationships.'
            ]
        },
        'tree': {
            'correct': 'Represent hierarchical relationships between parent and child nodes.',
            'distractors': [
                'Store unordered key-value associations.',
                'Manage a list of items in insertion order.',
                'Perform breadth-first traversal only.'
            ]
        },
        'hash table': {
            'correct': 'Map keys to values using a hash function for fast access.',
            'distractors': [
                'Store items in a fixed-size sorted array.',
                'Represent hierarchical relationships between nodes.',
                'Manage element removal in LIFO order.'
            ]
        }
    }
    default = {
        'correct': 'Represent a core computer science concept accurately.',
        'distractors': [
            'Describe an unrelated concept.',
            'Define a different data structure.',
            'Provide an irrelevant algorithm detail.'
        ]
    }
    choice = mapping.get(concept, default)
    opts = [choice['correct']] + choice['distractors']
    random.shuffle(opts)
    return opts, choice['correct']


def generate_numeric_options(a, b):
    correct = str(a + b)
    distractors = [str(a + b + 1), str(abs(a - b)), str(a * b)]
    opts = [correct] + distractors
    random.shuffle(opts)
    return opts, correct


def generate_formula_options(params):
    # This is a placeholder for formula-based MCQ generation
    # If the statement includes resistors or simple formulas, infer plausible distractors.
    if 'r1' in params and 'r2' in params:
        a = params.get('r1', 1)
        b = params.get('r2', 1)
        correct = str(a + b)
        distractors = [str(a + b + 2), str(a + b - 1 if a + b > 1 else 1), str(a * b)]
        opts = [correct] + distractors
        random.shuffle(opts)
        return opts, correct
    return (['A', 'B', 'C', 'D'], 'A')


def generate_fallback_mcq_options(correct_value):
    opts = [correct_value, 'Option B', 'Option C', 'Option D']
    random.shuffle(opts)
    return opts, correct_value


def render_template(tpl, params):
    stmt = tpl['statement_template']
    return stmt.format(**params)


def sample_params(param_spec):
    params = {}
    for name, spec in param_spec.items():
        ptype = spec.get('type')
        if ptype == 'int':
            params[name] = random.randint(spec['min'], spec['max'])
        elif ptype == 'float':
            params[name] = round(random.uniform(spec['min'], spec['max']), 2)
        elif ptype == 'choice':
            choices = spec.get('choices', [])
            if choices:
                params[name] = random.choice(choices)
            else:
                params[name] = spec.get('default')
        else:
            params[name] = spec.get('default')
    return params


def build_question_from_template(tpl):
    params = sample_params(tpl.get('params', {}))
    statement = render_template(tpl, params)
    q_uid = str(uuid.uuid4())
    q = {
        'question_uid': q_uid,
        'branch': tpl.get('branch'),
        'subject': tpl.get('subject'),
        'topic': tpl.get('topic'),
        'qtype': tpl.get('qtype'),
        'difficulty': tpl.get('difficulty'),
        'statement': statement,
        'params': params,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'template_id': tpl.get('id')
    }
    if tpl['qtype'] == 'MCQ':
        opts, correct = generate_mcq_options(tpl.get('option_strategy'))
        q['options'] = [{'label': chr(65+i), 'text': o} for i, o in enumerate(opts[:4])]
        q['correct_answer'] = correct
        q['explanation'] = 'Standard complexity; balanced tree yields O(log n) average.'
        q['marks'] = 2
        q['estimated_time'] = 5
    elif tpl['qtype'] == 'TF':
        q['options'] = ['True', 'False']
        q['correct_answer'] = 'True'
        q['explanation'] = 'Binary search has logarithmic time complexity.'
        q['marks'] = 1
        q['estimated_time'] = 1
    elif tpl['qtype'] == 'NUM':
        r1 = params.get('r1', 10)
        r2 = params.get('r2', 10)
        total = r1 + r2
        q['correct_answer'] = str(total)
        q['explanation'] = f'Total resistance in series is R1+R2 = {r1}+{r2} = {total} ohms.'
        q['marks'] = 3
        q['estimated_time'] = 7
    else:
        q['correct_answer'] = None
        q['explanation'] = ''
        q['marks'] = 1
        q['estimated_time'] = 3

    # canonical hash
    canon = canonicalize_text(q['statement'])
    q['canonical_text'] = canon
    q['canonical_hash'] = sha256_text(canon)
    return q


def export_json(questions, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def export_csv(questions, path):
    fieldnames = ['question_uid','branch','subject','topic','qtype','difficulty','statement','option_A','option_B','option_C','option_D','correct_answer','explanation','tags','estimated_time','marks']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for q in questions:
            row = {k: '' for k in fieldnames}
            row['question_uid'] = q['question_uid']
            row['branch'] = q.get('branch')
            row['subject'] = q.get('subject')
            row['topic'] = q.get('topic')
            row['qtype'] = q.get('qtype')
            row['difficulty'] = q.get('difficulty')
            row['statement'] = q.get('statement')
            if q.get('options') and isinstance(q['options'], list):
                for i, opt in enumerate(q['options'][:4]):
                    row[f'option_{chr(65+i)}'] = opt['text'] if isinstance(opt, dict) else opt
            row['correct_answer'] = q.get('correct_answer')
            row['explanation'] = q.get('explanation')
            row['tags'] = ';'.join(q.get('tags', []))
            row['estimated_time'] = q.get('estimated_time')
            row['marks'] = q.get('marks')
            writer.writerow(row)


def export_sql(questions, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('-- Sample INSERTs for questions table and mcq_options\n')
        for q in questions:
            stmt = q['statement'].replace("'", "''")
            uid = q['question_uid']
            f.write("INSERT INTO questions (question_uid, branch, subject, topic, qtype, difficulty, statement, canonical_hash, estimated_time, marks, approved, created_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}',{},{} ,true,'{}');\n".format(
                uid, q.get('branch',''), q.get('subject',''), q.get('topic',''), q.get('qtype',''), q.get('difficulty',''), stmt, q.get('canonical_hash',''), q.get('estimated_time',0), q.get('marks',1), q.get('created_at')
            ))
            if q.get('options') and isinstance(q['options'], list):
                f.write('-- options for last question\n')
                for opt in q['options']:
                    opt_text = opt['text'] if isinstance(opt, dict) else opt
                    label = opt['label'] if isinstance(opt, dict) and 'label' in opt else ''
                    is_correct = 'true' if opt_text == q.get('correct_answer') else 'false'
                    opt_text = opt_text.replace("'","''")
                    f.write("INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('{}','{}','{}',{});\n".format(uid, label, opt_text, is_correct))


def export_mongo(questions, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--outdir', type=str, default='./output')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    templates = json.load(open('templates.json', 'r', encoding='utf-8'))

    dedupe = set()
    questions = []
    i = 0
    trials = 0
    while i < args.count and trials < args.count * 10:
        trials += 1
        tpl = random.choice(templates)
        q = build_question_from_template(tpl)
        if q['canonical_hash'] in dedupe:
            continue
        dedupe.add(q['canonical_hash'])
        questions.append(q)
        i += 1

    export_json(questions, os.path.join(args.outdir, 'questions.json'))
    export_csv(questions, os.path.join(args.outdir, 'questions.csv'))
    export_sql(questions, os.path.join(args.outdir, 'questions.sql'))
    export_mongo(questions, os.path.join(args.outdir, 'questions.mongo.json'))

    print(f'Generated {len(questions)} questions in {args.outdir}')


if __name__ == '__main__':
    main()
