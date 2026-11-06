import numpy as np
import streamlit as st
import app_common as C
import schematics as S
import core as nl

C.page("3  恒星的漏光", "恒星不是一个点")
C.goal("为什么恒星不能被完全抵消；漏光（零深）和哪些因素有关；漏掉的星光和行星比谁亮。")

st.markdown("""
上一页假设恒星是一个点。实际上恒星是一个小圆盘：太阳放到 10 秒差距外，看起来的半径约 **0.47 mas**。
圆盘中心正好在黑条上，但边缘偏离了一点点，就会**漏过一点光**。漏过的比例叫做**零深**（null depth）。
""")

c1, c2 = st.columns([1, 2.6])
with c1:
    d = st.slider("恒星距离（秒差距 pc）", 3.0, 20.0, 10.0, 0.5)
    b = st.slider("基线 b（米）", 4.0, 40.0, 14.5, 0.5, key="b3")
    lam = st.slider("波长 λ（微米）", 4.0, 18.0, 10.0, 0.5, key="lam3")
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
**消零把恒星压暗了十万倍，但漏光依然比行星亮。** 后面几页的"斩波""旋转"和"长时间积分"，就是为了从这些漏光中把行星挑出来。
""")

st.success("**小结**：恒星的大小决定了消零的极限。基线越长、波长越短、恒星越近，漏光越多。")
C.think("把基线从 14.5 m 加倍到 29 m，零深变为多少倍？",
        "零深 ∝ b²，变为 4 倍。所以基线不是越长越好：长基线有利于分开近处的行星，但漏光更多。")
C.think("为什么近处的恒星漏光更多？",
        "距离减半，恒星看起来的角半径 ρ 加倍，零深 ∝ ρ²，变为 4 倍。不过近处的行星也更亮，所以近处的目标总体仍然更容易观测。")
