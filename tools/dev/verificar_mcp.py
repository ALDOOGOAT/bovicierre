#!/usr/bin/env python3
"""Prueba pública de Chrome DevTools MCP por stdio, sin sesiones personales."""
import json
import os
from pathlib import Path
import re
import select
import struct
import subprocess
import sys
import tempfile
import time


def read_response(process, request_id, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if select.select([process.stdout], [], [], max(0, deadline - time.monotonic()))[0]:
            line = process.stdout.readline()
            if not line:
                raise RuntimeError("El servidor MCP cerró stdout")
            response = json.loads(line)
            if response.get("id") == request_id:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response["result"]
    raise TimeoutError(f"MCP no respondió a {request_id}")


def main():
    if "--self-check" in sys.argv:
        with tempfile.TemporaryFile(mode="w+b", buffering=0) as output:
            output.write(b'{"method":"notification"}\n{"id":7,"result":{"ok":true}}\n')
            output.seek(0)
            class Process:
                stdout = output
            assert read_response(Process(), 7, 1) == {"ok": True}
            output.seek(0)
            output.truncate()
            output.write(b'{"id":8,"error":{"code":-1}}\n')
            output.seek(0)
            try:
                read_response(Process(), 8, 1)
                raise AssertionError("No se detectó error JSON-RPC")
            except RuntimeError:
                pass
        print("self-check: OK")
        return
    evidence = Path(__file__).resolve().parents[2] / "docs/ui/evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    command = ["sh", str(Path(__file__).with_name("chrome_devtools.sh")),
               "--workspace=" + str(evidence), "--viewport=1440x1000"]
    report = {"command": command, "date": time.strftime("%Y-%m-%d"), "checks": {}}
    report["node"] = subprocess.check_output([str(Path.home() / ".nvm/versions/node/v24.21.0/bin/node"), "--version"], text=True).strip()
    with tempfile.TemporaryFile(mode="w+") as errors:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=errors, bufsize=0, env=os.environ.copy(), start_new_session=True)
        request_id = 0
        def request(method, params):
            nonlocal request_id
            request_id += 1
            process.stdin.write((json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}) + "\n").encode())
            process.stdin.flush()
            return read_response(process, request_id)
        def call(name, arguments):
            result = request("tools/call", {"name": name, "arguments": arguments})
            if result.get("isError"):
                raise RuntimeError(result)
            report["checks"][f"{request_id}:{name}"] = "OK"
            return result
        try:
            report["initialize"] = request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "bovicierre-check", "version": "1"}})
            process.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
            process.stdin.flush()
            available = request("tools/list", {})["tools"]
            report["tools"] = [tool["name"] for tool in available]
            for slug, url in [("example", "https://example.com"),
                              ("cattlemax-financial", "https://help.cattlemax.com/article/525-ranch-related-financial-record-keeping"),
                              ("agriwebb-sale", "https://help.agriwebb.com/en/articles/3638340-sale-records-iam")]:
                result = call("new_page", {"url": url})
                page_id = int(re.search(r"^(\d+):.*\[selected\]", result["content"][0]["text"], re.M)[1])
                observed = call("evaluate_script", {"pageId": page_id, "function": """async () => {
                    await document.fonts.ready;
                    const heading = document.querySelector('h1,h2') || document.querySelector('a');
                    const css = heading ? getComputedStyle(heading) : null;
                    const gl = document.createElement('canvas').getContext('webgl');
                    const ext = gl && gl.getExtension('WEBGL_debug_renderer_info');
                    return {url:location.href, title:document.title, heading:heading?.textContent,
                        font:css?.fontFamily, fontSize:css?.fontSize, color:css?.color,
                        headings:[...document.querySelectorAll('h2')].map(e=>e.textContent),
                        renderer:ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : null};
                }"""})
                report[slug] = json.loads(re.search(r"```json\n(.*?)\n```", observed["content"][0]["text"], re.S)[1])
                report[slug]["console"] = call("list_console_messages", {"pageId": page_id})["content"][0]["text"]
                snapshot = call("take_snapshot", {"pageId": page_id})["content"][0]["text"]
                uid = (re.search(r'uid=(\S+) heading', snapshot) or re.search(r'uid=(\S+) link', snapshot))[1]
                call("get_css_styles", {"pageId": page_id, "uid": uid})
                for width in ([1440] if slug == "example" else [1440, 768, 390]):
                    call("emulate", {"pageId": page_id, "viewport": f"{width}x1000x1"})
                    call("take_screenshot", {"pageId": page_id, "filePath": str(evidence / f"{slug}-{width}.png")})
                    size = struct.unpack(">II", (evidence / f"{slug}-{width}.png").read_bytes()[16:24])
                    assert size == (width, 1000), size
                    report[slug].setdefault("screenshots", {})[str(width)] = list(size)
                print(f"{slug}: navegación, DOM/CSS, consola y capturas OK", flush=True)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            (evidence / "mcp-smoke.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
