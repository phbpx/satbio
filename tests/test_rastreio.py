import subprocess

import pytest

from satbio import rastreio


def _repo(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "teste@exemplo")
    git("config", "user.name", "teste")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("x = 1\n")
    git("add", ".")
    git("commit", "-qm", "inicial")
    return tmp_path


def test_codigo_limpo_registra_commit(tmp_path):
    raiz = _repo(tmp_path)
    estado = rastreio.estado_do_codigo(raiz, raiz / "saida")
    assert len(estado["commit"]) == 40 and estado["sujo"] is False and estado["diff_sha256"] is None


def test_codigo_sujo_e_recusado_por_padrao(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "src" / "mod.py").write_text("x = 2\n")
    with pytest.raises(RuntimeError, match="não commitadas"):
        rastreio.estado_do_codigo(raiz, raiz / "saida")


def test_codigo_sujo_permitido_salva_diff_inclusive_de_arquivo_novo(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "src" / "mod.py").write_text("x = 2\n")
    (raiz / "src" / "novo.py").write_text("y = 3\n")
    estado = rastreio.estado_do_codigo(raiz, raiz / "saida", permitir_sujo=True)
    diff = (raiz / "saida" / "codigo.diff").read_text()
    assert estado["sujo"] and estado["diff_sha256"]
    assert "+x = 2" in diff and "+y = 3" in diff
