#!/bin/bash

# Build script for Vercel deployment

set -e  # Exit on error

echo "🔨 Building Research Agent Pro..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build frontend
echo "🔧 Building frontend..."
npm run build

# Verify Python dependencies are available
echo "🐍 Verifying Python setup..."
python3 -m pip install -q -r requirements.txt

echo "✅ Build completed successfully!!"
