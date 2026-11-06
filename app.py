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
    这次，我们来做一件看起来很难的事：从耀眼的恒星旁边，找出一颗像地球一样暗淡的行星。

    先别急着看公式。我们会先试一试普通望远镜，再用光的干涉压低恒星光，最后从带噪声的数据中找出行星的位置。
    你可以边读边调参数。每次先猜一猜图会怎样变，再动手验证。
    """)

    st.header("难在哪里：在灯塔旁边找一只萤火虫")
    C.show(S.fig_contrast_cartoon())
    st.markdown("""
    想象一下：远处有一座灯塔，旁边飞着一只萤火虫。我们要看清的，就是那只萤火虫。

    在这里，灯塔是恒星，萤火虫是行星。以 10 微米的红外光为例，类地行星大约比类太阳恒星暗 **1000 万倍**。
    把它们放到 10 秒差距外，两者在天空上只隔着 **0.1 角秒**。也就是说，我们既要分开两个很近的光点，又要看见其中很暗的那个。
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
    **看一看：** 恒星和行星原本都是很小的光点，经过望远镜后却各自变成了有宽度的光斑。这是光的**衍射**造成的。

    **试试看：** 先把口径从 4 米调到 40 米，保持波长不变。光斑变窄了吗？再找一找 100 mas 处的行星曲线：它有没有高过恒星光斑的尾部？
    这里的两条曲线画的是各自的亮度；在真实图像里，我们收到的是它们叠加后的光。
    """)
    C.think("把口径调到 40 米，行星的像能露出来吗？",
            "不能。口径变大，光斑变窄，100 mas 处恒星的光确实暗了很多，但仍然比行星亮几千到几万倍。"
            "单靠一台更大的望远镜解决不了 1000 万倍的亮度差。")

    st.header("办法：让恒星的光自己抵消掉")
    st.markdown("""
    换个思路：如果能先把灯塔的光压暗，萤火虫会不会更容易看见？

    我们要用的办法叫**消零干涉**。让两束恒星光以合适的相位叠加，它们就能相互抵消。
    行星稍微偏离视线中心，它的光经过的路程不同，就不会在同一个条件下完全抵消。

    接下来，我们按这个顺序试一试：

    1. 叠加两列波，看看什么时候会变暗。
    2. 把两台望远镜放到不同位置，留下行星的光。
    3. 加入恒星的大小和尘埃，看看现实中会遇到什么麻烦。
    4. 让阵列旋转，记录行星的信号，再从噪声里找出它。

    准备好了，就在上面的列表中选择 **1：光的干涉**。你只需要用到正弦函数、角度和平方根。
    """)
    st.caption("单位提示：1 角秒（″）= 1/3600 度；1 mas（毫角秒）= 0.001 角秒。1 微米（µm）= 10⁻⁶ 米。")


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
    **记住这一点：** 同样强的两束光，在相位相反时可以抵消。下一节，我们用两台望远镜来试试这件事。
    """)
    C.think("光程差为 5 µm，对 10 µm 的光会抵消，对 5 µm 的光呢？",
            "对 5 µm 的光，5 µm 正好是 1 个完整波长，波峰又对上了波峰，变成相长干涉。"
            "**同一个光程差，对不同波长的光效果不同**——这就是后面透射图随波长变化的原因。")
    C.think("如果两列波振幅不一样（比如一个是 1，一个是 0.9），还能完全抵消吗？",
            "不能完全抵消，最暗时还剩 1 − 0.9 = 0.1 的振幅，亮度是 0.01。所以真实仪器要求两路光的强度非常接近。")


def render_two_telescopes():
    C.goal("""
    改变两台望远镜之间的距离，试着让恒星变暗、让行星通过。
    """)

    st.header("原理图")
    C.show(S.fig_bracewell_setup())
    st.markdown("""
    现在把两台望远镜一起对准恒星。它们之间的距离叫做**基线**，记作 b。

    先看左图。来自视线中心的恒星光同时到达两台望远镜。我们让其中一路多出半个波长的相位，再把两路合在一起。
    这样，两路恒星光在一个出口相互抵消。我们把这个出口叫做**暗输出**。

    再看右图。行星偏离中心一个小角度 θ，它的光到达两台望远镜时有一小段路程差，约为 b·θ。
    原来为恒星设置的相消条件，对行星不再刚好成立。所以暗输出里还能留下行星光。

    注意：另一侧的行星会让哪一路先到达发生变化，但下面的透过比例不受这个正负号影响。
    """)
    st.latex(r"T(\theta) \;=\; \sin^2\!\left(\pi\,\frac{b\,\theta}{\lambda}\right)")
    st.markdown("""
    这里的 T 表示透过比例。T = 0 表示被挡住，T = 1 表示完全通过。恒星位于 θ = 0，正好落在零点。
    """)

    st.header("动手：天空上的\"百叶窗\"")
    st.markdown("""
    把天空各个位置的透过比例画出来，就得到了明暗相间的条纹，很像一扇百叶窗。中心的恒星落在暗条上。

    **试试看：** 保持波长 10 微米、行星角距 100 mas，先把基线调到 2 米，再慢慢增大。
    看着蓝色的行星标记：它什么时候落到亮条上？继续增大基线，透过比例还会一直增加吗？
    """)
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

    st.success("""
    **你会看到：** 基线变长时，条纹变密。行星会交替经过亮条和暗条，所以基线需要配合目标的角距离来选择。
    """)
    C.think("基线调得特别短（比如 2 米），会怎样？",
            "条纹变得很宽，行星（100 mas）落在中间那条黑条里，和恒星一起被挡掉了。基线太短，分不开恒星和行星。")
    C.think("同一个基线，换成短波长（4 µm）和长波长（18 µm），哪个条纹更密？",
            "短波长更密。条纹间距 = λ/b，波长越短，间距越小。所以同一颗行星在不同波长下会落在不同的条纹上。")


def render_stellar_leakage():
    C.goal("""
    放大恒星所在的暗条，看看恒星为什么还会漏光。
    """)

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


def render_phase_chopping():
    C.goal("""
    比较两路输出，看看相减后尘埃和行星各自留下多少信号。
    """)

    st.header("一个新麻烦：尘埃")
    st.markdown("""
    压暗恒星之后，我们又遇到了一个麻烦：恒星周围的尘埃也会发出红外光。这部分光叫做**外黄道光**。
    如果尘埃分布在恒星两侧，两台望远镜的对称条纹会同时接收到它们的光。

    能不能让对称的背景相互抵消，同时留下偏在一边的行星？下面我们换成四台望远镜，得到两路输出，再试着把它们相减。
    """)
    C.show(S.fig_xarray_combiner())
    st.markdown("""
    沿着图中的箭头看一遍光的去向：

    1. 上边两台望远镜组成一对，下边两台组成另一对。每一对先用上一节的方法压暗恒星。
    2. 把两对的暗输出再次混合，并引入四分之一个波长的相位差，得到输出 3 和输出 4。
    3. 用输出 3 减去输出 4。这里把这个差值叫做**斩波信号**。

    先不用记住合束器的每个细节。接下来最值得比较的是：同一圈尘埃，在两路输出里是不是一样亮？
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
        st.markdown("""
    **比较一下：** 尘埃环在两路输出中的平均透过比例接近相同，相减后接近零。行星在两路中的透过比例不同，差值就保留下来。
    """)

    st.markdown("""
    **试试看：** 打开「显示一圈对称的尘埃环」，改变尘埃环半径，再比较两路数值。
    然后改变波长，看看相减后的尘埃信号是否仍接近零。

    右边的图用深蓝色表示正信号，棕色表示负信号。关于中心对称的两个位置，信号大小相同、符号相反。
    一圈对称的尘埃把这些位置都占满了，正负贡献就会抵消。

    这里去掉的是背景的**平均信号**。背景光子的随机起伏还在，第 6 节会接着看它。
    """)
    st.success("""
    **这一步做到了什么？** 两路输出相减后，对称背景的平均信号接近零，偏离中心的行星仍可能留下信号。
    """)
    C.think("如果尘埃盘有一团只在一侧的\"疙瘩\"，斩波后会怎样？",
            "疙瘩不对称，斩波后会留下信号，看起来像一颗行星。这是真实观测中需要小心的\"假行星\"。")
    C.think("斩波去掉了尘埃的光，是不是尘埃就完全没有影响了？",
            "不是。相减只去掉了尘埃光的**平均值**，但尘埃光子的随机起伏（噪声）还在，而且尘埃越亮噪声越大。第 6 节会讲。")


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
    st.markdown("""
    下面的两条曲线来自两个候选位置。先把方位角差和角距离差都设成 0，让它们完全重合。

    **再试一次：** 只把第二颗的方位角增加 10°，其他参数不变。两条曲线还一样吗？再把角距离改大一点，比较变化。
    第 7 节就会用这样的曲线去匹配观测数据。
    """)
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
        N = st.select_slider("平均每次接到的光子数 N", options=[10, 30, 100, 300, 1000, 3000, 10000], value=C.control_value('lesson_6_N', 100), key='lesson_6_N')
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

    st.success("""
    **这次实验告诉我们：** 相关图利用信号形状来寻找位置。提高 SNR 通常能让结果更稳定，但定位误差还受阵列、波长和重建方法影响。100 次模拟可以帮助你比较方案，不能当作所有观测的保证。
    """)
    C.think("为什么关掉加权后经常找错？",
            "短波长的数据噪声最大、行星信号又最弱。不加权时，这些噪声和长波长的有用信号同等对待，把相关图搅乱了。")
    C.think("找到位置以后，还能得到什么？",
            "在找到的位置上，逐个波长比较数据和指纹的幅度，就能得到行星在每个波长的亮度——也就是行星的**光谱**，可以用来研究它的温度和大气。")


def render_parameter_lab():
    C.goal("""
    自己选一个目标，找一组更容易发现宜居带行星的观测参数。
    """)

    st.markdown("""
    最后，把前面的想法放在一起，自己设计一次观测。

    这里假设每颗恒星旁边都有一颗地球大小的行星，放在接收恒星能量与地球相近的位置。
    这个位置位于我们粗略估计的**宜居带**；模型使用约 255 K 的行星有效温度，并不表示那里一定适合生命。

    **先试试看：** 保持类太阳恒星、10 pc 和 1 倍尘埃不变，只改变基线。看下面的曲线，哪个基线附近的 SNR 较高？
    接着只改距离，或者只改尘埃量，再比较曲线。一次只改一个条件，更容易看清它的作用。
    """)
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
    准备好后，选一个小任务试试。先做预测，再调参数，最后用图和数值解释你的选择。

    1. 把恒星换成**红矮星**，距离保持 10 pc。14.5 米基线合适吗？试着寻找一个 SNR 更高的基线。
    2. 换回**类太阳恒星**和 1 倍尘埃。逐渐增加距离：在 10 小时内，哪些距离还能达到这里的 SNR = 5 参考线？
    3. 回到 10 pc，把尘埃量从 1 调到 30。达到参考线需要的时间怎样变？
    4. 如果目标在 15 pc 外，而你只有 10 小时，试着选一条基线，并说明理由。

    这些结果来自一台理想仪器。先用它看清趋势，再想想真实仪器还会增加哪些限制。
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
    C.page("看见另一颗地球：消零干涉入门", "一起动手：压暗恒星，从噪声里找出行星")
    st.markdown("先猜一猜，再调一调。观察图怎样变化，需要时点开「想一想」查看提示。")
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
