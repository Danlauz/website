# -*- coding: utf-8 -*-
"""Génère un CV PDF soigné (FR + EN) à partir du contenu du CV.
Dépendance : reportlab (pip install reportlab). Sortie : à côté de ce script.
   python generate_cv.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

ACCENT = colors.HexColor("#F15A22")
INK    = colors.HexColor("#15181d")
MUTED  = colors.HexColor("#646c78")
OUT    = os.path.dirname(os.path.abspath(__file__))

def esc(t):
    return t.replace("&", "&amp;")

S = {
 'name':   ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=21, leading=24, textColor=INK),
 'title':  ParagraphStyle('title', fontName='Helvetica', fontSize=12.5, leading=15, textColor=ACCENT, spaceBefore=2),
 'affil':  ParagraphStyle('affil', fontName='Helvetica', fontSize=9.5, leading=12.5, textColor=MUTED, spaceBefore=1),
 'contact':ParagraphStyle('contact', fontName='Helvetica', fontSize=8.5, leading=12, textColor=MUTED, spaceBefore=5),
 'sec':    ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=ACCENT, spaceBefore=12, spaceAfter=2),
 'etitle': ParagraphStyle('etitle', fontName='Helvetica-Bold', fontSize=10.3, leading=12.5, textColor=INK, spaceBefore=6),
 'meta':   ParagraphStyle('meta', fontName='Helvetica', fontSize=9, leading=11.5, textColor=MUTED),
 'body':   ParagraphStyle('body', fontName='Helvetica', fontSize=9.3, leading=12.6, textColor=INK, spaceBefore=1),
 'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=9.3, leading=12.6, textColor=INK,
                          leftIndent=12, firstLineIndent=-12, spaceBefore=1.5),
}

def rule(flow):
    flow.append(Spacer(1, 2)); flow.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceAfter=1))

def section(flow, t):
    flow.append(Paragraph(esc(t), S['sec'])); rule(flow)

def entry(flow, title, meta, lines):
    flow.append(Paragraph(esc(title), S['etitle']))
    if meta: flow.append(Paragraph(esc(meta), S['meta']))
    for ln in lines: flow.append(Paragraph(esc(ln), S['body']))

def bullets(flow, items):
    for it in items:
        flow.append(Paragraph('<font color="#F15A22">&#9642;</font>&nbsp;&nbsp;' + esc(it), S['bullet']))

def header(flow, c):
    flow.append(Paragraph(c['name'], S['name']))
    flow.append(Paragraph(c['title'], S['title']))
    flow.append(Paragraph(c['affil'], S['affil']))
    links = " &nbsp;·&nbsp; ".join('<link href="%s"><font color="#F15A22">%s</font></link>' % (esc(u), esc(t)) for t, u in c['links'])
    flow.append(Paragraph(links, S['contact']))
    rule(flow)

def build(c, fn):
    doc = SimpleDocTemplate(os.path.join(OUT, fn), pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=14*mm,
                            title="CV — Dany Lauzon", author="Dany Lauzon")
    flow = []
    header(flow, c)
    for sec in c['sections']:
        section(flow, sec['h'])
        for e in sec.get('entries', []):
            entry(flow, e[0], e[1], e[2])
        if sec.get('bullets'):
            bullets(flow, sec['bullets'])
    doc.build(flow)
    print("OK", fn)

EMAIL = "dany.lauzon@polymtl.ca"
LINKS = [("dany.lauzon@polymtl.ca", "mailto:dany.lauzon@polymtl.ca"),
         ("GitHub", "https://github.com/Danlauz"),
         ("LinkedIn", "https://ca.linkedin.com/in/dany-lauzon-ph-d-ba9128115"),
         ("Google Scholar", "https://scholar.google.com/citations?user=1ltoBQIAAAAJ&hl=fr"),
         ("ORCID", "https://orcid.org/0000-0001-7774-4460")]

fr = {
 'name': "Dany Lauzon, Ph.D. (CPI)",
 'title': "Professeur adjoint en géostatistique",
 'affil': "Polytechnique Montréal — Département des génies civil, géologique et des mines",
 'links': LINKS,
 'sections': [
   {'h': "Formation", 'entries': [
      ("Doctorat en génie minéral", "Polytechnique Montréal · 2019–2022",
       ["<i>Thèse : Développement d'algorithmes pour le calage de modèles géologiques par méthodes géostatistiques discrètes et spectrales</i>",
        "Directeur : Denis Marcotte"]),
      ("Baccalauréat en génie géologique, spécialisation en environnement", "Polytechnique Montréal · 2015–2019", []),
   ]},
   {'h': "Expérience professionnelle", 'entries': [
      ("Professeur adjoint", "Polytechnique Montréal — Génies civil, géologique et des mines · 2024–présent", []),
      ("Stage post-doctoral", "Université de Neuchâtel · 2023–2024",
       ["<i>Projet : Simulation stochastique des réseaux karstiques par modèle génératif profond pour l'écoulement des eaux souterraines</i>",
        "Superviseur : Philippe Renard"]),
      ("Stage post-doctoral", "INRS — Centre Eau Terre et Environnement · 2022–2023",
       ["<i>Projet : Quantifier l'incertitude et améliorer la cartographie de la prospectivité dans les ceintures minérales à l'aide de l'apprentissage par transfert</i>",
        "Superviseur : Erwan Gloaguen"]),
   ]},
   {'h': "Domaines d'expertise", 'bullets': [
      "Géologie mathématique", "Processus stochastiques", "Eaux souterraines", "Algorithmes", "Modélisation et simulation"]},
   {'h': "Prix", 'bullets': [
      "<b>Bourse d'études supérieures du Canada Alexander Graham Bell – Doctorat (BES D)</b> (2021–2022) — CRSNG",
      "<b>Bourse d'études supérieures en recherche du Canada – Maîtrise (BESRC M)</b> (2019–2021) — CRSNG",
      "<b>Bourse de recherche de 1er cycle (BRPC)</b> (2018) — CRSNG + FRQNT (supplément)"]},
   {'h': "Distinctions", 'bullets': [
      "Lauréat du titre de meilleur enseignant du programme de génie des mines de Polytechnique Montréal (2026)",
      "Finaliste au titre de meilleur enseignant du programme de génie géologique de Polytechnique Montréal (2026)",
      "Lauréat du titre de meilleur enseignant du programme de génie géologique de Polytechnique Montréal (2025)",
      "Lauréat du titre de meilleur chargé de cours du programme de génie géologique de Polytechnique Montréal (2024)",
      "Lauréat du titre de meilleur chargé de cours du programme de génie géologique de Polytechnique Montréal (2023)",
      "Médaille du lieutenant-gouverneur pour la jeunesse (2020)"]},
   {'h': "Associations", 'bullets': [
      "Président et membre fondateur de l'Association des hydrogéosciences du Québec (AHGSQC)"]},
   {'h': "Affiliations professionnelles et sociétés savantes", 'bullets': [
      "Association des hydrogéosciences du Québec (AHGSQC)",
      "International Association for Mathematical Geosciences (IAMG)",
      "Société canadienne de géotechnique (CGS)",
      "International Association of Hydrogeologists (IAH)",
      "European Geosciences Union (EGU)", "American Geophysical Union (AGU)",
      "Ordre des ingénieurs du Québec (OIQ) — candidat à la profession d'ingénieur (CPI)"]},
   {'h': "Organisation de conférence", 'bullets': [
      "Membre du comité scientifique et organisateur de la 24e Conférence annuelle de l'IAMG à Montréal en 2026 (+250 participants attendus de l'international)",
      "Membre du comité scientifique et organisateur de la 2e Conférence annuelle de l'AHGSQC à l'INRS — Centre Eau Terre Environnement en 2026",
      "Membre du comité scientifique et organisateur de la 1re Conférence annuelle de l'AHGSQC à Polytechnique Montréal en 2025 (51 participants)"]},
   {'h': "Langues", 'bullets': [
      "<b>Français</b> : langue maternelle", "<b>Anglais</b> : bilingue professionnel"]},
 ],
}

en = {
 'name': "Dany Lauzon, Ph.D. (P.Eng.)",
 'title': "Assistant Professor in Geostatistics",
 'affil': "Polytechnique Montréal — Department of Civil, Geological and Mining Engineering",
 'links': LINKS,
 'sections': [
   {'h': "Education", 'entries': [
      ("Ph.D. in Mineral Engineering", "Polytechnique Montréal · 2019–2022",
       ["<i>Thesis: Development of algorithms for calibrating geological models using discrete and spectral geostatistical methods</i>",
        "Supervisor: Denis Marcotte"]),
      ("Bachelor in Geological Engineering, specialization in Environment", "Polytechnique Montréal · 2015–2019", []),
   ]},
   {'h': "Professional Experience", 'entries': [
      ("Assistant Professor", "Polytechnique Montréal — Civil, Geological and Mining Engineering · 2024–present", []),
      ("Postdoctoral Fellow", "University of Neuchâtel · 2023–2024",
       ["<i>Project: Stochastic simulation of karst networks using deep generative models for groundwater flow</i>",
        "Supervisor: Philippe Renard"]),
      ("Postdoctoral Fellow", "INRS — Water Earth and Environment Research Centre · 2022–2023",
       ["<i>Project: Quantifying uncertainty and improving prospectivity mapping in mineral belts using transfer learning</i>",
        "Supervisor: Erwan Gloaguen"]),
   ]},
   {'h': "Areas of Expertise", 'bullets': [
      "Mathematical geology", "Stochastic processes", "Groundwater", "Algorithms", "Modeling and simulation"]},
   {'h': "Awards", 'bullets': [
      "<b>Alexander Graham Bell Canada Graduate Scholarship – Doctoral (CGS D)</b> (2021–2022) — NSERC",
      "<b>Canada Graduate Scholarship – Master's (CGS M)</b> (2019–2021) — NSERC",
      "<b>Undergraduate Student Research Award (USRA)</b> (2018) — NSERC + FRQNT (supplement)"]},
   {'h': "Distinctions", 'bullets': [
      "Recipient of the Best Instructor award, Mining Engineering program, Polytechnique Montréal (2026)",
      "Candidate for the Best Instructor award, Geological Engineering program, Polytechnique Montréal (2026)",
      "Recipient of the Best Instructor award, Geological Engineering program, Polytechnique Montréal (2025)",
      "Recipient of the Best Lecturer award, Geological Engineering program, Polytechnique Montréal (2024)",
      "Recipient of the Best Lecturer award, Geological Engineering program, Polytechnique Montréal (2023)",
      "Lieutenant Governor's Youth Medal (2020)"]},
   {'h': "Associations", 'bullets': [
      "President and founding member of the Association des hydrogéosciences du Québec (AHGSQC)"]},
   {'h': "Professional Affiliations", 'bullets': [
      "Association des hydrogéosciences du Québec (AHGSQC)",
      "International Association for Mathematical Geosciences (IAMG)",
      "Canadian Geotechnical Society (CGS)",
      "International Association of Hydrogeologists (IAH)",
      "European Geosciences Union (EGU)", "American Geophysical Union (AGU)",
      "Ordre des ingénieurs du Québec (OIQ — P.Eng.)"]},
   {'h': "Conference Organization", 'bullets': [
      "Member of the scientific and organizing committee of the 24th Annual Conference of the IAMG in Montreal, 2026 (250+ international attendees expected)",
      "Member of the scientific and organizing committee of the 2nd Annual Conference of the AHGSQC at INRS, 2026",
      "Member of the scientific and organizing committee of the 1st Annual Conference of the AHGSQC at Polytechnique Montréal, 2025 (51 attendees)"]},
   {'h': "Languages", 'bullets': [
      "<b>French</b>: native language", "<b>English</b>: professional bilingual"]},
 ],
}

build(fr, "cv-dany-lauzon.pdf")
build(en, "cv-dany-lauzon-en.pdf")
