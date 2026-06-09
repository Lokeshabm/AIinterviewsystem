from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from interview.models import Interview, Question


class Command(BaseCommand):
    help = 'Import generated questions from JSON file into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to questions.json file (e.g., output/questions.json)'
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            default=False,
            help='Skip questions that already exist by statement text'
        )

    def handle(self, *args, **options):
        json_file = options.get('json_file')
        skip_dups = options.get('skip_duplicates')

        json_path = Path(json_file)
        if not json_path.exists():
            raise CommandError(f'File not found: {json_path}')

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON: {exc}')

        if not isinstance(questions_data, list):
            raise CommandError('Expected JSON file to contain a list of questions.')

        # Get or create "Question Bank" Interview (parent container for imported questions)
        admin_user, _ = User.objects.get_or_create(
            username='question_bank_admin',
            defaults={'email': 'admin@questionbank.local'}
        )
        question_bank, _ = Interview.objects.get_or_create(
            user=admin_user,
            role='Question Bank',
            defaults={'date': datetime.now()}
        )
        self.stdout.write(
            self.style.SUCCESS(f'Using Interview: {question_bank} (ID: {question_bank.id})')
        )

        created = 0
        skipped = 0
        errors = 0

        for idx, q_data in enumerate(questions_data, start=1):
            try:
                statement = q_data.get('statement', '').strip()
                if not statement:
                    errors += 1
                    continue

                # Check for duplicates by statement text
                if skip_dups and Question.objects.filter(text=statement).exists():
                    self.stdout.write(
                        self.style.WARNING(f'[{idx}] Skipping duplicate: {statement[:60]}...')
                    )
                    skipped += 1
                    continue

                # Create Question object attached to question bank
                q_obj = Question.objects.create(
                    interview=question_bank,
                    text=statement,
                    category='technical',  # default category
                )
                created += 1

                self.stdout.write(
                    self.style.SUCCESS(f'[{idx}] Created question: {statement[:60]}...')
                )
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f'[{idx}] Error importing question: {exc}')
                )
                errors += 1

        summary = f'\nImport complete: {created} created, {skipped} skipped, {errors} errors'
        if errors == 0:
            self.stdout.write(self.style.SUCCESS(summary))
        else:
            self.stdout.write(self.style.WARNING(summary))
