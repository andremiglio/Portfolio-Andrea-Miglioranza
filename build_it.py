"""Builds the Italian page (it/index.html) from the English one (index.html).

Run after every change to index.html:  python3 build_it.py
Texts come from i18n_it.py; anything without a translation stays as it is and is listed at the end.
"""
import html, re, os
from i18n_it import IT

src = open('index.html', encoding='utf-8').read()

def tr(text):
    key = html.unescape(text.strip())
    if key in IT:
        lead = text[: len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        return lead + html.escape(IT[key], quote=False) + trail, True
    return text, False

missing = set()

def do_body(part):
    def node(m):
        new, ok = tr(m.group(1))
        k = html.unescape(m.group(1).strip())
        if not ok and len(k.split()) > 1 and re.search('[a-z]', k):
            missing.add(k)
        return '>' + new + '<'
    part = re.sub(r'>([^<>]+)<', node, part)
    def attr(m):
        val = html.unescape(m.group(2))
        if val in IT:
            return f'{m.group(1)}="{html.escape(IT[val], quote=True)}"'
        if len(val.split()) > 1:
            missing.add('@' + val)
        return m.group(0)
    return re.sub(r'\b(alt|aria-label|title|placeholder)="([^"]*)"', attr, part)

# translate only the markup, never inside <style> or <script>
head_end = src.index('<body')
head, body = src[:head_end], src[head_end:]
pieces = re.split(r'(<script>[\s\S]*?</script>)', body)
body = ''.join(p if p.startswith('<script>') else do_body(p) for p in pieces)
out = head + body

# page-level settings
out = out.replace('<html lang="en">', '<html lang="it">', 1)
out = re.sub(r'<title>[^<]*</title>', '<title>Andrea Miglioranza, una mostra in sette stanze</title>', out, count=1)
out = re.sub(r'<meta name="description" content="[^"]*">',
             '<meta name="description" content="Portfolio di Andrea Miglioranza, studente di business che fa marketing con l’intelligenza artificiale: siti scroll-film per Extillo Gin, POP Energy e MIXCRAFT, un video di proposta commerciale e un assistente showroom per Cattelan Italia.">', out, count=1)
out = out.replace("say('Email copied')", "say('Email copiata')")
# link previews and canonical address for the Italian page
out = out.replace('<link rel="canonical" href="https://andreamiglioranza.com/">', '<link rel="canonical" href="https://andreamiglioranza.com/it/">')
out = out.replace('<meta property="og:url" content="https://andreamiglioranza.com/">', '<meta property="og:url" content="https://andreamiglioranza.com/it/">')
out = out.replace('<meta property="og:title" content="Andrea Miglioranza, portfolio">', '<meta property="og:title" content="Andrea Miglioranza, portfolio">')
out = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="Marketing con l’intelligenza artificiale: siti, animazioni di prodotto, video e assistenti che vendono. Progetti per Cattelan Italia, Audi Match e altri.">', out, count=1)
out = out.replace('https://andreamiglioranza.com/img/og.jpg', 'https://andreamiglioranza.com/img/og-it.jpg')
out = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Andrea Miglioranza, sorridente, accanto alla scritta Ciao, sono Andrea Miglioranza">', out, count=1)
out = out.replace('<meta property="og:locale" content="en_GB"><meta property="og:locale:alternate" content="it_IT">', '<meta property="og:locale" content="it_IT"><meta property="og:locale:alternate" content="en_GB">')
# language switch: Italian is the current one here
out = out.replace('<a href="/" lang="en" hreflang="en" aria-current="true">EN</a><a href="/it/" lang="it" hreflang="it">IT</a>',
                  '<a href="/" lang="en" hreflang="en">EN</a><a href="/it/" lang="it" hreflang="it" aria-current="true">IT</a>')
out = out.replace('aria-label="Language"', 'aria-label="Lingua"')
out = out.replace('var SITE_LANG = \'en\'', 'var SITE_LANG = \'it\'')
# assets live one folder up
for d in ('img/', 'extillo/', 'scroll-film/', 'cattelan/', 'assistente/'):
    out = out.replace(f'data-src="{d}', f'data-src="../{d}')
    out = out.replace(f'src="{d}', f'src="../{d}').replace(f'href="{d}', f'href="../{d}').replace(f'srcset="{d}', f'srcset="../{d}').replace(f"open('{d}", f"open('../{d}").replace(f'poster="{d}', f'poster="../{d}')

os.makedirs('it', exist_ok=True)
open('it/index.html', 'w', encoding='utf-8').write(out)
print('it/index.html written,', len(out), 'bytes')
if missing:
    print('Not translated:')
    for m in sorted(missing):
        print('  ', m[:110])
