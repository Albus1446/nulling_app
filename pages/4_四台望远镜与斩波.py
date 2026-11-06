import numpy as np
import streamlit as st
import app_common as C
import schematics as S
import core as nl

C.page("4  四台望远镜与斩波", "两路输出相减，去掉对称的背景")
C.goal("四台望远镜怎样组合成两路输出；为什么\"相减\"能去掉恒星周围对称的尘埃光，而留下行星。")

st.header("一个新麻烦：尘埃")
st.markdown("""
恒星周围常常有一圈温暖的**尘埃**（叫做外黄道光，exozodi），它在红外波段发光，总亮度可以是行星的几百倍。
两台望远镜的"百叶窗"是**左右对称**的：行星在右边能透过，左边对称位置上的尘埃也能透过——分不清哪个是行星。

解决办法是用**四台望远镜**，造出**两路互为镜像**的输出，再把它们**相减**。
""")
C.show(S.fig_xarray_combiner())
st.markdown("""
- 四台望远镜排成长方形。上边两台（1、4）为一对，下边两台（2、3）为一对，**每对先各自消掉恒星**（就是上一页的方法）。
- 再把两对剩下的光**交叉混合**（其中一路错开 1/4 个波长），得到**输出 3** 和 **输出 4**。
- 这两路输出的"百叶窗"图案**上下互为镜像**。把两路相减，得到**斩波信号**（chop）。
""")

st.header("动手：看看三张透射图")
c1, c2 = st.columns([1, 3])
with c1:
    lam = st.slider("波长 λ（微米）", 4.0, 18.0, 10.0, 0.5, key="lam4")
    q = st.slider("长方形的长宽比 q", 2.0, 8.0, 6.0, 0.5)
    ring = st.toggle("显示一圈对称的尘埃环", value=True)
    ring_r = st.slider("尘埃环半径（mas）", 20, 200, 60, 5, disabled=not ring)
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
        "不是。相减只去掉了尘埃光的**平均值**，但尘埃光子的随机起伏（噪声）还在，而且尘埃越亮噪声越大。第 6 页会讲。")
