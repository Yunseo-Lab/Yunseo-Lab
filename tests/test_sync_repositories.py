"""Regression coverage for changes that can silently lose profile curation."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from profile_data import load_data, category_for
from sync_repositories import reconcile


class RepositoryChanges(unittest.TestCase):
    def setUp(self):
        self.profile, repos = load_data()
        self.current = [deepcopy(next(r for r in repos if r['name'] == 'proj-engram'))]
        self.remote = deepcopy(self.current)
        self.remote[0]['owner'] = {'login': self.profile['owner']}

    def test_rename_preserves_art_and_approved_copy(self):
        self.remote[0]['name'] = 'proj-new-name'
        result, changes = reconcile(self.profile, self.current, self.remote)
        self.assertEqual(result[0]['illustration'], self.current[0]['illustration'])
        self.assertEqual(result[0]['description_override'], self.current[0]['description_override'])
        self.assertEqual(result[0]['id'], self.current[0]['id'])
        self.assertTrue(changes)

    def test_visibility_change_moves_to_public(self):
        self.remote[0].update(name='engram', private=False)
        result, _ = reconcile(self.profile, self.current, self.remote)
        self.assertEqual(category_for(result[0], self.profile), 'public')

    def test_unknown_private_prefix_does_not_guess(self):
        self.remote[0]['name'] = 'experiment-engram'
        with self.assertRaisesRegex(ValueError, 'approved'):
            reconcile(self.profile, self.current, self.remote)

    def test_new_repo_uses_category_art(self):
        self.remote.append(dict(id=9999999999, name='tool-example', private=True,
                                fork=False, description='반복 작업 자동화', owner={'login': self.profile['owner']}))
        result, _ = reconcile(self.profile, self.current, self.remote)
        self.assertEqual(result[-1]['illustration'], 'assets/illustrations/categories/tools.png')

    def test_empty_response_never_erases_inventory(self):
        with self.assertRaisesRegex(ValueError, 'Empty'):
            reconcile(self.profile, self.current, [])

    def test_missing_repo_requires_explicit_removal(self):
        other = dict(self.remote[0], id=9999999999, name='proj-other')
        with self.assertRaisesRegex(ValueError, 'Missing repositories'):
            reconcile(self.profile, self.current, [other])
        result, _ = reconcile(self.profile, self.current, [other], allow_removals=True)
        self.assertEqual([r['id'] for r in result], [9999999999])

    def test_description_change_flags_curated_override(self):
        self.remote[0]['description'] = '새 설명'
        _, changes = reconcile(self.profile, self.current, self.remote)
        self.assertTrue(any('REVIEW description_override' in c for c in changes))

    def test_missing_description_requires_actual_copy(self):
        self.remote[0]['description'] = None
        with self.assertRaisesRegex(ValueError, 'accurate GitHub description'):
            reconcile(self.profile, self.current, self.remote)


if __name__ == '__main__':
    unittest.main()
