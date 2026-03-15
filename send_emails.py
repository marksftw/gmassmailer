#!/usr/bin/env python3
"""
Google Workspace CLI Email Sender

Sends personalized emails to contacts using the gws CLI.

Usage:
    python3 send_emails.py --dry-run         # preview without sending
    python3 send_emails.py                   # send for real
    python3 send_emails.py --csv my.csv      # custom CSV file

Body file can be plain text (.txt) or HTML (.html).
HTML bodies are sent with the --html flag automatically.
"""

import argparse
import csv
import os
import subprocess
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Send personalized emails via gws CLI"
    )
    parser.add_argument(
        "-c", "--csv",
        help="Path to CSV file with columns: first_name, last_name, email (not used with --test)",
    )
    parser.add_argument(
        "-s", "--subject",
        required=True,
        help="Path to subject line file",
    )
    parser.add_argument(
        "-b", "--body",
        required=True,
        help="Path to body template file (.txt or .html) with {{first_name}}, {{last_name}} placeholders",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between sends (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without sending",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Send a single test email — prompts for a recipient email address",
    )
    args = parser.parse_args()

    if not args.test and not args.csv:
        parser.error("--csv is required when not using --test")

    return args


def validate_files(csv_path, subject_path, body_path):
    """Validate that all required files exist and are non-empty."""
    errors = []
    files = [(subject_path, "Subject"), (body_path, "Body")]
    if csv_path is not None:
        files.insert(0, (csv_path, "CSV"))
    for path, label in files:
        try:
            with open(path, "r") as f:
                content = f.read().strip()
                if not content:
                    errors.append(f"{label} file is empty: {path}")
        except FileNotFoundError:
            errors.append(f"{label} file not found: {path}")

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def read_contacts(csv_path):
    """Read contacts from CSV. Validates required columns."""
    contacts = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            print("Error: CSV file is empty or has no header row", file=sys.stderr)
            sys.exit(1)

        cleaned_fields = [field.strip() for field in reader.fieldnames]
        required = {"first_name", "last_name", "email"}
        missing = required - set(cleaned_fields)
        if missing:
            print(
                f"Error: CSV missing required columns: {', '.join(sorted(missing))}",
                file=sys.stderr,
            )
            print(f"Found columns: {', '.join(cleaned_fields)}", file=sys.stderr)
            sys.exit(1)

        for row_num, row in enumerate(reader, start=2):
            cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
            email = cleaned_row.get("email", "")
            if not email:
                print(f"Warning: Skipping row {row_num} - no email address", file=sys.stderr)
                continue
            contacts.append(cleaned_row)

    return contacts


def read_file(path):
    with open(path, "r") as f:
        return f.read().strip()


def personalize(template, contact):
    first_name = contact.get("first_name", "").title()
    last_name = contact.get("last_name", "").title()
    email = contact.get("email", "")
    result = template
    result = result.replace("{{first_name}}", first_name)
    result = result.replace("{{last_name}}", last_name)
    result = result.replace("{{email}}", email)
    return result


def send_email(to, subject, body, html=False):
    try:
        cmd = ["gws", "gmail", "+send", "--to", to, "--subject", subject, "--body", body]
        if html:
            cmd.append("--html")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            return False, error
        return True, None
    except FileNotFoundError:
        return False, "gws CLI not found. Install with: npm install -g @googleworkspace/cli"
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 30 seconds"


def main():
    args = parse_args()

    if args.test:
        # Test mode: prompt for a single recipient email
        validate_files(None, args.subject, args.body)

        test_email = input("Enter the email address to send a test to: ").strip()
        if not test_email:
            print("Error: No email address provided.", file=sys.stderr)
            sys.exit(1)

        subject = f"[TEST] {read_file(args.subject)}"
        body_template = read_file(args.body)
        is_html = os.path.splitext(args.body)[1].lower() in (".html", ".htm")

        contact = {
            "first_name": "Test",
            "last_name": "User",
            "email": test_email,
        }
        body = personalize(body_template, contact)

        print()
        print("=" * 50)
        print("TEST MODE - Sending a single test email")
        print("=" * 50)
        print(f"To:       {test_email}")
        print(f"Subject:  {subject}")
        print(f"Body:     {args.body} ({'HTML' if is_html else 'plain text'})")
        print("=" * 50)
        print()

        if args.dry_run:
            print("DRY RUN - Email not sent")
            print()
            print(f"Body:")
            print(body)
        else:
            print(f"Sending to {test_email}...", end=" ")
            success, error = send_email(test_email, subject, body, html=is_html)
            if success:
                print("Sent")
            else:
                print(f"FAILED - {error}")
                sys.exit(1)

        print()
        print("=" * 50)
        return

    # Normal mode: send to all contacts in CSV
    validate_files(args.csv, args.subject, args.body)

    contacts = read_contacts(args.csv)
    subject = read_file(args.subject)
    body_template = read_file(args.body)

    # Auto-detect HTML based on file extension
    is_html = os.path.splitext(args.body)[1].lower() in (".html", ".htm")

    total = len(contacts)
    if total == 0:
        print("No contacts found in CSV.", file=sys.stderr)
        sys.exit(1)

    print("=" * 50)
    if args.dry_run:
        print("DRY RUN MODE - No emails will be sent")
        print("=" * 50)
    print(f"Subject:  {subject}")
    print(f"Body:     {args.body} ({'HTML' if is_html else 'plain text'})")
    print(f"Contacts: {total}")
    print(f"Delay:    {args.delay}s between emails")
    print("=" * 50)
    print()

    sent = 0
    failed = 0
    failed_contacts = []

    for i, contact in enumerate(contacts, start=1):
        first_name = contact.get("first_name", "").title()
        last_name = contact.get("last_name", "").title()
        email = contact.get("email", "")
        body = personalize(body_template, contact)

        if args.dry_run:
            print(f"--- Email {i}/{total} ---")
            print(f"To:      {first_name} {last_name} <{email}>")
            print(f"Subject: {subject}")
            print(f"Body:")
            print(body)
            print()
        else:
            print(f"[{i}/{total}] Sending to {first_name} {last_name} <{email}>...", end=" ")
            success, error = send_email(email, subject, body, html=is_html)

            if success:
                print("Sent")
                sent += 1
            else:
                print(f"FAILED - {error}")
                failed += 1
                failed_contacts.append(f"  {email} - {error}")

            if i < total:
                time.sleep(args.delay)

    print()
    print("=" * 50)
    if args.dry_run:
        print(f"Dry run complete. {total} emails previewed.")
        print(f"Run without --dry-run to send.")
    else:
        print(f"Done!  Sent: {sent} | Failed: {failed} | Total: {total}")
        if failed_contacts:
            print()
            print("Failed contacts:")
            for line in failed_contacts:
                print(line)
    print("=" * 50)


if __name__ == "__main__":
    main()
