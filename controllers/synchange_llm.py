from typing import Dict, Any
import requests
import json
import urllib.request
import urllib.error

class SynchangeLLM():
    def __init__(self, 
                model: str, 
                api_url: str = "", #" https://a.com/b.php",
                sender: str = "", #"c",
                retries: int = 3,
                timeout: int = 10,
                access_id: str="", #"d",
                server_name :str = "meta_llama70b"):
        self.model = model
        self.base_url = api_url
        self.sender = sender
        self.retries = retries
        self.timeout = timeout
        self.access_id = access_id
        self.service_name = server_name
        self.base_prompt = (
            "You are an LLM agent, a prototype AI agent answering to prompts requested by users."
        )

    def chat(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "access_id":    self.access_id,
            "service_name": self.service_name,
            "query":        prompt
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
            data = json.loads(resp_text)
            if "error" in data:
                return {"response": f"Error: {data['error']}"}
            return data
        except urllib.error.URLError as e:
            return {"response": f"Error: {e}"}
        except json.JSONDecodeError:
            return {"response": "Error: Invalid JSON in response."}

    def send_request(self, prompt: str) -> str:
        full_prompt = (
            f"{self.base_prompt}\n\n"
            f"Input (from {self.sender}): {prompt}\n\n"
            "Provide only a concise final answer that directly addresses the query."
        )
        payload = {
            "access_id": self.access_id,
            "service_name": self.service_name,
            "query": full_prompt
        }
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.post(
                    self.base_url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    print(f"[Attempt {attempt}] HTTP {response.status_code}: {response.text.strip()}")
            except Exception as e:
                print(f"[Attempt {attempt}] Exception: {e}")
        return "Error: API call failed after multiple attempts"

    def test_connection(self)-> bool:
        payload = {
            "access_id":    self.access_id,
            "service_name": self.service_name,
            "query":        "Test the connection, return True or False"
        }
        response = requests.post(
            self.base_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=self.timeout
            )
        if response.status_code == 200:
            print(f"SynChangeLLM LLM backend connection is successful for model: {self.model}!\n")
            return True
        else:
            raise RuntimeError(f"SynChangeLLM connection is failed for {self.model}\n")
