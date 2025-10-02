from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, io, contextlib, re
from dotenv import load_dotenv
import openai

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# ------------------------------
# Configure OpenAI client
# ------------------------------
openai.api_type = "azure"
openai.api_base = OPENAI_ENDPOINT
openai.api_version = "2023-07-01-preview"
openai.api_key = OPENAI_KEY

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="Kafka AI Agent with Topic Memory")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Request Model
# ------------------------------
class PromptRequest(BaseModel):
    prompt: str

# ------------------------------
# Global topic memory
# ------------------------------
last_topic = None

def extract_topic_from_code(code: str):
    """Extract topic name from generated code if available."""
    match = re.search(r'topic_name\s*=\s*["\']([^"\']+)["\']', code)
    return match.group(1) if match else None

# ------------------------------
# Ask Azure OpenAI for Kafka Code + Explanation
# ------------------------------
def ask_openai_for_code(prompt: str, remembered_topic: str = None) -> dict:
    system_prompt = f"""
    You are a Kafka assistant agent.
    The user will ask questions about Kafka topics, configs, producing and consuming messages.

    Rules:
    - Respond ONLY with valid JSON object containing exactly two keys: "code" and "explanation".
    - Example response:
      {{"code": "from confluent_kafka.admin import AdminClient...", "explanation": "Your topic test-topic has retention 7 days"}}
    - "code" must be valid Python using confluent_kafka.
    - "explanation" must be a conversational English answer.
    - Assume bootstrap servers='{BOOTSTRAP_SERVERS}'.
    - If the user does not mention a topic but we have a remembered topic ({remembered_topic}), reuse that.
    - If no remembered topic exists, politely ask the user to provide a topic name.
    - To fetch topic configs (like retention.ms), ALWAYS use:
        from confluent_kafka.admin import AdminClient, ConfigResource
        admin = AdminClient({{"bootstrap.servers": "{BOOTSTRAP_SERVERS}"}})
        cr = ConfigResource("topic", topic_name)
        futures = admin.describe_configs([cr])
        for res, fut in futures.items():
            cfg = fut.result()
            entry = cfg.get("retention.ms")
            if entry and entry.value:
                retention_ms = int(entry.value)
                days = retention_ms / (1000*60*60*24)
                hours = retention_ms / (1000*60*60)
                print(f"Retention for {{topic_name}}: {{days:.2f}} days ({{hours:.2f}} hours)")
            else:
                print(f"Retention not explicitly set for {{topic_name}}")
    """

    resp = openai.chat.completions.create(
        model=OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = resp.choices[0].message.content.strip()
    print("AI RAW RESPONSE:", raw)  # Debug log

    # Handle ```json ... ``` wrappers
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        return json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail=f"AI response was not valid JSON: {raw}")

# ------------------------------
# Sandbox Executor for AI Code
# ------------------------------
def run_code_safely(code: str) -> str:
    buffer = io.StringIO()
    try:
        local_vars = {}
        with contextlib.redirect_stdout(buffer):
            exec(code, {"__builtins__": __builtins__}, local_vars)
        output = buffer.getvalue().strip() or str(local_vars.get("result", "<no result>"))
        return output
    except Exception as e:
        return f"Error while executing AI code: {e}"

# ------------------------------
# Main Endpoint
# ------------------------------
@app.post("/api/kafka")
def kafka_agent(req: PromptRequest):
    global last_topic
    try:
        ai_output = ask_openai_for_code(req.prompt, remembered_topic=last_topic)
        code = ai_output.get("code")
        explanation = ai_output.get("explanation", "")
        if not code:
            raise HTTPException(status_code=500, detail="AI did not return code")

        # Run the generated code
        result = run_code_safely(code)

        # Extract topic if present
        extracted = extract_topic_from_code(code)
        if extracted:
            last_topic = extracted
            print(f"Remembering topic: {last_topic}")

        return {
            "prompt": req.prompt,
            "topic_in_use": last_topic,
            "explanation": explanation,
            "executed_code": code,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
