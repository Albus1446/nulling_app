"""示意图模块：所有页面用到的原理示意图都在这里画。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle, Arc
from pathlib import Path

NAVY = "#141521"
DEEP_BLUE = "#2D3C81"
ACCENT_BLUE = "#4EA4EF"
LIGHT = "#DAE2ED"
WARM = "#937562"
STAR = WARM
PLANET = ACCENT_BLUE
DARK = NAVY
BRIGHT = LIGHT
DUST = DEEP_BLUE
GREY = "#9AAAC2"
RED = DEEP_BLUE  # 保留现有调用名称；第二条曲线使用深蓝色。
SIGNED_CMAP = LinearSegmentedColormap.from_list("nulling_signed", [WARM, "#FFFFFF", DEEP_BLUE])

# 字体随项目分发，云端绘图无需系统字体或运行时下载。
FONT_PATH = Path(__file__).resolve().parent / "assets/fonts/NotoSerifCJKsc-Regular.otf"
font_manager.fontManager.addfont(str(FONT_PATH))
FONT_FAMILY = font_manager.FontProperties(fname=str(FONT_PATH)).get_name()

MAS = np.pi / 180 / 3600 / 1000


def style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": [FONT_FAMILY, "DejaVu Serif"],
        "text.color": NAVY, "axes.labelcolor": NAVY, "axes.edgecolor": NAVY,
        "xtick.color": NAVY, "ytick.color": NAVY,
        "axes.unicode_minus": False, "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "figure.dpi": 110, "image.origin": "lower",
    })


style()


def prepare_figure(fig):
    """按实际字宽换行标题，并为轴标签、图例预留空间。"""
    if fig.get_layout_engine() is None:
        fig.set_layout_engine("constrained")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        title = ax.title
        text = title.get_text()
        if not text:
            continue
        available = ax.get_window_extent(renderer).width
        if title.get_window_extent(renderer).width <= available:
            continue
        lines = []
        for paragraph in text.splitlines():
            line = ""
            for char in paragraph:
                width = renderer.get_text_width_height_descent(line + char, title.get_fontproperties(), False)[0]
                if line and width > available:
                    lines.append(line)
                    line = char
                else:
                    line += char
            lines.append(line)
        title.set_text("\n".join(lines))


def _arrow(ax, p0, p1, color="k", lw=1.5, ms=12, ls="-", z=3):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, linestyle=ls, zorder=z))


def _dish(ax, x, y, w=0.9, color="0.25", label=None):
    """画一个碟形望远镜（开口朝上）。"""
    ax.add_patch(Arc((x, y + 0.35), w, 0.7, theta1=200, theta2=340, color=color, lw=3, zorder=4))
    ax.plot([x, x], [y - 0.05, y - 0.35], color=color, lw=2.5, zorder=4)
    ax.plot([x - 0.18, x + 0.18], [y - 0.35, y - 0.35], color=color, lw=2.5, zorder=4)
    if label:
        ax.text(x, y - 0.6, label, ha="center", va="top", fontsize=9)


def _box(ax, x, y, w, h, text, fc=LIGHT, ec="0.3", fs=9, z=4):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.2, zorder=z))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=z + 1)


# ---------------------------------------------------------------------------
# 首页：为什么难
# ---------------------------------------------------------------------------
def fig_contrast_cartoon():
    """萤火虫与灯塔：亮度与角距的直观示意。"""
    fig, ax = plt.subplots(figsize=(8.4, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    for r, a in zip(np.linspace(1.4, 0.3, 12), np.linspace(0.04, 0.5, 12)):
        ax.add_patch(Circle((2.2, 2), r, color=STAR, alpha=a, lw=0))
    ax.add_patch(Circle((2.2, 2), 0.28, color=LIGHT, zorder=3))
    ax.text(2.2, 0.2, "恒星（类太阳）", ha="center", fontsize=10)
    ax.add_patch(Circle((4.4, 2.6), 0.06, color=PLANET, zorder=3))
    ax.text(4.4, 2.85, "行星", ha="center", fontsize=10, color=PLANET)
    ax.annotate("", (4.33, 2.55), (2.5, 2.1), arrowprops=dict(arrowstyle="<->", color="0.3"))
    ax.text(3.1, 2.62, "0.1 角秒", fontsize=9, color="0.3", rotation=17, ha="center")
    ax.text(5.6, 3.2, "亮度相差约 1000 万倍\n（波长 10 微米）", fontsize=11, color=NAVY)
    ax.text(5.6, 2.1, "角距只有 0.1 角秒\n像从 2 公里外分辨相隔 1 毫米的两个点", fontsize=9, color=WARM, va="top")
    ax.text(5.6, 0.75, "在灯塔旁边，寻找一只萤火虫", fontsize=9.5, color=DEEP_BLUE)
    return fig


def fig_single_telescope_blur(D=4.0, lam_um=10.0, sep_mas=100.0, contrast=1e-7):
    """单台望远镜的像：恒星的衍射光斑把行星完全盖住。"""
    from scipy.special import j1
    lam = lam_um * 1e-6
    x = np.linspace(-800, 800, 2001)
    def airy(xm):
        u = np.pi * D * (np.abs(xm) * MAS) / lam
        u = np.where(u == 0, 1e-12, u)
        return (2 * j1(u) / u) ** 2
    star = airy(x)
    planet = contrast * airy(x - sep_mas)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.semilogy(x, star, color=STAR, lw=2, label="恒星的像")
    ax.semilogy(x, planet, color=PLANET, lw=2, label=f"行星的像（恒星的 {contrast:.1e}）")
    ax.axvline(sep_mas, color=PLANET, ls=":", lw=1)
    ax.set_ylim(min(1e-10, contrast/30), 2); ax.set_xlim(x[0], x[-1])
    ax.set_xlabel("离恒星的角距离 (mas)"); ax.set_ylabel("亮度（相对恒星中心）")
    ax.set_title(f"口径 {D:g} m 的望远镜在 {lam_um:g} µm 的像：衍射光斑宽约 λ/D = {lam / D / MAS:.0f} mas")
    ax.legend(loc="lower center")
    return fig


# ---------------------------------------------------------------------------
# 第 1 页：干涉
# ---------------------------------------------------------------------------
def fig_two_waves(dphi_deg):
    """两列波相加。"""
    t = np.linspace(0, 4 * np.pi, 600)
    d = np.deg2rad(dphi_deg)
    w1, w2 = np.sin(t), np.sin(t + d)
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 4.4), sharex=True, constrained_layout=True)
    axs[0].plot(t, w1, color=PLANET, lw=2); axs[0].set_ylabel("波 1")
    axs[1].plot(t, w2, color=RED, lw=2); axs[1].set_ylabel("波 2")
    axs[2].plot(t, w1 + w2, color="k", lw=2.5); axs[2].set_ylabel("相加")
    amp = abs(2 * np.cos(d / 2))
    word = "相长干涉：变亮" if amp > 1.6 else ("相消干涉：几乎为零" if amp < 0.3 else "部分相消")
    axs[2].set_title(f"合成振幅 = {amp:.2f}（单列波为 1），亮度 ∝ 振幅² = {amp ** 2:.2f}  →  {word}", fontsize=10)
    for ax in axs:
        ax.set_ylim(-2.2, 2.2); ax.axhline(0, color="0.8", lw=0.6); ax.set_yticks([-2, 0, 2])
    axs[0].set_title(f"两列波的相位差 = {dphi_deg:.0f}°（{dphi_deg / 360:.2f} 个波长）", fontsize=10)
    axs[2].set_xticks([])
    return fig


# ---------------------------------------------------------------------------
# 第 2 页：两台望远镜消零
# ---------------------------------------------------------------------------
def fig_bracewell_setup():
    """两台望远镜 + 合束器：恒星（正对）与行星（偏一点）的光路对比。"""
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.6), constrained_layout=True)
    for ax, tilt, src, col, title in [(axs[0], 0.0, "恒星（正对视线）", STAR, "恒星：两路同时到达，翻转后相互抵消"),
                                      (axs[1], 14.0, "行星（偏一点点）", PLANET, "行星：一路多走一段，抵消不完全")]:
        ax.set_xlim(-3.2, 4.2); ax.set_ylim(-3.6, 4.3); ax.axis("off"); ax.set_aspect("equal")
        th = np.deg2rad(tilt)
        xs = [-2.0, 2.0]
        # 入射平面波波前
        for k in range(4):
            y0 = 2.0 + 0.55 * k
            xx = np.array([-3.0, 3.0])
            ax.plot(xx, y0 + np.tan(th) * xx, color=col, lw=1.2, alpha=0.8)
        for x in xs:
            _arrow(ax, (x - np.tan(th) * 1.6 * 0, 3.9), (x, 0.55), color=col, lw=1.4)
        ax.text(-3.0, 3.95, src, ha="left", fontsize=9.5, color=col)
        for x, lab in zip(xs, ["望远镜 1", "望远镜 2"]):
            _dish(ax, x, 0.0, label=None)
            ax.text(x, -0.55, lab, ha="center", va="top", fontsize=9)
        if tilt > 0:
            # 额外光程：波前到达右侧望远镜之前，左侧还要多走一段
            # 同一个波前：左边在 yL 处到达望远镜 1 的上方时，右边还在更高的 yR 处
            yR = 2.0 + np.tan(th) * xs[1]
            yL = 2.0 + np.tan(th) * xs[0]
            ax.plot([xs[0] - 0.3, xs[1] + 0.3], [yL, yL], color=RED, lw=0.8, ls=":")
            ax.plot([xs[1], xs[1]], [yL, yR], color=RED, lw=4, solid_capstyle="butt", zorder=5)
            ax.text(xs[1] + 0.15, (yL + yR) / 2, "望远镜 2\n多走的光程", ha="left", va="center", fontsize=8.5, color=RED)
        ax.annotate("", (xs[0], -1.15), (xs[1], -1.15), arrowprops=dict(arrowstyle="<->", color="0.4"))
        ax.text(0, -1.05, "基线 b", ha="center", va="bottom", fontsize=9, color="0.3")
        # 光路到合束器
        ax.plot([xs[0], xs[0], -0.45], [-0.4, -2.0, -2.0], color="0.35", lw=1.4)
        ax.plot([xs[1], xs[1], 0.45], [-0.4, -2.0, -2.0], color="0.35", lw=1.4)
        _box(ax, 1.1, -1.55, 1.25, 0.52, "半波长翻转", fc=LIGHT, fs=8)
        _box(ax, 0, -2.0, 0.9, 0.55, "合束器", fs=9)
        _arrow(ax, (-0.25, -2.3), (-1.2, -3.2), color=BRIGHT, lw=2)
        _arrow(ax, (0.25, -2.3), (1.2, -3.2), color=DARK, lw=2 if tilt > 0 else 1, ls="-" if tilt > 0 else ":")
        ax.text(-1.3, -3.45, "亮输出\n（不用）", ha="center", va="top", fontsize=8.5, color="0.4")
        ax.text(1.3, -3.45, "暗输出：有光" if tilt > 0 else "暗输出：≈ 0", ha="center", va="top", fontsize=9,
                color=DARK, weight="bold")
        ax.set_title(title, fontsize=10.5)
    return fig


def fig_fringe_1d(b=14.5, lam_um=10.0, planet_mas=100.0, span=300):
    """天空上的明暗条纹（暗输出的透射）。"""
    lam = lam_um * 1e-6
    a = np.linspace(-span, span, 1201)
    T = np.sin(np.pi * b * a * MAS / lam) ** 2
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 3.9), sharex=True, gridspec_kw={"height_ratios": [1, 2.2]},
                            constrained_layout=True)
    axs[0].imshow(np.tile(T, (20, 1)), extent=[-span, span, 0, 1], cmap="gray", vmin=0, vmax=1, aspect="auto")
    axs[0].plot(0, 0.5, "*", color=STAR, ms=16, mec="k", mew=0.5)
    axs[0].plot(planet_mas, 0.5, "o", color=PLANET, ms=8, mec="w")
    axs[0].set_yticks([]); axs[0].set_title("从天空看：暗输出像一组明暗相间的\"百叶窗\"（白 = 透光，黑 = 挡光）", fontsize=10)
    axs[1].plot(a, T, color=DARK, lw=2)
    Tp = np.sin(np.pi * b * planet_mas * MAS / lam) ** 2
    axs[1].plot(0, 0, "*", color=STAR, ms=16, mec="k", mew=0.5, label="恒星：透过 0")
    axs[1].plot(planet_mas, Tp, "o", color=PLANET, ms=9, label=f"行星：透过 {Tp:.2f}")
    axs[1].set_xlabel("离视线的角度 (mas)"); axs[1].set_ylabel("透过比例")
    axs[1].set_ylim(-0.05, 1.12); axs[1].legend(loc="upper right", fontsize=9)
    axs[1].text(-span * 0.97, 1.02, f"条纹间距 λ/b = {lam / b / MAS:.0f} mas", fontsize=9, color="0.3")
    return fig


def fig_leak_zoom(b=14.5, lam_um=10.0, d_pc=10.0):
    """零点附近放大：恒星有大小，边缘会漏光。"""
    lam = lam_um * 1e-6
    rho = 0.00465 / d_pc * 1000          # mas
    span = max(3 * rho, 1.0)
    a = np.linspace(-span, span, 600)
    T = np.sin(np.pi * b * a * MAS / lam) ** 2
    rng = np.random.default_rng(0)
    r = rho * np.sqrt(rng.uniform(0, 1, 200000)); th = rng.uniform(0, 2 * np.pi, 200000)
    N = np.mean(np.sin(np.pi * b * r * np.cos(th) * MAS / lam) ** 2)
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.4), constrained_layout=True, gridspec_kw={"width_ratios": [1, 1.6]})
    ax = axs[0]
    ax.add_patch(Circle((0, 0), rho, color=STAR, alpha=0.85))
    ax.axvline(0, color=DARK, lw=2); ax.text(0.04 * span, -0.92 * span, "零点所在的\n暗线", fontsize=8.5, color=DARK)
    ax.set_xlim(-span, span); ax.set_ylim(-span, span); ax.set_aspect("equal")
    ax.set_xlabel("mas"); ax.set_title(f"恒星圆盘（半径 {rho:.2f} mas）", fontsize=10)
    ax = axs[1]
    ax.plot(a, T, color=DARK, lw=2, label="暗输出透过比例")
    ax.axvspan(-rho, rho, color=STAR, alpha=0.25, label="恒星圆盘覆盖的范围")
    ax.axhline(N, color=RED, ls="--", lw=1.2, label=f"平均漏光（零深）≈ {N:.1e}")
    ax.set_xlim(-span, span); ax.set_ylim(0, T.max() * 1.15)
    ax.set_xlabel("离视线的角度 (mas)"); ax.legend(loc="upper center", fontsize=8.5)
    ax.set_title("零点附近放大：越靠边漏得越多", fontsize=10)
    return fig, N, rho


# ---------------------------------------------------------------------------
# 第 3 页：四台望远镜
# ---------------------------------------------------------------------------
def fig_xarray_combiner():
    """X 型阵列布局 + 两级合束框图。"""
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.6), constrained_layout=True, gridspec_kw={"width_ratios": [1, 1.7]})
    ax = axs[0]
    L, q = 1.0, 3.0
    pos = [(L, q * L), (L, -q * L), (-L, -q * L), (-L, q * L)]
    cols = [ACCENT_BLUE, DEEP_BLUE, DEEP_BLUE, ACCENT_BLUE]
    ax.plot([L, -L], [q, q], color=ACCENT_BLUE, lw=1.5); ax.plot([L, -L], [-q, -q], color=DEEP_BLUE, lw=1.5)
    for k, ((x, y), c) in enumerate(zip(pos, cols)):
        ax.add_patch(Circle((x, y), 0.32, color=c, zorder=3))
        ax.text(x, y, str(k + 1), color="w", ha="center", va="center", fontsize=10, weight="bold", zorder=4)
    ax.text(0, q + 0.55, "第 A 对", ha="center", color=ACCENT_BLUE, fontsize=9.5)
    ax.text(0, -q - 0.85, "第 B 对", ha="center", color=DEEP_BLUE, fontsize=9.5)
    ax.annotate("", (-L, -q - 0.35), (L, -q - 0.35), arrowprops=dict(arrowstyle="<->", color="0.4"))
    ax.text(0, -q - 0.3, "b", ha="center", va="bottom", fontsize=9)
    ax.annotate("", (L + 0.6, -q), (L + 0.6, q), arrowprops=dict(arrowstyle="<->", color="0.4"))
    ax.text(L + 0.75, 0, "q·b", va="center", fontsize=9)
    ax.plot(0, 0, "+", color="k", ms=12); ax.text(0.15, 0.2, "合束器", fontsize=8.5)
    ax.set_xlim(-2.2, 2.6); ax.set_ylim(-4.3, 4.0); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("四台望远镜排成长方形（俯视）", fontsize=10.5)

    ax = axs[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off"); ax.set_aspect("equal")
    for y, lab, c in [(5.3, "1", ACCENT_BLUE), (4.4, "4", ACCENT_BLUE), (2.2, "2", DEEP_BLUE), (1.3, "3", DEEP_BLUE)]:
        ax.add_patch(Circle((0.5, y), 0.28, color=c)); ax.text(0.5, y, lab, color="w", ha="center", va="center", weight="bold")
        _arrow(ax, (0.8, y), (2.0, (4.85 if y > 3 else 1.75)), color=c, lw=1.3)
    _box(ax, 2.9, 4.85, 1.7, 0.75, "A 对消零\n(1 − 4)", fc=LIGHT, fs=9)
    _box(ax, 2.9, 1.75, 1.7, 0.75, "B 对消零\n(2 − 3)", fc=LIGHT, fs=9)
    _arrow(ax, (3.75, 4.85), (5.2, 3.55), color=DARK); _arrow(ax, (3.75, 1.75), (5.2, 2.85), color=DARK)
    ax.text(4.2, 4.55, "暗光 A", fontsize=8.5); ax.text(4.2, 1.95, "暗光 B", fontsize=8.5)
    _box(ax, 6.0, 3.2, 1.6, 1.05, "交叉合束\n（错开 1/4 波长）", fc=LIGHT, fs=8.5)
    _arrow(ax, (6.8, 3.5), (8.0, 4.6), color=DARK, lw=1.8); _arrow(ax, (6.8, 2.9), (8.0, 1.8), color=DARK, lw=1.8)
    _box(ax, 8.7, 4.85, 1.3, 0.6, "输出 3", fc="white", fs=9.5)
    _box(ax, 8.7, 1.55, 1.3, 0.6, "输出 4", fc="white", fs=9.5)
    _box(ax, 8.7, 3.2, 1.5, 0.75, "3 − 4\n= 斩波信号", fc=LIGHT, fs=9)
    _arrow(ax, (8.7, 4.5), (8.7, 3.6), color=RED, lw=1.2); _arrow(ax, (8.7, 1.9), (8.7, 2.8), color=RED, lw=1.2)
    ax.text(5.0, 0.25, "两级合束：先在每对内部消掉恒星，再把两对的暗光交叉混合成两路互为镜像的输出",
            ha="center", fontsize=8.5, color="0.3")
    ax.set_title("光的去向（框图）", fontsize=10.5)
    return fig


def fig_maps(T3, T4, ext_mas, planet_xy=None, ring_r=None, titles=("输出 3", "输出 4", "斩波 = 3 − 4")):
    fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.5), constrained_layout=True)
    for ax, img, t, cm, lo in zip(axs, [T3, T4, T3 - T4], titles, ["Blues", "Blues", SIGNED_CMAP], [0, 0, -1]):
        im = ax.imshow(img, extent=[-ext_mas, ext_mas, -ext_mas, ext_mas], cmap=cm, vmin=lo, vmax=1)
        ax.plot(0, 0, "*", color=STAR, ms=13, mec="k", mew=0.5)
        if planet_xy is not None:
            ax.plot(*planet_xy, "o", ms=9, mfc="none", mec=WARM if cm == "Blues" else NAVY, mew=2)
        if ring_r is not None:
            th = np.linspace(0, 2 * np.pi, 200)
            ax.plot(ring_r * np.cos(th), ring_r * np.sin(th), color=DUST, lw=2.5, alpha=0.9)
        ax.set_title(t); ax.set_xlabel("mas")
        fig.colorbar(im, ax=ax, shrink=0.78)
    axs[0].set_ylabel("mas")
    return fig


# ---------------------------------------------------------------------------
# 第 4 页：旋转
# ---------------------------------------------------------------------------
def fig_rotation(phi_deg, chop_map, ext_mas, planet_sky, track_xy, signal, phi_grid_deg, q=6.0):
    """左：天空中旋转的阵列；中：随阵列一起转的斩波图与行星位置；右：信号曲线。"""
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.7), constrained_layout=True, gridspec_kw={"width_ratios": [1, 1.15, 1.6]})
    phi = np.deg2rad(phi_deg)
    ax = axs[0]
    L = 1.0
    P = np.array([[L, q * L], [L, -q * L], [-L, -q * L], [-L, q * L]]) / (q * L) * 0.85
    R = np.array([[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]])
    Pr = P @ R.T
    ax.add_patch(Polygon(Pr, closed=True, fill=False, ec="0.5", lw=1))
    for k, (x, y) in enumerate(Pr):
        ax.add_patch(Circle((x, y), 0.07, color=[ACCENT_BLUE, DEEP_BLUE, DEEP_BLUE, ACCENT_BLUE][k], zorder=3))
    ax.plot(0, 0, "*", color=STAR, ms=14, mec="k", mew=0.5)
    ps = np.array(planet_sky) / np.max(np.abs(planet_sky)) * 0.55
    ax.plot(*ps, "o", color=PLANET, ms=8)
    ax.text(ps[0] + 0.06, ps[1] + 0.08, "行星", color=PLANET, fontsize=9)
    ax.add_patch(Arc((0, 0), 1.9, 1.9, theta1=10, theta2=80, color="0.5", lw=1))
    _arrow(ax, (0.33, 0.9), (0.15, 0.94), color="0.5", lw=1)
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"天空中：阵列转到 {phi_deg:.0f}°", fontsize=10)
    ax = axs[1]
    ax.imshow(chop_map, extent=[-ext_mas, ext_mas, -ext_mas, ext_mas], cmap=SIGNED_CMAP, vmin=-1, vmax=1)
    ax.plot(track_xy[0], track_xy[1], color="k", lw=0.8, ls="--")
    i = int(np.argmin(np.abs(phi_grid_deg - phi_deg)))
    ax.plot(track_xy[0][i], track_xy[1][i], "o", color=PLANET, ms=9, mec="w", mew=1.5)
    ax.plot(0, 0, "*", color=STAR, ms=12, mec="k", mew=0.5)
    ax.set_title("站在阵列上看：行星沿虚线圆走", fontsize=10); ax.set_xlabel("mas")
    ax = axs[2]
    ax.plot(phi_grid_deg, signal, color="k", lw=1.5)
    ax.plot(phi_grid_deg[i], signal[i], "o", color=PLANET, ms=9)
    ax.axvline(phi_grid_deg[i], color=PLANET, lw=0.8, ls=":")
    ax.axhline(0, color="0.8", lw=0.6)
    ax.set_xlabel("阵列转过的角度 (°)"); ax.set_ylabel("行星的斩波信号")
    ax.set_xlim(0, 360); ax.set_ylim(-1.05, 1.05)
    ax.set_title("记录下来的信号：行星的\"指纹\"", fontsize=10)
    return fig


def fig_null_depth(amplitude_ratio, phase_error_deg):
    phase = np.linspace(-180, 180, 721)
    a = amplitude_ratio
    dark = (1 + a*a - 2*a*np.cos(np.deg2rad(phase))) / (2*(1+a*a))
    current = (1 + a*a - 2*a*np.cos(np.deg2rad(phase_error_deg))) / (2*(1+a*a))
    fig, ax = plt.subplots(figsize=(7.8, 3.1), constrained_layout=True)
    ax.plot(phase, dark, color=DEEP_BLUE)
    ax.plot(phase_error_deg, current, 'o', color=ACCENT_BLUE, ms=8, label='当前残余相位误差')
    ax.set_xlabel('相对理想相消条件的相位误差（度）')
    ax.set_ylabel('暗输出 / 入射总强度')
    ax.set_ylim(-.025, 1.05); ax.legend()
    ax.set_title('两束光的振幅不等时，曲线的最低点也会抬高')
    return fig


def fig_optical_response(grid_mas, envelope, fringe, total):
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5), constrained_layout=True)
    extent = [grid_mas[0], grid_mas[-1], grid_mas[0], grid_mas[-1]]
    for ax, values, title in zip(axes, [envelope, fringe, total],
                               ['单集光器衍射包络 A', '阵列干涉条纹 T3', '共同响应 R3 = A × T3']):
        im = ax.imshow(values, extent=extent, origin='lower', cmap='Blues', vmin=0, vmax=1)
        ax.set_title(title); ax.set_xlabel('天空角度（mas）')
        ax.plot(0, 0, '+', color=WARM, ms=6)
    axes[0].set_ylabel('天空角度（mas）')
    fig.colorbar(im, ax=axes, shrink=.8, label='相对入射总功率的比例')
    return fig


def fig_phasors(vectors):
    vectors = np.asarray(vectors)
    nodes = np.r_[0j, np.cumsum(vectors)]
    fig, ax = plt.subplots(figsize=(5.0, 3.4), constrained_layout=True)
    for i in range(4):
        ax.annotate('', xy=(nodes[i+1].real, nodes[i+1].imag), xytext=(nodes[i].real, nodes[i].imag),
                    arrowprops=dict(arrowstyle='->', color=DEEP_BLUE, lw=1.6))
        midpoint = (nodes[i]+nodes[i+1])/2
        normal = 1j*vectors[i]/max(abs(vectors[i]), 1e-12)
        label = midpoint + .10*normal
        ax.text(label.real, label.imag, str(i+1), fontsize=9, color=WARM, ha='center', va='center')
    ax.plot([0, nodes[-1].real], [0, nodes[-1].imag], color=ACCENT_BLUE, lw=3, label='合成复振幅')
    ax.scatter([0], [0], color=NAVY, s=14)
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('实部'); ax.set_ylabel('虚部'); ax.legend(fontsize=8)
    ax.set_title('输出 3：四个带权相量首尾相接')
    return fig


def fig_sky_contributions(experiment, component='全部光源'):
    from matplotlib.colors import LogNorm, SymLogNorm
    names = list(experiment['sky']) if component == '全部光源' else [component]
    before = sum(experiment['sky'][name] for name in names) / experiment['reference_flux']
    after = sum(experiment['output'][name] for name in names) / experiment['reference_flux']
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8), constrained_layout=True)
    h = experiment['half_width']; extent = [-h, h, -h, h]
    positive_norm = LogNorm(vmin=1e-6, vmax=1e7)
    for ax, values, title in zip(axes[:2], [before, after[2]], ['入射天空亮度（像素通量）', '暗输出 3 的天空贡献']):
        im = ax.imshow(np.maximum(values, 1e-8), extent=extent, origin='lower', cmap='Blues', norm=positive_norm)
        ax.set_title(title)
    fig.colorbar(im, ax=list(axes[:2]), shrink=.75, label='相对于固定参考类地行星的通量')
    signed = axes[2].imshow(after[2]-after[3], extent=extent, origin='lower', cmap=SIGNED_CMAP,
                            norm=SymLogNorm(linthresh=1e-5, vmin=-100, vmax=100))
    axes[2].set_title('斩波 3 − 4 的天空贡献')
    fig.colorbar(signed, ax=axes[2], shrink=.75, label='带符号的相对通量')
    for ax in axes:
        ax.set_xlabel('天空角度（mas）')
        if experiment['in_view']:
            ax.plot(*experiment['planet_xy'], 'o', mfc='none', mec=WARM, mew=1, ms=9)
    axes[0].set_ylabel('天空角度（mas）')
    return fig
