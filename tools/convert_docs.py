"""Convertit les exports HTML Google Docs (scripts d'Ansou) en fragments propres pour le lecteur du site.

Usage : python3 tools/convert_docs.py <dossier des exports .html> <dossier de sortie (scripts/)>
Chaque fichier <slug>.html devient scripts/<slug>.html ; les images utiles vont dans scripts/img/.
"""
import base64, html, io, re, sys, pathlib, urllib.parse
from PIL import Image
from bs4 import BeautifulSoup, NavigableString, Tag

KEEP_IMAGES = {"mission-sens"}  # seuls documents dont les images font partie du contenu

def class_styles(soup):
    css = "".join(s.get_text() for s in soup.find_all("style"))
    bold, ital = set(), set()
    for name, body in re.findall(r"\.(c\d+)\{([^}]*)\}", css):
        if re.search(r"font-weight:\s*700", body): bold.add(name)
        if re.search(r"font-style:\s*italic", body): ital.add(name)
    return bold, ital

def clean_href(h):
    if h.startswith("https://www.google.com/url"):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(h).query).get("q")
        if q: return q[0]
    return h

def convert(src, slug, outdir):
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")
    bold, ital = class_styles(soup)
    imgdir = outdir / "img"; nimg = [0]

    def inline(node):
        out = []
        for ch in node.children:
            if isinstance(ch, NavigableString):
                out.append(html.escape(str(ch).replace("\xa0", " "), quote=False))
            elif isinstance(ch, Tag):
                if ch.name == "br": out.append("<br>")
                elif ch.name == "img": out.append(image(ch))
                elif ch.name == "a" and ch.get("href"):
                    href = clean_href(ch["href"])
                    if href.startswith("#"): out.append(inline(ch))
                    else: out.append(f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{inline(ch)}</a>')
                else:
                    inner = inline(ch)
                    cls = set(ch.get("class", []))
                    if inner.strip():
                        if cls & ital: inner = f"<em>{inner}</em>"
                        if cls & bold: inner = f"<strong>{inner}</strong>"
                    out.append(inner)
        s = "".join(out)
        s = re.sub(r"</strong><strong>", "", s); s = re.sub(r"</em><em>", "", s)
        return s

    def image(img):
        if slug not in KEEP_IMAGES: return ""
        m = re.match(r"data:image/(png|jpeg);base64,(.*)", img.get("src", ""), re.S)
        if not m: return ""
        nimg[0] += 1; ext = "jpg" if m.group(1) == "jpeg" else "png"
        imgdir.mkdir(parents=True, exist_ok=True)
        name = f"{slug}-{nimg[0]}.jpg"
        im = Image.open(io.BytesIO(base64.b64decode(m.group(2)))).convert("RGB")
        im.thumbnail((1200, 1200)); im.save(imgdir / name, "JPEG", quality=82, optimize=True)
        return f'<img src="scripts/img/{name}" alt="" loading="lazy">'

    def block(el):
        n = el.name
        if n in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = inline(el).strip()
            if not re.sub(r"<[^>]+>|\s", "", t): return ""
            lvl = "h3" if n in ("h1", "h2") else "h4"
            t = re.sub(r"</?strong>", "", t)
            if len(re.sub(r"<[^>]+>", "", t)) > 70: return f'<p class="lead">{t}</p>'  # phrase mise en titre dans le doc
            return f"<{lvl}>{t}</{lvl}>"
        if n == "p":
            t = inline(el).strip()
            if not re.sub(r"<br>|\s", "", t): return ""
            if re.fullmatch(r"(<strong>)?<img[^>]*>(</strong>)?", t): return f'<figure>{re.sub(r"</?strong>", "", t)}</figure>'
            return f"<p>{t}</p>"
        if n in ("ul", "ol"):
            items = [inline(li).strip() for li in el.find_all("li", recursive=False)]
            items = [i for i in items if re.sub(r"<[^>]+>|\s", "", i)]
            return f"<{n}>" + "".join(f"<li>{i}</li>" for i in items) + f"</{n}>" if items else ""
        if n == "table":
            rows = []
            for tr in el.find_all("tr"):
                cells = ["".join(block(c) for c in td.children if isinstance(c, Tag)) for td in tr.find_all("td", recursive=False)]
                rows.append(cells)
            if not rows: return ""
            # première ligne = en-têtes si elle est courte
            head = rows[0]
            plain = [re.sub(r"<[^>]+>", "", c).strip() for c in head]
            has_head = all(len(p) < 40 for p in plain)
            body = rows[1:] if has_head else rows
            body = [r for r in body if any(re.sub(r"<[^>]+>|\s", "", c) for c in r)]
            if not body: return ""
            out = ['<div class="sc-table"><table>']
            if has_head and any(plain): out.append("<thead><tr>" + "".join(f"<th>{html.escape(p)}</th>" for p in plain) + "</tr></thead>")
            out.append("<tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody>")
            out.append("</table></div>")
            return "".join(out)
        if n == "hr": return ""
        if n == "div": return "".join(block(c) for c in el.children if isinstance(c, Tag))
        return ""

    parts = [block(c) for c in soup.body.children if isinstance(c, Tag)]
    frag = "\n".join(p for p in parts if p)
    # sections annoncées « à venir » sans contenu : on retire le titre orphelin en fin de document
    frag = re.sub(r"\n?<h3>[^<]*\(à venir\)\s*</h3>\s*$", "", frag)
    (outdir / f"{slug}.html").write_text(frag + "\n", encoding="utf-8")
    return len(frag), nimg[0]

if __name__ == "__main__":
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.html")):
        print(f.stem, *convert(f, f.stem, out))
