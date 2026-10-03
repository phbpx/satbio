"""Estado do código para os manifestos de execução.

Um manifesto só permite reconstruir a execução se apontar para código
commitado. Por padrão os scripts recusam rodar com mudanças não commitadas;
com `permitir_sujo`, o diff é salvo ao lado do manifesto.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

# Caminhos cujo estado afeta o resultado de uma execução.
CAMINHOS_RASTREADOS = ["src", "scripts", "tests", "pyproject.toml", "uv.lock"]


def _git(raiz: Path, *args: str) -> str:
    resultado = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True, check=True)
    return resultado.stdout


def estado_do_codigo(raiz: Path, saida: Path, permitir_sujo: bool = False) -> dict:
    """Devolve {commit, sujo, arquivos_alterados, diff_sha256} para o manifesto.

    Levanta RuntimeError se houver mudanças não commitadas e `permitir_sujo`
    for falso. Com `permitir_sujo`, grava `codigo.diff` em `saida`.
    """
    commit = _git(raiz, "rev-parse", "HEAD").strip()
    status = _git(raiz, "status", "--porcelain", "--", *CAMINHOS_RASTREADOS)
    alterados = [linha[3:] for linha in status.splitlines() if linha.strip()]
    estado = {"commit": commit, "sujo": bool(alterados), "arquivos_alterados": alterados, "diff_sha256": None}
    if not alterados:
        # um diff de execução suja anterior não descreve esta execução
        (saida / "codigo.diff").unlink(missing_ok=True)
        return estado
    if not permitir_sujo:
        raise RuntimeError(
            "código com mudanças não commitadas em " + ", ".join(alterados)
            + "; faça o commit antes ou rode com --permitir-sujo (o diff será salvo junto do manifesto)")
    diff = _git(raiz, "diff", "HEAD", "--", *CAMINHOS_RASTREADOS)
    # Arquivos não rastreados não entram no `git diff`; são comparados com
    # /dev/null sem mexer no índice do repositório.
    novos = _git(raiz, "ls-files", "--others", "--exclude-standard", "--", *CAMINHOS_RASTREADOS).split()
    for arquivo in novos:
        r = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", arquivo], cwd=raiz,
                           capture_output=True, text=True)
        diff += r.stdout  # código de saída 1 significa "há diferenças"
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "codigo.diff").write_text(diff)
    estado["diff_sha256"] = hashlib.sha256(diff.encode()).hexdigest()
    return estado
