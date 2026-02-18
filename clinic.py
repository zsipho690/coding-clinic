#!/usr/bin/env python3
"""
clinic.py - Coding Clinic Booking System
All-in-one tool for booking, viewing, and canceling sessions
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from calendar_sync import CalendarSync

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

# Configuration files in same directory as script (portable!)
CONFIG_FILE = SCRIPT_DIR / 'clinic_config.json'
DATA_FILE = SCRIPT_DIR / 'bookings.json'


class ClinicBookingSystem:
    """Main booking system"""

    def __init__(self):
        self.sync = CalendarSync()
        self.config = self.load_config()
        self.bookings = self.load_bookings()

    def load_config(self):
        """Load configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {'student_calendar': None, 'clinic_calendar': None}

    def save_config(self):
        """Save configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✓ Configuration saved to {CONFIG_FILE}")

    def load_bookings(self):
        """Load bookings database"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_bookings(self):
        """Save bookings database"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.bookings, f, indent=2)

    # === SETUP COMMAND ===
    def setup(self, student_calendar, clinic_calendar):
        """Setup calendar configuration"""
        print("\n" + "="*70)
        print("SETTING UP CODING CLINIC BOOKING SYSTEM")
        print("="*70 + "\n")

        # Verify calendars exist
        calendars = self.sync.get_calendars()
        calendar_ids = [cal['id'] for cal in calendars]

        if student_calendar not in calendar_ids:
            print(f"❌ Error: Student calendar '{student_calendar}' not found")
            print("\nAvailable calendars:")
            for cal in calendars:
                print(f"  • {cal['summary']}: {cal['id']}")
            return

        if clinic_calendar not in calendar_ids:
            print(f"❌ Error: Clinic calendar '{clinic_calendar}' not found")
            return

        self.config['student_calendar'] = student_calendar
        self.config['clinic_calendar'] = clinic_calendar
        self.save_config()

        print(f"✓ Student calendar: {student_calendar}")
        print(f"✓ Clinic calendar: {clinic_calendar}")
        print(f"\n✓ Configuration saved to {CONFIG_FILE}\n")

    # === VIEW COMMAND ===
    def view(self, date=None, status=None):
        """View bookings"""
        print("\n" + "="*70)
        print("CODING CLINIC CALENDAR")
        print("="*70 + "\n")

        if not self.bookings:
            print("📅 No bookings found\n")
            return

        # Filter bookings
        filtered = self.bookings

        if date:
            filtered = [b for b in filtered if b['date'] == date]

        if status:
            filtered = [b for b in filtered if b['status'] == status]

        if not filtered:
            print(f"📅 No bookings found for your filters\n")
            return

        # Group by date
        by_date = {}
        for booking in sorted(filtered, key=lambda x: (x['date'], x['time'])):
            if booking['date'] not in by_date:
                by_date[booking['date']] = []
            by_date[booking['date']].append(booking)

        # Display
        for date, bookings_list in sorted(by_date.items()):
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            print(f"📅 {date_obj.strftime('%A, %B %d, %Y')}")
            print("-" * 70)

            for booking in bookings_list:
                status_icon = {
                    'available': '🟢',
                    'booked': '🔴',
                    'empty': '⚪'
                }.get(booking['status'], '⚪')

                print(
                    f"{status_icon} {booking['time']} - {booking['status'].upper()}")

                if booking['status'] == 'available':
                    print(f"   Volunteer: {booking['volunteer_name']}")
                elif booking['status'] == 'booked':
                    print(f"   Volunteer: {booking['volunteer_name']}")
                    print(f"   Student: {booking['student_email']}")
                    print(f"   Subject: {booking['subject']}")

                print()

        # Summary
        total = len(filtered)
        available = len([b for b in filtered if b['status'] == 'available'])
        booked = len([b for b in filtered if b['status'] == 'booked'])
        print("-" * 70)
        print(
            f"Summary: {available} Available | {booked} Booked | {total} Total\n")

    # === VOLUNTEER COMMAND ===
    def volunteer(self, date, time, name, email):
        """Volunteer for a time slot"""
        print("\n" + "="*70)
        print("VOLUNTEERING FOR SLOT")
        print("="*70 + "\n")

        # Check if slot already exists
        existing = next((b for b in self.bookings
                        if b['date'] == date and b['time'] == time), None)

        if existing and existing.get('volunteer_email') == email:
            print(f"❌ You already volunteered for {date} at {time}\n")
            return

        if existing and existing.get('volunteer_email'):
            print(
                f"❌ Slot already has volunteer: {existing['volunteer_name']}\n")
            return

        # Calculate end time (30 minutes later)
        start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=30)

        start_iso = start.isoformat()
        end_iso = end.isoformat()

        # Create event in calendars
        summary = f"Coding Clinic - Available (Volunteer: {name})"
        description = f"Volunteer: {name} ({email})"

        event_id = self.sync.create_event(
            self.config['clinic_calendar'],
            summary,
            description,
            start_iso,
            end_iso,
            attendees=[email]
        )

        if not event_id:
            print("❌ Failed to create calendar event\n")
            return

        # Save booking
        booking = {
            'date': date,
            'time': time,
            'status': 'available',
            'volunteer_name': name,
            'volunteer_email': email,
            'event_id': event_id
        }

        if existing:
            self.bookings.remove(existing)

        self.bookings.append(booking)
        self.save_bookings()

        print(f"✓ Volunteered for {date} at {time}")
        print(f"✓ Event created in calendar")
        print(f"✓ Status: AVAILABLE\n")

    # === BOOK COMMAND ===
    def book(self, date, time, subject, description, student_email):
        """Book a slot"""
        print("\n" + "="*70)
        print("BOOKING SESSION")
        print("="*70 + "\n")

        # Find the slot
        booking = next((b for b in self.bookings
                       if b['date'] == date and b['time'] == time), None)

        if not booking:
            print(f"❌ No slot found for {date} at {time}")
            print("   Run: python clinic.py view --date {date}\n")
            return

        if booking['status'] != 'available':
            if booking['status'] == 'booked':
                print(f"❌ Slot already booked by {booking['student_email']}\n")
            else:
                print(f"❌ Slot has no volunteer available\n")
            return

        # Calculate times
        start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=30)

        start_iso = start.isoformat()
        end_iso = end.isoformat()

        # Delete old volunteer event
        if booking.get('event_id'):
            self.sync.delete_event(
                self.config['clinic_calendar'], booking['event_id'])

        # Create new booking event
        summary = f"Coding Clinic: {subject}"
        desc = f"Subject: {subject}\n\nDescription: {description}\n\nStudent: {student_email}\nVolunteer: {booking['volunteer_name']} ({booking['volunteer_email']})"

        event_id = self.sync.create_event(
            self.config['clinic_calendar'],
            summary,
            desc,
            start_iso,
            end_iso,
            attendees=[student_email, booking['volunteer_email']]
        )

        if not event_id:
            print("❌ Failed to create booking\n")
            return

        # Update booking
        booking['status'] = 'booked'
        booking['student_email'] = student_email
        booking['subject'] = subject
        booking['description'] = description
        booking['event_id'] = event_id
        booking['booked_at'] = datetime.now().isoformat()

        self.save_bookings()

        print(f"✓ Booked session with {booking['volunteer_name']}")
        print(f"✓ Date: {date} at {time}")
        print(f"✓ Subject: {subject}")
        print(f"✓ Calendar events created\n")

    # === CANCEL COMMAND ===
    def cancel(self, date, time, email, is_volunteer=False):
        """Cancel a booking or volunteer slot"""
        print("\n" + "="*70)
        print("CANCELING" if not is_volunteer else "CANCELING VOLUNTEER SLOT")
        print("="*70 + "\n")

        # Find the slot
        booking = next((b for b in self.bookings
                       if b['date'] == date and b['time'] == time), None)

        if not booking:
            print(f"❌ No slot found for {date} at {time}\n")
            return

        if is_volunteer:
            # Cancel volunteer
            if booking.get('volunteer_email') != email:
                print(f"❌ This is not your volunteer slot\n")
                return

            if booking['status'] == 'booked':
                print(
                    f"❌ Cannot cancel - slot is booked by {booking['student_email']}")
                print("   Ask them to cancel their booking first\n")
                return

            # Delete event
            if booking.get('event_id'):
                self.sync.delete_event(
                    self.config['clinic_calendar'], booking['event_id'])

            self.bookings.remove(booking)
            self.save_bookings()

            print(f"✓ Canceled volunteer slot for {date} at {time}")
            print(f"✓ Slot removed from calendar\n")

        else:
            # Cancel booking
            if booking['status'] != 'booked':
                print(f"❌ Slot is not booked\n")
                return

            if booking.get('student_email') != email:
                print(f"❌ This is not your booking\n")
                return

            # Delete booking event
            if booking.get('event_id'):
                self.sync.delete_event(
                    self.config['clinic_calendar'], booking['event_id'])

            # Recreate volunteer event
            start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end = start + timedelta(minutes=30)

            summary = f"Coding Clinic - Available (Volunteer: {booking['volunteer_name']})"
            description = f"Volunteer: {booking['volunteer_name']} ({booking['volunteer_email']})"

            event_id = self.sync.create_event(
                self.config['clinic_calendar'],
                summary,
                description,
                start.isoformat(),
                end.isoformat(),
                attendees=[booking['volunteer_email']]
            )

            # Reset to available
            booking['status'] = 'available'
            booking['event_id'] = event_id
            booking.pop('student_email', None)
            booking.pop('subject', None)
            booking.pop('description', None)
            booking.pop('booked_at', None)

            self.save_bookings()

            print(f"✓ Canceled booking for {date} at {time}")
            print(f"✓ Slot now available again\n")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Coding Clinic Booking System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup (first time only)
  python clinic.py setup --student your@email.com --clinic clinic@email.com
  
  # View all bookings
  python clinic.py view
  
  # View specific date
  python clinic.py view --date 2026-02-15
  
  # View only available slots
  python clinic.py view --status available
  
  # Volunteer for a slot
  python clinic.py volunteer --date 2026-02-15 --time 10:00 --name "Your Name" --email your@email.com
  
  # Book a slot
  python clinic.py book --date 2026-02-15 --time 10:00 --subject "Python help" --description "Need help with loops" --email student@email.com
  
  # Cancel your booking
  python clinic.py cancel-booking --date 2026-02-15 --time 10:00 --email student@email.com
  
  # Cancel your volunteer slot
  python clinic.py cancel-volunteer --date 2026-02-15 --time 10:00 --email volunteer@email.com
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Setup command
    setup_parser = subparsers.add_parser(
        'setup', help='Setup calendar configuration')
    setup_parser.add_argument(
        '--student', required=True, help='Student calendar ID')
    setup_parser.add_argument(
        '--clinic', required=True, help='Clinic calendar ID')

    # View command
    view_parser = subparsers.add_parser('view', help='View bookings')
    view_parser.add_argument('--date', help='Filter by date (YYYY-MM-DD)')
    view_parser.add_argument(
        '--status', choices=['available', 'booked', 'empty'], help='Filter by status')

    # Volunteer command
    vol_parser = subparsers.add_parser(
        'volunteer', help='Volunteer for a slot')
    vol_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    vol_parser.add_argument('--time', required=True, help='Time (HH:MM)')
    vol_parser.add_argument('--name', required=True, help='Your name')
    vol_parser.add_argument('--email', required=True, help='Your email')

    # Book command
    book_parser = subparsers.add_parser('book', help='Book a slot')
    book_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    book_parser.add_argument('--time', required=True, help='Time (HH:MM)')
    book_parser.add_argument('--subject', required=True, help='Subject/topic')
    book_parser.add_argument(
        '--description', required=True, help='Description of help needed')
    book_parser.add_argument('--email', required=True, help='Your email')

    # Cancel booking command
    cancel_book_parser = subparsers.add_parser(
        'cancel-booking', help='Cancel a booking')
    cancel_book_parser.add_argument(
        '--date', required=True, help='Date (YYYY-MM-DD)')
    cancel_book_parser.add_argument(
        '--time', required=True, help='Time (HH:MM)')
    cancel_book_parser.add_argument(
        '--email', required=True, help='Your email')

    # Cancel volunteer command
    cancel_vol_parser = subparsers.add_parser(
        'cancel-volunteer', help='Cancel volunteer slot')
    cancel_vol_parser.add_argument(
        '--date', required=True, help='Date (YYYY-MM-DD)')
    cancel_vol_parser.add_argument(
        '--time', required=True, help='Time (HH:MM)')
    cancel_vol_parser.add_argument('--email', required=True, help='Your email')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize system
    clinic = ClinicBookingSystem()

    # Run command
    if args.command == 'setup':
        clinic.setup(args.student, args.clinic)

    elif args.command == 'view':
        clinic.view(date=args.date, status=args.status)

    elif args.command == 'volunteer':
        clinic.volunteer(args.date, args.time, args.name, args.email)

    elif args.command == 'book':
        clinic.book(args.date, args.time, args.subject,
                    args.description, args.email)

    elif args.command == 'cancel-booking':
        clinic.cancel(args.date, args.time, args.email, is_volunteer=False)

    elif args.command == 'cancel-volunteer':
        clinic.cancel(args.date, args.time, args.email, is_volunteer=True)


if __name__ == "__main__":
    main()
