from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Run the project-local question_generator to produce question sets.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of questions to generate')
        parser.add_argument('--outdir', type=str, default='question_generator/output', help='Output directory for generated files')

    def handle(self, *args, **options):
        count = options.get('count')
        outdir = options.get('outdir')

        project_root = Path(__file__).resolve().parents[3]
        generator_py = project_root / 'question_generator' / 'generator.py'

        if not generator_py.exists():
            raise CommandError(f'question_generator not found at {generator_py}')

        # Ensure output directory exists (relative to project root when a relative path is provided)
        outdir_path = Path(outdir)
        if not outdir_path.is_absolute():
            outdir_path = project_root / outdir_path
        outdir_path.mkdir(parents=True, exist_ok=True)

        cmd = [sys.executable, str(generator_py), '--count', str(count), '--outdir', str(outdir_path)]

        self.stdout.write(self.style.NOTICE(f'Running question generator: {cmd}'))
        try:
            result = subprocess.run(cmd, cwd=str(generator_py.parent), capture_output=True, text=True, check=True)
            if result.stdout:
                self.stdout.write(result.stdout)
            if result.stderr:
                self.stderr.write(result.stderr)
            self.stdout.write(self.style.SUCCESS(f'Generated questions in {outdir_path}'))
        except subprocess.CalledProcessError as exc:
            raise CommandError(f'Generator failed: {exc}\n{exc.stdout}\n{exc.stderr}')
