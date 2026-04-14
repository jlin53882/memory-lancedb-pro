#!/usr/bin/env python3
import subprocess
import sys

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

r = subprocess.run(
    [sys.executable, "-m", "pytest", "-q",
     "--ignore=tests/test_ftb_pipeline_smoke.py",
     "--ignore=tests/test_ftb_translator.py",
     "--ignore=tests/test_ftb_translator_clean.py",
     "--ignore=tests/test_ftb_translator_export.py",
     "--ignore=tests/test_ftbquests_snbt_extractor.py",
     "--ignore=tests/test_ftbquests_snbt_inject.py",
     "--ignore=tests/test_qc_services_facade.py",
     "--ignore=tests/test_qc_view_characterization.py",
     "--ignore=tests/test_untranslated_checker.py",
     "--ignore=tests/test_variant_comparator_tsv.py"],
    cwd=proj, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(r.stdout)
if r.stderr:
    print('STDERR:', r.stderr[-2000:])
print('Return code:', r.returncode)
