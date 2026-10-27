from pathlib import Path
from io import BytesIO
import base64
import html
import argparse
import hashlib
import fontTools
from profile_data import ROOT, load_data, grouped
from fontTools.ttLib import TTFont
from fontTools import subset

PROFILE, REPOSITORIES = load_data()
FONTS = {key: ROOT / value for key, value in PROFILE['fonts'].items() if key != 'license'}
METRICS = {key: TTFont(path, recalcTimestamp=False) for key, path in FONTS.items()}
FONT_CACHE = {}
USE_DISK_CACHE = True
SIZE = 410


def esc(text):
    return html.escape(str(text), quote=True)

def data_uri(path, media='image/png'):
    return 'data:' + media + ';base64,' + base64.b64encode(Path(path).read_bytes()).decode()

def measure(text, size, weight='regular'):
    font = METRICS[weight]
    cmap = font.getBestCmap()
    advances = font['hmtx'].metrics
    return sum(advances[cmap.get(ord(c), '.notdef')][0] for c in text) * size / font['head'].unitsPerEm

def wrap(text, width, size, weight='regular'):
    lines = []
    text = text.strip()
    while text:
        index = 1
        while index <= len(text) and measure(text[:index], size, weight) <= width:
            index += 1
        end = max(1, index - 1)
        if end < len(text):
            space = text.rfind(' ', 0, end + 1)
            if space > end * 0.55:
                end = space
        lines.append(text[:end].strip())
        text = text[end:].lstrip()
    return lines or ['']

def font_uri(text, weight):
    key = (text, weight)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    cache_key = hashlib.sha256(FONTS[weight].read_bytes() + (weight + text + fontTools.__version__ + 'NubiCard-v1').encode()).hexdigest()
    cache_path = ROOT / '.cache/font-subsets' / (cache_key + '.woff2')
    if USE_DISK_CACHE and cache_path.is_file():
        value = 'data:font/woff2;base64,' + base64.b64encode(cache_path.read_bytes()).decode()
        FONT_CACHE[key] = value
        return value
    font = TTFont(FONTS[weight], recalcTimestamp=False)
    # Rename modified subsets to respect the font's reserved names.
    for record in font['name'].names:
        if record.nameID in (1, 4, 6, 16):
            value = 'NubiCard-' + weight if record.nameID == 6 else 'NubiCard'
            record.string = value.encode(record.getEncoding(), errors='replace')
    opts = subset.Options()
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = 'woff2'
    buf = BytesIO()
    font.save(buf)
    if USE_DISK_CACHE:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(buf.getvalue())
    value = 'data:font/woff2;base64,' + base64.b64encode(buf.getvalue()).decode()
    FONT_CACHE[key] = value
    return value

def font_css(normal, bold):
    return ('@font-face{font-family:NubiCard;src:url("' + font_uri(normal, 'regular') + '") format("woff2");font-weight:400;}'
            '@font-face{font-family:NubiCard;src:url("' + font_uri(bold, 'bold') + '") format("woff2");font-weight:700;}')

def card_svg(repo, height, mobile=False):
    desc = repo['description']
    name = repo['name']
    title_size = repo['mobile_title_size'] if mobile else repo['title_size']
    lines = repo['mobile_lines'] if mobile else repo['lines']
    label = repo['label']
    fonts = font_css(desc + label, name)
    art = data_uri(ROOT / repo['illustration'])
    description = ''.join('<span>' + esc(line) + '</span>' for line in lines)
    copy_width, desc_size, line_height, art_size = (296, 18.8, 25, 100) if mobile else (266, 16, 22, 136)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{height}" viewBox="0 0 {SIZE} {height}" role="img" aria-label="{esc(name + ' — ' + desc)}">
<title>{esc(name)}</title><desc>{esc(desc)}</desc>
<foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml">
<style>{fonts}
*{{box-sizing:border-box}}.canvas{{width:{SIZE}px;height:{height}px;padding:5px 5px 9px;font-family:NubiCard,sans-serif;-webkit-font-smoothing:antialiased}}
.card{{position:relative;height:100%;border:1px solid #ddbdcd;border-radius:12px;background:#fbf6f9;overflow:hidden}}
.copy{{position:relative;z-index:1;width:{copy_width}px;padding:18px 0 16px 19px}}
.label{{font-size:12px;line-height:16px;color:#a15b7c;font-weight:400}}
.name{{margin-top:3px;font-size:{title_size}px;line-height:25px;font-weight:700;letter-spacing:-.4px;color:#211d28;white-space:nowrap}}
.description{{margin-top:10px;font-size:{desc_size}px;line-height:{line_height}px;color:#57515f;font-weight:400;letter-spacing:-.1px}}
.description span{{display:block;white-space:nowrap}}
.art{{position:absolute;right:0;bottom:15px;width:{art_size}px;height:{art_size}px;object-fit:contain}}
</style><div class="canvas"><div class="card"><div class="copy"><div class="label">{esc(label)}</div><div class="name">{esc(name)}</div><div class="description">{description}</div></div><img class="art" src="{art}" alt=""/></div></div>
</div></foreignObject></svg>'''

def section_svg(group, mobile=False):
    title, desc, count = group['title'], group['subtitle'], str(len(group['repos']))
    fonts = font_css(desc, title + count)
    art = data_uri(ROOT / group['illustration'])
    width, height, art_size, title_size, sub_size = (410, 110, 70, 28, 16.5) if mobile else (840, 106, 88, 34, 16)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title + ' · ' + count + ' · ' + desc)}"><title>{esc(title)}</title>
<foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml"><style>{fonts}
*{{box-sizing:border-box}}.heading{{width:{width}px;height:{height}px;display:flex;align-items:center;gap:19px;background:#fff;font-family:NubiCard,sans-serif;padding:7px 5px}}
img{{width:{art_size}px;height:{art_size}px;object-fit:contain;flex:none}}.heading>div{{flex:1;min-width:0}}.row{{display:flex;align-items:center;gap:14px}}.title{{font-weight:700;font-size:{title_size}px;line-height:42px;letter-spacing:-.8px;color:#211d28}}.count{{font-weight:700;font-size:16px;line-height:30px;padding:0 14px;border-radius:30px;background:#efdae5;color:#88445f}}.subtitle{{font-size:{sub_size}px;line-height:23px;color:#68616f;margin-top:2px}}
</style><div class="heading"><img src="{art}" alt=""/><div><div class="row"><span class="title">{esc(title)}</span><span class="count">{count}</span></div><div class="subtitle">{esc(desc)}</div></div></div></div></foreignObject></svg>'''


def card_data(repo, group):
    result = dict(repo)
    name = repo['name']
    desc = repo.get('description_override') or repo['description']
    result['description'] = desc
    for weight, text in [('regular', desc), ('bold', name)]:
        missing = sorted(set(text) - set(map(chr, METRICS[weight].getBestCmap())))
        if missing:
            raise ValueError(f'{name}: font lacks glyphs {missing}; review display copy or font sources')
    title_size = 22
    while measure(name, title_size, 'bold') > 256 and title_size > 17:
        title_size -= .5
    mobile_title_size = 24.5
    while measure(name, mobile_title_size, 'bold') > 280 and mobile_title_size > 20:
        mobile_title_size -= .5
    # Existing long names can extend beyond the body-copy column. Their title
    # must still fit inside the card, including the CSS letter spacing.
    if any(measure(name, size, 'bold') - .4 * (len(name)-1) > 370
           for size in (title_size, mobile_title_size)):
        raise ValueError(f'{name}: title is too long; adjust layout rather than truncate its name')
    lines = wrap(desc, 245, 16)
    mobile_lines = wrap(desc, 274, 18.8)
    result.update(
        label=group['prefix'] or ('public / fork' if repo['fork'] else 'public'),
        title_size=title_size, lines=lines, height=max(184, 96 + len(lines)*22),
        mobile_title_size=mobile_title_size, mobile_lines=mobile_lines,
        mobile_height=max(198, 102 + len(mobile_lines)*25),
        url=f"https://github.com/{PROFILE['owner']}/{name}")
    return result


def generated_files():
    files = {}
    groups = grouped(PROFILE, REPOSITORIES)
    for group in groups:
        group['repos'] = [card_data(r, group) for r in group['repos']]
        for index in range(0, len(group['repos']), 2):
            pair = group['repos'][index:index+2]
            desktop_height = max(r['height'] for r in pair)
            mobile_height = max(r['mobile_height'] for r in pair)
            for repo in pair:
                files[f"assets/generated/cards/{repo['name']}.svg"] = card_svg(repo, desktop_height)
                files[f"assets/generated/cards/{repo['name']}.mobile.svg"] = card_svg(repo, mobile_height, True)
        files[f"assets/generated/sections/{group['key']}.svg"] = section_svg(group)
        files[f"assets/generated/sections/{group['key']}.mobile.svg"] = section_svg(group, True)

    def raw(path):
        url = f"https://raw.githubusercontent.com/{PROFILE['owner']}/{PROFILE['repository']}/{PROFILE['branch']}/{path}"
        if path in files:
            url += '?v=' + hashlib.sha256(files[path].encode()).hexdigest()[:12]
        return url

    public = sum(not r['private'] for r in REPOSITORIES)
    banner = PROFILE['banner']
    output = ['<p align="center">',
              f'  <img src="{raw(banner["path"])}" alt="{esc(banner["alt"])}" width="100%">',
              '</p>', '', '# ' + PROFILE['display_name'], '',
              *PROFILE['introduction'], '', '<!-- BEGIN REPOSITORY INDEX -->',
              '## Explore the workspace', '',
              f'{len(REPOSITORIES)} repositories · {public} public · {len(REPOSITORIES)-public} private', '',
              '<table width="100%">', '<tr>']
    for group in groups:
        count = len(group['repos'])
        output.append(f'<td align="center" width="16%"><a href="#user-content-{group["anchor"]}"><img src="{raw(group["illustration"])}" alt="NUBI {esc(group["navigation_label"])}" width="110"><br><strong>{esc(group["navigation_label"])}</strong></a><br><sub>{count} {"repository" if count == 1 else "repositories"}</sub></td>')
    output += ['</tr>', '</table>', '']
    for group in groups:
        key = group['key']
        output += [f'<a name="{group["anchor"]}"></a>', '',
            f'<p><picture><source media="(max-width: 480px)" srcset="{raw("assets/generated/sections/"+key+".mobile.svg")}"><img src="{raw("assets/generated/sections/"+key+".svg")}" alt="{esc(group["title"])} · {len(group["repos"])} · {esc(group["subtitle"])}" width="840"></picture></p>', '', '<p>']
        for repo in group['repos']:
            name = repo['name']
            alt = esc(name + ' — ' + repo['description'])
            output.append(f'<a href="{repo["url"]}" title="{alt}"><picture><source media="(max-width: 767px)" srcset="{raw("assets/generated/cards/"+name+".mobile.svg")}"><img src="{raw("assets/generated/cards/"+name+".svg")}" alt="{alt}" width="410"></picture></a>')
        output += ['</p>', '']
    output += ['<sub>Private repository contents are available to authorized collaborators.</sub>',
               '<!-- END REPOSITORY INDEX -->', '']
    files['README.md'] = '\n'.join(output)
    return files


def main():
    parser = argparse.ArgumentParser(description='Rebuild the GitHub profile from repo-contained source data.')
    parser.add_argument('--check', action='store_true', help='Report stale/missing/orphaned generated files without changing tracked files.')
    parser.add_argument('--no-cache', action='store_true', help='Recompute embedded font subsets to check reproducibility.')
    args = parser.parse_args()
    global USE_DISK_CACHE
    USE_DISK_CACHE = not args.no_cache
    try:
        files = generated_files()
    except (ValueError, KeyError) as error:
        parser.exit(2, str(error) + '\n')
    expected = set(files)
    existing = {str(p.relative_to(ROOT)) for directory in ['cards', 'sections']
                for p in (ROOT/'assets/generated'/directory).glob('*.svg')}
    stale = [name for name, text in files.items() if not (ROOT/name).exists() or (ROOT/name).read_text() != text]
    orphaned = sorted(existing - expected)
    if args.check:
        if stale or orphaned:
            for name in stale: print('STALE', name)
            for name in orphaned: print('ORPHAN', name)
            return 1
        print(f'Profile is current: {len(REPOSITORIES)} repositories, {len(expected)-1} SVGs.')
        return 0
    for name in stale:
        path = ROOT/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[name])
    # Only SVGs in these two explicitly generated directories can be pruned.
    for name in orphaned:
        (ROOT/name).unlink()
    print(f'Built {len(REPOSITORIES)} repository cards; updated {len(stale)} files, removed {len(orphaned)} obsolete SVGs.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
