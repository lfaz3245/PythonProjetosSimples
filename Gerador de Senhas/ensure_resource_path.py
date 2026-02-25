# ensure_resource_path.py
import io
import re
from pathlib import Path

TARGET = Path("GeradordeSenha.py")
FUNCTION_TEXT = """\nimport sys\nimport os\n\ndef resource_path(relative_path):\n    \"\"\"\n    Retorna o caminho absoluto para um recurso, funcionando tanto em execução\n    normal quanto quando empacotado com PyInstaller (--onefile).\n    Uso: resource_path('assets/logo.png')\n    \"\"\"\n    if getattr(sys, 'frozen', False):\n        base = sys._MEIPASS\n    else:\n        base = os.path.abspath(\".\")\n    return os.path.join(base, relative_path)\n"""

def has_resource_function(text):
    # procura por definição simples da função resource_path
    return re.search(r"def\s+resource_path\s*\(", text) is not None

def insert_after_imports(text):
    # encontra o fim do bloco de imports (primeira linha não import/blank/comment)
    lines = text.splitlines(keepends=True)
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = i + 1
            continue
        # se a linha não é import, inserimos após a última import encontrada
        break
    # reconstruir texto com a função inserida
    before = "".join(lines[:insert_at])
    after = "".join(lines[insert_at:])
    return before + FUNCTION_TEXT + after

def main():
    if not TARGET.exists():
        print(f"[ensure_resource_path] Arquivo {TARGET} não encontrado.")
        return
    text = TARGET.read_text(encoding="utf-8")
    if has_resource_function(text):
        print("[ensure_resource_path] Função resource_path já presente. Nada a fazer.")
        return
    new_text = insert_after_imports(text)
    TARGET.write_text(new_text, encoding="utf-8")
    print("[ensure_resource_path] Função resource_path inserida com sucesso em", TARGET)

if __name__ == "__main__":
    main()