# Script para instalar dependências e executar a aplicação

try {
    Write-Host "Instalando dependências..." -ForegroundColor Green
    pip install -r requirements.txt

    Write-Host "Iniciando a aplicação..." -ForegroundColor Green
    $env:MQTT_ENABLED="false"  # Desabilitar MQTT por padrão
    python app.py
}
catch {
    Write-Host "Erro ao executar o script:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Pressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
