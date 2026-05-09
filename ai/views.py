import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize OpenRouter client
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

def test_page(request):
    """Render the OpenRouter API test page."""
    return render(request, 'ai/test.html')

@csrf_exempt
@require_http_methods(["POST"])
def generate_response(request):
    """
    API endpoint to generate AI response from OpenRouter.

    Expects JSON payload with:
    - prompt: str (required)
    - model: str (optional, default: meta-llama/llama-3-8b-instruct)
    - max_tokens: int (optional, default: 150)
    - temperature: float (optional, default: 0.7)

    Returns:
        JSON response with generated content or error message
    """
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt')
        model = data.get('model', 'meta-llama/llama-3-8b-instruct')
        max_tokens = data.get('max_tokens', 150)
        temperature = data.get('temperature', 0.7)

        if not prompt:
            return JsonResponse({'error': 'Missing required field: prompt'}, status=400)
        if len(prompt.strip()) == 0:
            return JsonResponse({'error': 'Prompt cannot be empty'}, status=400)
        if len(prompt) > 10000:
            return JsonResponse({'error': 'Prompt too long (max 10000 characters)'}, status=400)

        response = openrouter_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        response_text = response.choices[0].message.content.strip()

        logger.info(f"Generated OpenRouter response for prompt: {prompt[:50]}...")

        return JsonResponse({
            'success': True,
            'response': response_text,
            'model': model,
            'prompt_length': len(prompt)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        logger.error(f"Error generating OpenRouter response: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
