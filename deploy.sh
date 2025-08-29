#!/bin/bash

echo "🚀 AI Test Generator - Deployment Helper"
echo "========================================"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository. Please run this from your project root."
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  You have uncommitted changes. Please commit them first:"
    git status --short
    echo ""
    read -p "Do you want to commit all changes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Prepare for deployment"
        echo "✅ Changes committed"
    else
        echo "❌ Please commit your changes before deploying"
        exit 1
    fi
else
    echo "✅ Working directory is clean"
fi

# Push to remote
echo "📤 Pushing to remote repository..."
if git push origin main; then
    echo "✅ Code pushed to GitHub"
else
    echo "❌ Failed to push to GitHub. Please check your remote configuration."
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Deploy backend to Railway: https://railway.app"
echo "2. Deploy frontend to Vercel: https://vercel.com"
echo "3. Update CORS settings with your frontend domain"
echo "4. Set environment variables (GROQ_API_KEY, etc.)"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
echo ""
echo "🔑 Don't forget to set your GROQ_API_KEY in Railway!"
