import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            topic = data.get("topic", "technology")

            # Trigger GitHub Action
            github_token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPO")
            
            if not github_token or not repo:
                raise ValueError("Missing GITHUB_TOKEN or GITHUB_REPO environment variables in Vercel")

            url = f"https://api.github.com/repos/{repo}/actions/workflows/run_pipeline.yml/dispatches"
            payload = {
                "ref": "main",
                "inputs": {
                    "topic": topic
                }
            }
            
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Vercel-Dashboard"
            }, method="POST")
            
            urllib.request.urlopen(req)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": f"Triggered pipeline for {topic}!"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
