import numpy as np
import streamlit as st
import app_common as C
import schematics as S

C.page("2  两台望远镜消零", "让恒星的光自己抵消，行星的光留下来")
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
    b = st.slider("基线 b（米）", 2.0, 40.0, 14.5, 0.5)
    lam = st.slider("波长 λ（微米）", 4.0, 18.0, 10.0, 0.5)
    pmas = st.slider("行星离恒星的角距离（mas）", 10, 250, 100, 5)
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
