#!/bin/bash

# Claude Code Project Template - Initialization Script
# This script helps set up your project with the template configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Claude Code Project Template - Initialization          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print step headers
step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

# Function to print info
info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# Function to print warning
warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

# Function to print success
success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    echo -e "${RED}Error: CLAUDE.md not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Step 1: Project Information
step "Project Setup"
echo ""
read -p "  Enter your project name: " PROJECT_NAME
read -p "  Brief description (1 sentence): " PROJECT_DESC

# Step 2: Tech Stack Selection
step "Tech Stack"
echo ""
echo "  Available templates:"
echo "    1) TypeScript + React (frontend)"
echo "    2) Python + FastAPI (backend)"
echo "    3) Node.js + Express (backend)"
echo "    4) Custom (keep template placeholders)"
echo ""
read -p "  Select template [1-4]: " STACK_CHOICE

# Step 3: LLM Council Setup
step "LLM Council (Optional)"
echo ""
read -p "  Set up LLM Council for multi-model consultation? [y/N]: " SETUP_COUNCIL

# Step 4: Environment Setup
step "Environment Configuration"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        success "Created .env from .env.example"
        info "Edit .env to add your API keys"
    fi
else
    info ".env already exists, skipping"
fi

# Step 5: Copy CLAUDE.md template based on selection
step "Configuring CLAUDE.md"

case $STACK_CHOICE in
    1)
        if [ -f "examples/typescript-react/CLAUDE.md" ]; then
            cp examples/typescript-react/CLAUDE.md CLAUDE.md
            success "Applied TypeScript + React template"
        fi
        ;;
    2)
        if [ -f "examples/python-fastapi/CLAUDE.md" ]; then
            cp examples/python-fastapi/CLAUDE.md CLAUDE.md
            success "Applied Python + FastAPI template"
        fi
        ;;
    3)
        if [ -f "examples/node-express/CLAUDE.md" ]; then
            cp examples/node-express/CLAUDE.md CLAUDE.md
            success "Applied Node.js + Express template"
        fi
        ;;
    4)
        info "Keeping template placeholders for custom setup"
        ;;
    *)
        warn "Invalid selection, keeping current CLAUDE.md"
        ;;
esac

# Update project name and description in CLAUDE.md
if [ -n "$PROJECT_NAME" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" CLAUDE.md 2>/dev/null || true
        sed -i '' "s/\[BRIEF_DESCRIPTION\]/$PROJECT_DESC/g" CLAUDE.md 2>/dev/null || true
    else
        # Linux
        sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" CLAUDE.md 2>/dev/null || true
        sed -i "s/\[BRIEF_DESCRIPTION\]/$PROJECT_DESC/g" CLAUDE.md 2>/dev/null || true
    fi
    success "Updated project name and description"
fi

# Step 6: LLM Council Setup
if [[ "$SETUP_COUNCIL" =~ ^[Yy]$ ]]; then
    step "Setting up LLM Council"

    # Copy council config
    if [ -f "scripts/llm-council/config.example.yaml" ] && [ ! -f "scripts/llm-council/config.yaml" ]; then
        cp scripts/llm-council/config.example.yaml scripts/llm-council/config.yaml
        success "Created council config.yaml"
    fi

    # Check for Python and install dependencies
    if command -v python3 &> /dev/null; then
        read -p "  Install Python dependencies for LLM Council? [y/N]: " INSTALL_DEPS
        if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
            pip3 install -r scripts/llm-council/requirements.txt
            success "Installed LLM Council dependencies"
        fi
    else
        warn "Python 3 not found. Install dependencies manually:"
        info "pip3 install -r scripts/llm-council/requirements.txt"
    fi

    echo ""
    info "Configure API keys in .env (at least 2 providers required):"
    info "  - ANTHROPIC_API_KEY"
    info "  - OPENAI_API_KEY"
    info "  - GOOGLE_AI_API_KEY"
    info "  - XAI_API_KEY"
fi

# Step 7: Git Setup
step "Git Configuration"

if [ -d ".git" ]; then
    info "Git repository already initialized"
else
    read -p "  Initialize git repository? [Y/n]: " INIT_GIT
    if [[ ! "$INIT_GIT" =~ ^[Nn]$ ]]; then
        git init
        success "Initialized git repository"
    fi
fi

# Step 8: Summary
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo "Next steps:"
echo "  1. Review and customize CLAUDE.md for your project"
echo "  2. Add your API keys to .env"
if [[ "$SETUP_COUNCIL" =~ ^[Yy]$ ]]; then
echo "  3. Test LLM Council: /council-config"
fi
echo ""
echo "Available commands:"
echo "  /health         - Check project setup"
echo "  /brainstorm     - Explore options before coding"
echo "  /plan           - Create implementation plan"
echo "  /council        - Consult multiple AI models"
echo ""
echo -e "${BLUE}Happy coding with Claude Code!${NC}"
echo ""
