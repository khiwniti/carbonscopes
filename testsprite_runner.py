#!/usr/bin/env python3
"""
TestSprite MCP Runner v2 — CarbonScopes Production Readiness Testing
Runs steps after code_summary.yaml is already created.
"""
import subprocess, json, time, os, sys, urllib.parse

PROJECT_PATH = "/workspace/project/carbonscopes"
API_KEY = os.environ.get("TESTSPRITE_API_KEY", "")
MCP_CMD = ["npx", "@testsprite/testsprite-mcp@latest"]
LOG_FILE = f"{PROJECT_PATH}/testsprite_tests/runner_log.txt"

_id = [0]
def nid():
    _id[0] += 1
    return _id[0]

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def call_tool(proc, name, args, timeout=600):
    mid = nid()
    msg = {"jsonrpc":"2.0","id":mid,"method":"tools/call","params":{"name":name,"arguments":args}}
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    start = time.time()
    while time.time() - start < timeout:
        try:
            line = proc.stdout.readline()
        except:
            break
        if not line:
            time.sleep(0.3)
            continue
        try:
            data = json.loads(line.strip())
            if data.get("id") == mid:
                content = data.get("result",{}).get("content",[])
                if content and content[0].get("type") == "text":
                    try:
                        return json.loads(content[0]["text"])
                    except:
                        return content[0]["text"]
                return data.get("result", data.get("error"))
        except json.JSONDecodeError:
            continue
    return {"error": f"Timeout after {timeout}s for {name}"}

def start_mcp():
    env = os.environ.copy()
    if API_KEY:
        env["API_KEY"] = API_KEY
    proc = subprocess.Popen(
        MCP_CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, bufsize=1, env=env,
    )
    time.sleep(3)
    init_msg = {"jsonrpc":"2.0","id":nid(),"method":"initialize","params":{
        "protocolVersion":"2024-11-05","capabilities":{},
        "clientInfo":{"name":"oh-cs-v2","version":"2.0"}
    }}
    proc.stdin.write(json.dumps(init_msg) + "\n")
    proc.stdin.flush()
    resp = proc.stdout.readline()
    log(f"MCP connected")
    proc.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    proc.stdin.flush()
    time.sleep(1)
    return proc

def do_bootstrap(proc):
    """Bootstrap and auto-complete portal."""
    prd_path = f"{PROJECT_PATH}/PRD.md"
    
    mid = nid()
    msg = {"jsonrpc":"2.0","id":mid,"method":"tools/call","params":{"name":"testsprite_bootstrap","arguments":{
        "projectPath":PROJECT_PATH,"type":"backend","localPort":5002,"testScope":"codebase"
    }}}
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()

    config_path = f"{PROJECT_PATH}/testsprite_tests/tmp/config.json"
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(config_path):
            break

    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        port = config.get("serverPort")
        log(f"Portal on port {port}")
        
        r = subprocess.run([
            "curl","-s","-X","POST",
            f"http://localhost:{port}/api/commit?project_path={urllib.parse.quote(PROJECT_PATH)}",
            "-F","mode=backend", "-F","scope=codebase",
            "-F","port=5002", "-F","pathname=v1",
            "-F","backendAuthType=public",
            "-F",f"file=@{prd_path}",
        ], capture_output=True, text=True, timeout=30)
        log(f"Portal: {r.stdout.strip()}")
    else:
        log("WARNING: Config not found")

    start = time.time()
    while time.time() - start < 300:
        try:
            line = proc.stdout.readline()
        except:
            break
        if not line:
            time.sleep(0.3)
            continue
        try:
            data = json.loads(line.strip())
            if data.get("id") == mid:
                content = data.get("result",{}).get("content",[])
                if content and content[0].get("type") == "text":
                    try:
                        return json.loads(content[0]["text"])
                    except:
                        return content[0]["text"]
                return data.get("result", data.get("error"))
        except json.JSONDecodeError:
            continue
    return {"error": "Bootstrap timeout"}

def main():
    log("=" * 60)
    log("  TestSprite MCP v2 — CarbonScopes Testing")
    log("=" * 60)

    # Ensure PRD exists
    prd_path = f"{PROJECT_PATH}/PRD.md"
    if not os.path.exists(prd_path):
        with open(prd_path, "w") as f:
            f.write("# CarbonScopes PRD\n\nCarbon accounting platform. Backend: FastAPI port 5002.\n")

    # Ensure code_summary.yaml exists
    summary_path = f"{PROJECT_PATH}/testsprite_tests/tmp/code_summary.yaml"
    if not os.path.exists(summary_path):
        log("ERROR: code_summary.yaml not found. Run code summary first.")
        sys.exit(1)
    log(f"Code summary found: {summary_path}")

    proc = start_mcp()

    # Step 1: Bootstrap
    log("\n[1] Bootstrap...")
    result = do_bootstrap(proc)
    log(f"Bootstrap: {json.dumps(result)[:500] if isinstance(result, dict) else str(result)[:500]}")

    # Step 2: Generate standardized PRD
    log("\n[2] Generate standardized PRD...")
    result = call_tool(proc, "testsprite_generate_standardized_prd", {
        "projectPath": PROJECT_PATH,
    }, timeout=300)
    log(f"PRD: {json.dumps(result)[:2000] if isinstance(result, dict) else str(result)[:2000]}")

    # Step 3: Generate backend test plan
    log("\n[3] Generate backend test plan...")
    result = call_tool(proc, "testsprite_generate_backend_test_plan", {
        "projectPath": PROJECT_PATH,
    }, timeout=300)
    log(f"Test plan: {json.dumps(result)[:2000] if isinstance(result, dict) else str(result)[:2000]}")

    # Step 4: Generate & execute backend tests
    log("\n[4] Generate & execute backend tests (cloud, may take minutes)...")
    result = call_tool(proc, "testsprite_generate_code_and_execute", {
        "projectName": "carbonscopes",
        "projectPath": PROJECT_PATH,
        "testIds": [],
        "additionalInstruction": "Production readiness: security (rate limiting, CSRF, auth), API endpoints, error handling, edge cases",
        "serverMode": "development",
    }, timeout=900)
    log(f"Backend results: {json.dumps(result)[:4000] if isinstance(result, dict) else str(result)[:4000]}")

    # Save results
    results_dir = f"{PROJECT_PATH}/testsprite_tests"
    with open(f"{results_dir}/full_results.json", "w") as f:
        json.dump({"backend_tests": result}, f, indent=2, default=str)
    log(f"Results saved to {results_dir}/full_results.json")

    # Check for raw report
    raw_report = f"{results_dir}/tmp/raw_report.md"
    if os.path.exists(raw_report):
        with open(raw_report) as f:
            log(f"Raw report found ({len(f.read())} bytes)")
    
    # Check for generated test files
    for root, dirs, files in os.walk(results_dir):
        for fn in files:
            fp = os.path.join(root, fn)
            log(f"  Generated: {fp}")

    proc.kill()
    log("\n" + "=" * 60)
    log("  TestSprite Testing Complete!")
    log("=" * 60)

if __name__ == "__main__":
    main()