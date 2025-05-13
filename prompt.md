Detaljne Cursor instrukcije – ispravan project_id i URL

Fajl: tools/freedcamp_api.py

1️⃣  Dodaj RAW‑log odgovora

Ispod:

data = response.json()

ubaci liniju:

import json
logger.debug("[FC-RAW]
" + json.dumps(data, indent=2))

2️⃣  Napravi robustan project_id

Zameni ceo blok gde setuješ project_id sa:

# --- project_id extraction ---
project_id = data.get("project_id")                       # varijanta 1 (flat)

if not project_id and isinstance(data.get("project"), dict):
    project_id = data["project"].get("id")               # varijanta 2 (object)

if not project_id and isinstance(data.get("project"), int):
    project_id = data.get("project")                      # varijanta 3 (legacy scalar)

if not project_id:
    logger.warning("project_id not found – using env value")
    project_id = FREEDCAMP_PROJECT_ID                      # ultimate fallback

3️⃣  Formiraj URL sa novim project_id

task_url = f"https://freedcamp.com/view/{project_id}/tasks/{task_id}"

I zadrži debug:

logger.debug(f"[DEBUG] project_id: {project_id}")
logger.debug(f"[DEBUG] task_url : {task_url}")

4️⃣  Sačuvaj (⌘S / CTRL+S) i pusti hot‑reload

Ako uvicorn radi sa --reload, backend se automatski restartuje. U suprotnom, ručno ugasi i ponovo pokreni.

5️⃣  Test

Pošalji Slack botu novu poruku za zadatak.

U terminalu proveri [FC-RAW] – potraži project_id i id.

Slack poruka treba da sadrži link:

https://freedcamp.com/view/<PROJECT_ID>/tasks/<TASK_ID>

Klik vodi direktno na task.