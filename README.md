# Food Distribution System

This application is designed to provide a solution for efficient food distribution by allowing organizations to manage the distribution process effectively. In many cases, those responsible for distributing essential items such as food, are not aware of the recipients. This can lead to errors such as delivering parcels to individuals who have already received them or miscalculating the distribution.

The Food Distribution System aims to solve these problems by using a user-friendly form that collects information from individuals picking up their food packages. The form includes master data, family data, and master data of family members. Additionally, the system has a fingerprint sensor feature to prevent identification errors.

## Features

User-friendly form for data collection
Fingerprint sensor for accurate identification of individuals
Master data, family data, and master data of family members included in the form
Verification of recipients to prevent duplication of packages
System updates information on received packages
Designed to work in areas without an internet connection

## Project Structure

```
Food-Distribution-System/
├── backend/          # FastAPI backend (Python)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── config.py     # Settings (from .env)
│   │   ├── database.py   # SQLAlchemy engine & session
│   │   ├── models.py     # ORM models (Family, Person, Distribution)
│   │   ├── schemas.py    # Pydantic v2 schemas
│   │   └── routes.py     # API routes
│   ├── alembic/          # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/         # Vue 3 frontend (TypeScript)
│   ├── src/
│   │   ├── api/          # Axios API client
│   │   ├── components/   # Reusable components (NavBar)
│   │   ├── router/       # Vue Router configuration
│   │   ├── views/        # Route views
│   │   ├── App.vue       # Root component
│   │   ├── main.ts       # App entry point
│   │   └── style.css     # TailwindCSS imports
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── docs/             # Agent documentation (preserved)
├── AGENTS.md          # Agent skills config (preserved)
└── .gitignore
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Edit if needed
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

Health check: `GET /api/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### Running both

Open two terminals — one for backend, one for frontend. The Vite dev server proxies API calls automatically.

## Usage

Once the application is running, you will be presented with a user-friendly form. An operator in charge of distribution will enter the required information manually or use the fingerprint sensor to identify the recipient. The system will then verify if the recipient or any member of their household has already collected a package. If the recipient has not collected their package, they will receive it, and the system will update the information on the received packages. If the package has already been collected, the system will deny the transaction.

## Contribution

Contributions to this project are welcome. If you find a bug or have a feature request, please open an issue. If you would like to contribute code to the project, please submit a pull request.
