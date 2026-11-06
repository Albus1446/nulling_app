#!/usr/bin/env python
# coding: utf-8
"""
nulling_lecture.py —— 《消零干涉：从原理到行星探测》讲义配套模块

收录讲义各章推导并写出的函数，后面的章节直接导入使用。
每个函数的文档串注明它在哪一章首次出现。

单位约定
--------
角度  : rad（作图时换成 mas）
波长  : m
光谱光子通量 fgamma : ph s^-1 m^-2 m^-1（每单位波长）
计数率 : ph s^-1（已乘集光面积与谱道宽度，未乘效率）
计数   : e^-（已乘积分时间与总效率 eta）
"""

from __future__ import annotations

import copy

import numpy as np

# ---------------------------------------------------------------------------
# 常数
# ---------------------------------------------------------------------------
H_PLANCK = 6.62607e-34
K_BOLTZMANN = 1.380649e-23
C_LIGHT = 2.99792e8
M_PER_PC = 3.086e16
RADIUS_SUN = 6.957e8
RADIUS_EARTH = 6.371e6
AU_PER_RSUN = 0.00465047          # 1 R_sun 合多少 au
RAD2MAS = 180.0 / np.pi * 3600.0 * 1e3
MAS2RAD = 1.0 / RAD2MAS

DEFAULT_CONFIG = {
    "npix": 256,
    "instrument": {"D": 4.0, "wl_min_um": 4.0, "wl_max_um": 18.5, "spec_res": 20.0,
                   "quantum_eff": 0.7, "throughput": 0.05},
    "array": {"baseline": 14.5, "ratio": 6.0, "phi_n": 360, "integration_h": 10.0},
    "star": {"temperature": 5778.0, "radius": 1.0, "distance": 10.0, "ecl_lat": 0.79},
    "planet": {"temperature": 255.0, "ang_sep": 0.1, "ang_pa": 40.0, "radius": 1.0},
    "exozodi": 1.0,
}


def default_config(**overrides):
    """返回默认配置的深拷贝；用 star__distance=5.0 形式的关键字覆盖嵌套项。"""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    for key, value in overrides.items():
        parts = key.split("__")
        d = cfg
        for p in parts[:-1]:
            d = d[p]
        d[parts[-1]] = value
    return cfg


# ---------------------------------------------------------------------------
# 第 02 章：X 型阵列与合束
# ---------------------------------------------------------------------------
def collector_xy(L, q):
    """第 02 章。四个集光器在阵列系中的坐标：(L,qL), (L,-qL), (-L,-qL), (-L,qL)。"""
    x = np.array([L, L, -L, -L], dtype=float)
    y = np.array([q * L, -q * L, -q * L, q * L], dtype=float)
    return x, y


# 合束器两路暗输出的行向量（第 02 章）
U3 = 0.5 * np.array([1.0, 1j, -1j, -1.0])
U4 = 0.5 * np.array([1.0, -1j, 1j, -1.0])


def transmission(alpha, beta, wl, L, q):
    """第 02 章。逐臂相加得到两路暗输出的透射 (T3, T4)；alpha、beta 可为任意形状的数组。"""
    x, y = collector_xy(L, q)
    v = [np.exp(1j * 2.0 * np.pi * (x[k] * alpha + y[k] * beta) / wl) for k in range(4)]
    w3 = sum(U3[k] * v[k] for k in range(4))
    w4 = sum(U4[k] * v[k] for k in range(4))
    return np.abs(w3) ** 2 / 4.0, np.abs(w4) ** 2 / 4.0


def transmission_analytic(alpha, beta, wl, L, q):
    """第 02 章。理想 X 阵列透射的解析式；返回 dict: tm1, tm2（亮输出）, tm3, tm4（暗输出）, chop。"""
    a = 2 * np.pi * L * alpha / wl
    c = 2 * np.pi * q * L * beta / wl
    out = {
        "tm1": np.cos(a) ** 2 * np.cos(c - np.pi / 4) ** 2,
        "tm2": np.cos(a) ** 2 * np.cos(c + np.pi / 4) ** 2,
        "tm3": np.sin(a) ** 2 * np.cos(c - np.pi / 4) ** 2,
        "tm4": np.sin(a) ** 2 * np.cos(c + np.pi / 4) ** 2,
    }
    out["chop"] = out["tm3"] - out["tm4"]          # = sin^2(a) sin(2c)
    return out


# ---------------------------------------------------------------------------
# 第 03 章：仪器与目标场景
# ---------------------------------------------------------------------------
def wavelength_bins(wl_min_um, wl_max_um, spec_res):
    """第 03 章。恒定光谱分辨率 R 的波长网格；输入 µm，输出 (中心, 宽度, 边界)，单位 m。"""
    edge = wl_min_um
    centers, widths, edges = [], [], [edge]
    while edge < wl_max_um:
        w = edge / spec_res / (1.0 - 1.0 / spec_res / 2.0)
        if edge + w > wl_max_um:
            w = wl_max_um - edge
        centers.append(edge + w / 2.0)
        widths.append(w)
        edge += w
        edges.append(edge)
    return np.array(centers) * 1e-6, np.array(widths) * 1e-6, np.array(edges) * 1e-6


def planck_photon(wl, T):
    """第 03 章。光子数谱辐亮度 B_λ^γ，单位 ph s^-1 m^-2 m^-1 sr^-1。"""
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        f = 2.0 * C_LIGHT / wl**4 / (np.exp(H_PLANCK * C_LIGHT / (wl * K_BOLTZMANN * T)) - 1.0)
    return np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0)


def black_body(mode, wl, dwl, T, radius=None, distance=None):
    """第 03 章。谱道积分黑体光子通量。

    mode='radiance' : ph s^-1 m^-2 sr^-1
    mode='star'     : × π(R/d)^2，R 以太阳半径、d 以 pc 计 → ph s^-1 m^-2
    mode='planet'   : × π(R/d)^2，R 以地球半径计
    """
    flux = planck_photon(wl, T) * dwl
    if mode == "radiance":
        return flux
    R = radius * (RADIUS_SUN if mode == "star" else RADIUS_EARTH)
    return flux * np.pi * (R / (distance * M_PER_PC)) ** 2


def build_instrument(cfg):
    """第 03 章。仪器参数与视场网格。"""
    ins, arr = cfg["instrument"], cfg["array"]
    D, npix = float(ins["D"]), int(cfg["npix"])
    wl, dwl, edges = wavelength_bins(ins["wl_min_um"], ins["wl_max_um"], ins["spec_res"])
    hfov = wl / (2.0 * D)
    xm = np.tile(np.arange(npix), (npix, 1))
    radius_map = np.sqrt((xm - (npix - 1) / 2.0) ** 2 + (xm.T - (npix - 1) / 2.0) ** 2)
    return {
        "D": D, "b": float(arr["baseline"]), "L": float(arr["baseline"]) / 2.0, "q": float(arr["ratio"]),
        "npix": npix, "area": 4.0 * np.pi * (D / 2.0) ** 2, "eta": ins["quantum_eff"] * ins["throughput"],
        "wl": wl, "dwl": dwl, "edges": edges,
        "hfov": hfov, "hfov_mas": hfov * RAD2MAS, "rad_pix": 2.0 * hfov / npix, "mas_pix": 2.0 * hfov * RAD2MAS / npix,
        "radius_map": radius_map,
    }


def local_zodi_fgamma(wl, dwl, hfov, lat):
    """第 03 章。本地黄道光（整个视场）光谱通量密度。"""
    lon = 3.0 / 4.0 * np.pi
    b_tot = black_body("radiance", wl, dwl, 265.0) + 0.22 * black_body("radiance", wl, dwl, 5777.0) * (AU_PER_RSUN / 1.5) ** 2
    I = 4e-8 * b_tot * np.sqrt(np.pi / np.arccos(np.cos(lon) * np.cos(lat))
                               / (np.sin(lat) ** 2 + (0.6 * (wl / 11e-6) ** (-0.4) * np.cos(lat)) ** 2))
    return I * (np.pi * hfov**2) / dwl


def exozodi_map(inst, distance_pc, l_star, z):
    """第 03 章。外黄道光亮度图，形状 (n_wl, npix, npix)。"""
    npix = inst["npix"]
    ap = inst["radius_map"] <= npix / 2.0
    au_pix = inst["mas_pix"].reshape(-1, 1, 1) / 1e3 * distance_pc
    r_au = inst["radius_map"] * au_pix
    ok = (r_au >= 0.0344226 * np.sqrt(l_star)) & ap
    with np.errstate(divide="ignore", invalid="ignore"):
        T = np.where(ok, 278.3 * l_star**0.25 / np.sqrt(r_au), 0.0)
        sigma = np.where(ok, 7.11889e-8 * z * (r_au / np.sqrt(l_star)) ** (-0.34), 0.0)
    wl3, dwl3 = inst["wl"].reshape(-1, 1, 1), inst["dwl"].reshape(-1, 1, 1)
    m = black_body("radiance", wl3, dwl3, T) * sigma * inst["rad_pix"].reshape(-1, 1, 1) ** 2 / dwl3
    return m, T, sigma


def build_scene(cfg, inst):
    """第 03 章。目标场景：恒星盘、行星、本地黄道光、外黄道光。"""
    st, pl = cfg["star"], cfg["planet"]
    npix, wl, dwl = inst["npix"], inst["wl"], inst["dwl"]
    sc = {"T_star": st["temperature"], "R_star": st["radius"], "d": st["distance"], "lat": st["ecl_lat"],
          "z": cfg["exozodi"], "ang_sep": pl["ang_sep"], "ang_pa": pl["ang_pa"],
          "T_p": pl["temperature"], "R_p": pl["radius"]}
    sc["L_star"] = sc["R_star"] ** 2 * (sc["T_star"] / 5780.0) ** 4
    sc["planet_fgamma"] = black_body("planet", wl, dwl, sc["T_p"], sc["R_p"], sc["d"]) / dwl
    sc["ap"] = (inst["radius_map"] <= npix / 2.0).astype(float)
    sc["lz_fgamma"] = local_zodi_fgamma(wl, dwl, inst["hfov"], sc["lat"])
    sc["map_lz"] = sc["lz_fgamma"].reshape(-1, 1, 1) * sc["ap"] / sc["ap"].sum()
    # 恒星：n×n 网格上的均匀圆盘，网格跨度 ±R★
    n = 50
    sc["rho_star"] = AU_PER_RSUN * sc["R_star"] / sc["d"] / 3600.0 / 180.0 * np.pi   # 角半径 rad
    sc["star_fgamma"] = black_body("star", wl, dwl, sc["T_star"], sc["R_star"], sc["d"]) / dwl
    xm = np.tile(np.arange(n), (n, 1))
    disk = (((xm - (n - 1) / 2.0) ** 2 + (xm.T - (n - 1) / 2.0) ** 2) < (n / 2.0) ** 2).astype(float)
    sc["map_star"] = sc["star_fgamma"].reshape(-1, 1, 1) * disk / disk.sum()
    g = np.linspace(-sc["rho_star"], sc["rho_star"], n)
    sc["alpha_star"], sc["beta_star"] = np.meshgrid(g, g)
    sc["map_ez"], sc["T_ez"], sc["sigma_ez"] = exozodi_map(inst, sc["d"], sc["L_star"], sc["z"])
    sc["ez_fgamma"] = sc["map_ez"].sum(axis=(-2, -1))
    return sc


def planet_sky_position(scene):
    """第 03 章。行星天空坐标 (x, y)，rad；x 沿 RA，y 沿 Dec，方位角从 +x 向 +y 量。"""
    rho = scene["ang_sep"] / 3600.0 / 180.0 * np.pi
    pa = np.deg2rad(scene["ang_pa"])
    return rho * np.cos(pa), rho * np.sin(pa)


# ---------------------------------------------------------------------------
# 第 04 章：阵列旋转
# ---------------------------------------------------------------------------
def rotation_sampling(cfg, inst):
    """第 04 章。一圈 phi_n 步的旋转角、总积分时间，以及每步集光器的天空坐标 (phi_n, 4, 2)。"""
    phi_n = int(cfg["array"]["phi_n"])
    phi = np.linspace(0.0, 2.0 * np.pi, phi_n, endpoint=False)
    x, y = collector_xy(inst["L"], inst["q"])
    c, s = np.cos(phi)[:, None], np.sin(phi)[:, None]
    pos = np.stack([c * x - s * y, s * x + c * y], axis=-1)
    return {"phi_n": phi_n, "phi": phi, "t_int": float(cfg["array"]["integration_h"]) * 3600.0,
            "collector_sky": pos}


def sky_to_array(x, y, phi):
    """第 04 章。阵列逆时针转 phi 后，天空坐标 (x, y) 在阵列系中的坐标 R(-phi)(x, y)。"""
    c, s = np.cos(phi), np.sin(phi)
    return c * x + s * y, -s * x + c * y


def planet_track(scene, phi):
    """第 04 章。行星在阵列系中的轨迹（方位角 PA − phi）。"""
    xs, ys = planet_sky_position(scene)
    return sky_to_array(xs, ys, phi)


# ---------------------------------------------------------------------------
# 第 05 章：光子预算与 SNR
# ---------------------------------------------------------------------------
def fov_transmission_maps(inst):
    """第 05 章。视场内逐谱道透射图 (T3, T4)，形状 (n_wl, npix, npix)。"""
    n = inst["npix"]
    t3 = np.zeros((len(inst["wl"]), n, n)); t4 = np.zeros_like(t3)
    for w, wl in enumerate(inst["wl"]):
        g = np.linspace(-inst["hfov"][w], inst["hfov"][w], n)
        a, b = np.meshgrid(g, g)
        t3[w], t4[w] = transmission(a, b, wl, inst["L"], inst["q"])
    return t3, t4


def star_transmission_maps(inst, scene):
    """第 05 章。恒星盘网格上逐谱道透射 (T3, T4)。"""
    out3, out4 = [], []
    for wl in inst["wl"]:
        t3, t4 = transmission(scene["alpha_star"], scene["beta_star"], wl, inst["L"], inst["q"])
        out3.append(t3); out4.append(t4)
    return np.array(out3), np.array(out4)


def source_rates(map_src, t_map, inst):
    """第 05 章。亮度图 × 透射图 → 对视场求和 → 计数率 ph/s。"""
    return (map_src * t_map).sum(axis=(-2, -1)) * inst["area"] * inst["dwl"]


def photon_budget(inst, scene, samp):
    """第 05 章。两路暗输出中各光源的计数率、行星调制效率与光子噪声极限 SNR。"""
    t3m, t4m = fov_transmission_maps(inst)
    ts3, ts4 = star_transmission_maps(inst, scene)
    r = {
        "lz3": source_rates(scene["map_lz"], t3m, inst), "lz4": source_rates(scene["map_lz"], t4m, inst),
        "ez3": source_rates(scene["map_ez"], t3m, inst), "ez4": source_rates(scene["map_ez"], t4m, inst),
        "sl3": source_rates(scene["map_star"], ts3, inst), "sl4": source_rates(scene["map_star"], ts4, inst),
    }
    da, db = planet_track(scene, samp["phi"])
    tc = [transmission(da, db, wl, inst["L"], inst["q"]) for wl in inst["wl"]]
    r["tc3"] = np.array([t[0] for t in tc]); r["tc4"] = np.array([t[1] for t in tc])
    r["T_chop_rms"] = np.sqrt(((r["tc3"] - r["tc4"]) ** 2).mean(axis=1))
    r["T_mean"] = 0.5 * (r["tc3"] + r["tc4"]).mean(axis=1)
    k = samp["t_int"] * inst["eta"]
    A_dl = inst["area"] * inst["dwl"]
    r["S"] = scene["planet_fgamma"] * r["T_chop_rms"] * A_dl * k                    # 行星斩波信号（RMS）
    r["B"] = (r["lz3"] + r["lz4"] + r["ez3"] + r["ez4"] + r["sl3"] + r["sl4"]) * k  # 两路背景计数之和
    r["P"] = scene["planet_fgamma"] * 2 * r["T_mean"] * A_dl * k                    # 两路行星计数之和
    r["V"] = r["B"] + r["P"]
    r["snr_spec"] = r["S"] / np.sqrt(r["V"])
    r["snr_total"] = float(np.sqrt(np.sum(r["snr_spec"] ** 2)))
    r["null_depth"] = r["sl3"] / (scene["star_fgamma"] * A_dl)
    r["t3_map"], r["t4_map"] = t3m, t4m
    return r


# ---------------------------------------------------------------------------
# 第 06 章：观测数据与重建
# ---------------------------------------------------------------------------
def expected_counts(inst, scene, samp, budget):
    """第 06 章。每个谱道、每个旋转步两路暗输出的期望计数 (e3, e4) 与行星斩波期望，形状 (n_wl, phi_n)。"""
    k = samp["t_int"] / samp["phi_n"] * inst["eta"]
    A_dl = (inst["area"] * inst["dwl"])[:, None]
    pf = scene["planet_fgamma"][:, None]
    bg3 = (budget["lz3"] + budget["ez3"] + budget["sl3"])[:, None]
    bg4 = (budget["lz4"] + budget["ez4"] + budget["sl4"])[:, None]
    e3 = (pf * budget["tc3"] * A_dl + bg3) * k
    e4 = (pf * budget["tc4"] * A_dl + bg4) * k
    planet_chop = pf * (budget["tc3"] - budget["tc4"]) * A_dl * k
    return e3, e4, planet_chop


def simulate_chop(e3, e4, rng):
    """第 06 章。泊松抽样，返回斩波计数 c3 - c4，形状 (n_wl, phi_n)。"""
    return rng.poisson(e3) - rng.poisson(e4)


def correlation_templates(inst, samp, wl_idx=None, step=3, grid_mas=(-150.0, 150.0), n_grid=121):
    """第 06 章。为天空网格上每个候选位置、每个谱道、每个旋转步计算斩波模板。

    返回 dict: tm (n_phi_sel, n_wl_sel, n_grid, n_grid)，网格 x、y（rad），以及所选索引。
    模板与数据使用同一旋转约定（sky_to_array）。
    """
    wl_idx = np.arange(len(inst["wl"])) if wl_idx is None else np.asarray(wl_idx)
    phi_idx = np.arange(0, samp["phi_n"], step)
    g = np.linspace(grid_mas[0], grid_mas[1], n_grid) * MAS2RAD
    X, Y = np.meshgrid(g, g)
    tm = np.zeros((len(phi_idx), len(wl_idx), n_grid, n_grid), dtype=np.float32)
    for j, p in enumerate(samp["phi"][phi_idx]):
        a, b = sky_to_array(X, Y, p)
        for i, w in enumerate(wl_idx):
            tm[j, i] = transmission_analytic(a, b, inst["wl"][w], inst["L"], inst["q"])["chop"]
    return {"tm": tm, "wl_idx": wl_idx, "phi_idx": phi_idx, "x": g, "y": g}


def correlation_map(tpl, chop, weights=None):
    """第 06 章。相关图 C(θ) = Σ_λ Σ_φ w_λ d(λ,φ) t(λ,φ;θ)；chop 形状 (n_wl, phi_n)。"""
    d = chop[tpl["wl_idx"]][:, tpl["phi_idx"]].astype(float)
    if weights is not None:
        d = d * np.asarray(weights)[tpl["wl_idx"]][:, None]
    return np.einsum("jiyx,ij->yx", tpl["tm"], d.astype(np.float32)).astype(float)


def locate(tpl, cmap, frac=0.9):
    """第 06 章。峰值像素，以及峰值邻域（±3 像素）内 ≥ frac·峰值 的加权质心；单位 mas。"""
    X, Y = np.meshgrid(tpl["x"], tpl["y"])
    iy, ix = np.unravel_index(np.argmax(cmap), cmap.shape)
    peak = np.array([X[iy, ix], Y[iy, ix]]) * RAD2MAS
    sl = (slice(max(iy - 3, 0), iy + 4), slice(max(ix - 3, 0), ix + 4))
    sub = cmap[sl]
    reg = np.where(sub >= frac * cmap[iy, ix], sub, 0.0)
    cen = np.array([(X[sl] * reg).sum(), (Y[sl] * reg).sum()]) / reg.sum() * RAD2MAS
    return peak, cen


# ---------------------------------------------------------------------------
# 第 07 章：完整流程
# ---------------------------------------------------------------------------
def run_pipeline(cfg, seed=0, tpl=None, verbose=True):
    """第 07 章。目标场景 → 旋转 → 光子预算 → 泊松数据 → 相关图重建。"""
    inst = build_instrument(cfg)
    scene = build_scene(cfg, inst)
    samp = rotation_sampling(cfg, inst)
    bud = photon_budget(inst, scene, samp)
    e3, e4, pchop = expected_counts(inst, scene, samp, bud)
    chop = simulate_chop(e3, e4, np.random.default_rng(seed))
    if tpl is None:
        tpl = correlation_templates(inst, samp)
    w = 1.0 / (e3 + e4).mean(axis=1)
    cmap = correlation_map(tpl, chop, w)
    peak, cen = locate(tpl, cmap)
    true = np.array(planet_sky_position(scene)) * RAD2MAS
    out = {"inst": inst, "scene": scene, "samp": samp, "budget": bud, "e3": e3, "e4": e4, "chop": chop,
           "planet_chop": pchop, "tpl": tpl, "cmap": cmap, "rec_mas": cen, "true_mas": true,
           "err_mas": float(np.hypot(*(cen - true))), "snr_total": bud["snr_total"]}
    if verbose:
        print(f"谱道数 {len(inst['wl'])}；平均零深 {bud['null_depth'].mean():.3e}；"
              f"总 SNR {bud['snr_total']:.2f}；定位误差 {out['err_mas']:.2f} mas")
    return out


def set_style():
    """讲义统一的作图样式。"""
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 150, "font.size": 10, "axes.titlesize": 10,
        "axes.labelsize": 10, "legend.fontsize": 8.5, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
        "axes.spines.top": False, "axes.spines.right": False, "image.origin": "lower",
        "legend.frameon": False, "axes.unicode_minus": False,
        "font.sans-serif": ["PingFang SC", "Heiti SC", "Arial Unicode MS", "Noto Sans CJK SC", "DejaVu Sans"],
    })
