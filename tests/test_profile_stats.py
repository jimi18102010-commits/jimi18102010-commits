import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('stats', Path(__file__).parents[1] / 'generate_cards.py')
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


class StatsTests(unittest.TestCase):
    def test_population_and_pagination(self):
        calls = []
        def api(path):
            calls.append(path)
            if '&page=1' in path and path.startswith('users/'):
                return [{'owner': {'login': 'user'}, 'stargazers_count': 1, 'fork': False}] * 100
            if path.startswith('users/'):
                return [{'owner': {'login': 'user'}, 'stargazers_count': 999, 'fork': True},
                        {'owner': {'login': 'user'}, 'stargazers_count': 999, 'private': True},
                        {'owner': {'login': 'another'}, 'stargazers_count': 999}]
            return {'total_count': 3, 'incomplete_results': False}
        data = stats.collect_stats('user', api=api)
        self.assertEqual(data['public_repositories'], 101)
        self.assertEqual(data['public_nonfork_repositories'], 100)
        self.assertEqual(data['stars_on_public_nonfork_repositories'], 100)
        self.assertTrue(any('page=2' in p for p in calls))

    def test_incomplete_search_is_not_zero(self):
        def api(path):
            return [] if path.startswith('users/') else {'incomplete_results': True, 'total_count': 0}
        with self.assertRaises(RuntimeError):
            stats.collect_stats('user', api=api)

    def test_markers_preserve_surrounding_text(self):
        source = 'before\n' + stats.START + '\nold\n' + stats.END + '\nafter'
        data = {'updated_utc': '2026-10-13T00:00:00+00:00', 'public_repositories': 7,
                'public_nonfork_repositories': 4, 'stars_on_public_nonfork_repositories': 5,
                'open_authored_pull_requests': 1, 'merged_authored_pull_requests': 1}
        output = stats.update_readme(source, data)
        self.assertTrue(output.startswith('before\n'))
        self.assertTrue(output.endswith('\nafter'))
        self.assertNotIn('A++', output)
        self.assertIn('| Public non-fork repositories | 4 |', output)

    def test_bad_markers_and_username_rejected(self):
        with self.assertRaises(ValueError): stats.update_readme('missing markers', {})
        with self.assertRaises(ValueError): stats.collect_stats('../user')


if __name__ == '__main__':
    unittest.main()
