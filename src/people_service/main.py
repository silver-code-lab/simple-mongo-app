from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from bson import ObjectId
from .db import db

app = FastAPI(title="Simple App")


def to_public(doc):
    return {"id": str(doc["_id"]), "name": doc.get("name")}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items")
def list_items():
    docs = list(db.items.find({}, {"name": 1}))  
    return [to_public(d) for d in docs]

@app.post("/items")
def create_item(payload: dict):
    name = payload.get("name") if isinstance(payload, dict) else None
    if not isinstance(name, str) or not name.strip():
        raise HTTPException(400, "name is required")
    res = db.items.insert_one({"name": name})
    return JSONResponse(
        status_code=201,
        content={"ok": True, "item": {"id": str(res.inserted_id), "name": name}},
    )

@app.delete("/items/name/{name}")
def delete_items_by_name(name: str):
    res = db.items.delete_many({"name": name})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="no items with that name")
    return {"ok": True, "deleted": res.deleted_count, "name": name}

@app.delete("/items/id/{item_id}")
def delete_item_by_id(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid id format")
    res = db.items.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="item not found")
    return {"ok": True, "deleted": 1, "id": item_id}

@app.delete("/items")
def delete_all_items():
    res = db.items.delete_many({})
    return {"ok": True, "deleted": res.deleted_count}


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8" />
    <title>Simple App UI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root { color-scheme: light dark; }
      body { font-family: system-ui, Arial; margin: 2rem; }
      .card { max-width: 760px; padding: 1rem; border: 1px solid #ddd; border-radius: 12px; }
      input, button { padding: .6rem .8rem; font-size: 1rem; }
      button { cursor: pointer; }
      .row { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .5rem; }
      pre {
        background: #111;
        color: #0f0;
        padding: .75rem;
        border-radius: 8px;
        overflow:auto;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
      .muted { color:#666; font-size:.9rem; }
      .two { display:flex; gap:.5rem; flex-wrap:wrap; }
      label { font-weight:600; }
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Simple App UI</h2>

      <div class="row">
        <div class="two">
          <label for="nameInput">Name</label>
          <input id="nameInput" placeholder="e.g., hello" />
          <button onclick="doPost()">Add (POST)</button>
          <button onclick="doGet()">List (GET)</button>
          <button onclick="doDeleteByName()">Delete by name (DELETE-many)</button>
          <button onclick="doDeleteAll()">Clear all (DELETE)</button>
        </div>
      </div>

      <div class="row">
        <div class="two">
          <label for="idInput">ID</label>
          <input id="idInput" placeholder="Mongo ObjectId string" />
          <button onclick="doDeleteById()">Delete by ID (DELETE)</button>
        </div>
      </div>

      <p class="muted">Note: deleting by name uses delete_many; deleting by ID removes a single document.</p>

      <h3>Result</h3>
      <pre id="out">(click a button)</pre>
    </div>

    <script>
      async function doPost() {
        const name = document.getElementById('nameInput').value.trim();
        if (!name) return show({error:"please enter a name"});
        try {
          const res = await fetch('/items', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name})
          });
          const data = await res.json();
          show({status: res.status, data});
        } catch (e) { show({error: e.message || String(e)}); }
      }

      async function doGet() {
        try {
          const res = await fetch('/items');
          const data = await res.json();
          show({status: res.status, data});
        } catch (e) { show({error: e.message || String(e)}); }
      }

      async function doDeleteByName() {
        const name = document.getElementById('nameInput').value.trim();
        if (!name) return show({error:"please enter a name to delete"});
        try {
          const res = await fetch('/items/name/' + encodeURIComponent(name), { method: 'DELETE' });
          const text = await res.text();
          let data; try { data = JSON.parse(text) } catch { data = {raw:text} }
          show({status: res.status, data});
        } catch (e) { show({error: e.message || String(e)}); }
      }

      async function doDeleteById() {
        const id = document.getElementById('idInput').value.trim();
        if (!id) return show({error:"please enter an id to delete"});
        try {
          const res = await fetch('/items/id/' + encodeURIComponent(id), { method: 'DELETE' });
          const text = await res.text();
          let data; try { data = JSON.parse(text) } catch { data = {raw:text} }
          show({status: res.status, data});
        } catch (e) { show({error: e.message || String(e)}); }
      }

      async function doDeleteAll() {
        if (!confirm('Delete ALL items?')) return;
        try {
          const res = await fetch('/items', { method: 'DELETE' });
          const data = await res.json();
          show({status: res.status, data});
        } catch (e) { show({error: e.message || String(e)}); }
      }

      function show(obj) {
        document.getElementById('out').textContent = JSON.stringify(obj, null, 2);
      }
    </script>
  </body>
</html>
"""

