# Drafter AI Agent

Drafter AI Agent is a Python-based tool designed to assist users in creating, updating, saving, and emailing documents. It leverages the power of AI to streamline document management and communication.

## Features

- **Update Documents**: Modify the in-memory document content dynamically.
- **Save Documents**: Save the document to a `.txt` file with a specified filename.
- **Email Validation**: Validate email addresses before sending documents.
- **Send Documents via Email**: Email the saved document to a recipient.
- **AI-Powered Assistance**: Uses OpenAI's GPT-4 model for intelligent interactions.

## Requirements

Ensure you have the following installed:

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dshathwikr/drafter-ai-agent.git
   cd drafter-ai-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Fill in the required values for `SMTP_USERNAME`, `SMTP_PASSWORD`, and `OPENAI_API_KEY`.

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. Follow the prompts to update, save, or email your document.

## Environment Variables

- `SMTP_USERNAME`: Your SMTP username for sending emails.
- `SMTP_PASSWORD`: Your SMTP password for sending emails.
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 integration.

## Example Workflow

1. Start the agent.
2. Update the document content using the `update` tool.
3. Save the document to a `.txt` file using the `save` tool.
4. Provide an email address to send the document.

## File Structure

- `main.py`: Core logic for the Drafter AI Agent.
- `requirements.txt`: List of dependencies.
- `.env.example`: Example environment variables file.
