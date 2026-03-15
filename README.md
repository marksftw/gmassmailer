<p align="center">
  <img src="gmassmailer-icon.png" alt="gmassmailer logo" width="150">
</p>

# gMassMailer

A CLI bulk email sender that uses the [Google Workspace CLI (`gws`)](https://github.com/googleworkspace/cli) to send personalized emails from your Google Workspace or Gmail account. Supports plain text and HTML email bodies with template placeholders.

## Prerequisites

- **Python 3.6+**
- **Node.js / npm** (to install the `gws` CLI)
- **A Google account** with Gmail enabled

## Installation

### 1. Install the Google Workspace CLI

```bash
npm install -g @googleworkspace/cli
```

Verify it installed:

```bash
gws --version
```

### 2. Clone this repo

```bash
git clone https://github.com/marksftw/gmassmailer.git
cd gmassmailer
```

## Usage

### Sending Emails

#### Preview emails without sending (dry run)

```bash
python3 send_emails.py -c contacts.csv -s subject.txt -b body.txt --dry-run
```

#### Send emails

```bash
python3 send_emails.py -c contacts.csv -s subject.txt -b body.txt
```

#### Send HTML emails

```bash
python3 send_emails.py -c contacts.csv -s subject.txt -b body.html
```

#### Send a test email

Send a single test email to verify everything works. You'll be prompted for a recipient email address — no CSV file needed:

```bash
python3 send_emails.py -s subject.txt -b body.html --test
```

The subject will be prefixed with `[TEST]` and template placeholders will be filled with "Test User".

#### Custom delay between sends

```bash
python3 send_emails.py -c contacts.csv -s subject.txt -b body.txt --delay 2.5
```

#### All flags

| Flag | Description |
|---|---|
| `-c`, `--csv` | Path to CSV file (required unless using `--test`) |
| `-s`, `--subject` | Path to subject line file (required) |
| `-b`, `--body` | Path to body template file (required) |
| `--delay` | Seconds between sends (default: 1.0) |
| `--dry-run` | Preview emails without sending |
| `--test` | Send a single test email — prompts for a recipient address |

### Validating Emails (Optional but Recommended)

Before sending, validate that all email addresses in your CSV are properly formatted:

```bash
python3 validate_emails.py contacts.csv
```

This will catch missing `@` signs, invalid domains, empty entries, and other formatting issues. If everything looks good:

```
All email addresses are valid.
```

If there are problems, it will list them:

```
Found 2 invalid email(s):

  Row 3: John Smith - john@
  Row 5: Jane Doe - (empty)
```

## File Setup

You need three files to send emails:

### contacts.csv

A CSV file with `first_name`, `last_name`, and `email` columns:

```csv
first_name,last_name,email
jane,doe,jane.doe@example.com
john,smith,john.smith@example.com
```

### subject.txt

A single line with your email subject:

```
Your Subject Line Here
```

### Body file (plain text or HTML)

**Plain text** (`body.txt`):

```
Hello {{first_name}} {{last_name}},

This is a sample email body.

Thanks,
Your Name
```

**HTML** (`body.html`):

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Hello {{first_name}},</h1>
  <p>This is an <strong>HTML email</strong>.</p>
</body>
</html>
```

The script auto-detects the format based on file extension (`.html`/`.htm` = HTML, anything else = plain text).

### Template placeholders

Use these placeholders in your body and they'll be replaced per-contact:

| Placeholder | Replaced with |
|---|---|
| `{{first_name}}` | Contact's first name (title case) |
| `{{last_name}}` | Contact's last name (title case) |
| `{{email}}` | Contact's email address |

## Tips

- Use `--dry-run` first to verify your emails look correct before sending
- Use `--test` to send a single test email before doing a full send
- HTML emails support `<img>` tags with externally hosted images (e.g., Imgur, your own server)
- The `emails/` directory is gitignored, so you can keep your real contact lists and email templates there without committing them

## Google Developer Setup

Before you can send emails, you need to set up OAuth credentials in the Google Cloud Console so that `gws` can authenticate with your Gmail account.

### 1. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
3. Name your project and click **Create**

### 2. Enable the Gmail API

1. In your project, search for **Gmail API** in the top search bar
2. Click **Gmail API** and click **Enable**

### 3. Configure the OAuth consent screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** (or **Internal** if using Google Workspace)
3. Fill in the required fields (app name, support email)
4. Under **Scopes**, add:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
5. Under **Test users**, add the Gmail/Workspace email you'll send from
6. Click **Save**

### 4. Create OAuth credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Application type: **Desktop app** (important — do not use "Web application")
4. Click **Create** and download the JSON file
5. Move it to the gws config directory:
   ```bash
   cp ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
   ```

### 5. Authenticate with gws

```bash
gws auth login
```

This will print a URL. Open it in your browser, sign in with your Google account, and approve access. The `gws` CLI listens on a local port to catch the callback automatically. Once authenticated, your credentials are stored locally and you're ready to send.
