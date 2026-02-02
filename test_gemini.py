from google import genai
import settings

client = genai.Client(api_key=settings.Gemini_API_KEY)

response = client.models.generate_content(
    model="models/gemini-2.0-flash",
    contents="こんにちは。応答テストです"
)

print(response.text)
