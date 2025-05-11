# Sistema de Monitoramento Rural

Um sistema web para monitoramento e controle de sensores e atuadores em ambiente rural, utilizando Flask e MQTT para comunicação em tempo real.

## Requisitos

- Python 3.7 ou superior
- Pip (gerenciador de pacotes Python)
- Conexão com internet para download das dependências

## Configuração Inicial

Siga os passos abaixo para inicializar o sistema:

1. **Instalar dependências**

   ```bash
   pip install -r requirements.txt
   ```

2. **Criar banco de dados com dados de exemplo**

   ```bash
   python recreate_db.py --force
   ```

3. **Iniciar o servidor**

   ```bash
   python app.py
   ```

4. **Acessar o sistema**

   Abra seu navegador e acesse:
   ```
   http://localhost:5000
   ```

## Credenciais Padrão

O sistema vem configurado com os seguintes usuários:

- **Administrador**:
  - Usuário: `admin`
  - Senha: `admin123`

- **Usuários comuns**:
  - Usuário: `usuario1` / Senha: `senha123`
  - Usuário: `usuario2` / Senha: `senha123`

## Resolução de Problemas

### Porta em uso
Se receber um erro informando que a porta está em uso:
```
OSError: [Errno 98] Endereço já em uso
```
Execute o seguinte comando para encontrar e encerrar o processo:
```bash
# No Windows
netstat -ano | findstr :5000
taskkill /PID [PID_ENCONTRADO] /F

# No Linux/Mac
lsof -i :5000
kill -9 [PID_ENCONTRADO]
```

### Problemas com MQTT
Se o sistema não estiver recebendo dados em tempo real, verifique se o cliente MQTT está configurado corretamente no arquivo `.env` ou use as configurações padrão.