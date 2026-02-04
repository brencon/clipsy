# Claude Code Project Template - Initialization Script (PowerShell)
# This script helps set up your project with the template configuration

$ErrorActionPreference = "Stop"

# Colors
function Write-Step { param($msg) Write-Host "`n> $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "  i $msg" -ForegroundColor Cyan }
function Write-Warn { param($msg) Write-Host "  ! $msg" -ForegroundColor Yellow }
function Write-Success { param($msg) Write-Host "  + $msg" -ForegroundColor Green }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "       Claude Code Project Template - Initialization           " -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "CLAUDE.md")) {
    Write-Host "Error: CLAUDE.md not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Step 1: Project Information
Write-Step "Project Setup"
Write-Host ""
$PROJECT_NAME = Read-Host "  Enter your project name"
$PROJECT_DESC = Read-Host '  Brief description (1 sentence)'

# Step 2: Tech Stack Selection
Write-Step "Tech Stack"
Write-Host ""
Write-Host "  Available templates:"
Write-Host '    1) TypeScript + React (frontend)'
Write-Host '    2) Python + FastAPI (backend)'
Write-Host '    3) Node.js + Express (backend)'
Write-Host '    4) Custom (keep template placeholders)'
Write-Host ""
$STACK_CHOICE = Read-Host "  Select template [1-4]"

# Step 3: LLM Council Setup
Write-Step 'LLM Council (Optional)'
Write-Host ""
$SETUP_COUNCIL = Read-Host "  Set up LLM Council for multi-model consultation? [y/N]"

# Step 4: Environment Setup
Write-Step "Environment Configuration"

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success "Created .env from .env.example"
        Write-Info "Edit .env to add your API keys"
    }
} else {
    Write-Info ".env already exists, skipping"
}

# Step 5: Copy CLAUDE.md template based on selection
Write-Step "Configuring CLAUDE.md"

switch ($STACK_CHOICE) {
    "1" {
        if (Test-Path "examples/typescript-react/CLAUDE.md") {
            Copy-Item "examples/typescript-react/CLAUDE.md" "CLAUDE.md" -Force
            Write-Success "Applied TypeScript + React template"
        }
    }
    "2" {
        if (Test-Path "examples/python-fastapi/CLAUDE.md") {
            Copy-Item "examples/python-fastapi/CLAUDE.md" "CLAUDE.md" -Force
            Write-Success "Applied Python + FastAPI template"
        }
    }
    "3" {
        if (Test-Path "examples/node-express/CLAUDE.md") {
            Copy-Item "examples/node-express/CLAUDE.md" "CLAUDE.md" -Force
            Write-Success "Applied Node.js + Express template"
        }
    }
    "4" {
        Write-Info "Keeping template placeholders for custom setup"
    }
    default {
        Write-Warn "Invalid selection, keeping current CLAUDE.md"
    }
}

# Update project name and description in CLAUDE.md
if ($PROJECT_NAME) {
    $content = Get-Content "CLAUDE.md" -Raw
    $content = $content -replace '\[PROJECT_NAME\]', $PROJECT_NAME
    $content = $content -replace '\[BRIEF_DESCRIPTION\]', $PROJECT_DESC
    Set-Content "CLAUDE.md" $content
    Write-Success "Updated project name and description"
}

# Step 6: LLM Council Setup
if ($SETUP_COUNCIL -match '^[Yy]$') {
    Write-Step "Setting up LLM Council"

    # Copy council config
    if ((Test-Path "scripts/llm-council/config.example.yaml") -and -not (Test-Path "scripts/llm-council/config.yaml")) {
        Copy-Item "scripts/llm-council/config.example.yaml" "scripts/llm-council/config.yaml"
        Write-Success "Created council config.yaml"
    }

    # Check for Python and install dependencies
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $INSTALL_DEPS = Read-Host "  Install Python dependencies for LLM Council? [y/N]"
        if ($INSTALL_DEPS -match '^[Yy]$') {
            pip install -r scripts/llm-council/requirements.txt
            Write-Success "Installed LLM Council dependencies"
        }
    } else {
        Write-Warn "Python not found. Install dependencies manually:"
        Write-Info "pip install -r scripts/llm-council/requirements.txt"
    }

    Write-Host ""
    Write-Info 'Configure API keys in .env (at least 2 providers required):'
    Write-Info "  - ANTHROPIC_API_KEY"
    Write-Info "  - OPENAI_API_KEY"
    Write-Info "  - GOOGLE_AI_API_KEY"
    Write-Info "  - XAI_API_KEY"
}

# Step 7: Git Setup
Write-Step "Git Configuration"

if (Test-Path ".git") {
    Write-Info "Git repository already initialized"
} else {
    $INIT_GIT = Read-Host "  Initialize git repository? [Y/n]"
    if ($INIT_GIT -notmatch '^[Nn]$') {
        git init
        Write-Success "Initialized git repository"
    }
}

# Step 8: Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "                    Setup Complete!                             " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:"
Write-Host "  1. Review and customize CLAUDE.md for your project"
Write-Host "  2. Add your API keys to .env"
if ($SETUP_COUNCIL -match '^[Yy]$') {
    Write-Host "  3. Test LLM Council: /council-config"
}
Write-Host ""
Write-Host "Available commands:"
Write-Host "  /health         - Check project setup"
Write-Host "  /brainstorm     - Explore options before coding"
Write-Host "  /plan           - Create implementation plan"
Write-Host "  /council        - Consult multiple AI models"
Write-Host ""
Write-Host "Happy coding with Claude Code!" -ForegroundColor Blue
Write-Host ""
