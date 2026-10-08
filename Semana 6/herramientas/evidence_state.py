import os
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from news.models import Article

Article.objects.update(is_published=sys.argv[1] == 'restore')
print('Publication state updated for evidence capture.')
