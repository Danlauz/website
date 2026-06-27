# Assets Folder

## 📁 What Goes Here

This folder contains all media assets for your website:

### Logo
- **File:** `logo.png`
- **Recommended size:** 200x50 pixels (or similar horizontal format)
- **Format:** PNG with transparent background (or SVG)
- **Used in:** Navigation bar (top-left corner)

### Other Assets (Optional)
You can also add:
- `profile.jpg` - Your profile photo
- `favicon.ico` - Browser tab icon
- Any images used in your pages

## 🎨 Adding Your Logo

1. **Copy your logo file** to this folder
2. **Name it:** `logo.png` (or update the path in `_quarto.yml`)
3. **That's it!** The site is already configured to use it

## 📐 Logo Guidelines

**Good logo characteristics:**
- ✅ Horizontal/landscape orientation
- ✅ Clear and readable when small
- ✅ Good contrast with blue navbar background
- ✅ Transparent background (PNG)

**Recommended dimensions:**
- Width: 150-250 pixels
- Height: 40-60 pixels

## 🔗 Configuration

The logo is configured in `_quarto.yml`:
```yaml
navbar:
  logo: assets/logo.png
```

## 📝 Example Files to Add

```
assets/
├── logo.png           ← Your logo (REQUIRED for navbar)
├── profile.jpg        ← Your photo (optional, for homepage)
├── favicon.ico        ← Browser icon (optional)
└── README.md          ← This file
```

---

**Note:** Currently, the logo path is configured but the file doesn't exist yet. Add your `logo.png` file here to display it on the website!
