#!/bin/bash

# Medical Drone Voice Agent - Quick Start Script
# This script guides you through the entire setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo ""
echo "                                                               "
echo "     Medical Drone Voice Agent - Quick Start Setup            "
echo "                                                               "
echo ""
echo -e "${NC}"

# Step 1: Check Python
echo -e "\n${BLUE}Step 1: Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN} Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED} Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Step 2: Check if we're in the right directory
echo -e "\n${BLUE}Step 2: Checking directory...${NC}"
if [ -d "/Users/julih/Drone-SLAM" ]; then
    cd /Users/julih/Drone-SLAM
    echo -e "${GREEN} Found project directory${NC}"
else
    echo -e "${RED} Project directory not found${NC}"
    exit 1
fi

# Step 3: Create virtual environment if it doesn't exist
echo -e "\n${BLUE}Step 3: Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN} Virtual environment created${NC}"
else
    echo -e "${GREEN} Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Step 4: Install dependencies
echo -e "\n${BLUE}Step 4: Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r voice_agent/requirements.txt
echo -e "${GREEN} Dependencies installed${NC}"

# Step 5: Check .env file
echo -e "\n${BLUE}Step 5: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW} .env file not found. Creating template...${NC}"
    cat > .env << 'EOF'
# Vapi Configuration
VAPI_API_KEY=your_vapi_key_here
VAPI_PHONE_NUMBER=

# Groq Configuration
GROQ_API_KEY=your_groq_key_here

# Deepgram Configuration (optional)
DEEPGRAM_API_KEY=your_deepgram_key_here

# Server Configuration
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok-free.app
SERVER_PORT=8000

# Drone System Configuration
ROS_MASTER_URI=http://localhost:11311
DRONE_BASE_LOCATION=pharmacy_depot
EOF
    echo -e "${YELLOW} Please edit .env file with your API keys${NC}"
    echo -e "${YELLOW}  Run: nano .env${NC}"
    echo ""
    exit 0
else
    echo -e "${GREEN} .env file exists${NC}"
fi

# Step 6: Run system tests
echo -e "\n${BLUE}Step 6: Running system tests...${NC}"
python voice_agent/test_system.py env

# Step 7: Check if ngrok is installed
echo -e "\n${BLUE}Step 7: Checking ngrok...${NC}"
if command -v ngrok &> /dev/null; then
    echo -e "${GREEN} ngrok is installed${NC}"
else
    echo -e "${YELLOW} ngrok not found${NC}"
    echo ""
    echo "Install ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  Or download: https://ngrok.com/download"
    echo ""
fi

# Step 8: Display next steps
echo -e "\n${GREEN}${NC}"
echo -e "${GREEN}                    Setup Complete!                           ${NC}"
echo -e "${GREEN}${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Start the webhook server:${NC}"
echo "   python voice_agent/webhook_server.py"
echo ""
echo -e "${YELLOW}2. In a new terminal, start ngrok:${NC}"
echo "   ngrok http 8000"
echo ""
echo -e "${YELLOW}3. Copy the ngrok URL (https://xxxx.ngrok-free.app)${NC}"
echo "   Update WEBHOOK_BASE_URL in .env file"
echo ""
echo -e "${YELLOW}4. Create the Vapi assistant:${NC}"
echo "   python voice_agent/vapi_setup.py create"
echo ""
echo -e "${YELLOW}5. Get a phone number in Vapi dashboard:${NC}"
echo "   https://vapi.ai/dashboard → Phone Numbers → Buy Number"
echo ""
echo -e "${YELLOW}6. Test the system:${NC}"
echo "   python voice_agent/test_system.py simulate"
echo ""
echo -e "${YELLOW}7. Call your number and order medications! ${NC}"
echo ""

echo -e "${BLUE}Need help? Read: voice_agent/README.md${NC}"
echo ""
