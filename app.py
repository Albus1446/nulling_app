"""单页讲义：三个基础概念 → 合光矩阵 → 目标与尘埃实验。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import app_common as C
import core as nl
import optics as O
import schematics as S


def render_interference():
    C.goal("""
    调一调两列波的相位差，找出它们相加后最暗的位置。
    """)

    st.markdown("""
    先来看两列形状相同的波。下面两幅小图分别画出它们，最下面一幅画出相加的结果。

    如果波峰正好对上波峰，合成的波会更高；如果波峰对上波谷，两者就可能抵消。我们把这叫做**干涉**。
    两列波错开了多少，叫做**相位差**。

    **试试看：** 把相位差依次调到 **0°、180°、360°**。每调一次，都看看最下面的曲线。什么时候最亮？什么时候最暗？
    """)

    c1, c2 = st.columns([1, 2.4])
    with c1:
        dphi = st.slider("两列波的相位差（度）", 0, 360, C.control_value('lesson_1_dphi', 150), 5, key='lesson_1_dphi')
        st.markdown(f"""
    相位差 **{dphi}°** 相当于错开了 **{dphi / 360:.2f} 个波长**。

    试试拖到 **0°**、**180°**、**360°**，看看最下面的合成波。
    """)
    with c2:
        C.show(S.fig_two_waves(dphi))

    st.header("错开多少，由光多走的路程决定")
    st.markdown("""
    刚才，我们直接改变了相位差。望远镜里怎样做到这件事呢？可以让其中一束光多走一段路。

    这段多走的路叫做**光程差**。多走一个波长，波峰又会对上波峰；多走半个波长，波峰就对上了波谷。

    **再试一次：** 先保持波长为 10 微米，把光程差设成 5 微米。现在只把波长改成 5 微米。还是相消干涉吗？
    下面的公式把刚才观察到的关系写了出来。
    """)
    st.latex(r"\Delta\varphi = 360^\circ \times \frac{\Delta L}{\lambda}")
    c1, c2 = st.columns(2)
    with c1:
        lam = st.slider("波长（微米）", 4.0, 18.0, C.control_value('lesson_1_lam1', 10.0), 0.5, key='lesson_1_lam1')
    with c2:
        opd = st.slider("光程差（微米）", 0.0, 20.0, C.control_value('lesson_1_opd', 5.0), 0.25, key='lesson_1_opd')
    ph = 360 * opd / lam
    st.markdown(f"光程差 {opd:g} µm ÷ 波长 {lam:g} µm = **{opd / lam:.2f} 个波长**，相位差 = **{ph:.0f}°**"
                f"（相当于 {ph % 360:.0f}°）。")

    st.success("""
    **记住这一点：** 同样强的两束光，在相位相反时可以抵消。接下来先比较恒星和行星的亮度，再看需要把恒星压暗多少。
    """)
    C.think("光程差为 5 µm，对 10 µm 的光会抵消，对 5 µm 的光呢？",
            "对 5 µm 的光，5 µm 正好是 1 个完整波长，波峰又对上了波峰，变成相长干涉。"
            "**同一个光程差，对不同波长的光效果不同**——这就是后面透射图随波长变化的原因。")
    C.think("如果两列波振幅不一样（比如一个是 1，一个是 0.9），还能完全抵消吗？",
            "不能完全抵消，最暗时还剩 1 − 0.9 = 0.1 的振幅，亮度是 0.01。所以真实仪器要求两路光的强度非常接近。")

def render_stellar_leakage():


    st.markdown("""
    上一节，我们把恒星当成了一个点。现在把它放大一些：它其实是一个小圆盘。
    太阳如果位于 10 秒差距外，看起来的半径约为 **0.47 mas**。

    圆盘中心在暗条的零点上，边缘却偏开了一点点。边缘的光没有完全抵消，暗输出就会漏进一些恒星光。
    下面用**零深**表示漏进暗输出的恒星光占原来恒星光的比例；数值越小，消零越深。

    **试试看：** 先保持距离和波长不变，把基线从 14.5 米调到 29 米。先猜一猜：漏光会增加多少？再看图中的平均漏光数值。
    """)

    c1, c2 = st.columns([1, 2.6])
    with c1:
        d = st.slider("恒星距离（秒差距 pc）", 3.0, 20.0, C.control_value('lesson_3_d', 10.0), 0.5, key='lesson_3_d')
        b = st.slider("基线 b（米）", 4.0, 40.0, C.control_value('lesson_3_b3', 14.5), 0.5, key='lesson_3_b3')
        lam = st.slider("波长 λ（微米）", 4.0, 18.0, C.control_value('lesson_3_lam3', 10.0), 0.5, key='lesson_3_lam3')
    with c2:
        fig, N, rho = S.fig_leak_zoom(b=b, lam_um=lam, d_pc=d)
        C.show(fig)

    st.markdown(f"零深 ≈ **{N:.1e}**，也就是每 10 万个恒星光子中约有 **{N * 1e5:.1f}** 个漏进暗输出。")
    st.latex(r"N \approx \frac{1}{4}\left(\frac{\pi\, b\, \rho}{\lambda}\right)^2")

    st.caption("公式中的 ρ 表示恒星的角半径，单位使用弧度。")

    st.header("漏掉的星光，和行星比谁亮？")
    lam_m = np.array([lam * 1e-6]); dl = lam_m / 20
    star = nl.black_body("star", lam_m, dl, 5778.0, 1.0, d)[0]
    planet = nl.black_body("planet", lam_m, dl, 255.0, 1.0, d)[0]
    leak = star * N
    c1, c2, c3 = st.columns(3)
    c1.metric("恒星（相对单位）", f"{star / planet:.1e}")
    c2.metric("漏进暗输出的星光", f"{leak / planet:.0f}")
    c3.metric("行星", "1")
    st.markdown(f"""
    以行星为 1：恒星本来亮 {star / planet:.1e} 倍，消零之后漏进来的星光仍有约 **{leak / planet:.0f}** 倍。
    把行星的亮度记作 1，再比较两张数值卡片。消零以后，背景是否仍比行星亮？
    接下来，我们继续用斩波、旋转和更长的观测，尝试找出行星的信号。
    """)

    st.success("""
    **把两节连起来看：** 长基线能分开更近的行星，也会带来更多恒星漏光。选择基线时，这两件事要一起考虑。
    """)
    C.think("把基线从 14.5 m 加倍到 29 m，零深变为多少倍？",
            "零深 ∝ b²，变为 4 倍。所以基线不是越长越好：长基线有利于分开近处的行星，但漏光更多。")
    C.think("为什么近处的恒星漏光更多？",
            "距离减半，恒星看起来的角半径 ρ 加倍，零深 ∝ ρ²，变为 4 倍。不过近处的行星也更亮，所以近处的目标总体仍然更容易观测。")

def render_rotation():
    C.goal("""
    慢慢转动阵列，看看行星的位置怎样变成一条随角度变化的曲线。
    """)

    st.markdown("""
    刚才我们得到了一张斩波图。可是，只在某一个方向测到一个数，还很难判断行星在哪里。
    现在让四台望远镜组成的阵列绕着视线转起来。

    从天空看，是阵列在转；如果你站在阵列上看，透射图不动，行星却沿着一圈轨迹移动。
    它经过正信号区和负信号区时，记录的数值就会上下变化。

    **试试看：** 慢慢拖动「阵列转过的角度」。同时看中间图的行星和右边曲线上的圆点：它们是怎样对应的？
    在阵列和波长给定时，这条曲线随行星位置改变。我们把它当作行星位置的一枚「指纹」。
    """)

    c1, c2 = st.columns([1, 3.2])
    with c1:
        phi = st.slider("阵列转过的角度（度）", 0, 359, C.control_value('lesson_6_phi', 60), 1, key='lesson_6_phi')
        lam = st.slider("波长 λ（微米）", 4.0, 18.0, C.control_value('lesson_6_lam5', 10.0), 0.5, key='lesson_6_lam5')
        sep = st.slider("行星离恒星的角距离（mas）", 40, 180, C.control_value('lesson_6_sep5', 100), 5, key='lesson_6_sep5')
        pa = st.slider("行星的方位角（度）", 0, 359, C.control_value('lesson_6_pa', 40), 5, key='lesson_6_pa')
    L, q = 7.25, 6.0
    ext = 250
    g = np.linspace(-ext, ext, 241) * C.MAS
    A, B = np.meshgrid(g, g)
    T3, T4 = nl.transmission(A, B, lam * 1e-6, L, q)
    phis = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    psky = np.array([sep * np.cos(np.deg2rad(pa)), sep * np.sin(np.deg2rad(pa))])
    da, db = nl.sky_to_array(psky[0] * C.MAS, psky[1] * C.MAS, phis)
    t3, t4 = nl.transmission(da, db, lam * 1e-6, L, q)
    with c2:
        C.show(S.fig_rotation(phi, T3 - T4, ext, psky, (da / C.MAS, db / C.MAS), t3 - t4, np.rad2deg(phis)))
    st.caption("左：在天空中，阵列（四个圆点）绕恒星旋转。中：站在阵列上看，斩波图不动，行星沿虚线圆反向转动。右：记录下来的斩波信号，圆点是当前时刻。")

    st.header("不同位置，不同指纹")
    st.markdown("""
    下面的两条曲线来自两个候选位置。先把方位角差和角距离差都设成 0，让它们完全重合。

    **再试一次：** 只把第二颗的方位角增加 10°，其他参数不变。两条曲线还一样吗？再把角距离改大一点，比较变化。
    第 8 节就会用这样的曲线去匹配观测数据。
    """)
    c1, c2 = st.columns([1, 3.2])
    with c1:
        dpa = st.slider("第二颗的方位角比第一颗多（度）", 0, 90, C.control_value('lesson_6_dpa', 10), 1, key='lesson_6_dpa')
        dsep = st.slider("第二颗的角距离比第一颗多（mas）", -30, 30, C.control_value('lesson_6_dsep', 0), 1, key='lesson_6_dsep')
    psky2 = np.array([(sep + dsep) * np.cos(np.deg2rad(pa + dpa)), (sep + dsep) * np.sin(np.deg2rad(pa + dpa))])
    da2, db2 = nl.sky_to_array(psky2[0] * C.MAS, psky2[1] * C.MAS, phis)
    s2 = np.subtract(*nl.transmission(da2, db2, lam * 1e-6, L, q))
    with c2:
        fig, ax = plt.subplots(figsize=(8.4, 2.8))
        ax.plot(np.rad2deg(phis), t3 - t4, color=S.PLANET, lw=1.6, label=f"位置 1：{sep} mas，{pa}°")
        ax.plot(np.rad2deg(phis), s2, color=S.RED, lw=1.2, ls="--", label=f"位置 2：{sep + dsep} mas，{pa + dpa}°")
        ax.set_xlim(0, 360); ax.set_ylim(-1.05, 1.05); ax.axhline(0, color="0.8", lw=0.6)
        ax.set_xlabel("阵列转过的角度（°）"); ax.set_ylabel("斩波信号"); ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.5)
        C.show(fig)
    match = np.corrcoef(t3 - t4, s2)[0, 1]
    st.markdown(f"两条曲线的相似度（相关系数，1 表示完全相同）：**{match:.2f}**")

    st.success("""
    **你刚刚观察到：** 在给定阵列和波长时，行星的位置会影响旋转信号的形状。比较这些形状，就能为定位提供线索。
    """)
    C.think("恒星和对称的尘埃在旋转时，斩波信号会变吗？",
            "不会。它们关于中心对称，转到哪个角度都还是对称的，斩波信号始终为零。只有行星会产生随旋转变化的信号。")
    C.think("转了半圈之后，信号和前半圈有什么关系？",
            "正好反号。转半圈后，行星走到了对称点上，而斩波图在对称点上颜色相反。看右图：180° 之后的曲线是前 180° 的\"倒影\"。")

def render_photon_noise():
    C.goal("""
    多收集一些光子，再延长观测时间，比较随机起伏和信号的变化。
    """)

    st.header("像接雨滴一样数光子")
    st.markdown("""
    接下来，我们把随机起伏也放进实验里。

    探测器接收光，可以想成在数一颗颗到达的光子。它们不会按固定节奏排队到达，就像雨滴落进杯子一样：
    即使每次接雨的时间相同，接到的滴数也会有多有少。这种起伏叫做**光子噪声**。

    下面重复了 3000 次计数。每次的平均光子数是 N，但实际计数会围着 N 分布，典型起伏约为 **√N**。

    **试试看：** 把 N 从 100 调到 10000。直方图的宽度怎样变？旁边的「相对起伏」又怎样变？
    """)
    c1, c2 = st.columns([1, 2.4])
    with c1:
        N = st.select_slider("平均每次接到的光子数 N", options=[10, 30, 100, 300, 1000, 3000, 10000], value=C.control_value('lesson_7_N', 100), key='lesson_7_N')
        st.metric("起伏大小 √N", f"{np.sqrt(N):.0f}")
        st.metric("相对起伏 √N / N", f"{1 / np.sqrt(N):.1%}")
    with c2:
        rng = np.random.default_rng(0)
        x = rng.poisson(N, 3000)
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.hist(x, bins=40, color=S.GREY)
        ax.axvline(N, color="k", lw=1.5); ax.axvspan(N - np.sqrt(N), N + np.sqrt(N), color=S.BRIGHT, alpha=0.35)
        ax.set_xlabel("一次接到的光子数"); ax.set_ylabel("次数"); ax.set_title("重复 3000 次的结果：浅蓝色带宽约 ±√N")
        C.show(fig)
    st.markdown("""
    **比较一下：** 光子越多，计数起伏的绝对大小越大；但起伏占总数的比例反而越小。测量因此变得更稳定。
    """)

    st.header("暗输出里的光子从哪里来")
    bd = C.bundle()
    bud, inst = bd["bud"], bd["inst"]
    wl = inst["wl"] * 1e6
    k = bd["samp"]["t_int"] * inst["eta"]
    parts = {"恒星漏光": (bud["sl3"] + bud["sl4"]) * k, "本地黄道光（太阳系内的尘埃）": (bud["lz3"] + bud["lz4"]) * k,
             "外黄道光（目标恒星的尘埃）": (bud["ez3"] + bud["ez4"]) * k, "行星": bud["P"]}
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    bottom = np.zeros_like(wl)
    tot = sum(parts.values())
    for (name, v), col in zip(parts.items(), [S.STAR, S.GREY, S.DUST, S.PLANET]):
        ax.bar(wl, v / tot, bottom=bottom, width=inst["dwl"] * 1e6 * 0.92, color=col, label=name)
        bottom += v / tot
    ax.set_xlabel("波长（微米）"); ax.set_ylabel("所占比例"); ax.set_ylim(0, 1)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8.5)
    ax.set_title("10 秒差距外的类太阳恒星，观测 10 小时：两路暗输出里的光子来源")
    C.show(fig)
    st.markdown("""
    这张图把暗输出里的光子按来源分开了。先看看短波长一侧，再看看长波长一侧：主要的背景来源一样吗？

    恒星漏光和尘埃贡献了很多光子，行星只占很小一部分。斩波能减去对称背景的平均值，
    却不能让每次计数的随机起伏也刚好抵消。背景越亮，留下的光子噪声通常就越大。
    """)

    st.header("信噪比：信号比噪声大多少倍")
    st.latex(r"\mathrm{SNR} \approx \frac{N_{\mathrm{planet}}}{\sqrt{N_{\mathrm{background}}}}")
    st.markdown("""
    我们用**信噪比**，简称 SNR，比较行星信号和噪声的大小。SNR 越高，信号通常越容易辨认。

    在这个只考虑光子噪声的模型里，观测时间增加一倍，信号增加一倍，噪声只增加到原来的 √2 倍。
    因此，**SNR 与观测时间的平方根成正比**。

    **试试看：** 保持波长不变，把观测时间从 10 小时调到 40 小时。右图的点更接近曲线了吗？总 SNR 是否大约变成了两倍？
    这里用 SNR = 5 作为比较观测方案的参考门槛；真实探测还需要检查统计假设和其他噪声。
    """)
    c1, c2 = st.columns([1, 2.4])
    with c1:
        hours = st.slider("观测时间（小时）", 1.0, 50.0, C.control_value('lesson_7_hours', 10.0), 1.0, key='lesson_7_hours')
        w = st.select_slider("看哪个波长的数据（微米）", options=[f"{v:.1f}" for v in wl], value=C.control_value('lesson_7_w', f"{wl[22]:.1f}"), key='lesson_7_w')
        wi = [f"{v:.1f}" for v in wl].index(w)
        snr = bud["snr_total"] * np.sqrt(hours / 10)
        st.metric("全部波长合起来的 SNR", f"{snr:.1f}", delta="已达到 5" if snr >= 5 else "还不到 5")
        st.metric("达到 SNR = 5 需要", f"{10 * (5 / bud['snr_total']) ** 2:.1f} 小时")
    with c2:
        f = hours / 10
        rng = np.random.default_rng(1)
        e3, e4 = bd["e3"][wi] * f, bd["e4"][wi] * f
        data = rng.poisson(e3) - rng.poisson(e4)
        phis = np.rad2deg(bd["samp"]["phi"])
        sig = np.sqrt((e3 + e4).mean())
        fig, ax = plt.subplots(figsize=(7.4, 3.0))
        ax.plot(phis, data, ".", ms=3, color=S.GREY, label=f"测到的斩波数据（每 1° 一个点，噪声约 ±{sig:.0f}）")
        ax.plot(phis, bd["pchop"][wi] * f, color=S.PLANET, lw=1.8, label="行星信号（没有噪声时）")
        ax.axhline(0, color="0.8", lw=0.6)
        ax.set_xlabel("阵列转过的角度（°）"); ax.set_ylabel("光子数")
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.5)
        ax.set_title(f"{wl[wi]:.1f} µm 处，观测 {hours:g} 小时的单个波长数据", pad=24)
        C.show(fig)
    st.markdown("""
    单个波长的点可能仍很乱。我们还可以把多个波长、多个旋转角度的信息合起来，利用它们共同支持的信号。下一节就来试试。
    """)

    st.success("""
    **记住这个比例：** 在光子噪声主导、其他条件相同时，SNR 提高到两倍，需要约四倍的观测时间。
    """)
    C.think("要把 SNR 从 5 提高到 10，观测时间要变成多少倍？", "SNR ∝ √时间，SNR 翻倍需要 4 倍的时间。")
    C.think("为什么短波长的数据几乎没用？",
            "短波长时行星本身很暗（它的温度只有约 255 K，主要在长波长发光），而恒星漏光又最多（零深 ∝ 1/λ²）。信号小、噪声大。")

def render_planet_search():
    C.goal("""
    把观测数据和候选信号逐个比较，试着从噪声里找出行星。
    """)

    st.markdown("""
    现在，我们已经有了行星可能留下的信号形状，也知道实际数据会带着噪声。接下来怎样找位置？

    可以借用「听歌识曲」的思路：把一段嘈杂的录音，与曲库里的候选曲目逐个比较。这里的「曲库」换成了天空中不同位置对应的信号。

    对于每一个候选位置，我们先计算旋转信号，再把它与观测数据逐点比较，得到一个分数。
    把这些分数按天空位置排成图，就是下面的**相关图**。程序把得分最高的位置作为这次的定位结果。

    **试试看：** 先保留加权，点击几次「再观测一次」。圆圈标出真实位置，叉号标出找到的位置。每次都能找对吗？
    然后把观测时间调长，再比较结果。加权的作用，是让噪声较大的波长少影响一些判断。
    """)

    if "seed8" not in st.session_state:
        st.session_state.seed8 = 0
    c1, c2 = st.columns([1, 2.6])
    with c1:
        hours = st.slider("观测时间（小时）", 1.0, 40.0, C.control_value('lesson_8_h7', 10.0), 1.0, key='lesson_8_h7')
        weighted = st.toggle("按噪声大小给各波长加权", value=C.control_value('lesson_8_weighted', True), key='lesson_8_weighted')
        if st.button("再观测一次（换一组随机噪声）", key='action_8_resample'):
            st.session_state.seed8 += 1
    bd = C.bundle()
    tpl = C.templates()
    f = hours / 10
    e3, e4 = bd["e3"] * f, bd["e4"] * f
    rng = np.random.default_rng(st.session_state.seed8)
    data = nl.simulate_chop(e3, e4, rng)
    w = 1.0 / (e3 + e4).mean(axis=1) if weighted else None
    cm = nl.correlation_map(tpl, data, w)
    _, found = nl.locate(tpl, cm)
    true = bd["true"]
    err = float(np.hypot(*(found - true)))
    snr = bd["bud"]["snr_total"] * np.sqrt(f)
    with c1:
        st.metric("SNR", f"{snr:.1f}")
        st.metric("定位误差", f"{err:.1f} mas", delta="找对了" if err < 10 else "找错了",
                  delta_color="normal" if err < 10 else "inverse")
    with c2:
        fig, ax = plt.subplots(figsize=(5.6, 4.6))
        hw = 150
        im = ax.imshow(cm / np.abs(cm).max(), extent=[-hw, hw, -hw, hw], cmap=S.SIGNED_CMAP, vmin=-1, vmax=1)
        ax.plot(0, 0, "*", color=S.STAR, ms=14, mec="k", mew=0.5)
        ax.plot(*true, "o", ms=13, mfc="none", mec="k", mew=1.5, label="真实位置")
        ax.plot(*found, "x", ms=11, color="k", mew=2, label="找到的位置（最高分）")
        ax.set_xlabel("mas"); ax.set_ylabel("mas"); ax.legend(loc="lower left", fontsize=8.5)
        ax.set_title("相关图：每一点的颜色 = 该位置的相似度")
        fig.colorbar(im, ax=ax, shrink=0.8)
        C.show(fig)

    st.markdown("""
    **看一看：** 深蓝色代表较高的正分数，棕色代表负分数。真实位置附近通常有一个峰，中心对称的位置则有一个负的影子。

    附近还会出现别的峰，叫做**旁瓣**。噪声有时会把旁瓣抬高，使它超过真实位置的峰。
    所以，得分最高的位置是一次估计，还需要用更多数据来检查。
    """)

    st.header("多观测几次，统计一下")
    st.markdown("""
    一次观测可能刚好幸运，也可能刚好碰到很大的噪声。

    **再试一次：** 点击下面的按钮，在相同条件下生成 100 组独立噪声。我们暂把定位误差小于 10 mas 记作「找对」。
    记录找对的次数，再换一个观测时间重复一次。哪种方案更可靠？
    """)
    if st.button("开始 100 次模拟", key='action_8_simulate'):
        rng = np.random.default_rng(100)
        errs = np.array([np.hypot(*(nl.locate(tpl, nl.correlation_map(tpl, nl.simulate_chop(e3, e4, rng), w))[1] - true))
                         for _ in range(100)])
        ok = errs < 10
        c1, c2 = st.columns([1, 2.4])
        c1.metric("找对的次数（误差 < 10 mas）", f"{ok.sum()} / 100")
        if ok.any():
            c1.metric("找对时的典型误差", f"{np.median(errs[ok]):.1f} mas")
        with c2:
            fig, ax = plt.subplots(figsize=(6.4, 2.6))
            ax.hist(np.clip(errs, 0, 60), bins=30, color=S.GREY)
            ax.axvline(10, color=S.RED, ls="--", lw=1)
            ax.set_xlabel("误差（mas，超过 60 的计入最右一格）"); ax.set_ylabel("次数")
            C.show(fig)
        st.caption("试试：把观测时间调到 3 小时或 30 小时，或者关掉加权，再跑一次。")

    st.success("""
    **这次实验告诉我们：** 相关图利用信号形状来寻找位置。提高 SNR 通常能让结果更稳定，但定位误差还受阵列、波长和重建方法影响。100 次模拟可以帮助你比较方案，不能当作所有观测的保证。
    """)
    C.think("为什么关掉加权后经常找错？",
            "短波长的数据噪声最大、行星信号又最弱。不加权时，这些噪声和长波长的有用信号同等对待，把相关图搅乱了。")
    C.think("找到位置以后，还能得到什么？",
            "在找到的位置上，逐个波长比较数据和指纹的幅度，就能得到行星在每个波长的亮度——也就是行星的**光谱**，可以用来研究它的温度和大气。")

def render_contrast():
    C.goal("比较恒星和行星的亮度，再看看衍射光斑怎样影响分辨。")
    st.markdown("""
    假设一座灯塔旁边有一只萤火虫。两者都能发光，但我们收到的光相差多少？
    这里把**行星通量除以恒星通量**定义为对比度 C。C = 10⁻⁷，表示行星只有恒星的一千万分之一亮。
    对比度描述光源本身的亮度差；能否分开两个光点，还要看它们的角距离和望远镜的衍射光斑。

    **试试看：** 先保持口径 4 米不变，把对比度从 10⁻⁷ 调到 10⁻⁴。只改变行星的亮度，恒星曲线会怎样？
    然后把对比度调回去，只增大口径，比较光斑的宽度。
    """)
    c1, c2 = st.columns([1, 2.6])
    with c1:
        exponent = st.slider("对比度的十进制指数", -10., -3., C.control_value('lesson_2_contrast', -7.), .5, key='lesson_2_contrast')
        diameter = st.slider("单集光器口径（米）", 1., 40., C.control_value('lesson_2_D', 4.), .5, key='lesson_2_D')
        wavelength = st.slider("波长（微米）", 4., 18., C.control_value('lesson_2_wl', 10.), .5, key='lesson_2_wl')
        st.metric("行星 / 恒星", f"{10**exponent:.1e}")
        st.metric("恒星 / 行星", f"{10**(-exponent):.1e}")
    with c2:
        C.show(S.fig_single_telescope_blur(D=diameter, lam_um=wavelength, contrast=10**exponent))
    st.markdown("棕色曲线是恒星，蓝色曲线是行星。这里分别画出两者的光斑，真实观测接收到的是叠加后的强度。")
    C.think("把恒星和行星一起移到更远处，对比度会改变吗？",
            "在忽略消光、两者仍处于同一系统的条件下，两者通量都按距离平方反比下降，比值近似不变；角距离却会变小。")


def render_null_depth():
    C.goal("把对比度与消零深度分开：一个描述光源，另一个描述恒星光被压低了多少。")
    st.markdown("""
    上一节的 C 是行星与恒星的通量比。现在我们调节仪器，看看能把恒星压暗到什么程度。
    在这个双光束实验里，把**暗输出强度除以亮输出强度**记作消零深度 N。数值越小，消零越深。

    **试试看：** 先把两束光的振幅比设成 1、残余相位误差设成 0°。再只改变其中一项。
    波峰和波谷相加后，还能刚好为零吗？
    """)
    c1, c2 = st.columns([1, 2.6])
    with c1:
        amp = st.slider("第二束 / 第一束的振幅比", .5, 1.5, C.control_value('lesson_3_amp', 1.), .01, key='lesson_3_amp')
        error = st.slider("残余相位误差（度）", -20., 20., C.control_value('lesson_3_error', 0.), .25, key='lesson_3_error')
        null, leakage = O.two_beam_null(amp, error)
        st.metric("消零深度 N（暗 / 亮）", f"{null:.2e}")
        st.metric("漏光 / 入射总强度", f"{leakage:.2e}")
    with c2:
        C.show(S.fig_null_depth(amp, error))
    st.latex(r"N=\frac{1+a^2-2a\cos\delta}{1+a^2+2a\cos\delta}")
    st.markdown("a 是振幅比，δ 是偏离理想相消条件的相位误差。深消零时，暗/亮比与漏光/入射总光近似相等。")
    st.header("再看一个限制：恒星有大小")
    st.markdown("下面暂时恢复理想振幅和相位，只看恒星圆盘带来的几何漏光。这里的漏光比例以入射恒星总通量为分母。")
    render_stellar_leakage()


def render_combiner():
    C.goal("先看四路电场怎样通过矩阵合成，再把单孔衍射包络放进去。")
    st.markdown("""
    现在把两台集光器扩展为四台。按图中编号，四个位置依次是 (L,qL)、(L,−qL)、(−L,−qL)、(−L,qL)，其中 L=b/2。
    对同一个天空方向，每个集光器收到一束带有几何相位的电场。**先把复振幅按矩阵相加，再取模平方**，得到输出强度。
    """)
    with st.expander("先看四集光器的位置与光路", expanded=False):
        C.show(S.fig_xarray_combiner())
    st.latex(r"\mathbf w=U\mathbf v,\qquad U=\frac12\begin{pmatrix}1&i&i&1\\1&-i&-i&1\\1&i&-i&-1\\1&-i&i&-1\end{pmatrix}")
    st.markdown("矩阵的每一列对应一个集光器，每一行对应一路输出。1、−1、i、−i 分别表示 0、π、π/2、−π/2 的相位权重。第 3、4 行对应两路暗输出；把它们相减，就得到斩波信号。")
    st.latex(r"v_j=\exp\!\left[\frac{2\pi i}{\lambda}(x_j\alpha+y_j\beta)\right],\qquad T_k=\frac{|(U\mathbf v)_k|^2}{4}")
    st.markdown("轴上恒星让四路输入同相。看看第 3 行的系数：1+i−i−1=0，所以这个方向被消零。分母 4 是四臂入射总功率；四路 T 相加为 1。")
    st.header("干涉和衍射，怎样同时进入合光？")
    st.markdown("""
    每台集光器还有有限的口径。对相同、无像差的圆孔，在夫琅禾费近似下，可以把响应分成两部分：
    **单孔衍射包络 A** 决定大范围的接收权重，**阵列干涉项 T** 决定里面细密的明暗条纹。
    它们来自同一个场叠加问题；相同孔径让共同的衍射振幅可以提到求和号外。
    """)
    st.latex(r"e(\theta)=\frac{2J_1(u)}{u},\quad u=\frac{\pi D\theta}{\lambda},\quad E_k=e(\theta)(U\mathbf v)_k,\quad R_k=A\,T_k,\ A=|e|^2")
    st.caption("这里使用理想圆孔的衍射包络示范分离关系；实际单模光纤接收权重还需做模场重叠积分。")
    c1, c2, c3 = st.columns(3)
    with c1:
        diameter = st.slider("单孔口径 D（米）", 1., 12., C.control_value('lesson_4_D', 4.), .5, key='lesson_4_D')
        baseline = st.slider("消零基线 b（米）", 4., 40., C.control_value('lesson_4_b', 14.5), .5, key='lesson_4_b')
    with c2:
        wavelength = st.slider("波长（微米）", 4., 18., C.control_value('lesson_4_wl', 10.), .5, key='lesson_4_wl')
        ratio = st.slider("长短基线比 q", 2., 8., C.control_value('lesson_4_q', 6.), .5, key='lesson_4_q')
    with c3:
        alpha = st.slider("试探光源的 α（mas）", -200., 200., C.control_value('lesson_4_alpha', 0.), 5., key='lesson_4_alpha')
        beta = st.slider("试探光源的 β（mas）", -200., 200., C.control_value('lesson_4_beta', 0.), 5., key='lesson_4_beta')
    samples = max(241, int(np.ceil(800*C.MAS*ratio*baseline/(wavelength*1e-6)*3)) | 1)
    grid = np.linspace(-400, 400, samples)
    X, Y = np.meshgrid(grid*C.MAS, grid*C.MAS)
    fringe = O.response(X, Y, wavelength*1e-6, baseline, ratio, diameter, diffraction=False)
    envelope = O.airy_amplitude(X, Y, wavelength*1e-6, diameter)**2
    C.show(S.fig_optical_response(grid, envelope, fringe[2], envelope*fringe[2]))
    st.markdown("**试试看：** 先只改 D，观察包络宽度；再只改 b，观察条纹间距。恒星、行星参数没有参与这张仪器响应图的计算。")
    point = O.response(alpha*C.MAS, beta*C.MAS, wavelength*1e-6, baseline, ratio, diameter)
    columns = st.columns(4)
    for k, col in enumerate(columns): col.metric(f"输出 {k+1} / 入射总功率", f"{point[k]:.4f}")
    C.show(S.fig_phasors(O.COMBINER[2] * O.fields(alpha*C.MAS, beta*C.MAS, wavelength*1e-6, baseline, ratio)))
    st.caption("相量图画出干涉项；上面的四路功率还乘入了衍射包络。轴上四个带权相量闭合，离轴后通常不再闭合。")


def render_sky_lab():
    C.goal("固定仪器，改变目标与尘埃，再把天空亮度乘上接收响应，比较输出图。")
    st.markdown("""
    刚才的响应图回答：来自天空某个方向的光，有多少进入某一路输出？现在再问：这个方向原本有多少光？
    把恒星、行星和尘埃的亮度分布放进来，才能算出实际接收到的贡献。
    不同天空位置的热辐射彼此不相干，所以对每个方向完成合束后，**相加强度**。
    """)
    st.latex(r"F_k=\int I(\alpha,\beta)R_k(\alpha,\beta)\,d\Omega")
    st.markdown("**先做一组对照：** 保持仪器不变，只把行星半径调为两倍，比较它的位置和通量；再只增加尘埃量，比较背景。")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("目标恒星")
        ts = st.slider("恒星温度（K）", 3000., 8000., C.control_value('lesson_5_ts', 5778.), 1., key='lesson_5_ts', format='%.0f')
        rs = st.slider("恒星半径（太阳半径）", .3, 2., C.control_value('lesson_5_rs', 1.), .1, key='lesson_5_rs')
        distance = st.slider("系统距离（pc）", 3., 30., C.control_value('lesson_5_distance', 10.), .5, key='lesson_5_distance')
    with c2:
        st.subheader("行星")
        tp = st.slider("行星温度（K）", 150., 450., C.control_value('lesson_5_tp', 255.), 5., key='lesson_5_tp', format='%.0f')
        rp = st.slider("行星半径（地球半径）", .5, 3., C.control_value('lesson_5_rp', 1.), .1, key='lesson_5_rp')
        orbit = st.slider("投影分离距离（au）", .2, 3., C.control_value('lesson_5_orbit', 1.), .1, key='lesson_5_orbit')
        pa = st.slider("行星方位角（度）", 0., 350., C.control_value('lesson_5_planet_pa', 40.), 5., key='lesson_5_planet_pa')
    with c3:
        st.subheader("黄道尘")
        ez = st.slider("外黄道尘量（太阳系倍数）", 0., 50., C.control_value('lesson_5_ez', 1.), .5, key='lesson_5_ez')
        lz = st.slider("本地黄道光强度系数", 0., 5., C.control_value('lesson_5_lz', 1.), .1, key='lesson_5_lz')
        latitude = st.slider("目标黄道纬度（度）", 0., 90., C.control_value('lesson_5_lat', 45.), 5., key='lesson_5_lat')
    with st.expander("仪器参数：把衍射与干涉的变化也加进来"):
        c1, c2 = st.columns(2)
        with c1:
            wl = st.slider("观测波长（微米）", 4., 18., C.control_value('lesson_5_wl', 10.), .5, key='lesson_5_wl')
            diameter = st.slider("集光器口径（米）", 1., 12., C.control_value('lesson_5_D', 4.), .5, key='lesson_5_D')
        with c2:
            baseline = st.slider("基线（米）", 4., 40., C.control_value('lesson_5_b', 14.5), .5, key='lesson_5_b')
            rotation = st.slider("阵列旋转角（度）", 0., 180., C.control_value('lesson_5_rotation', 0.), 5., key='lesson_5_rotation')
    experiment = O.sky_experiment(star_temperature=ts, star_radius=rs, distance=distance,
        planet_temperature=tp, planet_radius=rp, orbit_au=orbit, position_angle=pa,
        exozodi=ez, local_zodi=lz, latitude=latitude, wavelength_um=wl,
        baseline=baseline, diameter=diameter, rotation=rotation)
    component = st.radio("查看哪些光源", ['全部光源', '恒星', '行星', '本地黄道光', '外黄道光'],
        index=['全部光源', '恒星', '行星', '本地黄道光', '外黄道光'].index(C.control_value('lesson_5_component', '全部光源')),
        key='lesson_5_component', horizontal=True)
    C.show(S.fig_sky_contributions(experiment, component))
    st.caption("固定参考通量：10 pc 处、255 K、地球半径的行星在 10 微米谱道内的入射通量。色标固定，不随滑动条自动归一化。圆圈标出行星。")
    st.caption("这是透射加权的天空贡献图，不是直接拍摄或重建的探测器图像。恒星和行星未分辨，用单像素示意；恒星漏光在独立细网格上积分。")
    if not experiment['in_view']: st.info("行星已移出当前 ±400 mas 的示意视场。可以减小投影距离或增大系统距离。")
    c1, c2, c3 = st.columns(3)
    c1.metric("本谱道对比度（行星 / 恒星）", f"{experiment['planet_flux']/experiment['stellar_flux']:.2e}")
    c2.metric("恒星角半径", f"{experiment['rho_mas']:.2f} mas")
    c3.metric("输出 3 的恒星漏光 / 入射恒星", f"{experiment['stellar_counts'][2]/experiment['stellar_flux']:.2e}")
    table = ['| 光源 | 输出 3 | 输出 4 | 差值 3 − 4 |', '|---|---:|---:|---:|']
    for name, image in experiment['output'].items():
        rates = image.sum(axis=(1, 2))
        table.append(f"| {name} | {rates[2]:.3g} | {rates[3]:.3g} | {rates[2]-rates[3]:+.3g} |")
    st.markdown('\n'.join(table))
    st.caption("表中单位：光子 / 秒 / 平方米，单谱道宽度 Δλ=λ/20；未乘集光总面积与后端效率。")
    st.markdown("""
    **接着试试看：**

    - 只增加恒星半径：恒星更亮，也更大，几何漏光会怎样变？
    - 只改变行星的方位角或投影距离：行星会经过哪一条明纹或暗纹？
    - 只改变外黄道尘量：输出 3 的背景怎样变？对称尘埃在输出 3 − 4 的总通量里还剩多少？
    - 只改变黄道纬度：本地黄道光的背景强度是否改变？

    正负尘埃贡献是在对整个对称分布积分后抵消，单个像素仍可能非零。平均值抵消也不会消除光子噪声。
    这里采用黑体恒星/行星和正面朝向的轴对称尘埃盘。恒星光度会同时影响尘埃温度；温度、半径与行星位置可独立调节，用来分辨各因素的作用。
    """)

SECTIONS = {
    1: ("光的干涉", "先叠加两列波", render_interference),
    2: ("对比度", "再比较恒星和行星有多亮", render_contrast),
    3: ("消零深度", "看看恒星光被压低了多少", render_null_depth),
    4: ("四集光器合光矩阵", "把干涉与衍射放在同一个响应里", render_combiner),
    5: ("恒星、行星与黄道尘", "用滑动条比较天空贡献图", render_sky_lab),
    6: ("进阶：旋转阵列", "从空间位置到信号形状", render_rotation),
    7: ("进阶：光子噪声", "背景平均值抵消后，噪声还在", render_photon_noise),
    8: ("进阶：找到行星", "比较候选信号，估计位置", render_planet_search),
}


def section_label(index):
    return f"{index}: {SECTIONS[index][0]}"


def main():
    C.page("从光的干涉到四集光器消零", "先猜一猜，再调一调：三个概念、一个合光矩阵、一组天空实验")
    st.markdown("依次认识光干涉、对比度和消零深度，再看四路光怎样合成，最后改变恒星、行星与黄道尘参数。")
    section = st.radio("选择章节：", list(SECTIONS), format_func=section_label, key="curriculum_section")
    st.divider()
    _, subtitle, render = SECTIONS[section]
    st.header(section_label(section)); st.caption(subtitle)
    render()
    C.save_controls(section)


if __name__ == "__main__":
    main()
