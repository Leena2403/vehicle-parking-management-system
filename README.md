# vehicle-parking-management-system

<div align="center">

# 🅿️ Parking Portal

### A full-stack web application for smart parking management

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-CC0000?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

> Book a spot. Park smart. Release when done. — All from your browser.

[Features](#-features) · [Tech Stack](#-tech-stack) · [Getting Started](#-getting-started) · [Project Structure](#-project-structure) · [API Routes](#-api-routes) · [Database Schema](#-database-schema) · [Screenshots](#-screenshots) · [Contributing](#-contributing)

</div>

---

## ✨ Features

### 👤 User Side
| Feature | Description |
|--------|-------------|
| 🔐 **Sign Up / Login** | Register with username, email & password; secure session-based auth |
| 🗺️ **Browse Parking Lots** | View all available lots with location, price & availability at a glance |
| 🎫 **Book a Spot** | One-click booking on the next available spot in any lot |
| 🚗 **Vehicle Guard** | Prevents double-booking — one active reservation per vehicle at a time |
| ⏱️ **Release & Pay** | Release your spot and get a live cost breakdown (hourly rate × time used) |
| 📊 **Personal Summary** | Visual charts — bookings over the last 7 days & reservation status breakdown |
| ✏️ **Edit Profile** | Update name, email, and password anytime |
| ❌ **Delete Account** | Full self-service account deletion with cascade cleanup |

### 🛡️ Admin Side
| Feature | Description |
|--------|-------------|
| 🔑 **Separate Admin Login** | Isolated admin authentication portal |
| 🏗️ **Add Parking Lots** | Create lots with name, address, pin code, price & number of spots |
| ✏️ **Edit Lots** | Modify lot details (blocked if active reservations exist) |
| 🗑️ **Delete Lots** | Safe deletion — blocked if any spot is currently occupied |
| 🔍 **Smart Search** | Search by location name or specific spot ID |
| 👥 **User Management** | View all users who have made at least one reservation |
| 📍 **Spot Management** | View, inspect history, and delete individual parking spots |

---

## 🛠 Tech Stack

```
Backend      →  Python 3.11 · Flask · Flask-SQLAlchemy
Database     →  SQLite (parking.db)
ORM          →  SQLAlchemy (declarative models)
Templating   →  Jinja2
Charts       →  Matplotlib (server-side PNG generation, headless Agg backend)
Timezone     →  zoneinfo · Asia/Kolkata (IST)
Frontend     →  HTML5 · CSS3 (custom stylesheets per role)
Auth         →  Flask Sessions
```

---

## Getting Started

### Prerequisites

- Python **3.11+**
- `pip`

### 1 · Clone the repository

```bash
git clone https://github.com/your-username/parking-portal.git
cd parking-portal
```

### 2 · Create & activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3 · Install dependencies

```bash
pip install flask flask-sqlalchemy matplotlib
```

### 4 · Run the app

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**

> On first run, the app auto-creates `instance/parking.db` and seeds a default admin account.

### 5 · Log in as Admin

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

> **Change these credentials immediately in production!**

---

## 📁 Project Structure

```
Placement Portal/
│
├── app.py                      # App factory — creates Flask app, registers blueprint, seeds admin
├── extensions.py               # SQLAlchemy db instance (avoids circular imports)
│
├── models/
│   └── model.py                # ORM models: User_Info, Parking_Lot, Parking_Spot, Reservation
│
├── controllers/
│   └── file_1.py               # All route handlers via Flask Blueprint
│
├── templates/
│   ├── index.html              # Landing page
│   ├── login.html              # User login
│   ├── signup.html             # User registration
│   ├── signup_success.html     # Post-registration confirmation
│   ├── base_user.html          # User layout base template
│   ├── user_dashboard.html     # User home — lots + reservations
│   ├── book_parking.html       # Booking form
│   ├── release_parking_spot.html   # Release confirmation + cost
│   ├── user_summary.html       # User charts page
│   ├── user_edit_profile.html  # Profile edit form
│   ├── base_admin.html         # Admin layout base template
│   ├── admin_login.html        # Admin login
│   ├── admin_dashboard.html    # Admin home — all lots
│   ├── add_lot.html            # Add new parking lot
│   ├── edit_parking_lot.html   # Edit existing lot
│   ├── admin_parking_spot.html # Single spot view + delete
│   ├── admin_parking_spot_details.html  # Spot reservation history
│   ├── admin_users.html        # All users with reservations
│   ├── admin_search.html       # Search form
│   ├── admin_search_results.html       # Search results
│   └── admin_summary.html      # Admin summary page
│
├── static/
│   ├── css/
│   │   ├── style.css           # Global styles
│   │   ├── user_dashboard.css  # User dashboard styles
│   │   └── admin_dashboard.css # Admin dashboard styles
│   └── images/
│       ├── brand logo.png
│       ├── canvas image.jpg
│       └── about us.avif
│
└── instance/
    └── parking.db              # SQLite database (auto-generated)
```

---

## API Routes

### Public Routes
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Landing page |
| `GET/POST` | `/login` | User login |
| `GET/POST` | `/signup` | User registration |
| `GET/POST` | `/admin_login` | Admin login |

### User Routes *(session required)*
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/user_dashboard` | Main dashboard with lots & reservations |
| `GET` | `/show_book_form/<lot_id>` | Booking form for a specific lot |
| `POST` | `/book_lot` | Confirm booking |
| `GET` | `/release/<reservation_id>` | Preview release cost |
| `POST` | `/confirm_release` | Finalize release & free spot |
| `GET` | `/summary` | Personal analytics with charts |
| `GET/POST` | `/edit_profile` | Update profile |
| `POST` | `/delete_user` | Delete account & session |
| `GET` | `/logout` | Clear session |

### Admin Routes *(admin session required)*
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/admin_home` | Admin dashboard — all lots |
| `GET` | `/admin_users` | Users who have reservations |
| `GET/POST` | `/admin_search` | Search by location or spot ID |
| `GET/POST` | `/add_lot` | Create a new parking lot |
| `GET/POST` | `/edit_parking_lot/<lot_id>` | Edit lot (blocked if active reservations) |
| `POST` | `/delete_lot/<lot_id>` | Delete lot (blocked if occupied) |
| `GET/POST` | `/view_parking_spot/<spot_id>` | View & optionally delete a spot |
| `GET` | `/admin_spot_details/<spot_id>` | Full reservation history for a spot |
| `GET/POST` | `/admin_summary` | Admin summary page |
| `GET/POST` | `/admin_logout` | Admin logout |

---

## 🗄️ Database Schema

```
┌─────────────────────────┐        ┌──────────────────────────┐
│       user_info          │        │       parking_lot         │
├─────────────────────────┤        ├──────────────────────────┤
│ id            INTEGER PK│        │ id            INTEGER PK  │
│ email         STRING    │        │ prime_location_name STRING│
│ full_name     STRING    │        │ price         FLOAT       │
│ user_name     STRING UQ │        │ address       STRING      │
│ pwd           STRING    │        │ pin_code      STRING      │
│ role          INTEGER   │        │ maximum_number_of_spots   │
└─────────┬───────────────┘        └──────────┬───────────────┘
          │                                    │
          │  1:N                               │  1:N
          ▼                                    ▼
┌─────────────────────────────────────────────────────────┐
│                      parking_spot                        │
├─────────────────────────────────────────────────────────┤
│ id       INTEGER PK                                      │
│ lot_id   FK → parking_lot.id  (CASCADE DELETE)          │
│ status   CHAR(1)  'A' = Available · 'O' = Occupied      │
└──────────────────────────────┬──────────────────────────┘
                               │
                               │  1:N
                               ▼
┌─────────────────────────────────────────────────────────┐
│                       reservation                        │
├─────────────────────────────────────────────────────────┤
│ id                  INTEGER PK                           │
│ spot_id             FK → parking_spot.id                 │
│ user_id             FK → user_info.id                    │
│ vehicle_number      STRING                               │
│ parking_timestamp   DATETIME                             │
│ leaving_timestamp   DATETIME (nullable)                  │
│ parking_cost        FLOAT                                │
│ status              STRING  'Active' · 'Released'        │
└─────────────────────────────────────────────────────────┘

role:  0 = Admin   |   1 = Regular User
```

---

## Analytics

The app generates **server-side charts** using Matplotlib (headless `Agg` backend):

- **Bar Chart** — bookings per day over the past 7 days
- **Pie Chart** — breakdown of reservation statuses (`Active` vs `Released`)

Charts are rendered to PNG and served from the `static/` directory.

---

## Known Limitations & Improvement Areas

> These are great starting points if you want to contribute!

- [ ] **Passwords stored in plaintext** — integrate `werkzeug.security` (bcrypt hashing)
- [ ] **No login decorators** — add `@login_required` guards using Flask-Login
- [ ] **Admin auth not session-based** — admin sessions should be tracked separately
- [ ] **No input sanitization** — add server-side validation and flash error messages
- [ ] **Static chart files** — charts overwrite each other; use user-scoped filenames or in-memory base64
- [ ] **No pagination** — large datasets will slow down dashboards
- [ ] **`admin_summary` route is empty** — wire up real admin-level analytics
- [ ] **`admin_logout` renders login template** — should redirect instead

---

## Contributing

Contributions are welcome! Here's how to get started:

```bash
# 1. Fork the repo and clone your fork
git clone https://github.com/your-username/parking-portal.git

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git commit -m "feat: add login_required decorator"

# 4. Push and open a Pull Request
git push origin feature/your-feature-name
```

---
---

<div align="center">

Built with ❤️ using Flask · SQLAlchemy · Matplotlib

⭐ Star this repo if you found it useful!

</div>
