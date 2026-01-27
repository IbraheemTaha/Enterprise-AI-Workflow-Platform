import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL", "http://api:8000")

def chat(message, history):
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": message}]},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def check_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        return response.json()
    except:
        return {"status": "API not available"}

with gr.Blocks(title="Enterprise AI Platform") as demo:
    gr.Markdown("# 🚀 Enterprise AI Workflow Platform")
    gr.Markdown("**Supported LLM Providers:** OpenAI, Anthropic Claude, Google Gemini, Amazon Nova")
    
    with gr.Tab("Chat"):
        chatbot = gr.ChatInterface(chat)
    
    with gr.Tab("System Health"):
        health_output = gr.JSON()
        health_btn = gr.Button("Check Health")
        health_btn.click(check_health, outputs=health_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
