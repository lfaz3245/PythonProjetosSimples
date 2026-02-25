@echo off
setlocal

set SPEC=GeradordeSenha.spec
set ICON=app_icon.ico
set MAIN=GeradordeSenha.py
set ENSURE=ensure_resource_path.py

REM Ativa venv se existir
if exist venv\Scripts\activate (
  call venv\Scripts\activate
)

REM Garante que o helper exista e insere a função resource_path se necessário
if not exist %ENSURE% (
  echo [Aviso] %ENSURE% nao encontrado. Crie o arquivo ensure_resource_path.py conforme instrucoes.
) else (
  echo [Info] Verificando e inserindo resource_path em %MAIN% (se necessario)...
  python %ENSURE%
)

REM Atualiza pip e instala dependências mínimas
python -m pip install --upgrade pip
pip install --upgrade pyinstaller ttkbootstrap

REM Limpa builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GeradordeSenha.exe del /q GeradordeSenha.exe

REM Aviso sobre ícone
if not exist %ICON% (
  echo [Aviso] icone %ICON% nao encontrado. O build prosseguira sem icone.
) else (
  echo [Info] icone %ICON% encontrado e sera usado.
)

REM Executa PyInstaller com o .spec
pyinstaller %SPEC%

if %ERRORLEVEL% neq 0 (
  echo Build falhou.
  pause
  exit /b %ERRORLEVEL%
)

echo Build concluido. Executavel em dist\GeradordeSenha\GeradordeSenha.exe
pause
endlocal