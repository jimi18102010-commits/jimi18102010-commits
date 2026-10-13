"""Refresh README statistics from GitHub; no hardcoded ranks, counts or language shares."""
import argparse
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

START = '<!-- github-stats:start -->'
END = '<!-- github-stats:end -->'


def github_json(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'github-profile-stats'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request('https://api.github.com/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def collect_stats(username, api=github_json):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})', username):
        raise ValueError('Invalid GitHub username')
    repos = []
    page = 1
    while True:
        batch = api(f'users/{username}/repos?per_page=100&type=owner&page={page}')
        repos.extend(r for r in batch if not r.get('private', False) and r['owner']['login'].lower() == username.lower())
        if len(batch) < 100:
            break
        page += 1
    original = [r for r in repos if not r.get('fork', False)]
    result = {'username': username, 'public_repositories': len(repos),
              'public_nonfork_repositories': len(original),
              'stars_on_public_nonfork_repositories': sum(r['stargazers_count'] for r in original)}
    for state, key in [('is:open', 'open_authored_pull_requests'), ('is:merged', 'merged_authored_pull_requests')]:
        query = urllib.parse.urlencode({'q': f'type:pr author:{username} {state}', 'per_page': 1})
        found = api('search/issues?' + query)
        if found.get('incomplete_results'):
            raise RuntimeError('GitHub search returned incomplete statistics')
        result[key] = found['total_count']
    result['updated_utc'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    result['source'] = 'GitHub REST API; public owned repositories; PR counts across GitHub'
    return result


def render_stats(stats):
    rows = [('Public repositories (including forks)', 'public_repositories'),
            ('Public non-fork repositories', 'public_nonfork_repositories'),
            ('Stars on public non-fork repositories', 'stars_on_public_nonfork_repositories'),
            ('Open authored pull requests (across GitHub)', 'open_authored_pull_requests'),
            ('Merged authored pull requests (across GitHub)', 'merged_authored_pull_requests')]
    return '\n'.join([START, '### GitHub snapshot', '', '| Metric | Count |', '| :--- | ---: |',
                      *(f'| {label} | {stats[key]} |' for label, key in rows), '',
                      f"Updated: {stats['updated_utc']} (UTC). Source: GitHub REST API.",
                      'Repository counts exclude private repositories; fork stars are not counted as original-project stars.',
                      'Commit totals, language percentages and developer ranks are intentionally not estimated.', END])


def update_readme(readme, stats):
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(END) <= readme.index(START):
        raise ValueError('README must contain exactly one ordered statistics marker pair')
    before = readme[:readme.index(START)]
    after = readme[readme.index(END) + len(END):]
    return before + render_stats(stats) + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', default=os.environ.get('GITHUB_REPOSITORY_OWNER', 'jimi18102010-commits'))
    parser.add_argument('--readme', type=Path, default=Path('README.md'))
    parser.add_argument('--output', type=Path, default=Path('profile-stats.json'))
    args = parser.parse_args()
    # Complete all network reads and validation before changing any files.
    stats = collect_stats(args.username)
    content = update_readme(args.readme.read_text(encoding='utf-8'), stats)
    args.output.write_text(json.dumps(stats, indent=2) + '\n', encoding='utf-8')
    args.readme.write_text(content, encoding='utf-8')
    print('Updated profile statistics from GitHub REST API')


if __name__ == '__main__':
    main()
