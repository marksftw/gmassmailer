#!/usr/bin/env python3
"""
Email Address Validator

Validates email addresses in a CSV file and prints any invalid entries.

Usage:
    python3 validate_emails.py contacts.csv
"""

import csv
import re
import sys

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_emails.py <csv_file>", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]

    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                print("Error: CSV file is empty or has no header row", file=sys.stderr)
                sys.exit(1)

            cleaned_fields = [field.strip() for field in reader.fieldnames]
            if "email" not in cleaned_fields:
                print("Error: CSV missing required 'email' column", file=sys.stderr)
                sys.exit(1)

            invalid = []
            for row_num, row in enumerate(reader, start=2):
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                email = cleaned_row.get("email", "")
                first_name = cleaned_row.get("first_name", "")
                last_name = cleaned_row.get("last_name", "")

                if not email:
                    invalid.append((row_num, first_name, last_name, "(empty)"))
                elif not EMAIL_REGEX.match(email):
                    invalid.append((row_num, first_name, last_name, email))

    except FileNotFoundError:
        print(f"Error: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    if invalid:
        print(f"Found {len(invalid)} invalid email(s):\n")
        for row_num, first, last, email in invalid:
            print(f"  Row {row_num}: {first} {last} - {email}")
        sys.exit(1)
    else:
        print("All email addresses are valid.")


if __name__ == "__main__":
    main()
