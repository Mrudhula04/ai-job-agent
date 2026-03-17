#!/bin/bash
echo "🚀 Setting up AI Job Finder Agent..."

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
chmod +x job-finder-agent.py
chmod +x schedule_daily.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit my_profile.json with your details"
echo "2. Run: python3 job-finder-agent.py"
