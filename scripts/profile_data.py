"""Shared, dependency-free validation for the profile's source data."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / 'data/profile.json'
REPOSITORIES_PATH = ROOT / 'data/repositories.json'


def load_data(root=ROOT):
    root = Path(root)
    profile = json.loads((root / 'data/profile.json').read_text())
    document = json.loads((root / 'data/repositories.json').read_text())
    validate(profile, document['repositories'], root)
    return profile, document['repositories']


def category_for(repo, profile):
    categories = {c['key']: c for c in profile['categories']}
    prefixes = [c['prefix'] for c in categories.values() if c['prefix']]
    name = repo['name']
    if not repo['private']:
        if any(name.startswith(prefix) for prefix in prefixes):
            raise ValueError(f'{name}: public repositories must not use a private prefix')
        return 'public'
    override = repo.get('category_override')
    if name in profile.get('protected_repository_names', []) and override in categories and override != 'public':
        return override
    for category in categories.values():
        prefix = category['prefix']
        if prefix and name.startswith(prefix):
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
                raise ValueError(f'{name}: private names must use lowercase kebab-case')
            return category['key']
    raise ValueError(f'{name}: private repository needs an approved proj-/lab-/study-/tool-/notes- category')


def source_path(root, relative, prefix='assets/'):
    if not isinstance(relative, str) or not relative.startswith(prefix):
        raise ValueError(f'Expected a {prefix} source path: {relative}')
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'Missing or unsafe source file: {relative}')
    return path


def validate(profile, repositories, root=ROOT, check_files=True):
    if not repositories:
        raise ValueError('Refusing an empty repository inventory')
    keys = [c['key'] for c in profile['categories']]
    if keys != ['public', 'projects', 'labs', 'study', 'tools', 'notes']:
        raise ValueError('Preserve the approved six-category navigation order')
    ids, names = set(), set()
    for repo in repositories:
        if not isinstance(repo['id'], int) or repo['id'] in ids or repo['name'] in names:
            raise ValueError(f'Duplicate or invalid repository identity: {repo["name"]}')
        ids.add(repo['id']); names.add(repo['name'])
        if not isinstance(repo.get('private'), bool) or not isinstance(repo.get('fork'), bool):
            raise ValueError(f'{repo["name"]}: visibility and fork must be booleans')
        if not isinstance(repo.get('description'), str) or not repo['description'].strip():
            raise ValueError(f'{repo["name"]}: add an accurate GitHub description first')
        if 'description_override' in repo and not repo['description_override'].strip():
            raise ValueError(f'{repo["name"]}: empty description override')
        category_for(repo, profile)
        if check_files:
            source_path(root, repo['illustration'], 'assets/illustrations/')
    if check_files:
        source_path(root, profile['banner']['path'], 'assets/branding/')
        for category in profile['categories']:
            source_path(root, category['illustration'], 'assets/illustrations/')
        for font in profile['fonts'].values():
            source_path(root, font, 'assets/fonts/')


def grouped(profile, repositories):
    result = []
    for category in profile['categories']:
        group = dict(category)
        preferred = category.get('preferred_ids', [])
        rows = [dict(r) for r in repositories if category_for(r, profile) == category['key']]
        rows.sort(key=lambda r: (
            preferred.index(r['id']) if r['id'] in preferred else len(preferred),
            r['fork'] if category['key'] == 'public' else False,
            r['name'].casefold()))
        group['repos'] = rows
        result.append(group)
    return result
