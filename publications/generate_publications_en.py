#!/usr/bin/env python3
"""
Generate a single clean publication page from BibTeX files (English version)
Author: Dany Lauzon
Date: 2026-02-02

Usage:
    python generate_publications_simple_en.py

Generates a single page with all publications in clean APA style.
"""

from pathlib import Path
import re


class SimpleBibParser:
    """Simple BibTeX parser without external dependencies"""
    
    @staticmethod
    def parse_bib_file(filepath):
        """Parse a BibTeX file and return list of entry dictionaries"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        entries = []
        
        # Find all @type{key, ... } blocks
        pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,\s*(.*?)\n\}'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            entry_type = match.group(1).lower()
            entry_key = match.group(2).strip()
            fields_str = match.group(3)
            
            entry = {
                'ENTRYTYPE': entry_type,
                'ID': entry_key
            }
            
            # Parse fields
            field_pattern = r'(\w+)\s*=\s*[{"](.*?)["}]\s*(?:,|$)'
            field_matches = re.finditer(field_pattern, fields_str, re.DOTALL)
            
            for field_match in field_matches:
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2).strip()
                entry[field_name] = field_value
            
            entries.append(entry)
        
        return entries


class APAPublicationGenerator:
    """Generate simple APA-style publication list"""
    
    def __init__(self, author_name="Lauzon, D.", author_variants=None):
        self.author_name = author_name
        self.author_variants = author_variants or [
            "Lauzon, Dany",
            "Dany Lauzon", 
            "D. Lauzon",
            "Lauzon, D."
        ]
        self.parser = SimpleBibParser()
        
    def parse_bib_file(self, filepath):
        """Parse a BibTeX file and return entries"""
        if not Path(filepath).exists():
            return []
        return self.parser.parse_bib_file(filepath)
    
    def format_authors_apa(self, authors_str):
        """Format author list in APA style with main author bolded"""
        if not authors_str:
            return ""
        
        # Split authors by 'and'
        authors = [a.strip() for a in authors_str.split(' and ')]
        
        formatted_authors = []
        for author in authors:
            # Check if this is our author (any variant)
            is_main_author = any(
                variant.lower() in author.lower() 
                for variant in self.author_variants
            )
            
            if is_main_author:
                formatted_authors.append(f"**{author}**")
            else:
                formatted_authors.append(author)
        
        # APA style: comma-separated with & before last author
        if len(formatted_authors) == 1:
            return formatted_authors[0]
        elif len(formatted_authors) == 2:
            return f"{formatted_authors[0]}, & {formatted_authors[1]}"
        else:
            return ", ".join(formatted_authors[:-1]) + f", & {formatted_authors[-1]}"
    
    def clean_latex(self, text):
        """Remove LaTeX formatting from text"""
        if not text:
            return text
        # Remove curly braces used for capitalization
        text = re.sub(r'\{([^}]*)\}', r'\1', text)
        # Remove backslashes
        text = text.replace('\\&', '&')
        return text
    
    def format_entry_apa(self, entry):
        """Format a single entry in APA style"""
        entry_type = entry.get('ENTRYTYPE', '')
        
        # Authors
        authors = self.format_authors_apa(entry.get('author', ''))
        
        # Year
        year = entry.get('year', 'n.d.')
        
        # Title
        title = self.clean_latex(entry.get('title', 'Untitled'))
        
        # Build citation based on type
        parts = []
        
        if authors:
            parts.append(f"{authors} ({year}).")
        else:
            parts.append(f"({year}).")
        
        # Add title and venue based on type
        if entry_type == 'article':
            # Journal article
            parts.append(f"{title}.")
            journal = self.clean_latex(entry.get('journal', ''))
            volume = entry.get('volume', '')
            number = entry.get('number', '')
            pages = entry.get('pages', '')
            
            venue_parts = []
            if journal:
                venue_parts.append(f"*{journal}*")
            if volume:
                if number:
                    venue_parts.append(f"*{volume}*({number})")
                else:
                    venue_parts.append(f"*{volume}*")
            if pages:
                venue_parts.append(pages)
            
            if venue_parts:
                parts.append(", ".join(venue_parts) + ".")
        
        elif entry_type in ['inproceedings', 'conference']:
            # Conference paper
            parts.append(f"{title}.")
            booktitle = self.clean_latex(entry.get('booktitle', ''))
            address = entry.get('address', '')
            pages = entry.get('pages', '')
            
            venue_parts = []
            if booktitle:
                venue_parts.append(f"*{booktitle}*")
            if pages:
                venue_parts.append(f"pp. {pages}")
            
            # Add location if available
            if venue_parts:
                parts.append(", ".join(venue_parts) + ".")
            
            if address:
                parts.append(f"{address}.")
        
        elif entry_type == 'phdthesis':
            # Thesis
            parts.append(f"*{title}*.")
            school = entry.get('school', '')
            thesis_type = entry.get('type', 'PhD thesis')
            
            if school:
                parts.append(f"{thesis_type}, {school}.")
            else:
                parts.append(f"{thesis_type}.")
        
        elif entry_type == 'book':
            # Book
            parts.append(f"*{title}*.")
            publisher = entry.get('publisher', '')
            address = entry.get('address', '')
            
            pub_parts = []
            if address:
                pub_parts.append(address)
            if publisher:
                pub_parts.append(publisher)
            
            if pub_parts:
                parts.append(": ".join(pub_parts) + ".")
        
        elif entry_type == 'misc':
            # Misc publications
            parts.append(f"{title}.")
            pub_type = self.clean_latex(entry.get('type', ''))
            journal = self.clean_latex(entry.get('journal', ''))
            
            if journal:
                parts.append(f"*{journal}*.")
            elif pub_type:
                parts.append(f"*{pub_type}*.")
        
        else:
            # Fallback
            parts.append(f"{title}.")
        
        # Add DOI or URL at the end
        doi = entry.get('doi', '')
        url = entry.get('url', '')
        
        citation = " ".join(parts)
        
        if doi:
            doi_url = f"https://doi.org/{doi}"
            citation += f" [DOI]({doi_url})"
        elif url:
            citation += f" [Link]({url})"
        
        return citation
    
    def group_entries_by_category_and_year(self, categories):
        """Group all entries by category first, then by year within each category"""
        by_category = {
            'Peer-reviewed journal articles': {},
            'Conference abstracts and presentations': {},
            'Theses': {},
            'Books and educational resources': {}
        }
        
        for category, entries in categories.items():
            for entry in entries:
                year = entry.get('year', 'n.d.')
                if year not in by_category[category]:
                    by_category[category][year] = []
                by_category[category][year].append(entry)
        
        # Sort years within each category (descending)
        for category in by_category:
            years = by_category[category].keys()
            sorted_years = sorted(
                [y for y in years if y.isdigit()], 
                key=int, 
                reverse=True
            )
            by_category[category]['_sorted_years'] = sorted_years
        
        return by_category
    
    def generate_unified_page(self, bib_files, output_file="publications.qmd"):
        """Generate a single page with all publications grouped by type"""
        
        print("=" * 70)
        print("📚 Generating unified publications page")
        print("=" * 70)
        print()
        
        # Load all entries by category
        categories = {
            'Peer-reviewed journal articles': [],
            'Conference abstracts and presentations': [],
            'Theses': [],
            'Books and educational resources': []
        }
        
        # Parse each file
        for category, bib_file in bib_files.items():
            if not Path(bib_file).exists():
                print(f"⚠️  {bib_file} not found, skipping...")
                continue
            
            print(f"📖 Reading {bib_file}...")
            entries = self.parse_bib_file(bib_file)
            
            if entries:
                categories[category] = entries
                print(f"  ✓ {len(entries)} entry(ies) found")
            else:
                print(f"  ⚠️  No entries found")
        
        print()
        
        # Group all entries by category first, then year
        by_category = self.group_entries_by_category_and_year(categories)
        
        # Category display order
        category_order = [
            'Peer-reviewed journal articles',
            'Conference abstracts and presentations',
            'Theses',
            'Books and educational resources'
        ]
        
        # Generate the unified page
        output = []
        
        # YAML header
        output.append("---")
        output.append('title: "Publications"')
        output.append("---")
        output.append("")
        
        # Generate sections by category, with timeline within each
        total_count = 0
        for category in category_order:
            category_data = by_category[category]
            sorted_years = category_data.get('_sorted_years', [])
            
            if not sorted_years:
                continue
            
            # Add main category header
            output.append(f"## {category}")
            output.append("")
            
            # Add entries organized by year
            for year in sorted_years:
                entries = category_data[year]
                
                if not entries:
                    continue
                
                # Add year as subheading
                output.append(f"### {year}")
                output.append("")
                
                # Add all entries for this year
                for entry in entries:
                    citation = self.format_entry_apa(entry)
                    output.append(citation)
                    output.append("")
                    total_count += 1
                
                output.append("")
        
        # Add footer
        output.append("---")
        output.append("")
        output.append(f"*Total: {total_count} publications | Last updated: February 2026*")
        
        # Write to file
        output_path = Path(output_file)
        output_path.write_text("\n".join(output), encoding='utf-8')
        
        print("=" * 70)
        print(f"✅ File created: {output_file}")
        print(f"📊 Total: {total_count} publications")
        print("=" * 70)
        print()
        
        return output_file


def main():
    """Main function"""
    
    # Initialize generator
    generator = APAPublicationGenerator(
        author_name="Lauzon, D.",
        author_variants=["Lauzon, Dany", "Dany Lauzon", "D. Lauzon", "Lauzon, D."]
    )
    
    # Configuration: category -> bib file
    bib_files = {
        'Peer-reviewed journal articles': 'MyResearch_Article.bib',
        'Conference abstracts and presentations': 'MyResearch_Conference.bib',
        'Theses': 'MyResearch_Thesis.bib',
        'Books and educational resources': 'MyResearch_Book.bib'
    }
    
    # Generate unified page
    generator.generate_unified_page(bib_files, output_file="publications_en.qmd")
    
    print("📋 Next steps:")
    print("  1. Review the generated publications_en.qmd file")
    print("  2. Add it to your _quarto.yml if needed")
    print("  3. Run 'quarto render' to build your site")
    print()


if __name__ == "__main__":
    main()
