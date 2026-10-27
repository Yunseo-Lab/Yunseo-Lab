"""Read GitHub metadata and optionally update local sources; never mutate GitHub."""
import argparse
import json
import subprocess
from pathlib import Path
from profile_data import ROOT, load_data, validate, category_for


def gh(*args):
    result = subprocess.run(['gh', *args], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def reconcile(profile, current, snapshot, allow_removals=False):
    owner = profile['owner']
    # --paginate --slurp returns pages; fixtures may also contain a flat list.
    rows = [r for page in snapshot for r in page] if snapshot and isinstance(snapshot[0], list) else snapshot
    rows = [r for r in rows if r.get('owner', {}).get('login', '').casefold() == owner.casefold()]
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate GitHub inventory; no local files were changed')
    previous = {r['id']: r for r in current}
    missing = [r['name'] for r in current if r['id'] not in {n['id'] for n in rows}]
    if missing and not allow_removals:
        raise ValueError('Missing repositories: ' + ', '.join(missing) + '. Verify account access/deletion/transfer before --allow-removals.')
    output, changes = [], []
    for row in rows:
        old = previous.get(row['id'])
        repo = dict(old or {'id': row['id']})
        for field in ['name', 'private', 'fork', 'description']:
            repo[field] = row[field]
        category = category_for(repo, profile)
        if old is None:
            repo['illustration'] = next(c['illustration'] for c in profile['categories'] if c['key'] == category)
            changes.append('ADD ' + repo['name'])
        elif repo != old:
            changes.append('UPDATE ' + old['name'] + ' → ' + repo['name'])
            if repo['description'] != old['description'] and 'description_override' in repo:
                changes.append('REVIEW description_override: ' + repo['name'])
        output.append(repo)
    changes += ['REMOVE ' + name for name in missing]
    output.sort(key=lambda r: r['id'])
    validate(profile, output, ROOT)
    return output, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only comparison (default).')
    mode.add_argument('--apply', action='store_true', help='Update data/repositories.json locally only.')
    parser.add_argument('--snapshot', type=Path, help='Use a saved gh API response instead of the network.')
    parser.add_argument('--allow-removals', action='store_true', help='Accept verified deletions/transfers in local inventory.')
    args = parser.parse_args()
    try:
        profile, current = load_data()
        if args.snapshot:
            snapshot = json.loads(args.snapshot.read_text())
        else:
            if gh('api', 'user')['login'].casefold() != profile['owner'].casefold():
                raise ValueError('Authenticate gh as ' + profile['owner'] + ' to include private repositories')
            snapshot = gh('api', 'user/repos?affiliation=owner&per_page=100', '--paginate', '--slurp')
        output, changes = reconcile(profile, current, snapshot, args.allow_removals)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, str(error) + '\n')
    if not changes:
        print(f'GitHub metadata is current: {len(current)} repositories.')
        return 0
    print('\n'.join(changes))
    if not args.apply:
        return 1
    (ROOT/'data/repositories.json').write_text(json.dumps({'schema_version': 1, 'repositories': output}, ensure_ascii=False, indent=2) + '\n')
    print('Updated local sources. Review overrides/artwork, then rebuild the profile.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
