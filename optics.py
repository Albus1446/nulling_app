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


def spectral_observation(**parameters):
    """沿用天空实验的 ±400 mas 接收场，计算一整圈、10 小时的多谱道计数。

    各波长独立积分以控制内存；圆对称背景的两暗路取对称平均，
    避免浮点积分误差被当作斩波信号。返回计数包含四孔面积与后端效率。
    """
    cfg = nl.default_config(instrument__D=parameters.get('diameter', 4.),
                            array__baseline=parameters.get('baseline', 14.5))
    inst = nl.build_instrument(cfg)
    samp = nl.rotation_sampling(cfg, inst)
    phi = samp['phi']
    e3, e4, signals, fluxes = [], [], [], []
    parts = {name: [] for name in ['恒星漏光', '本地黄道光', '外黄道光', '行星']}
    names = {'恒星漏光': '恒星', '本地黄道光': '本地黄道光', '外黄道光': '外黄道光'}
    for wl, dwl in zip(inst['wl'], inst['dwl']):
        args = dict(parameters, wavelength_um=wl*1e6, rotation=0., npix=81)
        exp = sky_experiment(**args)
        # 天空实验采用 Δλ=λ/20；换成边界严格相接的光谱谱道。
        factor = dwl/(wl/20) * inst['area'] * inst['eta']
        background = 0.
        for label, source in names.items():
            rate = exp['output'][source][2:].sum() * factor
            parts[label].append(rate * samp['t_int'])
            background += rate/2
        x, y = np.array(exp['planet_xy']) * nl.MAS2RAD
        a, b = nl.sky_to_array(x, y, phi)
        r = response(a, b, wl, inst['b'], inst['q'], inst['D'])
        planet = exp['planet_flux'] * factor if exp['in_view'] else 0.
        dt = samp['t_int']/len(phi)
        e3.append((background + planet*r[2])*dt)
        e4.append((background + planet*r[3])*dt)
        signals.append(planet*(r[2]-r[3])*dt)
        fluxes.append(planet*dt)
        parts['行星'].append(planet*(r[2]+r[3]).mean()*samp['t_int'])
    e3, e4, signals = map(np.array, (e3, e4, signals))
    variance = e3+e4
    snr = np.sqrt(np.sum(signals**2 / np.maximum(variance, 1e-30)))
    return dict(inst=inst, samp=samp, e3=e3, e4=e4, signal=signals,
                variance=variance, parts={k: np.array(v) for k, v in parts.items()},
                planet_counts=np.array(fluxes), snr=float(snr),
                true=np.array(exp['planet_xy']), in_view=exp['in_view'])


def search_templates(observation, half_width=150., n_grid=61):
    """多波长位置模板；保留真实谱形、衍射包络和每步积分时间。"""
    inst, samp = observation['inst'], observation['samp']
    tpl = nl.correlation_templates(inst, samp, wl_idx=np.where(inst['wl'] > 6e-6)[0],
                                   step=8, grid_mas=(-half_width, half_width), n_grid=n_grid)
    x, y = np.meshgrid(tpl['x'], tpl['y'])
    envelope = np.array([airy_amplitude(x, y, wl, inst['D'])**2 for wl in inst['wl'][tpl['wl_idx']]])
    tpl['tm'] *= (envelope * observation['planet_counts'][tpl['wl_idx'], None, None])[None]
    return tpl


def matched_filter(data, templates, variance):
    """沿最后一维计算带方差权重的分数和非负最小二乘幅度。

    score=<d,t>/sqrt(<t,t>)；每个候选模板归一化，避免高透射位置天然得高分。
    零响应模板给出零分；方差应使用两路计数之和或背景主导近似。
    """
    weight = 1/np.maximum(np.asarray(variance), 1e-30)
    norm2 = np.sum(templates**2 * weight, axis=-1)
    cross = np.sum(templates * (data*weight), axis=-1)
    good = norm2 > 1e-24
    score = np.divide(cross, np.sqrt(norm2), out=np.zeros_like(cross), where=good)
    amplitude = np.maximum(0., np.divide(cross, norm2, out=np.zeros_like(cross), where=good))
    return score, amplitude
