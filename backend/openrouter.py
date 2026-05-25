"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_URL


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    image_base64: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via Ollama local API (OpenAI-compatible endpoint).
    If image_base64 is provided (data URL), attaches it to the last user message
    as multimodal content for vision-capable models.
    """
    headers = {
        "Content-Type": "application/json",
    }

    if image_base64:
        messages = list(messages)
        last = dict(messages[-1])
        last['content'] = [
            {"type": "text", "text": last['content']},
            {"type": "image_url", "image_url": {"url": image_base64}},
        ]
        messages = messages[:-1] + [last]

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
    image_base64: Optional[str] = None,
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel, optionally with an image.
    """
    import asyncio

    tasks = [query_model(model, messages, image_base64=image_base64) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
