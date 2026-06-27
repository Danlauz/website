#!/bin/bash

# Quick Start Script for Dany Lauzon's Website
# This script helps you get started with building and previewing the site

echo "🌐 Dany Lauzon's Academic Website - Quick Start"
echo "================================================"
echo ""

# Check if Quarto is installed
if ! command -v quarto &> /dev/null; then
    echo "❌ Quarto is not installed!"
    echo ""
    echo "Please install Quarto from: https://quarto.org/docs/get-started/"
    echo ""
    echo "Installation commands:"
    echo "  macOS:   brew install quarto"
    echo "  Linux:   Download from https://quarto.org/docs/download/"
    echo "  Windows: Download installer from https://quarto.org/docs/download/"
    exit 1
fi

echo "✅ Quarto is installed"
echo ""

# Display menu
echo "What would you like to do?"
echo ""
echo "1. Preview the website (opens in browser)"
echo "2. Build the website for deployment"
echo "3. Clean build files"
echo "4. Check Quarto version"
echo "5. Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting preview server..."
        echo "The website will open in your browser at http://localhost:XXXX"
        echo "Press Ctrl+C to stop the server"
        echo ""
        quarto preview
        ;;
    2)
        echo ""
        echo "🔨 Building website..."
        quarto render
        echo ""
        echo "✅ Website built successfully!"
        echo "📁 Output files are in the _site/ directory"
        echo ""
        echo "To deploy:"
        echo "  - Upload the contents of _site/ to your web server"
        echo "  - Or push to GitHub and enable GitHub Pages"
        echo "  - Or connect to Netlify for automatic deployment"
        ;;
    3)
        echo ""
        echo "🧹 Cleaning build files..."
        rm -rf _site/
        rm -rf .quarto/
        echo "✅ Clean complete!"
        ;;
    4)
        echo ""
        quarto --version
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "For more information, see README.md"
