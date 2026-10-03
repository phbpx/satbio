import zipfile

import pytest

from satbio import wabad


def test_arquivos_do_registro_le_md5():
    reg = {"files": [{"key": "RBA.zip", "size": 10, "checksum": "md5:abc",
                      "links": {"self": "https://exemplo/RBA.zip"}}]}
    assert wabad.arquivos_do_registro(reg)["RBA.zip"] == {
        "url": "https://exemplo/RBA.zip", "tamanho": 10, "md5": "abc"}


def test_baixar_recusa_arquivo_sem_md5(tmp_path):
    with pytest.raises(ValueError, match="sem md5"):
        wabad.baixar({"url": "https://exemplo/x", "tamanho": 1, "md5": None}, tmp_path / "x")


def test_extrair_wavs_achata_pastas_e_ignora_outros_arquivos(tmp_path):
    zip_path = tmp_path / "RBA.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("RBA/sub/RBA_20221009_050240.wav", b"x")
        zf.writestr("RBA/leia-me.txt", b"x")
        zf.writestr("__MACOSX/RBA/._RBA_20221009_050240.wav", b"x")
    extraidos = wabad.extrair_wavs(zip_path, tmp_path / "audio")
    assert [p.name for p in extraidos] == ["RBA_20221009_050240.wav"]


def test_extrair_wavs_recusa_nomes_repetidos_em_pastas_diferentes(tmp_path):
    zip_path = tmp_path / "RBA.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("gravador1/RBA_20221009_050240.wav", b"x")
        zf.writestr("gravador2/RBA_20221009_050240.wav", b"y")
    with pytest.raises(ValueError, match="repetidos"):
        wabad.extrair_wavs(zip_path, tmp_path / "audio")


def test_extrair_wavs_nao_escreve_fora_do_destino(tmp_path):
    zip_path = tmp_path / "mal.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../../fora.wav", b"x")
    destino = tmp_path / "audio"
    extraidos = wabad.extrair_wavs(zip_path, destino)
    assert all(p.parent == destino for p in extraidos)
    assert not (tmp_path.parent / "fora.wav").exists()


def test_ler_pontos_descarta_contato_e_converte_taxa(tmp_path):
    csv = tmp_path / "Metadata.csv"
    csv.write_text(
        '"Site ID","Study area","Recording location","Biome","Latitude","Longitude",'
        '"Recorder (+ microphone)","Ominidirectional","Sampling rate","Recording date",'
        '"Minutes Annotated","Contact","Reference"\n'
        '"RBA","Area","Brazil","Forest",-6.2,-35.2,"AudioMoth","Yes","48 kHz","2022",15,"x@y.z","ref"\n'
        '"ARD","Misiones","Argentina","Forest",-25.7,-54.2,"SM4","Yes","44.1 kHz","2021",84,"a@b.c","Muñoz"\n',
        encoding="cp1252")
    # byte inválido em cp1252, como no Metadata.csv real
    csv.write_bytes(csv.read_bytes().replace(b"Misiones", b"Caraj\x98s"))
    pontos = wabad.ler_pontos(csv, ["RBA", "ARD"]).set_index("sitio")
    assert not any("contact" in c.lower() or "contato" in c.lower() for c in pontos.columns)
    assert pontos.loc["RBA", "latitude"] == pytest.approx(-6.2)
    assert pontos.loc["RBA", "taxa_declarada_hz"] == 48000
    assert pontos.loc["ARD", "taxa_declarada_hz"] == 44100
    assert pontos.loc["RBA", "grupo_validacao"] == "RBA"
