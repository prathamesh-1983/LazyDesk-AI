import requests
from .config import REQUEST_TIMEOUT_SECONDS

class OllamaError(RuntimeError):
    """Friendly error raised when local Ollama requests fail."""

class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = REQUEST_TIMEOUT_SECONDS):
        self.base_url = base_url.strip().rstrip("/")
        self.model = model.strip()
        self.timeout = timeout
        if not self.base_url:
            raise OllamaError("Enter an Ollama server URL.")
        if not self.model:
            raise OllamaError("Enter a model name.")

    def list_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return [m.get("name", "") for m in response.json().get("models", []) if m.get("name")]
        except requests.RequestException as exc:
            raise OllamaError(
                "Could not reach Ollama. Start Ollama and check the server URL. "
                f"Details: {exc}"
            ) from exc
        except ValueError as exc:
            raise OllamaError("Ollama returned an unexpected response.") from exc

    def generate(self, prompt: str, system: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        if system:
            payload["system"] = system
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code == 404:
                raise OllamaError(
                    f"Model or endpoint not found. Check the model name '{self.model}' "
                    "and run `ollama pull " + self.model + "` if needed."
                )
            response.raise_for_status()
            data = response.json()
            output = data.get("response", "").strip()
            if not output:
                raise OllamaError("The model returned an empty response. Try again or choose another model.")
            return output
        except OllamaError:
            raise
        except requests.Timeout as exc:
            raise OllamaError("The model took too long to respond. Try shorter text or a smaller model.") from exc
        except requests.RequestException as exc:
            raise OllamaError(
                "Could not generate a response. Confirm Ollama is running and the model is downloaded. "
                f"Details: {exc}"
            ) from exc
        except ValueError as exc:
            raise OllamaError("Ollama returned an invalid response.") from exc
