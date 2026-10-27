"""Check all source/generated assets and README links without network access."""
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs, unquote
import hashlib
import xml.etree.ElementTree as ET
from profile_data import ROOT, load_data, grouped


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.anchors = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            if 'href' in attrs: self.links.append(attrs['href'])
            if 'name' in attrs: self.anchors.append(attrs['name'])
        if tag in ('img', 'source'):
            self.images.append(attrs.get('src') or attrs.get('srcset'))


def check():
    profile, repos = load_data()
    readme = (ROOT/'README.md').read_text()
    parsed = Links()
    parsed.feed(readme)
    assert readme.count('<!-- BEGIN REPOSITORY INDEX -->') == 1
    assert readme.count('<!-- END REPOSITORY INDEX -->') == 1
    assert 'Selected work' not in readme
    public = sum(not r['private'] for r in repos)
    assert f'{len(repos)} repositories · {public} public · {len(repos)-public} private' in readme
    expected_links = Counter(f'https://github.com/{profile["owner"]}/{r["name"]}' for r in repos)
    assert Counter(link for link in parsed.links if link.startswith('https://github.com/')) == expected_links, 'Repository link mismatch'
    sources = {profile['banner']['path'], *profile['fonts'].values()}
    sources.update(profile.get('branding', {}).values())
    sources.update(r['illustration'] for r in repos)
    sources.update(c['illustration'] for c in profile['categories'])
    generated = set()
    for group in grouped(profile, repos):
        assert group['anchor'] in parsed.anchors
        assert '#user-content-' + group['anchor'] in parsed.links
        for suffix in ('.svg', '.mobile.svg'):
            generated.add(f'assets/generated/sections/{group["key"]}{suffix}')
            for repo in group['repos']:
                path = f'assets/generated/cards/{repo["name"]}{suffix}'
                generated.add(path)
                svg = ET.parse(ROOT/path).getroot()
                assert svg.find('{http://www.w3.org/2000/svg}title').text == repo['name']
                assert svg.find('{http://www.w3.org/2000/svg}desc').text == repo.get('description_override', repo['description'])
    for relative in generated:
        svg = ET.parse(ROOT/relative).getroot()
        for node in svg.iter():
            assert node.tag.rsplit('}', 1)[-1] != 'script', relative
            if 'src' in node.attrib:
                assert node.attrib['src'].startswith('data:image/png;base64,'), relative
    prefix = f'/{profile["owner"]}/{profile["repository"]}/{profile["branch"]}/'
    referenced = set()
    for image in parsed.images:
        url = urlparse(image)
        assert url.netloc == 'raw.githubusercontent.com' and url.path.startswith(prefix), image
        relative = unquote(url.path[len(prefix):])
        assert (ROOT/relative).is_file(), relative
        referenced.add(relative)
        if relative in generated:
            assert parse_qs(url.query).get('v') == [hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()[:12]], relative
    assert generated <= referenced, 'Unreferenced generated image'
    actual = {str(p.relative_to(ROOT)) for p in (ROOT/'assets').rglob('*') if p.is_file()}
    assert actual == sources | generated, f'Unused/missing assets: {sorted(actual ^ (sources | generated))}'
    print(f'Valid: {len(repos)} repository links, {len(generated)} SVGs, {len(sources)} source assets; no unused assets.')


if __name__ == '__main__':
    check()
