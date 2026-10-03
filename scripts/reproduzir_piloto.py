"""Reproduz o piloto inteiro: semanas 2, 3 e 4 e as figuras, nesta ordem.

Uso:
    uv run python scripts/reproduzir_piloto.py [--permitir-sujo]

Precisa de internet (Zenodo e catálogo STAC do INPE). Na primeira execução
baixa cerca de 213 MB do WABAD; as seguintes reaproveitam o que já foi
baixado se o md5 conferir. Leva cerca de 10 minutos, quase todos na
extração da série óptica.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ETAPAS = ["semana2_wabad.py", "semana3_stac.py", "semana4_integracao.py", "figuras_piloto.py"]
ACEITAM_SUJO = {"semana2_wabad.py", "semana3_stac.py", "semana4_integracao.py"}


def main(permitir_sujo: bool) -> None:
    for etapa in ETAPAS:
        comando = [sys.executable, str(RAIZ / "scripts" / etapa)]
        if permitir_sujo and etapa in ACEITAM_SUJO:
            comando.append("--permitir-sujo")
        print(f"\n=== {etapa} ===", flush=True)
        subprocess.run(comando, cwd=RAIZ, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--permitir-sujo", action="store_true", help="repassa --permitir-sujo às etapas")
    main(parser.parse_args().permitir_sujo)
