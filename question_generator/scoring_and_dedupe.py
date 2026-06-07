import hashlib
import re
from typing import Dict, List

DIFFICULTY_MAP = {
    'Easy': 1.0,
    'Medium': 2.0,
    'Hard': 3.0,
    'Expert': 4.0,
}


def normalize_statement(statement: str) -> str:
    text = ' '.join(statement.split()).lower()
    return text


def canonical_hash(statement: str) -> str:
    normalized = normalize_statement(statement)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def compute_difficulty_score(base_difficulty: str, qtype: str, features: Dict[str, bool]) -> float:
    score = DIFFICULTY_MAP.get(base_difficulty, 2.0)
    type_adjust = {
        'MCQ': 0.3,
        'TF': -0.5,
        'NUM': 0.5,
        'CODE': 1.0,
        'SA': 0.8,
        'LA': 1.0,
        'CASE': 1.2,
    }
    score += type_adjust.get(qtype, 0.0)
    if features.get('multi_step'):
        score += 0.5
    if features.get('numeric_derivation'):
        score += 0.5
    if features.get('application_focus'):
        score += 0.3
    if features.get('theoretical'):
        score += 0.2
    return max(1.0, min(score, 4.5))


def difficulty_bin(score: float) -> str:
    if score < 1.75:
        return 'Easy'
    if score < 2.5:
        return 'Medium'
    if score < 3.5:
        return 'Hard'
    return 'Expert'


def extract_tags(statement: str, keywords: List[str]) -> List[str]:
    tags = []
    lower = statement.lower()
    for keyword in keywords:
        if keyword.lower() in lower:
            tags.append(keyword.lower().replace(' ', '-'))
    return list(dict.fromkeys(tags))


def is_duplicate(candidate_hash: str, existing_hashes: set) -> bool:
    return candidate_hash in existing_hashes


def quality_score(correct_rate: float, avg_time: float, difficulty: float) -> float:
    score = difficulty * 0.4 + correct_rate * 0.4 - avg_time * 0.2
    return max(0.0, min(score, 10.0))
