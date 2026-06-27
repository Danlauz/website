# Dany Lauzon - Academic Website

A modern, bilingual (French/English) academic website built with Quarto, featuring dark/light mode toggle and responsive design.

## 🌟 Features

- ✅ **Fully Bilingual**: Complete French and English versions
- ✅ **Dark/Light Mode**: Seamless theme switching
- ✅ **Modern Design**: Professional academic styling with Polytechnique Montréal branding
- ✅ **Responsive**: Works perfectly on desktop, tablet, and mobile
- ✅ **Publications Management**: Organized display of articles, conferences, and thesis
- ✅ **Course Materials**: Integrated course notes and educational resources
- ✅ **Code Showcases**: Highlight open-source projects
- ✅ **Student Portal**: Information for prospective and current students

## 📁 Structure

```
dany-lauzon-website/
├── _quarto.yml              # Main configuration file
├── custom.scss              # Light theme styling
├── custom-dark.scss         # Dark theme styling
├── styles.css               # Additional CSS
├── index.qmd                # French homepage
├── cv.qmd                   # French CV
├── etudiants.qmd            # French students page
├── publications/
│   ├── articles.qmd         # French articles
│   ├── conferences.qmd      # French conferences
│   └── these.qmd            # French thesis
├── cours/
│   ├── geostatistique.qmd   # French course notes
│   └── livre.qmd            # French book page
└── en/                      # English version
    ├── index.qmd
    ├── cv.qmd
    ├── students.qmd
    ├── publications/
    │   ├── articles.qmd
    │   ├── conferences.qmd
    │   └── thesis.qmd
    └── courses/
        ├── geostatistics.qmd
        └── book.qmd
```

## 🚀 Getting Started

### Prerequisites

Install Quarto from https://quarto.org/docs/get-started/

### Build the Website

```bash
# Navigate to the website directory
cd dany-lauzon-website

# Preview the site locally
quarto preview

# Build the site for deployment
quarto render
```

The rendered website will be in the `_site/` directory.

## 🎨 Customization

### Colors

Edit the colors in `custom.scss` and `custom-dark.scss`:

```scss
$primary: #00559f;  // Polytechnique blue
```

### Content

All content is in `.qmd` files. Simply edit the Markdown content:

- **Homepage**: `index.qmd` (French) or `en/index.qmd` (English)
- **CV**: `cv.qmd` (French) or `en/cv.qmd` (English)
- **Publications**: Files in `publications/` or `en/publications/`
- **Course materials**: Files in `cours/` or `en/courses/`

### Navigation

Edit the sidebar structure in `_quarto.yml`:

```yaml
sidebar:
  - id: sidebar-fr
    contents:
      - text: "Accueil"
        file: index.qmd
      # Add more items...
```

## 📝 Adding Content

### Add a New Publication

Edit `publications/articles.qmd`:

```markdown
::: {.publication-item}
#### Title of the Article
::: {.authors}
**Lauzon, D.**, Co-author, A.
:::
::: {.venue}
*Journal Name*, Volume(Issue), Pages
:::
[{{< fa file-pdf >}} PDF](#) | [{{< fa link >}} DOI](#)
:::
```

### Add a New Course Module

Edit `cours/geostatistique.qmd`:

```markdown
::: {.publication-item}
#### Module Title
- Concept 1
- Concept 2
- Concept 3

[{{< fa download >}} Notes (PDF)](#) | [{{< fa code >}} Python Notebook](#)
:::
```

## 🌐 Deployment

### GitHub Pages

1. Create a GitHub repository
2. Push your code
3. Enable GitHub Pages in repository settings
4. Set source to `gh-pages` branch or `docs` folder

### Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `quarto render`
3. Set publish directory: `_site`

### Custom Server

Upload the contents of `_site/` to your web server.

## 🔗 Links to Update

Before deploying, update these links in your files:

- GitHub profile URL
- LinkedIn profile URL
- Email address
- Institution URLs
- PDF download links
- DOI links
- Code repository links

Search for `#` placeholders in `.qmd` files and replace with actual URLs.

## 📧 Contact

**Dany Lauzon**  
Polytechnique Montréal  
Email: dany.lauzon@polymtl.ca

## 📄 License

This website template is open source. Feel free to use it for your own academic website.

## 🙏 Acknowledgments

- Built with [Quarto](https://quarto.org)
- Inspired by [Charles L. Bérubé's website](https://charles-berube.netlify.app)
- Styling inspired by Polytechnique Montréal branding

---

*Website created January 2025*
