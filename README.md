# 🏥 Coding Clinic Booking System

A simplified command-line tool for managing WeThinkCode Coding Clinic bookings with Google Calendar integration.

---

## 📋 Project Overview

This system allows students to:

- ✅ Volunteer their time to help other students
- ✅ Book coding clinic sessions with available volunteers
- ✅ View all bookings in a clean calendar format
- ✅ Cancel bookings or volunteer slots
- ✅ Sync automatically with Google Calendar

All operations sync in real-time with Google Calendar — no double bookings, no confusion!

---

## 📁 Project Structure

coding_clinic/
├── clinic.py # Main booking system (all commands)
├── calendar_sync.py # Google Calendar synchronization
├── secrets/
│ ├── credentials.json # Google API credentials (you download this)
│ └── token.pickle # Auto-generated authentication token
├── requirements.txt # Python dependencies
├── clinic_config.json # Auto-generated configuration
├── bookings.json # Auto-generated bookings database
└── README.md # This file

### File Descriptions

- **clinic.py** — Main application with all booking commands (`setup`, `view`, `volunteer`, `book`, `cancel`)
- **calendar_sync.py** — Handles Google Calendar API authentication and operations
- **secrets/credentials.json** — OAuth 2.0 credentials from Google Cloud Console (you must download this)
- **secrets/token.pickle** — Auto-generated after first authentication (do not edit)
- **requirements.txt** — Python package dependencies for pip
- **clinic_config.json** — Auto-generated config file (stores calendar IDs)
- **bookings.json** — Auto-generated database of all bookings

---

# 🚀 Setup Instructions

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dateutil
```

## Dependencies Installed

- google-api-python-client — Google Calendar API client

- google-auth-httplib2 — HTTP library for Google authentication

- google-auth-oauthlib — OAuth 2.0 authentication flow

- python-dateutil — Date/time parsing utilities

## Step 2: Get Google Calendar Credentials

Go to: https://console.cloud.google.com/

Create a new project (or select existing)

Project name: Coding Clinic Booking

Enable Google Calendar API

Go to Credentials → Create Credentials → OAuth client ID

Configure consent screen (choose External)

Application type: Desktop App

Name: Coding Clinic Desktop

Download credentials

Save as:

```bash
secrets/credentials.json
```

## Step 3: Test Calendar Connection

```bash
python calendar_sync.py
```

Expected output:

```pgsql
✓ Connected to Google Calendar
✓ Found 2 calendar(s):

  • My Calendar
    ID: your-email@gmail.com
    (Primary Calendar)
```

A browser window will open for first-time authentication.
Grant calendar access when prompted.

## Step 4: Configure the System

```bash
python clinic.py setup --student YOUR_EMAIL@gmail.com --clinic CLINIC_EMAIL@gmail.com
```

Example:

```bash
python clinic.py setup --student student@wethinkcode.co.za --clinic clinic@wethinkcode.co.za
```

# 📖 Usage Guide

```bash
All Available Commands
# Setup (run once)
python clinic.py setup --student EMAIL --clinic EMAIL

# View all bookings
python clinic.py view

# View specific date
python clinic.py view --date 2026-02-15

# View only available slots
python clinic.py view --status available

# Volunteer for a slot
python clinic.py volunteer --date 2026-02-15 --time 10:00 --name "Your Name" --email your@email.com

# Book a session
python clinic.py book --date 2026-02-15 --time 10:00 --subject "Python help" --description "Need help with loops" --email student@email.com

# Cancel your booking
python clinic.py cancel-booking --date 2026-02-15 --time 10:00 --email student@email.com

# Cancel your volunteer slot
python clinic.py cancel-volunteer --date 2026-02-15 --time 10:00 --email volunteer@email.com

```

## Command Help

```bash
python clinic.py --help
python clinic.py setup --help
python clinic.py view --help
python clinic.py volunteer --help
python clinic.py book --help
python clinic.py cancel-booking --help
python clinic.py cancel-volunteer --help
```

## 🎯 Complete Workflow Example

```bash
# 1. Setup (first time only)
python clinic.py setup --student me@email.com --clinic clinic@email.com

# 2. View current calendar
python clinic.py view

# 3. Volunteer for a time slot
python clinic.py volunteer --date 2026-02-15 --time 10:00 --name "Alex" --email alex@email.com

# 4. View calendar
python clinic.py view --date 2026-02-15

# 5. Book the slot
python clinic.py book --date 2026-02-15 --time 10:00 --subject "Git help" --description "Merge conflicts" --email student@email.com

# 6. Cancel booking
python clinic.py cancel-booking --date 2026-02-15 --time 10:00 --email student@email.com

# 7. Cancel volunteer slot
python clinic.py cancel-volunteer --date 2026-02-15 --time 10:00 --email alex@email.com

```

## 🔧 Troubleshooting

Problem: credentials.json not found

```bash
ls secrets/credentials.json
```

If not found, download from Google Cloud Console and save as:

```bash
secrets/credentials.json
```

Problem: "Not Found" error when accessing calendar

Run:

```bash
python calendar_sync.py
```

Note the calendar IDs shown

Use those exact IDs in setup:

```bash
python clinic.py setup --student EXACT_ID --clinic EXACT_ID
```

Problem: Module not found

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install google-api-python-client
pip install google-auth-httplib2
pip install google-auth-oauthlib
pip install python-dateutil
```

Problem: Authentication window won’t open

```bash
rm secrets/token.pickle
python calendar_sync.py
```

Problem: "Slot not found" when booking

Someone must volunteer first:

```bash
python clinic.py volunteer --date 2026-02-15 --time 10:00 --name "Name" --email email@example.com
```

Then book:

```bash
python clinic.py book --date 2026-02-15 --time 10:00 --subject "Help" --description "Need help" --email student@email.com
```

## ✅ Minimum Requirements Before Submission

All acceptance tests must pass:

```bash
python -m unittest tests/test_main.py
```

- Google Calendar authentication must work

- No hardcoded file paths

- requirements.txt installs correctly

# 🏁 Final Notes

- Do not commit token.pickle to GitHub

- Keep credentials.json private

- Always test before submission

- Make sure LMS acceptance tests pass before review
