### Cursor Prompt – **“Use real Freedcamp permalink”**

````
You are editing a FastAPI + Agent SDK project.

Goal → stop hard-coding the Freedcamp task URL and use the permalink returned
by the API.

----------------------------------------------------------------
1. ✏️  Open   src/tools/freedcamp_api.py
2. Locate the block that handles a successful response
   (inside create_freedcamp_task, right after res.json()).
   Replace it with the diff below.

```diff
@@
-        task_id  = task_data.get("id")
-        task_url = f"https://freedcamp.com/view/{PROJECT_ID}/tasks/{task_id}"
-
-        if task_id:
-            logger.info(f"Successfully created Freedcamp task {task_id}. URL: {task_url}")
-            return {
-                "success": True,
-                "task_id": task_id,
-                "task_url": task_url,
-                "response": task_data,
-            }
+        task_id  = task_data.get("id")
+        task_url = task_data.get("url")  # API returns full or relative link
+
+        # prepend host if link is relative
+        if task_url and task_url.startswith("/"):
+            task_url = f"https://freedcamp.com{task_url}"
+
+        if task_id and task_url:
+            logger.info(f"Successfully created Freedcamp task {task_id}. URL: {task_url}")
+            return {
+                "success": True,
+                "task_id": task_id,
+                "task_url": task_url,
+                "response": task_data,
+            }
````

3. ❌ **Do not** change any other files.
4. 💾 Save, run `python -m tools.freedcamp_api` or the existing smoke
   test to confirm the returned `task_url` opens the task directly.

---
