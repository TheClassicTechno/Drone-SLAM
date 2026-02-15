#!/bin/bash
# MedWing Quick Demo Setup Script
# For TreeHacks 2026

set -e  # Exit on error

echo "🚁 MedWing - Quick Setup"
echo "========================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
echo "✅ Prerequisites OK"
echo ""

# Setup backend
echo "🔧 Setting up backend..."
cd voice_agent

if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit voice_agent/.env with your API keys before running"
fi

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Backend setup complete"
echo ""

cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontendWeb

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node modules already installed"
fi

echo "✅ Frontend setup complete"
echo ""

cd ..

# Summary
echo "🎉 Setup Complete!"
echo "===================="
echo ""
echo "📝 Next Steps:"
echo "1. Edit voice_agent/.env with your API keys (VAPI, Zoom, etc.)"
echo ""
echo "2. Start the backend:"
echo "   cd voice_agent"
echo "   source venv/bin/activate"
echo "   python webhook_server.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontendWeb"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "🚀 For demo: Call your VAPI phone number and test voice ordering!"
echo ""
