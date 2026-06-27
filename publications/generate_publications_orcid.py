#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère publications.qmd (FR) et publications_en.qmd (EN) à partir d'un profil ORCID.

- Lit la liste des travaux depuis l'API publique ORCID.
- Enrichit chaque référence (auteurs complets, revue, volume, pages) via Crossref (par DOI).
- Regroupe par catégorie et par année, met votre nom en gras.
- N'utilise que la bibliothèque standard Python : AUCUNE installation requise.
- Nécessite un accès Internet au moment de l'exécution.

ATTENTION : ce script ÉCRASE publications.qmd et publications_en.qmd.

Usage (depuis le dossier du projet) :
    python publications/generate_publications_orcid.py
puis :
    quarto render
"""

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ------------------------------------------------------------------ CONFIG
ORCID_ID    = "0000-0001-7774-4460"
CONTACT     = "dany.lauzon@polymtl.ca"          # politesse API (User-Agent)
BOLD_FAMILY = "lauzon"                           # nom de famille à mettre en gras
OWNER       = ("Lauzon", "Dany")                 # auteur par défaut si la source n'en liste aucun
OUT_DIR     = Path(__file__).resolve().parent    # dossier publications/
TIMEOUT     = 30
PAUSE       = 0.34                                # délai entre appels réseau (politesse)

UA = f"GeoStatPoly-website/1.0 (mailto:{CONTACT})"

# Ordre + titres des sections (FR / EN)
SECTIONS = ["journal", "conference", "thesis", "book", "other"]
TITLES = {
    "fr": {
        "journal":    "Articles de revue par les pairs",
        "conference": "Résumés et articles de conférence",
        "thesis":     "Thèses",
        "book":       "Livres et ressources pédagogiques",
        "other":      "Autres contributions",
        "page":       "Publications",
        "updated":    "Dernière mise à jour",
        "total":      "publications",
        "source":     "Généré automatiquement depuis",
    },
    "en": {
        "journal":    "Peer-reviewed journal articles",
        "conference": "Conference abstracts and papers",
        "thesis":     "Theses",
        "book":       "Books and educational resources",
        "other":      "Other contributions",
        "page":       "Publications",
        "updated":    "Last updated",
        "total":      "publications",
        "source":     "Automatically generated from",
    },
}
MONTHS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]
MONTHS_EN = ["", "January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]

ORCID_TYPE_MAP = {
    "journal-article": "journal",
    "conference-paper": "conference",
    "conference-abstract": "conference",
    "conference-poster": "conference",
    "lecture-speech": "conference",
    "dissertation-thesis": "thesis",
    "dissertation": "thesis",
    "supervised-student-publication": "journal",
    "book": "book",
    "book-chapter": "book",
    "edited-book": "book",
    "report": "book",
}


# ------------------------------------------------------------------ HTTP
def http_get(url, accept):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt == 2:
                print(f"  ! échec réseau pour {url} ({e})", file=sys.stderr)
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


# ------------------------------------------------------------------ ORCID
def fetch_orcid_works():
    url = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
    data = http_get(url, "application/json")
    if not data:
        sys.exit("Impossible de joindre l'API ORCID. Vérifiez votre connexion / l'identifiant.")
    works = []
    for group in data.get("group", []):
        s = group.get("work-summary", [{}])[0]
        doi = None
        for ext in (s.get("external-ids") or {}).get("external-id", []):
            if (ext.get("external-id-type") or "").lower() == "doi":
                doi = (ext.get("external-id-value") or "").strip()
                break
        year = None
        pd = s.get("publication-date")
        if pd and pd.get("year"):
            year = pd["year"].get("value")
        works.append({
            "title": (s.get("title") or {}).get("title", {}).get("value", "Sans titre"),
            "journal": (s.get("journal-title") or {}).get("value") if s.get("journal-title") else None,
            "type": (s.get("type") or "other"),
            "year": year,
            "doi": doi,
        })
    return works


# ------------------------------------------------------------------ Crossref / DOI
def fetch_csl(doi):
    url = f"https://doi.org/{doi}"
    return http_get(url, "application/vnd.citationstyles.csl+json")


# ------------------------------------------------------------------ Normalisation
def csl_year(csl):
    for k in ("issued", "published-print", "published-online"):
        dp = (csl.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return None


def build_record(w):
    """Combine les données ORCID + Crossref en un enregistrement unifié."""
    csl = fetch_csl(w["doi"]) if w["doi"] else None
    if csl:
        authors = [(a.get("family", "").strip(), a.get("given", "").strip())
                   for a in csl.get("author", []) if a.get("family") or a.get("given")]
        rec = {
            "authors": authors,
            "title": (csl.get("title") or w["title"]).strip().rstrip("."),
            "container": (csl.get("container-title") or w["journal"] or "").strip(),
            "volume": str(csl.get("volume", "")).strip(),
            "issue": str(csl.get("issue", "")).strip(),
            "page": str(csl.get("page", "")).strip(),
            "year": csl_year(csl) or w["year"],
            "doi": w["doi"],
        }
    else:
        rec = {
            "authors": [], "title": w["title"].strip().rstrip("."),
            "container": (w["journal"] or "").strip(), "volume": "", "issue": "",
            "page": "", "year": w["year"], "doi": w["doi"],
        }
    if not rec["authors"]:
        rec["authors"] = [OWNER]
    rec["category"] = ORCID_TYPE_MAP.get(w["type"], "other")
    return rec


# ------------------------------------------------------------------ Formatage
def format_authors(authors):
    if not authors:
        return ""
    parts = []
    for fam, giv in authors:
        name = f"{fam}, {giv}" if giv else fam
        if fam.lower() == BOLD_FAMILY:
            name = f"**{name}**"
        parts.append(name)
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", & " + parts[-1]


def format_entry(rec):
    bits = []
    auth = format_authors(rec["authors"])
    if auth:
        bits.append(auth)
    yr = f"({rec['year']})" if rec["year"] else ""
    if yr:
        bits.append(yr)
    line = " ".join(bits)
    if line:
        line += ". "
    line += rec["title"] + "."
    if rec["container"]:
        line += f" *{rec['container']}*"
        if rec["volume"]:
            line += f", *{rec['volume']}*"
            if rec["issue"]:
                line += f"({rec['issue']})"
        if rec["page"]:
            line += f", {rec['page']}"
        line += "."
    if rec["doi"]:
        line += f" [DOI](https://doi.org/{rec['doi']})"
    return line.strip()


def build_page(records, lang):
    t = TITLES[lang]
    today = time.localtime()
    months = MONTHS_FR if lang == "fr" else MONTHS_EN
    date_str = f"{months[today.tm_mon]} {today.tm_year}"

    out = ["---", f'title: "{t["page"]}"', "---", ""]
    total = 0
    for cat in SECTIONS:
        recs = [r for r in records if r["category"] == cat]
        if not recs:
            continue
        out.append(f"## {t[cat]}")
        out.append("")
        years = sorted({r["year"] for r in recs if r["year"]},
                       key=lambda y: int(y), reverse=True)
        no_year = [r for r in recs if not r["year"]]
        for y in years:
            out.append(f"### {y}")
            out.append("")
            for r in [x for x in recs if x["year"] == y]:
                out.append("::: {.publication-item}")
                out.append(format_entry(r))
                out.append(":::")
                out.append("")
                total += 1
        for r in no_year:
            out.append("::: {.publication-item}")
            out.append(format_entry(r))
            out.append(":::")
            out.append("")
            total += 1

    out.append("---")
    out.append("")
    out.append(f'*{t["total"].capitalize()}: {total} · {t["updated"]}: {date_str} · '
               f'{t["source"]} [ORCID](https://orcid.org/{ORCID_ID})*')
    return "\n".join(out) + "\n", total


# ------------------------------------------------------------------ Main
def main():
    print(f"→ Lecture du profil ORCID {ORCID_ID} …")
    works = fetch_orcid_works()
    print(f"  {len(works)} travaux trouvés. Enrichissement via Crossref …")
    records = []
    for i, w in enumerate(works, 1):
        records.append(build_record(w))
        if w["doi"]:
            time.sleep(PAUSE)
        print(f"  [{i}/{len(works)}] {w['title'][:60]}")

    for lang, fname in (("fr", "publications.qmd"), ("en", "publications_en.qmd")):
        page, total = build_page(records, lang)
        (OUT_DIR / fname).write_text(page, encoding="utf-8")
        print(f"✓ {fname} écrit ({total} entrées)")

    print("Terminé. Relancez `quarto render` pour mettre à jour le site.")


if __name__ == "__main__":
    main()
