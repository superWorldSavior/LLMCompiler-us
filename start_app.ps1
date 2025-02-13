# Démarrer Node-RED depuis son dossier dédié
Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy Bypass -File `"$PSScriptRoot\node_red\start_node_red.ps1`"" -WindowStyle Hidden

# Attendre que Node-RED soit complètement démarré
Start-Sleep -Seconds 5

# Démarrer l'application FastAPI avec poetry
poetry run uvicorn main:app --reload
