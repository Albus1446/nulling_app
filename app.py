"""单页互动讲义：选择章节，只渲染当前章节。"""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import app_common as C
import core as nl
import schematics as S


def render_introduction():
    st.markdown("""
    天文学家想直接"看见"围绕其他恒星运转的类地行星，并分析它的光，判断那里有没有水、有没有大气。
    这件事难在哪里？又可以用什么巧妙的办法做到？这套互动讲义用 8 个章节，带你一步步走完整个思路。
    """)

    st.header("难在哪里：在灯塔旁边找一只萤火虫")
    C.show(S.fig_contrast_cartoon())
    st.markdown("""
    - **太暗**：在中红外波段（波长约 10 微米），一颗类地行星比它的恒星暗大约 **1000 万倍**。
    - **太近**：如果这个系统离我们 10 秒差距（约 33 光年），行星和恒星在天空上只相隔 **0.1 角秒**。
    """)

    st.subheader("动手试试：单台望远镜能分开它们吗？")
    c1, c2 = st.columns([1, 3])
    with c1:
        D = st.slider("望远镜口径 D（米）", 1.0, 40.0, C.control_value('lesson_0_D', 4.0), 0.5, key='lesson_0_D')
        lam = st.slider("观测波长（微米）", 4.0, 18.0, C.control_value('lesson_0_lam', 10.0), 0.5, key='lesson_0_lam')
        st.markdown(f"衍射光斑的大小约为 **λ/D ≈ {lam * 1e-6 / D / C.MAS:.0f} mas**，而行星离恒星只有 **100 mas**。")
    with c2:
        C.show(S.fig_single_telescope_blur(D=D, lam_um=lam))
    st.markdown("""
    图中橙线是恒星经过望远镜后的像（因为光的**衍射**，一个点会变成一个有宽度的光斑），蓝线是行星的像。
    不管口径怎么调，行星那条线始终远远低于恒星光斑的"裙边"——行星被恒星的光淹没了。
    """)
    C.think("把口径调到 40 米，行星的像能露出来吗？",
            "不能。口径变大，光斑变窄，100 mas 处恒星的光确实暗了很多，但仍然比行星亮几千到几万倍。"
            "单靠一台更大的望远镜解决不了 1000 万倍的亮度差。")

    st.header("办法：让恒星的光自己抵消掉")
    st.markdown("""
    **消零干涉（nulling interferometry）** 的想法是：用几台分开放置的望远镜一起看同一颗恒星，
    把它们收集到的光以"波峰对波谷"的方式叠在一起，**让正对着我们的恒星光相互抵消**；
    而行星偏离中心一点点，它的光抵消不干净，就被保留下来。

    | 节 | 主题 | 一句话 |
    |---|---|---|
    | 1 | 光的干涉 | 两列波相差半个波长时会相互抵消 |
    | 2 | 两台望远镜消零 | 恒星正对、行星偏一点，抵消程度不同 |
    | 3 | 恒星的漏光 | 恒星不是一个点，边缘会漏一点光 |
    | 4 | 四台望远镜与斩波 | 两路输出相减，去掉对称的背景 |
    | 5 | 旋转阵列 | 转起来，行星的位置变成一串"指纹"信号 |
    | 6 | 光子噪声与信噪比 | 光是一颗颗光子，计数有随机起伏 |
    | 7 | 找到行星 | 拿"指纹库"去比对，找出行星在哪 |
    | 8 | 参数实验室 | 自己设计望远镜、挑选目标 |

    **怎么用**：每节先看示意图，再拖动滑块观察图怎样变化，最后点开"想一想"检验自己。
    需要的数学只有：正弦函数、角度与弧度、平方根。
    """)
    st.caption("单位提示：1 角秒（″）= 1/3600 度；1 mas（毫角秒）= 0.001 角秒。1 微米（µm）= 10⁻⁶ 米。")


def render_interference():
    C.goal("什么是相位差；为什么两列波\"波峰对波谷\"时会相互抵消。")

    st.markdown("""
    光是一种波。两列同样的波叠加在一起时，结果取决于它们**错开了多少**（相位差）：

    - 波峰对波峰：叠加后振幅变成 2 倍，亮度（∝ 振幅²）变成 4 倍——**相长干涉**；
    - 波峰对波谷：叠加后正好抵消，变暗为零——**相消干涉**。

    生活中的例子：**降噪耳机**会录下周围的噪音，再播放一列"波峰对波谷"的反向声波，让噪音被抵消。
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
    如果一束光比另一束**多走了一段路程**（叫做**光程差**），它就会落后一段。
    多走一个完整波长，正好落后一圈，波峰又对上了波峰；多走半个波长，就变成波峰对波谷。
    """)
    st.latex(r"\text{相位差} = 360^\circ \times \frac{\text{光程差}}{\text{波长}}")
    c1, c2 = st.columns(2)
    with c1:
        lam = st.slider("波长（微米）", 4.0, 18.0, C.control_value('lesson_1_lam1', 10.0), 0.5, key='lesson_1_lam1')
    with c2:
        opd = st.slider("光程差（微米）", 0.0, 20.0, C.control_value('lesson_1_opd', 5.0), 0.25, key='lesson_1_opd')
    ph = 360 * opd / lam
    st.markdown(f"光程差 {opd:g} µm ÷ 波长 {lam:g} µm = **{opd / lam:.2f} 个波长**，相位差 = **{ph:.0f}°**"
                f"（相当于 {ph % 360:.0f}°）。")

    st.success("**小结**：两束光的光程差为半个波长（或 1.5、2.5…… 个波长）时相互抵消。"
               "下一节就用这个原理，把恒星的光\"抵消\"掉。")
    C.think("光程差为 5 µm，对 10 µm 的光会抵消，对 5 µm 的光呢？",
            "对 5 µm 的光，5 µm 正好是 1 个完整波长，波峰又对上了波峰，变成相长干涉。"
            "**同一个光程差，对不同波长的光效果不同**——这就是后面透射图随波长变化的原因。")
    C.think("如果两列波振幅不一样（比如一个是 1，一个是 0.9），还能完全抵消吗？",
            "不能完全抵消，最暗时还剩 1 − 0.9 = 0.1 的振幅，亮度是 0.01。所以真实仪器要求两路光的强度非常接近。")


def render_two_telescopes():
    C.goal("两台望远镜怎样把正对的恒星\"关掉\"；为什么偏一点点的行星能留下来；天空上的\"百叶窗\"。")

    st.header("原理图")
    C.show(S.fig_bracewell_setup())
    st.markdown("""
    两台望远镜相隔一段距离 **b**（叫做**基线**），同时对准恒星。

    1. **恒星正对视线**（左图）：它的光像一排排水平的波前，同时到达两台望远镜，两路光完全一样。
       在合束器之前，把其中一路**翻转半个波长**，两路光就变成"波峰对波谷"，在**暗输出**里相互抵消。
    2. **行星偏了一个很小的角度 θ**（右图）：波前是斜的，望远镜 2 要比望远镜 1 **多走一段光程** ≈ b·θ。
       这段额外的光程打乱了"波峰对波谷"，抵消不完全，暗输出里就有了行星的光。
    """)
    st.latex(r"\text{暗输出的透过比例} \;=\; \sin^2\!\left(\pi\,\frac{b\,\theta}{\lambda}\right)")
    st.markdown("θ = 0（恒星）时为 0；b·θ 等于半个波长时为 1（完全透过）。")

    st.header("动手：天空上的\"百叶窗\"")
    st.markdown("把暗输出对天空各个方向的透过比例画出来，就像一扇明暗相间的百叶窗。恒星永远在正中间的黑条上。")
    c1, c2 = st.columns([1, 2.6])
    with c1:
        b = st.slider("基线 b（米）", 2.0, 40.0, C.control_value('lesson_2_b', 14.5), 0.5, key='lesson_2_b')
        lam = st.slider("波长 λ（微米）", 4.0, 18.0, C.control_value('lesson_2_lam', 10.0), 0.5, key='lesson_2_lam')
        pmas = st.slider("行星离恒星的角距离（mas）", 10, 250, C.control_value('lesson_2_pmas', 100), 5, key='lesson_2_pmas')
        Tp = np.sin(np.pi * b * pmas * C.MAS / (lam * 1e-6)) ** 2
        st.metric("行星透过比例", f"{Tp:.2f}")
        st.metric("条纹间距 λ/b", f"{lam * 1e-6 / b / C.MAS:.0f} mas")
        best = lam * 1e-6 / (2 * pmas * C.MAS)
        st.caption(f"让行星正好落在第一条亮纹上的基线：b = λ/(2θ) ≈ {best:.1f} m")
    with c2:
        C.show(S.fig_fringe_1d(b=b, lam_um=lam, planet_mas=pmas))

    st.success("**小结**：两台望远镜 + 半个波长的翻转 = 正对的恒星被抵消。基线越长，条纹越密；"
               "调好基线，就能让行星落在亮条上。")
    C.think("基线调得特别短（比如 2 米），会怎样？",
            "条纹变得很宽，行星（100 mas）落在中间那条黑条里，和恒星一起被挡掉了。基线太短，分不开恒星和行星。")
    C.think("同一个基线，换成短波长（4 µm）和长波长（18 µm），哪个条纹更密？",
            "短波长更密。条纹间距 = λ/b，波长越短，间距越小。所以同一颗行星在不同波长下会落在不同的条纹上。")


def render_stellar_leakage():
    C.goal("为什么恒星不能被完全抵消；漏光（零深）和哪些因素有关；漏掉的星光和行星比谁亮。")

    st.markdown("""
    上一节假设恒星是一个点。实际上恒星是一个小圆盘：太阳放到 10 秒差距外，看起来的半径约 **0.47 mas**。
    圆盘中心正好在黑条上，但边缘偏离了一点点，就会**漏过一点光**。漏过的比例叫做**零深**（null depth）。
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
    st.latex(r"\text{零深} \approx \frac{1}{4}\left(\frac{\pi\, b\, \rho}{\lambda}\right)^2"
             r"\qquad(\rho = \text{恒星的角半径})")

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
    **消零把恒星压暗了十万倍，但漏光依然比行星亮。** 后面几节的"斩波""旋转"和"长时间积分"，就是为了从这些漏光中把行星挑出来。
    """)

    st.success("**小结**：恒星的大小决定了消零的极限。基线越长、波长越短、恒星越近，漏光越多。")
    C.think("把基线从 14.5 m 加倍到 29 m，零深变为多少倍？",
            "零深 ∝ b²，变为 4 倍。所以基线不是越长越好：长基线有利于分开近处的行星，但漏光更多。")
    C.think("为什么近处的恒星漏光更多？",
            "距离减半，恒星看起来的角半径 ρ 加倍，零深 ∝ ρ²，变为 4 倍。不过近处的行星也更亮，所以近处的目标总体仍然更容易观测。")


def render_phase_chopping():
    C.goal("四台望远镜怎样组合成两路输出；为什么\"相减\"能去掉恒星周围对称的尘埃光，而留下行星。")

    st.header("一个新麻烦：尘埃")
    st.markdown("""
    恒星周围常常有一圈温暖的**尘埃**（叫做外黄道光，exozodi），它在红外波段发光，总亮度可以是行星的几百倍。
    两台望远镜的"百叶窗"是**左右对称**的：行星在右边能透过，左边对称位置上的尘埃也能透过——分不清哪个是行星。

    解决办法是用**四台望远镜**，造出**两路互为镜像**的输出，再把它们**相减**。
    """)
    C.show(S.fig_xarray_combiner())
    st.markdown("""
    - 四台望远镜排成长方形。上边两台（1、4）为一对，下边两台（2、3）为一对，**每对先各自消掉恒星**（就是上一节的方法）。
    - 再把两对剩下的光**交叉混合**（其中一路错开 1/4 个波长），得到**输出 3** 和 **输出 4**。
    - 这两路输出的"百叶窗"图案**上下互为镜像**。把两路相减，得到**斩波信号**（chop）。
    """)

    st.header("动手：看看三张透射图")
    c1, c2 = st.columns([1, 3])
    with c1:
        lam = st.slider("波长 λ（微米）", 4.0, 18.0, C.control_value('lesson_4_lam4', 10.0), 0.5, key='lesson_4_lam4')
        q = st.slider("长方形的长宽比 q", 2.0, 8.0, C.control_value('lesson_4_q', 6.0), 0.5, key='lesson_4_q')
        ring = st.toggle("显示一圈对称的尘埃环", value=C.control_value('lesson_4_ring', True), key='lesson_4_ring')
        ring_r = st.slider("尘埃环半径（mas）", 20, 200, C.control_value('lesson_4_ring_r', 60), 5, disabled=not ring, key='lesson_4_ring_r')
    L = 14.5 / 2; ext = 250
    g = np.linspace(-ext, ext, 301) * C.MAS
    A, B = np.meshgrid(g, g)
    T3, T4 = nl.transmission(A, B, lam * 1e-6, L, q)
    pxy = np.array([76.6, 64.3])
    with c2:
        C.show(S.fig_maps(T3, T4, ext, planet_xy=pxy, ring_r=ring_r if ring else None))

    if ring:
        th = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
        r3, r4 = nl.transmission(ring_r * np.cos(th) * C.MAS, ring_r * np.sin(th) * C.MAS, lam * 1e-6, L, q)
        p3, p4 = nl.transmission(pxy[0] * C.MAS, pxy[1] * C.MAS, lam * 1e-6, L, q)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**尘埃环**（平均透过比例）")
            st.metric("输出 3", f"{r3.mean():.3f}"); st.metric("输出 4", f"{r4.mean():.3f}")
            st.metric("相减（斩波）", f"{r3.mean() - r4.mean():+.1e}")
        with c2:
            st.markdown("**行星**（透过比例）")
            st.metric("输出 3", f"{p3:.3f}"); st.metric("输出 4", f"{p4:.3f}")
            st.metric("相减（斩波）", f"{p3 - p4:+.3f}")
        st.markdown("尘埃环在两路输出中一样亮，相减后几乎为零；行星在两路中亮度不同，相减后留下来。")

    st.markdown("""
    **为什么会这样？** 斩波图（右图）有一个特点：任意一点和它关于中心的**对称点**，颜色正好相反（红对蓝）。
    所以一个关于恒星对称的东西（恒星本身、尘埃环、均匀的背景），红的部分和蓝的部分相互抵消，相减后什么也不剩；
    只有偏在一边的行星留下信号。
    """)
    st.success("**小结**：四台望远镜 → 两路镜像输出 → 相减（斩波）→ 对称的背景消失，行星留下。")
    C.think("如果尘埃盘有一团只在一侧的\"疙瘩\"，斩波后会怎样？",
            "疙瘩不对称，斩波后会留下信号，看起来像一颗行星。这是真实观测中需要小心的\"假行星\"。")
    C.think("斩波去掉了尘埃的光，是不是尘埃就完全没有影响了？",
            "不是。相减只去掉了尘埃光的**平均值**，但尘埃光子的随机起伏（噪声）还在，而且尘埃越亮噪声越大。第 6 节会讲。")


def render_rotation():
    C.goal("为什么要让望远镜阵列绕着恒星方向旋转；行星的位置怎样被编码进一条随时间变化的信号。")

    st.markdown("""
    如果阵列不动，行星只停在百叶窗的某一点，我们每个波长只得到一个数，没法确认它是行星。

    让整个阵列**绕着对准恒星的方向慢慢转一圈**（比如 10 小时转一圈）。站在阵列上看，行星就沿着一个圆圈走，
    依次穿过斩波图的红区、白区、蓝区，信号一会儿正、一会儿负。**这条信号曲线的形状只由行星的位置决定**，就像它的指纹。
    """)

    c1, c2 = st.columns([1, 3.2])
    with c1:
        phi = st.slider("阵列转过的角度（度）", 0, 359, C.control_value('lesson_5_phi', 60), 1, key='lesson_5_phi')
        lam = st.slider("波长 λ（微米）", 4.0, 18.0, C.control_value('lesson_5_lam5', 10.0), 0.5, key='lesson_5_lam5')
        sep = st.slider("行星离恒星的角距离（mas）", 40, 180, C.control_value('lesson_5_sep5', 100), 5, key='lesson_5_sep5')
        pa = st.slider("行星的方位角（度）", 0, 359, C.control_value('lesson_5_pa', 40), 5, key='lesson_5_pa')
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
    st.markdown("下面把两颗位置不同的\"候选行星\"的信号画在一起。只要位置差一点，曲线就明显不同——这就是能从信号中找出行星位置的原因。")
    c1, c2 = st.columns([1, 3.2])
    with c1:
        dpa = st.slider("第二颗的方位角比第一颗多（度）", 0, 90, C.control_value('lesson_5_dpa', 10), 1, key='lesson_5_dpa')
        dsep = st.slider("第二颗的角距离比第一颗多（mas）", -30, 30, C.control_value('lesson_5_dsep', 0), 1, key='lesson_5_dsep')
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

    st.success("**小结**：旋转把行星的**空间位置**变成了**时间上的信号**。每个波长都有一条这样的曲线，合起来就是行星独一无二的指纹。")
    C.think("恒星和对称的尘埃在旋转时，斩波信号会变吗？",
            "不会。它们关于中心对称，转到哪个角度都还是对称的，斩波信号始终为零。只有行星会产生随旋转变化的信号。")
    C.think("转了半圈之后，信号和前半圈有什么关系？",
            "正好反号。转半圈后，行星走到了对称点上，而斩波图在对称点上颜色相反。看右图：180° 之后的曲线是前 180° 的\"倒影\"。")


def render_photon_noise():
    C.goal("什么是光子噪声；为什么观测时间越长越好；信噪比（SNR）怎么理解。")

    st.header("像接雨滴一样数光子")
    st.markdown("""
    探测器接收光，其实是在**数光子**。光子到达是随机的，就像下雨时数一个杯子里接到的雨滴：
    平均每次接到 N 滴，但每次实际接到的数会上下浮动，浮动大小约为 **√N**。这种随机起伏叫做**光子噪声**。
    """)
    c1, c2 = st.columns([1, 2.4])
    with c1:
        N = st.select_slider("平均每次接到的光子数 N", options=[10, 30, 100, 300, 1000, 3000, 10000], value=C.control_value('lesson_6_N', 100), key='lesson_6_N')
        st.metric("起伏大小 √N", f"{np.sqrt(N):.0f}")
        st.metric("相对起伏 √N / N", f"{1 / np.sqrt(N):.1%}")
    with c2:
        rng = np.random.default_rng(0)
        x = rng.poisson(N, 3000)
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.hist(x, bins=40, color=S.GREY)
        ax.axvline(N, color="k", lw=1.5); ax.axvspan(N - np.sqrt(N), N + np.sqrt(N), color=S.BRIGHT, alpha=0.35)
        ax.set_xlabel("一次接到的光子数"); ax.set_ylabel("次数"); ax.set_title("重复 3000 次的结果：黄色带宽约 ±√N")
        C.show(fig)
    st.markdown("N 越大，起伏的绝对值越大，但**相对**起伏越小。所以光子越多，测量越准。")

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
    for (name, v), col in zip(parts.items(), [S.STAR, "#2CA02C", S.DUST, S.PLANET]):
        ax.bar(wl, v / tot, bottom=bottom, width=inst["dwl"] * 1e6 * 0.92, color=col, label=name)
        bottom += v / tot
    ax.set_xlabel("波长（微米）"); ax.set_ylabel("所占比例"); ax.set_ylim(0, 1)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8.5)
    ax.set_title("10 秒差距外的类太阳恒星，观测 10 小时：两路暗输出里的光子来源")
    C.show(fig)
    st.markdown("""
    短波长时几乎全是恒星漏光（第 3 节），长波长时以尘埃的光为主。行星只占极小一部分——
    它们的平均值被斩波去掉了，但它们的**光子噪声**还在，这才是真正限制我们的东西。
    """)

    st.header("信噪比：信号比噪声大多少倍")
    st.latex(r"\text{SNR} = \frac{\text{行星信号}}{\text{噪声}} \approx \frac{\text{行星光子数}}{\sqrt{\text{背景光子数}}}")
    st.markdown("""
    观测时间加倍，行星光子数加倍，噪声只增加 √2 倍，所以 **SNR ∝ √时间**。
    天文学家通常要求 **SNR ≥ 5** 才算"探测到"。
    """)
    c1, c2 = st.columns([1, 2.4])
    with c1:
        hours = st.slider("观测时间（小时）", 1.0, 50.0, C.control_value('lesson_6_hours', 10.0), 1.0, key='lesson_6_hours')
        w = st.select_slider("看哪个波长的数据（微米）", options=[f"{v:.1f}" for v in wl], value=C.control_value('lesson_6_w', f"{wl[22]:.1f}"), key='lesson_6_w')
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
    st.markdown("单个波长的数据噪声很大，几乎看不出行星。把所有波长、所有旋转角度的信息合在一起，SNR 才够大。")

    st.success("**小结**：光子噪声 ≈ √N；SNR ∝ √观测时间；尘埃和漏光越多，噪声越大，需要的时间越长。")
    C.think("要把 SNR 从 5 提高到 10，观测时间要变成多少倍？", "SNR ∝ √时间，SNR 翻倍需要 4 倍的时间。")
    C.think("为什么短波长的数据几乎没用？",
            "短波长时行星本身很暗（它的温度只有约 255 K，主要在长波长发光），而恒星漏光又最多（零深 ∝ 1/λ²）。信号小、噪声大。")


def render_planet_search():
    C.goal("怎样从带噪声的数据中找出行星的位置；什么是相关图；为什么数据越多越可靠。")

    st.markdown("""
    这一步很像手机上的**听歌识曲**：录下一段嘈杂的音乐，拿去和曲库里每一首歌比对，最像的那首就是答案。

    1. **指纹库**：对天空中每一个可能的位置，算出"如果行星在这里，信号应该长什么样"（第 5 节的曲线，每个波长一条）。
    2. **比对**：把实际测到的数据和每一个指纹逐点相乘再加起来，得到一个"相似度分数"。
    3. **找最大值**：把所有位置的分数画成一张图（**相关图**），最亮的地方就是行星。

    比对时，噪声大的波长（短波长）分量会降低权重，噪声小的分量权重高——就像嘈杂的片段在听歌识曲里不太算数。
    """)

    if "seed7" not in st.session_state:
        st.session_state.seed7 = 0
    c1, c2 = st.columns([1, 2.6])
    with c1:
        hours = st.slider("观测时间（小时）", 1.0, 40.0, C.control_value('lesson_7_h7', 10.0), 1.0, key='lesson_7_h7')
        weighted = st.toggle("按噪声大小给各波长加权", value=C.control_value('lesson_7_weighted', True), key='lesson_7_weighted')
        if st.button("再观测一次（换一组随机噪声）", key='action_7_resample'):
            st.session_state.seed7 += 1
    bd = C.bundle()
    tpl = C.templates()
    f = hours / 10
    e3, e4 = bd["e3"] * f, bd["e4"] * f
    rng = np.random.default_rng(st.session_state.seed7)
    data = nl.simulate_chop(e3, e4, rng)
    w = 1.0 / (e3 + e4).mean(axis=1) if weighted else None
    cm = nl.correlation_map(tpl, data, w)
    _, found = nl.locate(tpl, cm)
    true = bd["true"]
    err = float(np.hypot(*(found - true)))
    snr = bd["bud"]["snr_total"] * np.sqrt(f)
    with c1:
        st.metric("SNR", f"{snr:.1f}")
        st.metric("找到的位置与真实位置相差", f"{err:.1f} mas", delta="找对了" if err < 10 else "找错了",
                  delta_color="normal" if err < 10 else "inverse")
    with c2:
        fig, ax = plt.subplots(figsize=(5.6, 4.6))
        hw = 150
        im = ax.imshow(cm / np.abs(cm).max(), extent=[-hw, hw, -hw, hw], cmap="RdBu_r", vmin=-1, vmax=1)
        ax.plot(0, 0, "*", color=S.STAR, ms=14, mec="k", mew=0.5)
        ax.plot(*true, "o", ms=13, mfc="none", mec="k", mew=1.5, label="真实位置")
        ax.plot(*found, "x", ms=11, color="k", mew=2, label="找到的位置（最亮处）")
        ax.set_xlabel("mas"); ax.set_ylabel("mas"); ax.legend(loc="lower left", fontsize=8.5)
        ax.set_title("相关图：每一点的颜色 = 该位置的相似度")
        fig.colorbar(im, ax=ax, shrink=0.8)
        C.show(fig)

    st.markdown("""
    **观察**：相关图在行星处最亮（红）；在关于恒星对称的位置有一个"负的影子"（蓝），因为那里的指纹正好和行星反号。
    行星周围还有一圈圈较亮的"回声"（旁瓣）——有噪声时，偶尔某个回声会比真正的行星更亮，就会**找错位置**。
    """)

    st.header("多观测几次，统计一下")
    st.markdown("同样的条件重复观测 100 次，看看有多少次找对了。")
    if st.button("开始 100 次模拟", key='action_7_simulate'):
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

    st.success("**小结**：相关图 = 拿每个位置的指纹去和数据比对。SNR 越高，真正的行星越突出，越不容易被\"回声\"冒充。"
               "要可靠地定位，通常需要 SNR 达到 10 以上，比单纯\"探测到\"（SNR ≈ 5）要求更高。")
    C.think("为什么关掉加权后经常找错？",
            "短波长的数据噪声最大、行星信号又最弱。不加权时，这些噪声和长波长的有用信号同等对待，把相关图搅乱了。")
    C.think("找到位置以后，还能得到什么？",
            "在找到的位置上，逐个波长比较数据和指纹的幅度，就能得到行星在每个波长的亮度——也就是行星的**光谱**，可以用来研究它的温度和大气。")


def render_parameter_lab():
    C.goal("把前面学到的东西合起来：距离、尘埃、恒星类型和基线怎样决定一颗类地行星能不能被看见。")

    st.markdown("行星总是放在它的恒星的**宜居带**里（接收到的光和地球从太阳接收到的一样多，温度约 255 K）。")
    c1, c2, c3 = st.columns(3)
    with c1:
        star = st.radio("恒星类型", list(C.STAR_TYPES), key='lesson_8_star', index=list(C.STAR_TYPES).index(C.control_value('lesson_8_star', next(iter(C.STAR_TYPES)))))
        T_star, R_star = C.STAR_TYPES[star]
    with c2:
        d = st.slider("恒星距离（pc）", 4.0, 20.0, C.control_value('lesson_8_d', 10.0), 0.5, key='lesson_8_d')
        z = st.select_slider("尘埃量（外黄道光，单位：太阳系的倍数）", options=[0.5, 1, 2, 3, 5, 10, 20, 30, 50], value=C.control_value('lesson_8_z', 1), key='lesson_8_z')
    with c3:
        b = st.slider("基线 b（米）", 6.0, 80.0, C.control_value('lesson_8_b', 14.5), 0.5, key='lesson_8_b')
        hours = st.slider("观测时间（小时）", 1.0, 50.0, C.control_value('lesson_8_h8', 10.0), 1.0, key='lesson_8_h8')

    L_star = R_star**2 * (T_star / 5780) ** 4
    a_au = np.sqrt(L_star)
    sep_mas = a_au / d * 1000
    bd = C.bundle(baseline=b, distance=d, exozodi=float(z), T_star=T_star, R_star=R_star)
    scale = np.sqrt(hours / 10.0)           # SNR ∝ √观测时间
    snr = bd["bud"]["snr_total"] * scale
    need = hours * (5 / snr) ** 2

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("宜居带离恒星", f"{a_au:.2f} au")
    m2.metric("看起来的角距离", f"{sep_mas:.0f} mas")
    m3.metric(f"SNR（{hours:g} 小时）", f"{snr:.1f}", delta="可以探测" if snr >= 5 else "还不够", delta_color="normal" if snr >= 5 else "inverse")
    m4.metric("达到 SNR = 5 需要", f"{need:.1f} 小时" if need < 1e4 else "> 10000 小时")

    st.subheader("哪个基线最好？")
    bs = np.array([6, 8, 10, 12, 14.5, 18, 22, 28, 36, 46, 60, 80.0])
    snrs = np.array([C.bundle(baseline=x, distance=d, exozodi=float(z), T_star=T_star, R_star=R_star)["bud"]["snr_total"] for x in bs]) * scale
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.plot(bs, snrs, "o-", color=S.PLANET)
    ax.plot(b, snr, "*", color=S.RED, ms=16, label="当前选择")
    ax.axhline(5, color="0.5", ls=":", lw=1); ax.text(bs[0], 5.2, "SNR = 5", fontsize=8.5, color="0.4")
    ax.set_xscale("log"); ax.set_xticks(bs); ax.set_xticklabels([f"{x:g}" for x in bs]); ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("基线 b（米）"); ax.set_ylabel(f"SNR（{hours:g} 小时）"); ax.legend(loc="upper left")
    C.show(fig)
    best = bs[np.argmax(snrs)]
    st.markdown(f"在这组条件下，SNR 最高的基线约为 **{best:g} m**（上面只计算了图中这几个基线）。"
                f"粗略估计：让行星落在第一条亮纹上的基线 b ≈ λ/(2θ)，在 10 µm 处约为 **{10e-6 / (2 * sep_mas * C.MAS):.0f} m**。")

    st.subheader("挑战任务")
    st.markdown("""
    1. 选择**红矮星**、10 pc。用 14.5 m 的基线能看到它的宜居带行星吗？要多长的基线？
    2. 选择**类太阳恒星**、1 倍尘埃。最远能到多少 pc，仍可在 10 小时内达到 SNR = 5？
    3. 把尘埃量从 1 调到 30，需要的观测时间变成多少倍？
    4. 对于一颗 15 pc 外的类太阳恒星，如果只有 10 小时，你会选择什么基线？
    """)
    C.think("红矮星的宜居带很近（十几 mas），为什么在合适的基线下反而容易观测？",
            "红矮星本身很暗、看起来很小，漏光少；而宜居带行星的温度和大小和地球一样，发出的红外光一样多。"
            "只要基线足够长（几十米），让行星落在亮纹上，SNR 反而更高。")
    C.think("这个实验室假设了一台\"完美\"的仪器。真实的仪器还要考虑什么？",
            "例如四路光的强度能否做到完全相等、光程能否控制到纳米级、望远镜指向是否稳定。这些都会让恒星多漏光，是更深入的课题。")


# 章节导航与渲染函数一一对应；计算和图件仍放在独立模块中。
SECTIONS = (
    ('导读：为什么难，怎样看见行星', '一套给大一同学的互动讲义 · 在本页选择章节，循序学习', render_introduction),
    ('光的干涉', '两列波叠在一起，会变亮还是变暗？', render_interference),
    ('两台望远镜消零', '让恒星的光自己抵消，行星的光留下来', render_two_telescopes),
    ('恒星的漏光', '恒星不是一个点', render_stellar_leakage),
    ('四台望远镜与斩波', '两路输出相减，去掉对称的背景', render_phase_chopping),
    ('旋转阵列', '转起来，行星的位置变成一串"指纹"', render_rotation),
    ('光子噪声与信噪比', '光是一颗一颗到来的', render_photon_noise),
    ('找到行星', '拿"指纹库"去比对', render_planet_search),
    ('参数实验室', '自己设计望远镜，挑选观测目标', render_parameter_lab),
)


def section_label(index):
    return f"{index}: {SECTIONS[index][0]}"


def main():
    C.page("看见另一颗地球：消零干涉入门", "给大一同学的互动讲义 · 从光的干涉，到找到一颗行星")
    st.markdown("先选一个章节，再拖动滑块观察变化，最后点开「想一想」检验自己。")
    section = st.radio(
        "选择章节：", range(len(SECTIONS)), format_func=section_label,
        key="selected_section",
    )
    st.divider()
    _, subtitle, render = SECTIONS[section]
    st.header(section_label(section))
    if section:
        st.caption(subtitle)
    render()
    C.save_controls(section)


if __name__ == "__main__":
    main()
