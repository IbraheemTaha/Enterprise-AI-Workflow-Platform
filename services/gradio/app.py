import gradio as gr
import requests
import os
from pathlib import Path


def load_readme(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"*Error loading documentation: {str(e)}*"

API_URL = os.getenv("API_URL", "http://api:8000")


def load_models(provider):
    """Fetch available models for the selected provider from the API."""
    try:
        resp = requests.get(f"{API_URL}/v1/models", params={"provider": provider}, timeout=15)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            if models:
                return gr.Dropdown(choices=models, value=models[0])
        return gr.Dropdown(choices=[])
    except Exception:
        return gr.Dropdown(choices=[])


def chat_fn(message, history, provider, model):
    """Chat function for gr.ChatInterface — returns assistant response string."""
    if not model:
        return "No model selected. Expand the Settings panel, click Refresh Models, and pick a model."

    messages = list(history) + [{"role": "user", "content": message}]

    try:
        resp = requests.post(
            f"{API_URL}/v1/chat/completions",
            json={"messages": messages, "provider": provider, "model": model},
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def check_health():
    try:
        return requests.get(f"{API_URL}/health", timeout=10).json()
    except Exception as e:
        return {"status": "API not available", "error": str(e)}


with gr.Blocks(title="Enterprise AI Platform") as demo:
    gr.Markdown("# 🚀 Enterprise AI Workflow Platform")
    gr.Markdown("**Supported providers:** OpenAI, Anthropic, Google Gemini, Amazon Bedrock")

    with gr.Tab("Chat"):
        gr.Markdown("""
Chat with any supported LLM provider through the unified API gateway.

**How to start:** expand **Additional inputs** below the chat box → select a Provider → click **↻ Refresh Models** → pick a Model → type your message.
""")
        # render=False keeps these out of the main layout;
        # they will appear only inside ChatInterface's "Additional inputs" accordion.
        provider_dd = gr.Dropdown(
            choices=["openai", "anthropic", "google", "aws"],
            value="openai",
            label="Provider",
            render=False,
        )
        model_dd = gr.Dropdown(choices=[], label="Model", interactive=True, render=False)

        # Refresh button sits above the chat interface, visible at all times
        refresh_btn = gr.Button("↻ Refresh Models")

        gr.ChatInterface(
            fn=chat_fn,
            type="messages",
            additional_inputs=[provider_dd, model_dd],
        )

        # Update model list when provider changes or refresh is clicked
        provider_dd.change(load_models, inputs=[provider_dd], outputs=[model_dd])
        refresh_btn.click(load_models, inputs=[provider_dd], outputs=[model_dd])

    with gr.Tab("API Health"):
        gr.Markdown("""
Reports which LLM providers have API keys configured in the FastAPI backend.

Click **Check API Health** to query the `/health` endpoint. Each provider shows `true` if its API key is present. For full system health (all services), use the **System Health** page in Streamlit.
""")
        health_output = gr.JSON(label="Health Response")
        gr.Button("Check API Health", variant="primary").click(check_health, outputs=health_output)

    with gr.Tab("Guide"):
        _guide_path = Path(__file__).parent / "GRADIO_README.md"
        gr.Markdown(load_readme(str(_guide_path)))

    # Pre-populate the model dropdown for the default provider on page load
    demo.load(load_models, inputs=[provider_dd], outputs=[model_dd])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
