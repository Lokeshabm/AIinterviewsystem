# AI Interview Preparation System

A Django-based interview preparation platform with resume upload, AI question generation, interview evaluation, scoring, and certificate download.

## Features

- User registration, login, logout
- Resume upload and parsing for PDF/DOCX
- OpenRouter-based interview question generation and answer evaluation
- Interview interface with camera preview, speech-to-text, timer, and progress
- Score tracking and certificate generation with ReportLab
- Authenticated dashboard and score pages

## Setup

1. Clone or open the project folder.
2. Create a virtual environment and activate it.
3. Install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in the required values:

```bash
DJANGO_SECRET_KEY=your-actual-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
OPENROUTER_API_KEY=your-openrouter-api-key
MEDIA_ROOT=media
MEDIA_URL=/media/
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

8. Visit `http://127.0.0.1:8000/`.

## OpenRouter Integration

### Configuration

- **API Key**: Get your key from OpenRouter (https://openrouter.ai/)
- **Models**: Uses `meta-llama/llama-3-8b-instruct` by default
- **Environment**: Key stored securely in `.env`
- **Validation**: System checks for a valid OpenRouter API key before requests

### API Endpoint

**POST** `/api/ai/generate/`

**Request Body:**
```json
{
  "prompt": "Your question or prompt here",
  "model": "meta-llama/llama-3-8b-instruct",
  "max_tokens": 150,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI generated response",
  "model": "meta-llama/llama-3-8b-instruct",
  "prompt_length": 25
}
```

### Testing Locally

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Test the API endpoint with curl:
   ```bash
   curl -X POST http://localhost:8000/api/ai/generate/ \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, how are you?"}'
   ```

### Frontend Example

```javascript
async function getAIResponse(prompt) {
    try {
        const response = await fetch('/api/ai/generate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                prompt: prompt,
                model: 'meta-llama/llama-3-8b-instruct',
                max_tokens: 150,
                temperature: 0.7
            })
        });

        const data = await response.json();

        if (data.success) {
            return data.response;
        }
        throw new Error(data.error);
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

## Security Best Practices

- API keys are stored in environment variables, never in code
- Input validation on prompts (length limits, sanitization)
- CSRF protection for web requests
- HTTPS in production
- Monitor API usage and quota

## Project Structure

```
ai_interview_system/
├── ai/                          # OpenRouter integration app
│   ├── views.py                 # API views
│   ├── urls.py                  # URL routing
│   └── ...
├── interview/                   # Main interview app
├── ai_interview_system/         # Django settings
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables

## Question Generation and Import

### Generate Questions

Use the built-in question generator to create interview questions:

```bash
python manage.py generate_questions --count 100 --outdir question_generator/output
```

The generator uses parameterized templates and deduplication by canonical text hash to ensure diversity and avoid duplicate questions.

**Parameters:**
- `--count`: Number of questions to generate (default: 50)
- `--outdir`: Output directory (default: question_generator/output)

**Output files** in the specified directory:
- `generated_questions.json`: Primary JSON format (used for import)
- `questions.json`: Full question objects with metadata
- `questions.csv`: Tabular format with options A-D, correct answers, explanations
- `questions.sql`: SQL INSERT statements for database
- `questions.mongo.json`: MongoDB document format

**Generator files:**
- `question_generator/generator.py`: Main generation script with template-based question creation
- `question_generator/templates.json`: Question templates for various subjects and difficulty levels
- `question_generator/schema.sql`: PostgreSQL schema reference
- `question_generator/mongo_schema.json`: MongoDB document schema example

### Import Questions

Import generated questions into the database as a "Question Bank":

```bash
python manage.py import_questions question_generator/output/generated_questions.json
```

Or via the web interface:
1. Log in to the dashboard
2. Navigate to `/interview/import_questions/`
3. Enter the path to the JSON file: `question_generator/output/generated_questions.json`
4. Click "Import Questions"

The imported questions are stored in a special "Question Bank" Interview record and can be used for future interviews.

**Options:**

```bash
python manage.py import_questions <json_file> --skip-duplicates
```

- `--skip-duplicates`: Skip questions that already exist in the database

## Testing

- Register a new user
- Upload a PDF or DOCX resume
- Start an interview and answer the questions
- View saved scores and download a certificate if eligible

## Notes

- Keep your OpenRouter API key secret and never expose it in the frontend
- Use valid PDF/DOCX resume files under 5 MB
- Generated questions are deduplicated by canonical text hash to ensure diversity
- Imported questions are stored in a Question Bank Interview for centralized management
- The question generator is a reference implementation for template-based question generation

