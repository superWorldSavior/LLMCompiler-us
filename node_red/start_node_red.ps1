# Se positionner dans le dossier Node-RED
Set-Location $PSScriptRoot

# Installer les dépendances si nécessaire
if (-not (Test-Path "node_modules")) {
    npm install
}

# Démarrer Node-RED avec le dossier courant comme userDir
node-red -u .
