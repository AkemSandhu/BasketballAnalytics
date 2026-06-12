# NBA Analytics Platform

Full‑stack application that computes advanced NBA player metrics (impact score, skill badges, role clustering, talent, team fit) and serves them via REST API with an interactive frontend.

## Project Structure

├── common/ # Shared code (database models, schemas, config)

├── pipeline/ # Data processing & ML pipeline (Python)

├── backend/ # FastAPI backend (to be built)

├── frontend/ # React frontend (to be built)

├── docker-compose.yml

├── .gitignore

└── README.md

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Git

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd nba-analytics-platform