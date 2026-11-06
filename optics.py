"""教学用前向模型：圆孔衍射、四臂合束，以及非相干天空的通量积分。"""
import numpy as np
from scipy.special import j1

import core as nl


# 列顺序为 r1=(L,qL), r2=(L,-qL), r3=(-L,-qL), r4=(-L,qL)。
# 后两行与只读参考 code_main 中的 get_perturbed_transmission 完全一致。
COMBINER = 0.5 * np.array([
    [1, 1j, 1j, 1],
    [1, -1j, -1j, 1],
    [1, 1j, -1j, -1],
    [1, -1j, 1j, -1],
], dtype=complex)


def airy_amplitude(alpha, beta, wavelength, diameter):
    """相同、无像差圆孔在夫琅禾费近似下的共同振幅包络。轴上极限为 1。"""
    u = np.pi * diameter * np.hypot(alpha, beta) / wavelength
    safe = np.where(u == 0, 1.0, u)
    return np.where(u == 0, 1.0, 2 * j1(u) / safe)


def fields(alpha, beta, wavelength, baseline, ratio=6.0):
    alpha, beta = np.broadcast_arrays(alpha, beta)
    x, y = nl.collector_xy(baseline / 2, ratio)
    return np.stack([np.exp(2j * np.pi * (xi * alpha + yi * beta) / wavelength) for xi, yi in zip(x, y)])


def response(alpha, beta, wavelength, baseline, ratio=6.0, diameter=4.0, diffraction=True):
    """四路功率/四臂入射总功率；无衍射时各路之和为 1，有衍射时为 A。"""
    amplitude = np.tensordot(COMBINER, fields(alpha, beta, wavelength, baseline, ratio), axes=(1, 0))
    power = np.abs(amplitude) ** 2 / 4
    if diffraction:
        power *= airy_amplitude(alpha, beta, wavelength, diameter) ** 2
    return power


def two_beam_null(amplitude_ratio, phase_error_deg):
    """暗/亮输出强度比 N，与漏光/输入总强度 L 同时返回。"""
    a, phase = amplitude_ratio, np.deg2rad(phase_error_deg)
    dark = (1 + a*a - 2*a*np.cos(phase)) / 2
    bright = (1 + a*a + 2*a*np.cos(phase)) / 2
    return dark / bright, dark / (1 + a*a)


def sky_experiment(*, star_temperature=5778., star_radius=1., distance=10.,
                   planet_temperature=255., planet_radius=1., orbit_au=1., position_angle=40.,
                   exozodi=1., local_zodi=1., latitude=45., wavelength_um=10.,
                   baseline=14.5, ratio=6., diameter=4., rotation=0., half_width=400., npix=161):
    """单谱道、正面朝向的轴对称尘埃盘。地图单位 ph/s/m²/像素（Δλ=λ/20）。

    天空像素彼此非相干，先计算各方向的响应，再相加强度。
    未分辨的恒星/行星在展示网格上用一个像素标记；响应分别由细恒星盘积分、
    精确行星坐标计算，避免把未分辨恒星误当作完美轴上点源。
    """
    wl = wavelength_um * 1e-6
    dwl = wl / 20
    half = half_width * nl.MAS2RAD
    # 至少用三个像素采样最短的 λ/(q b) 条纹，避免长基线下的数值混叠。
    npix = max(npix, int(np.ceil(2*half*ratio*baseline/wl*3)) | 1)
    cfg = nl.default_config(npix=npix, instrument__D=diameter, star__temperature=star_temperature,
                            star__radius=star_radius, star__distance=distance,
                            star__ecl_lat=np.deg2rad(latitude), planet__temperature=planet_temperature,
                            planet__radius=planet_radius, planet__ang_sep=orbit_au/distance,
                            planet__ang_pa=position_angle, exozodi=exozodi)
    inst = nl.build_instrument(cfg)
    inst.update(wl=np.array([wl]), dwl=np.array([dwl]), hfov=np.array([half]),
                hfov_mas=np.array([half_width]), rad_pix=np.array([2*half/npix]),
                mas_pix=np.array([2*half_width/npix]))
    scene = nl.build_scene(cfg, inst)
    grid = (np.arange(npix) - (npix-1)/2) * 2*half/npix
    X, Y = np.meshgrid(grid, grid)
    a, b = nl.sky_to_array(X, Y, np.deg2rad(rotation))
    transfer = response(a, b, wl, baseline, ratio, diameter)
    px, py = nl.planet_sky_position(scene)
    pa, pb = nl.sky_to_array(px, py, np.deg2rad(rotation))
    planet_transfer = response(pa, pb, wl, baseline, ratio, diameter)
    sa, sb = nl.sky_to_array(scene['alpha_star'], scene['beta_star'], np.deg2rad(rotation))
    stellar_transfer = response(sa, sb, wl, baseline, ratio, diameter)
    stellar_flux = scene['star_fgamma'][0] * dwl
    planet_flux = scene['planet_fgamma'][0] * dwl
    stellar_counts = (stellar_transfer * scene['map_star'][0] * dwl).sum(axis=(1, 2))
    sky = {'恒星': np.zeros_like(X), '行星': np.zeros_like(X),
           '本地黄道光': scene['map_lz'][0] * dwl * local_zodi,
           '外黄道光': scene['map_ez'][0] * dwl}
    center = npix // 2
    sky['恒星'][center, center] = stellar_flux
    ix = int(np.argmin(abs(grid-px))); iy = int(np.argmin(abs(grid-py)))
    in_view = np.hypot(px, py) <= half
    if in_view: sky['行星'][iy, ix] = planet_flux
    output = {name: image[None, :, :] * transfer for name, image in sky.items()}
    output['恒星'][:] = 0
    output['恒星'][:, center, center] = stellar_counts
    output['行星'][:] = 0
    if in_view: output['行星'][:, iy, ix] = planet_flux * planet_transfer
    reference_flux = nl.black_body('planet', np.array([10e-6]), np.array([10e-6/20]), 255., 1., 10.)[0]
    return dict(sky=sky, output=output, transfer=transfer, grid=grid/nl.MAS2RAD,
                half_width=half_width, reference_flux=reference_flux,
                stellar_flux=stellar_flux, planet_flux=planet_flux,
                stellar_counts=stellar_counts, planet_transfer=planet_transfer,
                rho_mas=scene['rho_star']/nl.MAS2RAD,
                planet_xy=(px/nl.MAS2RAD, py/nl.MAS2RAD), in_view=in_view)
