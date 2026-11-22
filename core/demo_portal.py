"""Local-only disposable task portal for exercising QA Studio; no external services."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HTML = r'''<!doctype html><html><head><meta charset="utf-8"><title>QA Task Portal</title>
<style>body{font:18px system-ui;background:#edf2f8;color:#17283f;margin:60px auto;max-width:850px}main{background:white;padding:32px;border-radius:16px}label{display:block;margin:18px 0}input,select,button{font:inherit;padding:10px;margin:8px;border:1px solid #8b9bb0;border-radius:6px}button{background:#124e88;color:white}#notice{color:#155d36}nav{padding:12px;background:#dae6f5}</style></head>
<body><h1>QA Task Portal</h1><main id="app"></main><script>
const app=document.querySelector('#app');
const state={tasks:[]};
function login(){app.innerHTML=`<h2>Sign in</h2><form id="login"><label>Email<input type="email" id="email"></label><label>Password<input type="password" id="password"></label><button type="submit">Sign in</button><p role="alert" id="error"></p></form>`;
document.querySelector('form').onsubmit=async(e)=>{e.preventDefault();let r=await fetch('/api/login',{method:'POST',body:JSON.stringify({email:email.value,password:password.value})});if(r.ok){sessionStorage.setItem('qa-session','yes');dashboard()}else{document.querySelector('#error').textContent='Invalid credentials'}}}
function dashboard(){history.replaceState({},'', '/dashboard');app.innerHTML=`<h2>Dashboard</h2><nav><button id="tasks">Tasks</button><button id="logout">Log out</button></nav><p>Welcome to your task workspace.</p>`;tasks.onclick=list;logout.onclick=()=>{sessionStorage.clear();login()}}
function list(){history.replaceState({},'', '/tasks');app.innerHTML=`<h2>Tasks</h2><button id="new-task">New task</button><label>Search<input type="search" id="search"></label><div id="results"></div><button id="broken">Broken API</button>`;document.querySelector('#new-task').onclick=form;document.querySelector('#broken').onclick=()=>fetch('/api/broken');search.onkeydown=async(e)=>{if(e.key==='Enter'){let r=await fetch('/api/search?q='+encodeURIComponent(search.value));let data=await r.json();document.querySelector('#results').textContent=data.items.join(', ')}}}
function form(){history.replaceState({},'', '/tasks/new');app.innerHTML=`<h2>Create a task</h2><form><label>Title<input id="title"></label><label>Priority<select id="priority"><option>Normal</option><option>High</option></select></label><label><input id="notify" type="checkbox">Notify team</label><button type="submit">Create task</button></form><p id="notice"></p>`;document.querySelector('form').onsubmit=async(e)=>{e.preventDefault();let r=await fetch('/api/tasks',{method:'POST',body:JSON.stringify({title:title.value,priority:priority.value,notify:notify.checked})});if(r.ok){document.querySelector('#notice').textContent='Task created';history.replaceState({},'', '/tasks/created')}}}
if(sessionStorage.getItem('qa-session'))dashboard();else login();
</script></body></html>'''


class PortalHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, body, content_type='application/json'):
        body = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/search':
            return self.reply(200, {'items': ['Office QA task']})
        if path == '/api/broken':
            return self.reply(503, {'error': 'Deliberate regression fixture'})
        self.reply(200, HTML, 'text/html; charset=utf-8')

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or '{}')
        if self.path == '/api/login':
            ok = body.get('email') == 'qa@example.test' and body.get('password') == 'local-demo-only'
            return self.reply(200 if ok else 401, {'authenticated': ok})
        if self.path == '/api/tasks':
            valid = body.get('title') == 'Office QA task' and body.get('priority') == 'High' and body.get('notify') is True
            return self.reply(201 if valid else 422, {'id': 1, 'title': body.get('title')})
        self.reply(404, {})


def make_server(port=0):
    return ThreadingHTTPServer(('127.0.0.1', port), PortalHandler)


if __name__ == '__main__':
    server = make_server(8765)
    print('QA Task Portal: http://127.0.0.1:8765', flush=True)
    print('Demo login: qa@example.test / local-demo-only', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

DEMO_FLOW = 'Login as QA; click "Tasks"; click "New task"; fill "Title" with "Office QA task"; select "High" from "Priority"; check "Notify team"; click "Create task"; verify API "/api/tasks" status code 201; verify "Task created"'
