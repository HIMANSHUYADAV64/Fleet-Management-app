# 🚚 FleetPro - Fleet Management System

FleetPro is a full-featured **Fleet Management System** built with **FastAPI (backend)**, **MongoDB/SQL (database)**, and a **React + TailwindCSS (frontend)**.  
It helps transport companies manage vehicles, drivers, routes, payments, alerts, and real-time tracking on an interactive dashboard.

---

## ✨ Features

- 📊 **Dashboard Analytics**
  - KPI cards (Vehicles, Drivers, Active Trips, Revenue, Alerts)
  - Realtime graphs & charts
  - Active trip list

- 🚛 **Fleet Management**
  - Vehicles CRUD (Add, Edit, Delete, View)
  - Driver Management
  - Route Assignment

- 💳 **Payment & Legal**
  - Record payments with TDS, net balance, and status
  - Legal documents and expiry tracking

- 🌍 **Live Tracking**
  - Integrated **Google Maps/Mapbox** for real-time vehicle location
  - WebSocket updates for active trips
  - Trip playback animation with timeline slider

- ⚠️ **Alerts & Notifications**
  - Alerts for expiring documents, delayed trips, or failed payments

- 🔐 **Authentication**
  - JWT-based authentication
  - Google Sign-In integration

- 📤 **Export**
  - Export data to PDF/Excel for reports

- 📱 **Responsive UI**
  - Professional design with TailwindCSS
  - Works on desktop, tablet, and mobile

---

## 🛠️ Tech Stack

**Frontend**
- React + Vite
- TailwindCSS + Shadcn UI
- Recharts (analytics)
- Mapbox/Google Maps (tracking)
- Axios (API calls)

**Backend**
- FastAPI (Python)
- JWT Authentication
- Pydantic Models
- WebSockets (real-time updates)

**Database**
- MongoDB (NoSQL) or PostgreSQL/MySQL (SQL option)

**Other**
- Docker (optional containerized deployment)
- Nginx (for hosting)
- GitHub Actions (CI/CD ready)

---

## ⚡ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/fleetpro.git
cd fleetpro



Backend Setup (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Frontend Setup (React + Vite)
cd frontend
npm install
npm run dev

Frontend .env

VITE_BACKEND_URL=http://localhost:8000
VITE_MAPBOX_KEY=your_mapbox_key


DATABASE_URL=mongodb://localhost:27017/fleetpro
JWT_SECRET=your_secret_key
MAPBOX_API_KEY=your_mapbox_key

Project structure
FleetPro/
│── backend/           # FastAPI backend
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── database/
│
│── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── App.jsx
│
│── README.md
│── requirements.txt   # Backend dependencies
│── package.json       # Frontend dependencies

<img width="1913" height="907" alt="Screenshot 2025-07-11 132519" src="https://github.com/user-attachments/assets/dc7a79a9-2db8-45c9-b337-768dd78b7fb9" />

