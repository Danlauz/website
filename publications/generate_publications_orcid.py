#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère publications.qmd (FR) et publications_en.qmd (EN) en fusionnant deux sources :

  1. supplement.json : liste de référence (vos publications, complète, incluant
     les conférences). C'est la source qui fait foi sur le formatage.
  2. ORCID (API publique) : détecte automatiquement tout NOUVEL article absent
     de la liste de référence, et l'enrichit via Crossref (auteurs, revue, pages).

Les deux sources sont fusionnées sans doublon (comparaison par titre normalisé).
Si ORCID est inaccessible, la page reste complète grâce à supplement.json.

N'utilise que la bibliothèque standard Python. Accès Internet requis à l'exécution.

Pour ajouter manuellement une publication (par ex. une conférence), il suffit
d'ajouter une entrée dans publications/supplement.json.
"""

import json, sys, time, re
import urllib.request, urllib.error
from pathlib import Path

ORCID_ID    = "0000-0001-7774-4460"
CONTACT     = "dany.lauzon@polymtl.ca"
BOLD_FAMILY = "lauzon"
OWNER       = ["Lauzon", "D."]
DIR         = Path(__file__).resolve().parent
SUPP_PATH   = DIR / "supplement.json"
TIMEOUT     = 30
PAUSE       = 0.34
UA = f"GeoStatPoly-website/1.0 (mailto:{CONTACT})"

SECTIONS = ["journal", "conf_article", "conf_oral", "conf_poster", "workshop", "thesis", "book"]
TITLES = {
  "fr": {"journal": "Articles de revue par les pairs",
         "conf_article": "Actes de conférence (revus par les pairs)",
         "conf_oral": "Présentations orales en conférence",
         "conf_poster": "Affiches (posters)",
         "workshop": "Ateliers et formations",
         "thesis": "Thèses", "book": "Livres et ressources pédagogiques",
         "page": "Publications", "updated": "Dernière mise à jour", "total": "publications", "link": "lien"},
  "en": {"journal": "Peer-reviewed journal articles",
         "conf_article": "Peer-reviewed conference papers",
         "conf_oral": "Conference oral presentations",
         "conf_poster": "Conference posters",
         "workshop": "Workshops and training",
         "thesis": "Theses", "book": "Books and educational resources",
         "page": "Publications", "updated": "Last updated", "total": "publications", "link": "link"},
}
MONTHS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MONTHS_EN = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ORCID_TYPE_MAP = {"journal-article": "journal", "conference-paper": "conf_article", "conference-abstract": "conf_oral",
  "conference-poster": "conf_poster", "lecture-speech": "conf_oral", "dissertation-thesis": "thesis", "dissertation": "thesis",
  "book": "book", "book-chapter": "book", "edited-book": "book", "report": "book", "supervised-student-publication": "journal"}


def http_get(url, accept):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if a == 2:
                print(f"  ! réseau {url} ({e})", file=sys.stderr)
                return None
            time.sleep(1.2 * (a + 1))
    return None


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:70]


def load_supplement():
    if not SUPP_PATH.exists():
        return []
    data = json.loads(SUPP_PATH.read_text(encoding="utf-8"))
    out = []
    for e in data:
        out.append({"category": e.get("category", "journal"), "year": str(e.get("year", "")),
                    "authors": [list(a) for a in e.get("authors", [])], "title": e.get("title", "").strip(),
                    "venue": e.get("venue", ""), "details": e.get("details", ""), "note": e.get("note", ""),
                    "url": e.get("url", "")})
    return out


def fetch_orcid_works():
    data = http_get(f"https://pub.orcid.org/v3.0/{ORCID_ID}/works", "application/json")
    if not data:
        return []
    works = []
    for g in data.get("group", []):
        s = g.get("work-summary", [{}])[0]
        doi = None
        for ext in (s.get("external-ids") or {}).get("external-id", []):
            if (ext.get("external-id-type") or "").lower() == "doi":
                doi = (ext.get("external-id-value") or "").strip()
                break
        pd = s.get("publication-date")
        year = pd["year"]["value"] if pd and pd.get("year") else ""
        works.append({"title": (s.get("title") or {}).get("title", {}).get("value", "Sans titre"),
                      "journal": (s.get("journal-title") or {}).get("value") if s.get("journal-title") else None,
                      "type": s.get("type") or "other", "year": year, "doi": doi})
    return works


def fetch_csl(doi):
    return http_get(f"https://doi.org/{doi}", "application/vnd.citationstyles.csl+json")


def csl_year(csl):
    for k in ("issued", "published-print", "published-online"):
        dp = (csl.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return ""


def orcid_to_record(w):
    csl = fetch_csl(w["doi"]) if w["doi"] else None
    if csl:
        authors = [[a.get("family", "").strip(), a.get("given", "").strip()]
                   for a in csl.get("author", []) if a.get("family") or a.get("given")]
        vol = str(csl.get("volume", "")).strip()
        iss = str(csl.get("issue", "")).strip()
        pg = str(csl.get("page", "")).strip()
        details = vol + (f"({iss})" if iss else "") + (f", {pg}" if pg else "")
        container = csl.get("container-title") or w["journal"] or ""
        if isinstance(container, list):
            container = container[0] if container else ""
        return {"category": ORCID_TYPE_MAP.get(w["type"], "journal"), "year": csl_year(csl) or w["year"],
                "authors": authors or [OWNER], "title": (csl.get("title") or w["title"]).strip(),
                "venue": str(container).strip(), "details": details.strip(", "),
                "note": "", "url": "https://doi.org/" + w["doi"] if w["doi"] else ""}
    return {"category": ORCID_TYPE_MAP.get(w["type"], "journal"), "year": w["year"], "authors": [OWNER],
            "title": w["title"].strip(), "venue": (w["journal"] or "").strip(), "details": "", "note": "", "url": ""}


def format_authors(authors):
    parts = []
    for a in authors:
        fam = a[0]
        giv = a[1] if len(a) > 1 else ""
        name = fam + (", " + giv if giv else "")
        if fam.lower() == BOLD_FAMILY:
            name = "**" + name + "**"
        parts.append(name)
    if len(parts) <= 1:
        return parts[0] if parts else ""
    return ", ".join(parts[:-1]) + ", & " + parts[-1]


def format_entry(rec, lang):
    link = TITLES[lang]["link"]
    auth = format_authors(rec["authors"])
    s = (auth + " " if auth else "") + f"({rec['year']}). "
    title = rec["title"].rstrip(".")
    if rec["category"] == "journal":
        s += title + ". "
        if rec["venue"]:
            s += "*" + rec["venue"] + "*"
            if rec["details"]:
                s += ", " + rec["details"]
            s += ". "
    else:
        s += "*" + title + "*"
        if rec.get("note"):
            s += " [" + rec["note"] + "]"
        s += ". "
        if rec["venue"]:
            s += rec["venue"] + ". "
    if rec["url"]:
        s += f"[{link}]({rec['url']})"
    return s.strip()


def build_page(records, lang):
    t = TITLES[lang]
    today = time.localtime()
    months = MONTHS_FR if lang == "fr" else MONTHS_EN
    out = ["---", f'title: "{t["page"]}"', "---", ""]
    total = 0
    for cat in SECTIONS:
        recs = [r for r in records if r["category"] == cat]
        if not recs:
            continue
        out.append(f"## {t[cat]}")
        out.append("")
        years = sorted({r["year"] for r in recs if r["year"]},
                       key=lambda y: int(y) if str(y).isdigit() else 0, reverse=True)
        noyear = [r for r in recs if not r["year"]]
        for y in years:
            out.append(f"### {y}")
            out.append("")
            for r in [x for x in recs if x["year"] == y]:
                out += ["::: {.publication-item}", format_entry(r, lang), ":::", ""]
                total += 1
        for r in noyear:
            out += ["::: {.publication-item}", format_entry(r, lang), ":::", ""]
            total += 1
    out.append("---")
    out.append("")
    out.append(f'*{t["total"].capitalize()}: {total} · {t["updated"]}: {months[today.tm_mon]} {today.tm_year}*')
    return "\n".join(out) + "\n", total


def main():
    supp = load_supplement()
    print(f"Liste de référence : {len(supp)} entrées")
    seen = {norm_title(r["title"]) for r in supp}
    works = fetch_orcid_works()
    print(f"ORCID : {len(works)} travaux")
    added = 0
    for w in works:
        if norm_title(w["title"]) in seen:
            continue
        rec = orcid_to_record(w)
        if w["doi"]:
            time.sleep(PAUSE)
        supp.append(rec)
        seen.add(norm_title(w["title"]))
        added += 1
        print(f"  + nouvel article ORCID : {w['title'][:60]}")
    print(f"Ajouts ORCID : {added}")
    for lang, fn in (("fr", "publications.qmd"), ("en", "publications_en.qmd")):
        page, total = build_page(supp, lang)
        (DIR / fn).write_text(page, encoding="utf-8")
        print(f"✓ {fn} ({total} entrées)")
    print("Terminé.")


if __name__ == "__main__":
    main()
