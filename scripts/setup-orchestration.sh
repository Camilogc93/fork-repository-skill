#!/bin/bash
# Setup script for Agent Orchestration System
# Creates all necessary directories and initializes configuration files

set -e

echo "🚀 Setting up Agent Orchestration System..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create agent configuration directories
echo -e "${BLUE}Creating agent configuration directories...${NC}"
mkdir -p .claude/agents/roles
mkdir -p .claude/agents/project-context
mkdir -p .claude/agents/session-state

# Create runtime communication directories
echo -e "${BLUE}Creating runtime communication directories...${NC}"
mkdir -p .agent-comm/agents/status
mkdir -p .agent-comm/orchestration/tasks/{pending,in-progress,blocked,completed}
mkdir -p .agent-comm/orchestration/workflows
mkdir -p .agent-comm/messaging/{inbox,sent}
mkdir -p .agent-comm/shared-knowledge/{api-contracts,design-decisions,handoffs}
mkdir -p .agent-comm/checkpoints
mkdir -p .agent-comm/logs

# Create .gitkeep files for empty directories
echo -e "${BLUE}Creating .gitkeep files...${NC}"
touch .claude/agents/session-state/.gitkeep
touch .agent-comm/agents/status/.gitkeep
touch .agent-comm/orchestration/tasks/pending/.gitkeep
touch .agent-comm/orchestration/tasks/in-progress/.gitkeep
touch .agent-comm/orchestration/tasks/blocked/.gitkeep
touch .agent-comm/orchestration/tasks/completed/.gitkeep
touch .agent-comm/orchestration/workflows/.gitkeep
touch .agent-comm/messaging/inbox/.gitkeep
touch .agent-comm/messaging/sent/.gitkeep
touch .agent-comm/shared-knowledge/api-contracts/.gitkeep
touch .agent-comm/shared-knowledge/design-decisions/.gitkeep
touch .agent-comm/shared-knowledge/handoffs/.gitkeep
touch .agent-comm/checkpoints/.gitkeep

# Create log files if they don't exist
echo -e "${BLUE}Initializing log files...${NC}"
if [ ! -f .agent-comm/logs/decisions.log ]; then
    cat > .agent-comm/logs/decisions.log << 'EOF'
# Decision Log
# Records all architectural and technical decisions made during orchestration
# Format: [TIMESTAMP] [DECISION_TYPE] Description

EOF
fi

if [ ! -f .agent-comm/logs/tasks.log ]; then
    cat > .agent-comm/logs/tasks.log << 'EOF'
# Task Log
# Records all task lifecycle events (created, assigned, started, completed, blocked)
# Format: [TIMESTAMP] [TASK_ID] [EVENT] Description

EOF
fi

if [ ! -f .agent-comm/logs/communications.log ]; then
    cat > .agent-comm/logs/communications.log << 'EOF'
# Communications Log
# Records all inter-agent messages and orchestrator communications
# Format: [TIMESTAMP] [FROM] -> [TO] [MESSAGE_TYPE] Summary

EOF
fi

# Create agent registry if it doesn't exist
echo -e "${BLUE}Initializing agent registry...${NC}"
if [ ! -f .agent-comm/agents/registry.json ]; then
    cat > .agent-comm/agents/registry.json << 'EOF'
{
  "version": "1.0.0",
  "max_concurrent_agents": 5,
  "agents": {},
  "last_updated": null
}
EOF
fi

# Create .gitignore for .agent-comm
echo -e "${BLUE}Creating .gitignore for runtime files...${NC}"
if [ ! -f .agent-comm/.gitignore ]; then
    cat > .agent-comm/.gitignore << 'EOF'
# Agent Communication Runtime Files
# These are generated during agent execution and should not be committed

# Agent status files (ephemeral)
agents/status/*.json

# Task files (runtime state)
orchestration/tasks/pending/*.json
orchestration/tasks/in-progress/*.json
orchestration/tasks/blocked/*.json
orchestration/tasks/completed/*.json

# Workflows (runtime state)
orchestration/workflows/*.json

# Dependencies graph (runtime)
orchestration/dependencies.json

# Messages (ephemeral)
messaging/inbox/**/*.json
messaging/sent/*.json

# Checkpoints (can be large)
checkpoints/*.json

# Shared knowledge generated at runtime
shared-knowledge/api-contracts/*.yaml
shared-knowledge/api-contracts/*.json
shared-knowledge/design-decisions/*.md
shared-knowledge/handoffs/*.json

# Keep log files for debugging
!logs/
logs/*.log

# Keep .gitkeep files
!.gitkeep
!**/.gitkeep
EOF
fi

echo ""
echo -e "${GREEN}✅ Agent Orchestration System setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Define agent roles in .claude/agents/roles/"
echo "  2. Configure project context in .claude/agents/project-context/"
echo "  3. Install Python dependencies (if needed)"
echo "  4. Run orchestration with: claude 'orchestrate feature: <your feature>'"
echo ""
echo "Directory structure created:"
echo "  📁 .claude/agents/          - Agent configurations"
echo "  📁 .agent-comm/             - Runtime coordination"
echo "  📄 scripts/setup-orchestration.sh - This setup script"
echo ""
