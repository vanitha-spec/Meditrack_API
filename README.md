# 🏥 MediTrack — Healthcare Management API

> **Author:** RaviVarma

A full-stack **Healthcare Management System** built with **Django + Django REST Framework + JWT + Bootstrap 5** where:

- 🧑‍⚕️ **Doctors** manage their profile, create availability slots, and handle appointments
- 👤 **Patients** browse doctors, book appointments, and view prescriptions
- 🔐 **JWT Authentication** with role-based access
- 🌐 **Bootstrap 5** frontend with role-aware UI
- 🌱 **Dummy data** seeder to see the app working instantly

---

## 📚 Table of Contents

1. [What This Project Does](#-what-this-project-does)
2. [How the Application Runs (Flow Diagram)](#-how-the-application-runs-flow-diagram)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [File-by-File Explanation](#-file-by-file-explanation)
6. [Database Models](#-database-models)
7. [REST API Endpoints](#-rest-api-endpoints)
8. [Dummy Data Seeder](#-dummy-data-seeder)
9. [Function Reference](#-function-reference)
10. [Frontend Pages](#-frontend-pages)
11. [How to Run Locally](#-how-to-run-locally)
12. [How to Use the App](#-how-to-use-the-app)
13. [Common Errors & Fixes](#-common-errors--fixes)
14. [What I Learned](#-what-i-learned)
15. [Interview Talking Points](#-interview-talking-points)

---

## 🎯 What This Project Does

MediTrack is a **mini version of Practo/Apollo 24x7** with two user roles.

### 🧑‍⚕️ Doctor
- Register / Login
- Create and update own profile (specialization, experience, fees, bio)
- Create availability slots (date + time)
- View all booked appointments
- Add prescription notes after the consultation
- Mark appointments as **completed** or **no_show**

### 👤 Patient
- Register / Login
- Browse all doctors (public)
- View a doctor's available slots
- Book an appointment
- View own appointments (upcoming + past)
- Cancel pending appointments

### 🔐 Security
- JWT-based authentication (access + refresh tokens)
- Role-based permissions (doctors can't book, patients can't create slots)
- Ownership checks (only slot owner can delete)
- One appointment per slot (prevents double-booking)
- Past-date validation

---

## 🔄 How the Application Runs (Flow Diagram)

```
┌───────────────────────────────────────────────────────────────┐
│                    BROWSER (User)                              │
│   Login / Register / Doctors / Book / Dashboards               │
└───────────────────────────┬───────────────────────────────────┘
                            │ JWT + fetch()
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    DJANGO SERVER                               │
│                                                                │
│  accounts/          doctors/            appointments/          │
│  ─────────          ────────            ─────────────           │
│  • User             • DoctorProfile     • Appointment          │
│  • register         • AvailabilitySlot  • book / cancel        │
│  • login            • slots API         • status / notes       │
│                                                                │
│                    utils/responses.py                          │
│                    (success / error helpers)                   │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │  SQLite Database     │
                  │                      │
                  │  Tables:             │
                  │  • accounts_user     │
                  │  • doctors_doctor... │
                  │  • doctors_avail...  │
                  │  • appointments_app  │
                  └──────────────────────┘
```

### 🔁 Typical Request Flow — Booking an Appointment

```
1. Patient clicks "Book" on a slot
        │
        ▼
2. Browser JS → fetch('/api/appointments/book/', JWT, {slot: id})
        │
        ▼
3. Django routes → appointments.views.book_appointment()
        │
        ▼
4. Check role: is_patient() → ✅
        │
        ▼
5. Check slot exists and is not booked → ✅
        │
        ▼
6. Create Appointment + mark slot.is_booked = True
        │
        ▼
7. Response: { success: true, message: "..." }
        │
        ▼
8. Browser shows success + refreshes slots
```

### 🔁 Typical Request Flow — Login

```
1. User submits login form
        │
        ▼
2. Browser JS → fetch('/api/login/', {username, password})
        │
        ▼
3. Django routes → accounts.views.login_user()
        │
        ▼
4. LoginSerializer validates credentials via authenticate()
        │
        ▼
5. get_tokens_for_user() → RefreshToken.for_user(user)
        │
        ▼
6. Response: { user, tokens: { access, refresh } }
        │
        ▼
7. Browser stores access token + role in localStorage
        │
        ▼
8. Redirect to /doctors/
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Django 5.x | Web framework |
| API | Django REST Framework | RESTful JSON APIs |
| Auth | Simple JWT | Token-based auth |
| Database | SQLite | Local development |
| Frontend | HTML, CSS, Bootstrap 5 | Responsive UI |
| Scripts | Vanilla JavaScript | API calls, DOM updates |
| Env Config | python-decouple | `.env` handling |
| Seeder | Django Management Commands | Dummy data |

---

## 📁 Project Structure

```
meditrack/
│
├── manage.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
├── db.sqlite3
│
├── meditrack/                     # Main project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                      # App 1: User authentication
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # Custom User with role
│   ├── serializers.py             # Register, Login
│   ├── views.py                   # register_user, login_user
│   ├── urls.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           ├── __init__.py
│           └── seed_users.py
│
├── doctors/                       # App 2: Doctor profiles + slots
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # DoctorProfile, AvailabilitySlot
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           ├── __init__.py
│           └── seed_doctors.py
│
├── appointments/                  # App 3: Appointment booking
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # Appointment
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           ├── __init__.py
│           └── seed_appointments.py
│
├── utils/                         # App 4: Helpers
│   ├── __init__.py
│   └── responses.py               # success_response, error_response
│
├── templates/                     # HTML pages
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── doctors.html
│   ├── my_appointments.html
│   └── doctor_dashboard.html
│
└── static/
    └── css/
        └── style.css
```

---

## 📂 File-by-File Explanation

### 🔹 `manage.py`
Django's command-line utility. Used for `runserver`, `migrate`, `seed_*`, etc.

### 🔹 `requirements.txt`
Python dependencies:
```
Django
djangorestframework
djangorestframework-simplejwt
python-decouple
```

### 🔹 `.env`
Environment variables (not committed):
```
SECRET_KEY=your-secret-key
DEBUG=True
```

### 🔹 `.env.example`
Template showing what variables are needed (safe to commit).

### 🔹 `.gitignore`
Excludes `env/`, `db.sqlite3`, `.env`, `media/`, `__pycache__/`.

---

### 📁 `meditrack/` (Main project)

| File | Purpose |
|------|---------|
| `settings.py` | Registers apps, DRF, JWT, custom User, templates, static |
| `urls.py` | Routes API + frontend pages; serves media in dev |
| `wsgi.py` / `asgi.py` | Deployment entry points (auto-generated) |

---

### 📁 `accounts/`

| File | Purpose |
|------|---------|
| `models.py` | `User` extends `AbstractUser` + `role` field (doctor/patient) |
| `admin.py` | Registers User with `role` in admin list |
| `serializers.py` | `RegisterSerializer`, `LoginSerializer` |
| `views.py` | `register_user`, `login_user`, `get_tokens_for_user` |
| `urls.py` | `/api/register/`, `/api/login/` |
| `management/commands/seed_users.py` | Creates 3 doctors, 5 patients, 1 admin |

---

### 📁 `doctors/`

| File | Purpose |
|------|---------|
| `models.py` | `DoctorProfile` (OneToOne User), `AvailabilitySlot` (FK doctor) |
| `admin.py` | Admin registration for both models |
| `serializers.py` | `DoctorProfileSerializer`, `AvailabilitySlotSerializer` |
| `views.py` | 6 views (profile upsert, list, detail, slot create/list/delete) |
| `urls.py` | 6 endpoints |
| `management/commands/seed_doctors.py` | 3 profiles + 8 slots each |

---

### 📁 `appointments/`

| File | Purpose |
|------|---------|
| `models.py` | `Appointment` (OneToOne slot, FK patient, status, notes) |
| `admin.py` | Admin registration |
| `serializers.py` | `AppointmentSerializer` with nested read-only fields |
| `views.py` | 6 API views + 5 page views |
| `urls.py` | 6 endpoints |
| `management/commands/seed_appointments.py` | 6 sample appointments |

---

### 📁 `utils/`

| File | Purpose |
|------|---------|
| `responses.py` | `success_response()`, `error_response()` |

---

### 📁 `templates/`

| File | Purpose |
|------|---------|
| `base.html` | Master layout + role-aware navbar + `logout()` JS |
| `login.html` | Login form + API call + token storage |
| `register.html` | Register form (role dropdown) |
| `doctors.html` | Doctor cards + booking modal with slots |
| `my_appointments.html` | Patient's appointments + cancel |
| `doctor_dashboard.html` | Profile form, slot creation, appointments |

---

### 📁 `static/css/`

| File | Purpose |
|------|---------|
| `style.css` | Card hover, rounded inputs, custom badges |

---

## 🗄 Database Models

### `User` (accounts)
| Field | Type | Notes |
|-------|------|-------|
| `username` | CharField | From AbstractUser |
| `email` | EmailField | From AbstractUser |
| `password` | CharField | Hashed automatically |
| `role` | CharField | `doctor` / `patient` |
| `is_staff`, `is_superuser` | Boolean | From AbstractUser |

### `DoctorProfile` (doctors)
| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOne(User) | Linked to doctor account |
| `specialization` | CharField | e.g. Cardiologist |
| `experience_years` | PositiveInteger | 0–60 |
| `consultation_fee` | Decimal(8,2) | ≥ 0 |
| `bio` | TextField | Optional |
| `is_available` | Boolean | Accepting patients |
| `created_at` | DateTime | Auto |

### `AvailabilitySlot` (doctors)
| Field | Type | Notes |
|-------|------|-------|
| `doctor` | FK(DoctorProfile) | Owner |
| `date` | DateField | Must not be in past |
| `start_time` | TimeField | |
| `end_time` | TimeField | Must be > start |
| `is_booked` | Boolean | Auto-set on booking |
| `created_at` | DateTime | Auto |

**Constraint:** `unique_together = ('doctor', 'date', 'start_time')`

### `Appointment` (appointments)
| Field | Type | Notes |
|-------|------|-------|
| `slot` | OneToOne(AvailabilitySlot) | Prevents double-booking |
| `patient` | FK(User) | Who booked |
| `status` | CharField | pending / completed / cancelled / no_show |
| `notes` | TextField | Doctor's prescription |
| `created_at` | DateTime | Auto |

---

## 🌐 REST API Endpoints

### 🔐 Authentication

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/register/` | Public | Register (doctor/patient) |
| POST | `/api/login/` | Public | Login → JWT tokens |

### 🧑‍⚕️ Doctor Profile

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/doctors/` | Public | List all doctors |
| GET | `/api/doctors/<id>/` | Public | Single doctor detail |
| POST | `/api/doctors/profile/` | Doctor | Create/update own profile |

### 📅 Availability Slots

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/slots/create/` | Doctor | Create slot |
| GET | `/api/slots/?doctor=<id>` | Public | Slots for a doctor |
| DELETE | `/api/slots/<id>/delete/` | Doctor | Delete own unbooked slot |

### 🩺 Appointments

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/appointments/book/` | Patient | Book a slot |
| GET | `/api/my-appointments/` | Patient | Own appointments |
| PUT | `/api/appointments/<id>/cancel/` | Patient | Cancel |
| GET | `/api/doctor/appointments/` | Doctor | Doctor's appointments |
| PUT | `/api/appointments/<id>/status/` | Doctor | Mark completed/no_show |
| PUT | `/api/appointments/<id>/notes/` | Doctor | Add prescription |

### 🔑 Required Headers for Protected Endpoints

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 📥 Example — Register a Doctor

**POST** `http://127.0.0.1:8000/api/register/`

```json
{
    "username": "dr_verma",
    "email": "verma@test.com",
    "password": "doctor1234",
    "role": "doctor"
}
```

**Response (201):**
```json
{
    "success": true,
    "message": "User registered successfully.",
    "data": {
        "user": { "id": 4, "username": "dr_verma", "role": "doctor" },
        "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
    }
}
```

### 📥 Example — Book an Appointment

**POST** `http://127.0.0.1:8000/api/appointments/book/`

**Headers:**
```
Authorization: Bearer <patient_access_token>
Content-Type: application/json
```

**Body:**
```json
{ "slot": 3 }
```

**Response (201):**
```json
{
    "success": true,
    "message": "Appointment booked successfully.",
    "data": {
        "id": 1,
        "patient_username": "ravi",
        "doctor_username": "dr_sharma",
        "doctor_specialization": "Cardiologist",
        "slot_date": "2026-10-20",
        "slot_start": "10:00:00",
        "slot_end": "10:30:00",
        "status": "pending"
    }
}
```

### 📤 Standard Response Format

**Success:**
```json
{ "success": true, "message": "...", "data": { ... } }
```

**Error:**
```json
{ "success": false, "message": "...", "errors": { "field": ["..."] } }
```

### ❌ Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (wrong role / not owner) |
| 404 | Not Found |

---

## 🌱 Dummy Data Seeder

MediTrack ships with **management commands** that populate the database instantly.

### Command 1 — Seed Users

```bash
python manage.py seed_users
```

**Creates:**
- 1 admin (`admin` / `admin1234`)
- 3 doctors (`dr_sharma`, `dr_patel`, `dr_khan` / `doctor1234`)
- 5 patients (`ravi`, `priya`, `arjun`, `sneha`, `vikram` / `patient1234`)

### Command 2 — Seed Doctor Profiles + Slots

```bash
python manage.py seed_doctors
```

**Creates:**
- 3 doctor profiles with specialization, experience, fee, bio
- 8 availability slots per doctor (next 2 days, 4 time slots each)
- Total: **24 slots**

### Command 3 — Seed Appointments

```bash
python manage.py seed_appointments
```

**Creates 6 appointments:**
| Patient | Doctor | Status |
|---------|--------|--------|
| ravi | dr_sharma | pending |
| priya | dr_sharma | completed (with notes) |
| arjun | dr_patel | pending |
| sneha | dr_patel | no_show |
| vikram | dr_khan | completed (with notes) |
| ravi | dr_khan | cancelled |

### Run All at Once

```bash
python manage.py seed_all
```

### Reset + Reseed

```bash
del db.sqlite3              # Windows
rm db.sqlite3               # Mac/Linux

python manage.py migrate
python manage.py seed_all
```

---

## 🧩 Function Reference

### `accounts/views.py`

| Function | Purpose |
|----------|---------|
| `get_tokens_for_user(user)` | Generate JWT access + refresh tokens |
| `register_user(request)` | Handle POST `/api/register/` |
| `login_user(request)` | Handle POST `/api/login/` |

### `doctors/views.py`

| Function | Purpose |
|----------|---------|
| `create_or_update_profile(request)` | Doctor profile upsert |
| `list_doctors(request)` | Public doctor list |
| `doctor_detail(request, doctor_id)` | Public doctor detail |
| `create_slot(request)` | Doctor adds availability slot |
| `list_slots(request)` | Public slot list (filter by `?doctor=`) |
| `delete_slot(request, slot_id)` | Doctor deletes own unbooked slot |

### `appointments/views.py`

| Function | Purpose |
|----------|---------|
| `book_appointment(request)` | Patient books a slot |
| `my_appointments(request)` | Patient's own list |
| `cancel_appointment(request, id)` | Patient cancels; frees slot |
| `doctor_appointments(request)` | Doctor's own bookings |
| `update_appointment_status(request, id)` | Mark completed/no_show |
| `add_appointment_notes(request, id)` | Add prescription notes |
| `page_login`, `page_register`, `page_doctors` | Page renderers |
| `page_my_appointments`, `page_doctor_dashboard` | Page renderers |

### `utils/responses.py`

| Function | Purpose |
|----------|---------|
| `success_response(data, message, status)` | Standard success JSON |
| `error_response(message, status, errors)` | Standard error JSON |

### `serializers.py` — Custom methods

| Method | Purpose |
|--------|---------|
| `RegisterSerializer.validate_username()` | Unique username check |
| `RegisterSerializer.validate_email()` | Unique email check |
| `RegisterSerializer.validate_role()` | Role must be doctor/patient |
| `RegisterSerializer.create()` | Hashes password via `create_user()` |
| `LoginSerializer.validate()` | Authenticates credentials |
| `DoctorProfileSerializer.validate_experience_years()` | 0–60 check |
| `DoctorProfileSerializer.validate_consultation_fee()` | Not negative |
| `AvailabilitySlotSerializer.validate()` | end_time > start_time AND date not in past |
| `ApplicationSerializer.get_resume_url()` | Build full URL |

---

## 🖥 Frontend Pages

| Page | URL | Who | Purpose |
|------|-----|-----|---------|
| Login | `/login/` | Public | Login form |
| Register | `/register/` | Public | Register as doctor/patient |
| Doctors | `/doctors/` | Public | Browse doctors + booking modal |
| My Appointments | `/my-appointments/` | Patient | Own bookings + cancel |
| Doctor Dashboard | `/doctor/` | Doctor | Profile, slots, appointments |
| Admin | `/admin/` | Superuser | Data inspection |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### Step 1 — Setup

```bash
# Clone
git clone <your-repo-url>
cd meditrack

# Create virtual environment
python -m venv env

# Activate
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure Environment

Create `.env` in the project root:

```
SECRET_KEY=your-random-secret-key
DEBUG=True
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4 — Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5 — Seed Dummy Data (Recommended)

```bash
python manage.py seed_all
```

This creates admin + 3 doctors + 5 patients + 24 slots + 6 appointments.

### Step 6 — Run the Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

---

## 🎮 How to Use the App

### 🧑‍⚕️ As a Doctor

1. **Login** as `dr_sharma` / `doctor1234` (if seeded)
   — OR — **Register** with role = Doctor
2. Navbar shows **Dashboard**
3. Click **Dashboard** → save your profile (specialization, fees, bio)
4. Add availability slots (future date + time range)
5. View **My Appointments** (auto-populated by seeder)
6. Add **notes** to an appointment (prescription)
7. Mark **Completed** or **No Show**

### 👤 As a Patient

1. **Login** as `ravi` / `patient1234` (if seeded)
   — OR — **Register** with role = Patient
2. Navbar shows **My Appointments**
3. Click **Doctors** → browse specialists
4. Click **View Slots & Book** on any doctor
5. Modal opens with available slots → click **Book**
6. Go to **My Appointments** → see status badge (PENDING / COMPLETED / CANCELLED)
7. Cancel pending appointments if needed

### 🔄 Cross-Role Flow Example

```
Doctor adds slot ──────────► Patient sees slot ──────► Patient books
                                                              │
                                                              ▼
                                              Appointment created (pending)
                                                              │
                                                              ▼
                                                    Doctor sees it in dashboard
                                                              │
                                                              ▼
                                              Doctor adds notes + marks completed
                                                              │
                                                              ▼
                                                    Patient sees updated status
```


```
PATIENT REQUESTS
       │
       ▼
  ┌────────────┐
  │ REQUESTED  │  (gray) — Slot still free
  └─────┬──────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
┌─────────┐ ┌──────────┐
│ACCEPTED │ │ REJECTED │  (slot stays free)
│ (blue)  │ │  (red)   │
└────┬────┘ └──────────┘
     │
     ├──► COMPLETED (green)
     ├──► NO_SHOW   (yellow)
     └──► CANCELLED (by patient)

```

---

## 🐛 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AUTH_USER_MODEL refers to model 'accounts.User'` | Custom User not created yet | Create model, then migrate |
| `Unknown command: 'seed_appointments'` | Missing `management/commands/` folder or `__init__.py` | Add empty `__init__.py` in both folders |
| `401 Unauthorized` | Missing/invalid JWT | Add `Authorization: Bearer <token>` header |
| `403 Only doctors can ...` | Logged in as patient | Login with the correct role |
| `400 Slot date cannot be in the past` | Past date submitted | Choose a future date |
| `400 End time must be after start time` | Invalid slot times | Ensure end > start |
| `400 This slot is already booked` | Double-booking attempt | Pick another slot |
| `400 Please create your doctor profile first` | Doctor without profile | Save profile in dashboard first |
| `Cannot delete a slot that is already booked` | Booked slot | Cancel the appointment first |
| Static files not loading | `STATICFILES_DIRS` not set | Check `settings.py` |

### Debug Tips

1. **Open browser console** (F12) → check for JS errors
2. **Check Network tab** → see the actual API request + response
3. **Check server terminal** → look for Python tracebacks
4. **Use Postman** to test endpoints independently of the frontend

---

## 🎓 What I Learned

- Building a **multi-app Django project** with clean separation of concerns
- **Custom User model** with role-based access (`doctor` / `patient`)
- **JWT authentication** with access + refresh tokens
- **Function-based views** with clear docstrings
- **RESTful API** design with standardized JSON responses
- **OneToOneField**, **ForeignKey**, **unique_together** relationships
- **Auto state transitions** (slot becomes booked on booking; freed on cancel)
- **Cross-field validation** in DRF serializers
- **Role-aware Bootstrap frontend** with vanilla JS
- **Management commands** to seed realistic dummy data
- **File organization** mirroring real-world Django projects

---

## 🧠 Interview Talking Points

1. **Why a custom User model?**
   > *"I needed a `role` field to distinguish doctors from patients. Django's default User doesn't support roles out of the box, so I extended `AbstractUser` and added helper methods `is_doctor()` and `is_patient()`."*

2. **How do you prevent double-booking?**
   > *"The Appointment model uses a `OneToOneField` to `AvailabilitySlot`, which guarantees one appointment per slot at the database level. On top of that, I check `slot.is_booked` in the view before creating an appointment, and flip the flag when booking succeeds."*

3. **How do you free a slot on cancel?**
   > *"When a patient cancels, the appointment status changes to `cancelled`, and I reset `slot.is_booked = False` so another patient can book the same slot."*

4. **How do you validate slot timings?**
   > *"The `AvailabilitySlotSerializer` has a `validate()` method that checks two rules: `end_time > start_time`, and the slot date is not in the past. Both return `ValidationError` with clear messages."*

5. **Why function-based views?**
   > *"For a small API, function-based views are simpler to read and debug. Each view does one thing, and permissions are checked at the top in plain Python — easy to explain and test."*

6. **How do you enforce role permissions?**
   > *"Every protected view starts with `if not request.user.is_doctor()` or `is_patient()`. If the role doesn't match, it returns 403 immediately. I also check ownership — e.g., only the slot's doctor can delete it."*

7. **How do you seed test data?**
   > *"I wrote Django management commands (`seed_users`, `seed_doctors`, `seed_appointments`) that create realistic dummy data. Running `python manage.py seed_all` populates the entire database in seconds, so anyone cloning the repo can see the app working immediately."*

8. **Why JWT over sessions?**
   > *"JWT is stateless — the server doesn't need to store sessions, which scales better and works well for APIs consumed by separate frontends or mobile apps."*

9. **How do you structure the project?**
   > *"Each domain has its own app: `accounts` for authentication, `doctors` for profiles and slots, `appointments` for bookings, and `utils` for shared helpers. This keeps concerns separate and the codebase easy to navigate."*

10. **What would you add next?**
    > *"Search and filter for doctors by specialization, email notifications on booking, file uploads for prescriptions, and a doctor review system."*

---

## 🚀 Future Enhancements (Optional)

- 🔍 Search / filter doctors by specialization
- 📧 Email notifications on booking
- 📄 Prescription PDF generation
- ⭐ Doctor ratings and reviews
- 📱 Video consultation integration
- 🐳 Docker setup for consistent environments
- ☁️ Deploy to Render / Railway

---

## 📜 License

MIT — free to use, modify, and learn from.

---

## 👨‍💻 Author

**RaviVarma**
- 🎓 Fresher | Python • Django • REST API Developer
- 🔗 GitHub: [github.com/varma5359](https://github.com/varma5359)


> *"Built from scratch — every line of code understood and documented."*