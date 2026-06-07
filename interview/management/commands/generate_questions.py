import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from question_generator.generator import build_question_from_template, export_json, export_csv, export_sql
except ImportError:
    build_question_from_template = None
    export_json = None
    export_csv = None
    export_sql = None


def load_question_templates():
    template_path = Path(settings.BASE_DIR) / 'question_generator' / 'templates.json'
    if not template_path.exists():
        raise FileNotFoundError(f'Could not find question templates at {template_path}')
    with template_path.open('r', encoding='utf-8') as f:
        return json.load(f)


class Command(BaseCommand):
    help = 'Generate questions using question_generator templates and export them to a file.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of questions to generate.')
        parser.add_argument('--outdir', type=str, default='question_generator/output_django', help='Output directory for generated files.')
        parser.add_argument('--format', choices=['json', 'csv', 'sql'], default='json', help='Export format.')
        parser.add_argument('--role', type=str, default='', help='Optional role keyword to prioritize template selection.')

    def handle(self, *args, **options):
        if build_question_from_template is None:
            raise RuntimeError('question_generator.generator is not available. Ensure question_generator is importable.')

        count = options['count']
        outdir = Path(settings.BASE_DIR) / options['outdir']
        outdir.mkdir(parents=True, exist_ok=True)
        fmt = options['format']
        role = options['role'].strip().lower()

        templates = load_question_templates()
        if not templates:
            raise RuntimeError('No question templates were loaded.')

        if role:
            templates = [tpl for tpl in templates if role in tpl.get('branch', '').lower() or role in tpl.get('subject', '').lower() or role in tpl.get('topic', '').lower()]
        if not templates:
            templates = load_question_templates()

        questions = []
        for i, tpl in enumerate(templates):
            if len(questions) >= count:
                break
            questions.append(build_question_from_template(tpl))

        outpath = outdir / f'generated_questions.{fmt}'
        if fmt == 'json':
            if export_json is None:
                raise RuntimeError('JSON exporter is not available.')
            export_json(questions, outpath)
        elif fmt == 'csv':
            if export_csv is None:
                raise RuntimeError('CSV exporter is not available.')
            export_csv(questions, outpath)
        elif fmt == 'sql':
            if export_sql is None:
                raise RuntimeError('SQL exporter is not available.')
            export_sql(questions, outpath)

        self.stdout.write(self.style.SUCCESS(f'Generated {len(questions)} questions to {outpath}'))
