
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="deepseek/deepseek-r1:free",
  messages=[
    {
      "role": "user",
      "content": "de quelle couleur est le cheval blanc ?"
    }
  ]
)
print(completion.choices[0].message.content)