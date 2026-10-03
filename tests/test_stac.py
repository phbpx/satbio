from datetime import date, datetime

import numpy as np
import pystac
import pytest
import rasterio
from rasterio.transform import from_origin

from satbio import stac


def _item(inicio: str, fim: str, tile: str = "041012", sem: tuple[str, str] | None = None) -> pystac.Item:
    item = pystac.Item(id=f"S2-16D_V2_{tile}_{inicio.replace('-', '')}", geometry=None, bbox=None,
                       datetime=datetime.fromisoformat(inicio),
                       properties={"start_datetime": f"{inicio}T00:00:00Z", "end_datetime": f"{fim}T00:00:00Z",
                                   "bdc:tiles": [tile], "eo:cloud_cover": 20.0, "updated": "2023-07-29T16:44:57Z"})
    nodata = {"NDVI": -9999.0, "EVI": -9999.0, "PROVENANCE": -1.0}
    escala = {b: 0.0001 for b in stac.BANDAS_ESPECTRAIS + stac.INDICES}
    for banda in stac.BANDAS_LIDAS:
        eo = {"name": banda, "nodata": nodata.get(banda, 0.0), "scale": escala.get(banda, 1.0)}
        if sem and sem[0] == banda:
            eo[sem[1]] = None
        item.add_asset(banda, pystac.Asset(href=f"{tile}/{banda}", extra_fields={"eo:bands": [eo]}))
    return item


def _leitor(valores: dict):
    # valor escalar vira janela 3×3 uniforme; arrays passam como estão
    def ler(href, lon, lat):
        v = valores[href.split("/")[-1]]
        return np.asarray(v) if np.ndim(v) else np.full((3, 3), v)
    return ler


POSICAO = stac.Posicao(x=5_000_000.0, y=9_000_000.0, linha=10, coluna=20, dist_borda_px=10)
VALORES_OK = {"B02": 200, "B04": 300, "B08": 3000, "B8A": 2800, "B11": 1400, "NDVI": 8000, "EVI": 5000,
              "SCL": 4, "CLEAROB": 2, "TOTALOB": 3, "PROVENANCE": 12}


def _verificador(scl_origem=4):
    """Verificador falso: SCL de origem fixo (escalar ou 3×3).

    None simula "sem cena no dia"; "sem_dado" simula cena sem dado no pixel.
    """
    def verificar(datas, posicao, lon, lat, b04_cubo):
        res = stac.ResultadoOrigem.vazio(datas.shape)
        if scl_origem is None:
            return res
        res.n_cenas[:] = 1
        if isinstance(scl_origem, str):
            return res
        res.n_com_dado[:] = 1
        res.scl = np.broadcast_to(np.asarray(scl_origem, dtype=float), datas.shape).copy()
        res.cena[:] = "S2A_MSIL2A_FALSA"
        res.dif_b04[:] = 0.0
        return res
    return verificar


def _linha(valores=VALORES_OK, item=None, posicao=POSICAO, scl_origem=4):
    return stac.linha_da_composicao(item or _item("2022-01-01", "2022-01-16"), -35.2, -6.2, posicao,
                                    leitor=_leitor(valores), verificador=_verificador(scl_origem))


def test_janela_termina_na_vespera_da_primeira_gravacao():
    inicio, corte = stac.janela(datetime(2022, 10, 9, 5, 2, 40))
    assert corte == date(2022, 10, 8)
    assert inicio == date(2021, 10, 8)


@pytest.mark.parametrize("fim,entra", [("2022-10-08", True), ("2022-10-09", False)])
def test_composicao_so_entra_se_terminar_ate_o_corte(fim, entra):
    assert stac.antes_do_corte(datetime.fromisoformat(fim), date(2022, 10, 8)) is entra


def test_filtrar_janela_descarta_composicoes_que_cruzam_inicio_ou_corte():
    itens = [_item("2021-10-01", "2021-10-16"), _item("2021-10-16", "2021-11-01"),
             _item("2022-09-30", "2022-10-08"), _item("2022-10-01", "2022-10-16")]
    mantidos = stac.filtrar_janela(itens, date(2021, 10, 8), date(2022, 10, 8))
    assert [stac.periodo(i)[0].date() for i in mantidos] == [date(2021, 10, 16), date(2022, 9, 30)]


def test_um_item_por_periodo_escolhe_tile_mais_longe_da_borda():
    a, b = _item("2022-01-01", "2022-01-16", "041012"), _item("2022-01-01", "2022-01-16", "041013")
    posicoes = {"041012": stac.Posicao(0, 0, 0, 5, 0), "041013": stac.Posicao(0, 0, 50, 50, 50)}
    escolhidos = stac.um_item_por_periodo([a, b], -35.2, -6.2,
                                          localizador=lambda href, lon, lat: posicoes[href.split("/")[0]])
    assert [(i.id, p.dist_borda_px) for i, p in escolhidos] == [(b.id, 50)]


def test_um_item_por_periodo_mantem_periodo_sem_raster_como_none():
    def fora(href, lon, lat):
        raise ValueError("fora do raster")
    escolhidos = stac.um_item_por_periodo([_item("2022-01-01", "2022-01-16")], -35.2, -6.2, localizador=fora)
    assert len(escolhidos) == 1 and escolhidos[0][1] is None
    linha = _linha(posicao=None)
    assert linha["valido"] is False and linha["motivo_invalido"] == "ponto fora do raster"


def test_data_da_observacao_cruza_a_virada_do_ano():
    assert stac.data_da_observacao(date(2022, 12, 19), 360) == date(2022, 12, 26)
    assert stac.data_da_observacao(date(2022, 12, 19), 3) == date(2023, 1, 3)


def test_linha_da_composicao_aplica_escala_calcula_ndmi_e_registra_pixel():
    linha = _linha()
    assert linha["B04"] == pytest.approx(0.03) and linha["B02"] == pytest.approx(0.02)
    assert linha["NDVI"] == pytest.approx(0.8)
    assert linha["NDMI"] == pytest.approx((0.28 - 0.14) / (0.28 + 0.14))
    assert linha["data_observacao"] == date(2022, 1, 12)
    assert (linha["pixel_linha"], linha["pixel_coluna"]) == (10, 20)
    assert linha["valido"] and linha["motivo_invalido"] is None


def test_linha_da_composicao_marca_nuvem_e_nodata_sem_descartar():
    linha = _linha({**VALORES_OK, "NDVI": -9999}, scl_origem=9)
    assert linha["valido"] is False
    assert "SCL origem 9" in linha["motivo_invalido"] and "banda sem dado" in linha["motivo_invalido"]
    assert linha["NDVI"] is None and linha["B04"] == pytest.approx(0.03)


def test_regra_principal_usa_scl_da_origem_e_guarda_variantes_do_cubo():
    # cubo diz vegetação, cena de origem diz nuvem: só as variantes do cubo aceitam
    linha = _linha({**VALORES_OK, "SCL": 4}, scl_origem=8)
    assert linha["valido"] is False and linha["SCL_origem"] == 8 and linha["SCL"] == 4
    assert linha["valido_scl_cubo_b02"] is True and linha["valido_somente_scl_cubo"] is True
    # cubo diz nuvem, cena de origem diz vegetação: a regra principal aceita
    linha = _linha({**VALORES_OK, "SCL": 9}, scl_origem=4)
    assert linha["valido"] is True and linha["valido_scl_cubo_b02"] is False
    assert linha["cena_origem"] == "S2A_MSIL2A_FALSA"


@pytest.mark.parametrize("scl_origem,motivo", [(None, "sem cena de origem no dia"),
                                               ("sem_dado", "cena de origem sem dado no pixel")])
def test_sem_cena_ou_sem_dado_na_origem_o_pixel_e_invalido(scl_origem, motivo):
    linha = _linha(scl_origem=scl_origem)
    assert linha["valido"] is False and linha["motivo_invalido"] == motivo


@pytest.mark.parametrize("provenance,motivo", [(40, "PROVENANCE fora do período"), (-1, "PROVENANCE sem dado")])
def test_linha_da_composicao_exige_provenance_dentro_do_periodo(provenance, motivo):
    linha = _linha({**VALORES_OK, "PROVENANCE": provenance})
    assert linha["valido"] is False and motivo in linha["motivo_invalido"]


@pytest.mark.parametrize("banda,campo", [("B04", "scale"), ("SCL", "nodata")])
def test_meta_banda_falha_sem_escala_ou_nodata(banda, campo):
    with pytest.raises(ValueError, match="sem"):
        _linha(item=_item("2022-01-01", "2022-01-16", sem=(banda, campo)))


def test_nevoa_invalida_o_pixel_mas_nao_a_variante_somente_scl_cubo():
    linha = _linha({**VALORES_OK, "B02": 2500, "SCL": 5}, scl_origem=5)
    assert linha["valido"] is False and "névoa (B02 0.250" in linha["motivo_invalido"]
    assert linha["valido_scl_cubo_b02"] is False and linha["valido_somente_scl_cubo"] is True


def test_centros_da_janela_seguem_linhas_e_colunas_do_cubo():
    pos = stac.Posicao(0, 0, 5, 5, 5, crs="EPSG:3857", x_centro=100.0, y_centro=200.0, res=10.0)
    centros = pos.centros_da_janela(1)
    assert centros[0][0] == (90.0, 210.0) and centros[1][1] == (100.0, 200.0) and centros[2][2] == (110.0, 190.0)


def _cena_utm(tmp_path, nome, scl, b04, x0, y0):
    """Cena fictícia em UTM 25S: SCL e B04 em grade de 10 m a partir de (x0, y0)."""
    item = pystac.Item(id=nome, geometry=None, bbox=None, datetime=datetime(2022, 1, 12), properties={})
    for banda, dados in [("SCL", scl), ("B04", b04)]:
        caminho = tmp_path / f"{nome}_{banda}.tif"
        altura, largura = np.shape(dados)
        with rasterio.open(caminho, "w", driver="GTiff", height=altura, width=largura, count=1, dtype="uint16",
                           crs="EPSG:32725", transform=from_origin(x0, y0, 10, 10)) as ds:
            ds.write(np.asarray(dados, dtype="uint16"), 1)
        item.add_asset(banda, pystac.Asset(href=str(caminho)))
    return item


def _verificador_local(cenas_por_dia, lon, lat):
    verificador = object.__new__(stac.VerificadorOrigem)  # sem conexão: cenas já no cache
    verificador._cenas = {(lon, lat, dia): cenas for dia, cenas in cenas_por_dia.items()}
    return verificador


def test_verificador_origem_le_cada_pixel_da_janela_no_lugar_certo(tmp_path):
    # Cubo e cena na mesma grade UTM de 10 m: o pixel (i, j) da janela cai no pixel (20+i-1, 20+j-1) da cena.
    x0, y0 = 300_000.0, 9_300_000.0
    pos = stac.Posicao(0, 0, 1, 1, 1, crs="EPSG:32725", x_centro=x0 + 205, y_centro=y0 - 205, res=10.0)
    scl = np.full((40, 40), 4)
    scl[19, 21], scl[21, 19], scl[21, 21] = 8, 5, 9  # nordeste, sudoeste, sudeste da janela
    scl[19, 19] = 3  # noroeste
    cena = _cena_utm(tmp_path, "S2A_MSIL2A_20220112T000000_N0301_R000_TXXX_A", scl, np.full((40, 40), 500), x0, y0)
    dia, outro_dia = date(2022, 1, 12), date(2022, 1, 13)
    datas = np.full((3, 3), dia, dtype=object)
    datas[1, 0] = outro_dia  # pixel com outra data: nenhuma cena nesse dia
    datas[0, 1] = None  # pixel sem PROVENANCE: não é consultado
    v = _verificador_local({dia: [cena], outro_dia: []}, 0.0, 0.0)
    res = v(datas, pos, 0.0, 0.0, np.full((3, 3), 0.05))
    assert (res.scl[0, 0], res.scl[0, 2], res.scl[2, 0], res.scl[2, 2], res.scl[1, 1]) == (3, 8, 5, 9, 4)
    assert res.n_cenas[1, 0] == 0 and np.isnan(res.scl[1, 0])
    assert res.n_cenas[0, 1] == 0 and res.cena[0, 1] is None
    assert res.dif_b04[1, 1] == pytest.approx(0.0)


def test_verificador_origem_trata_fora_da_cena_como_sem_dado_e_desempata_pela_reflectancia(tmp_path):
    x0, y0 = 300_000.0, 9_300_000.0
    pos = stac.Posicao(0, 0, 1, 1, 1, crs="EPSG:32725", x_centro=x0 + 205, y_centro=y0 - 205, res=10.0)
    # A: cobre só até a coluna 20 (a coluna da direita da janela fica fora); SCL 9 com B04 que não bate.
    a = _cena_utm(tmp_path, "S2A_MSIL2A_20220112T000000_N0400_R000_TAAA_A",
                  np.full((40, 21), 9), np.full((40, 21), 1000 + 900), x0, y0)
    # B: N0301 (sem offset), SCL 4 e B04 que reproduz o cubo (0,05).
    b = _cena_utm(tmp_path, "S2A_MSIL2A_20220112T000000_N0301_R000_TBBB_B",
                  np.full((40, 40), 4), np.full((40, 40), 500), x0, y0)
    dia = date(2022, 1, 12)
    res = _verificador_local({dia: [a, b]}, 0.0, 0.0)(np.full((3, 3), dia, dtype=object), pos, 0.0, 0.0,
                                                      np.full((3, 3), 0.05))
    assert res.n_com_dado[1, 1] == 2 and res.cena[1, 1].endswith("_B") and res.scl[1, 1] == 4
    assert not res.conflito[1, 1]  # discordam, mas B reproduz o cubo
    assert res.n_com_dado[1, 2] == 1  # fora da extensão de A


def test_verificador_origem_marca_conflito_quando_nenhuma_cena_reproduz_o_cubo(tmp_path):
    x0, y0 = 300_000.0, 9_300_000.0
    pos = stac.Posicao(0, 0, 1, 1, 1, crs="EPSG:32725", x_centro=x0 + 205, y_centro=y0 - 205, res=10.0)
    a = _cena_utm(tmp_path, "S2A_MSIL2A_20220112T000000_N0301_R000_TAAA_A", np.full((40, 40), 9),
                  np.full((40, 40), 900), x0, y0)
    b = _cena_utm(tmp_path, "S2A_MSIL2A_20220112T000000_N0301_R000_TBBB_B", np.full((40, 40), 4),
                  np.full((40, 40), 800), x0, y0)
    dia = date(2022, 1, 12)
    res = _verificador_local({dia: [a, b]}, 0.0, 0.0)(np.full((3, 3), dia, dtype=object), pos, 0.0, 0.0,
                                                      np.full((3, 3), 0.05))
    assert res.conflito[1, 1]


def test_offset_de_reflectancia_depende_da_baseline():
    assert stac.offset_reflectancia("S2B_MSIL2A_20220621T124259_N0400_R009_T25MBN_X") == 1000
    assert stac.offset_reflectancia("S2A_MSIL2A_20211218T124321_N0500_R009_T25MBN_X") == 1000
    assert stac.offset_reflectancia("S2A_MSIL2A_20220112T124321_N0301_R009_T25MBN_X") == 0


def test_janela_resume_so_os_pixels_validos():
    scl = np.full((3, 3), 4)
    scl[0, 0] = 9  # um pixel de nuvem na janela (SCL da cena de origem)
    ndvi = np.full((3, 3), 8000)
    ndvi[0, 0] = 1000
    ndvi[2, 2] = 9000
    linha = _linha({**VALORES_OK, "NDVI": ndvi}, scl_origem=scl)
    assert linha["viz_n_pixels"] == 9 and linha["viz_n_validos"] == 8
    assert linha["viz_NDVI_mediana"] == pytest.approx(0.8)
    assert linha["viz_NDVI_dp"] == pytest.approx(np.std([0.8] * 7 + [0.9]))
    assert linha["valido"] and linha["NDVI"] == pytest.approx(0.8)


def test_ler_pixel_e_localizar_usam_o_mesmo_pixel(tmp_path):
    caminho = tmp_path / "raster.tif"
    dados = np.arange(100, dtype="int16").reshape(10, 10)
    with rasterio.open(caminho, "w", driver="GTiff", height=10, width=10, count=1, dtype="int16",
                       crs="EPSG:4326", transform=from_origin(-36.0, -6.0, 0.1, 0.1)) as ds:
        ds.write(dados, 1)
    # lon -35.75 -> coluna 2; lat -6.35 -> linha 3
    assert stac.ler_pixel(str(caminho), -35.75, -6.35) == dados[3, 2]
    pos = stac.localizar(str(caminho), -35.75, -6.35)
    assert (pos.linha, pos.coluna, pos.dist_borda_px) == (3, 2, 2)
    assert (pos.x_centro, pos.y_centro, pos.res) == pytest.approx((-35.75, -6.35, 0.1))
    with pytest.raises(ValueError, match="fora do raster"):
        stac.ler_pixel(str(caminho), -30.0, -6.35)


def test_ler_janela_preenche_com_nodata_fora_do_raster(tmp_path):
    caminho = tmp_path / "raster.tif"
    with rasterio.open(caminho, "w", driver="GTiff", height=10, width=10, count=1, dtype="int16",
                       crs="EPSG:4326", transform=from_origin(-36.0, -6.0, 0.1, 0.1), nodata=-9999) as ds:
        ds.write(np.ones((10, 10), dtype="int16"), 1)
    janela = stac.ler_janela(str(caminho), -35.95, -6.05)  # pixel do canto (0, 0)
    assert janela.shape == (3, 3)
    assert (janela[0, :] == -9999).all() and (janela[:, 0] == -9999).all() and janela[1, 1] == 1
