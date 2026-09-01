---
# Metadata used by both Quarto and vanilla Pandoc.
title: "Electrodynamics from an Action to the Beginning of QED"
lang: en
toc: true
toc-depth: 3

# Quarto-only render recipes. Vanilla Pandoc ignores this `format` map and uses
# the four explicit defaults files under ../config/ through the root Makefile.
format:
  html:
    output-file: math.html
    html-math-method: mathml
    css: assets/fonts.css
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    code-copy: true
    code-overflow: wrap
    email-obfuscation: javascript
    format-links:
      - text: MathJax 4 HTML
        href: math-mathjax.html
        icon: filetype-html
      - pdf
      - typst
  mathjax4-html:
    output-file: math-mathjax.html
    css: assets/fonts.css
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    code-copy: true
    code-overflow: wrap
    email-obfuscation: javascript
    format-links:
      - text: MathML HTML
        href: math.html
        icon: filetype-html
      - pdf
      - typst
  pdf:
    output-file: math-lualatex.pdf
    pdf-engine: lualatex
    latex-tinytex: false
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    monofont: JetBrains Mono
    babelfonts:
      greek: Gentium
      hebrew: Ezra SIL
      # Font filename stem: OSFONTDIR finds the Regular and Bold files.
      chinese-hant: NotoSansCJKtc
  typst:
    output-file: math-typst.pdf
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

## The unifying idea

Classical electrodynamics and quantum electrodynamics are built from the same electromagnetic variable: the four-potential $A_\mu$. Its derivatives form the electromagnetic field tensor $F_{\mu\nu}$, and a gauge symmetry explains why different potentials can represent the same electric and magnetic fields.

The shortest route through the subject is therefore

$$\text{action}
\longrightarrow A_\mu
\longrightarrow F_{\mu\nu}
\longrightarrow \text{gauge symmetry}
\longrightarrow \text{field equations}.$$

In classical electrodynamics, the electric current is usually prescribed from outside the theory. In the classical field equations underlying QED, the source is instead a dynamical Dirac field describing charged matter. This single change produces the coupled Maxwell--Dirac equations and carries us to the point where genuinely quantum machinery must begin.

## Conventions

We use natural units,

$$\hbar=c=\epsilon_0=\mu_0=1,$$

and the Minkowski metric

$$\eta_{\mu\nu}=\operatorname{diag}(+1,-1,-1,-1).$$

Greek indices run over spacetime coordinates $0,1,2,3$, repeated indices are summed, and $\partial_\mu\equiv \partial/\partial x^\mu$. The four-potential and four-current are

$$A^\mu=(\phi,\mathbf A),
\qquad
J^\mu=(\rho,\mathbf J).$$

Other sign conventions are common. They may change the appearance of intermediate formulas but not the physics.

# Part I: Classical electrodynamics

## 1. Begin with the action

An action assigns a number to an entire history of a physical system. The actual history is selected by the stationary-action principle, $\delta S=0$. For the electromagnetic field coupled to a prescribed current $J^\mu$, take

$$S[A]=\int d^4x\,\mathcal L,
\qquad
\mathcal L=-\frac14 F_{\mu\nu}F^{\mu\nu}-J^\mu A_\mu.$$

This compact expression contains the field dynamics and its coupling to matter. The first term is the electromagnetic field's own Lagrangian density. The second says that a current acts as a source for the potential.

At this stage, $J^\mu$ is not determined by the electromagnetic action. It might describe a known distribution of charges and currents in a wire, antenna, or beam. Treating the matter that produces this current dynamically will be the main step toward QED.

## 2. The four-potential and the field tensor

The electromagnetic field tensor is defined in terms of the potential by

$$\boxed{F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu.}$$

It is antisymmetric: $F_{\mu\nu}=-F_{\nu\mu}$. An antisymmetric $4\times4$ tensor has six independent components, exactly the number contained in the three components of $\mathbf E$ and the three components of $\mathbf B$.

In three-vector language, the definition of $F_{\mu\nu}$ is equivalent to

$$\boxed{
\mathbf E=-\boldsymbol\nabla\phi-\frac{\partial\mathbf A}{\partial t},
\qquad
\mathbf B=\boldsymbol\nabla\times\mathbf A.
}$$

Thus $A_\mu$ is one relativistic object that packages the scalar and vector potentials, while $F_{\mu\nu}$ packages the observable electric and magnetic fields.

## 3. Gauge invariance

The potential is not unique. For any sufficiently smooth scalar function $\chi(x)$, the transformation

$$\boxed{A_\mu\longrightarrow A'_\mu=A_\mu+\partial_\mu\chi}$$

leaves the field tensor unchanged:

$$F'_{\mu\nu}
=\partial_\mu(A_\nu+\partial_\nu\chi)
-\partial_\nu(A_\mu+\partial_\mu\chi)
=F_{\mu\nu}.$$

The extra terms cancel because ordinary partial derivatives commute. Consequently, $\mathbf E$ and $\mathbf B$ are unchanged as well. A gauge transformation therefore changes the mathematical description but not the physical electromagnetic field.

The free-field term in the action is automatically gauge invariant because it depends only on $F_{\mu\nu}$. The source term changes, up to a boundary term, by

$$\Delta S_{\mathrm{source}}
=-\int d^4x\,J^\mu\partial_\mu\chi
=\int d^4x\,\chi\,\partial_\mu J^\mu.$$

It is gauge invariant when the current is conserved:

$$\boxed{\partial_\mu J^\mu=0}
\qquad\Longleftrightarrow\qquad
\frac{\partial\rho}{\partial t}+\boldsymbol\nabla\cdot\mathbf J=0.$$

Gauge freedom is a redundancy, but a useful one. A gauge condition such as the Lorenz gauge, $\partial_\mu A^\mu=0$, can simplify calculations without changing the measurable fields.

## 4. Maxwell's sourced equations from stationary action

Vary the potential by $A_\nu\to A_\nu+\delta A_\nu$, while holding the prescribed current fixed. Since

$$\delta F_{\mu\nu}
=\partial_\mu\delta A_\nu-\partial_\nu\delta A_\mu,$$

the variation of the action is, after integrating by parts and discarding a boundary term,

$$\delta S
=\int d^4x\,
\left(\partial_\mu F^{\mu\nu}-J^\nu\right)\delta A_\nu.$$

Stationary action for arbitrary $\delta A_\nu$ gives

$$\boxed{\partial_\mu F^{\mu\nu}=J^\nu.}$$

This one covariant equation contains Gauss's law and the Ampère--Maxwell law:

$$\boldsymbol\nabla\cdot\mathbf E=\rho,
\qquad
\boldsymbol\nabla\times\mathbf B
-\frac{\partial\mathbf E}{\partial t}
=\mathbf J.$$

Taking $\partial_\nu$ of the covariant equation gives $\partial_\nu J^\nu=0$, because the contraction of the symmetric derivative $\partial_\nu\partial_\mu$ with the antisymmetric tensor $F^{\mu\nu}$ vanishes. Charge conservation is therefore required by the structure of Maxwell's equation as well as by gauge invariance of the source coupling.

## 5. Maxwell's homogeneous equations from the definition of $F_{\mu\nu}$

The remaining two Maxwell equations do not arise as independent Euler--Lagrange equations for $A_\mu$. They follow identically from the way $F_{\mu\nu}$ was defined:

$$\boxed{
\partial_\lambda F_{\mu\nu}
+\partial_\mu F_{\nu\lambda}
+\partial_\nu F_{\lambda\mu}=0.
}$$

This is the Bianchi identity. In three-vector notation it gives

$$\boldsymbol\nabla\cdot\mathbf B=0,
\qquad
\boldsymbol\nabla\times\mathbf E
+\frac{\partial\mathbf B}{\partial t}=0.$$

The split is conceptually useful. Two Maxwell equations are equations of motion obtained from the action; the other two are identities guaranteed by expressing the fields in terms of a potential.

## 6. The classical structure in one view

The classical theory can now be read as a short logical chain:

1.  Choose $A_\mu$ as the electromagnetic variable.
2.  Build the gauge-invariant tensor $F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu$.
3.  Form the simplest Lorentz- and gauge-invariant field term, $-\tfrac14F_{\mu\nu}F^{\mu\nu}$.
4.  Couple the potential to a conserved external current through $-J^\mu A_\mu$.
5.  Vary the action to obtain $\partial_\mu F^{\mu\nu}=J^\nu$; obtain the other Maxwell equations from the Bianchi identity.

This completes the action-based formulation of classical electromagnetism with a prescribed source.

# Part II: The classical field equations underlying QED

## 7. Replace the prescribed current by a matter field

To make the source dynamical, introduce a Dirac spinor field $\psi(x)$. It describes charged spin-$\tfrac12$ matter such as electrons at the relativistic field level. Define its Dirac adjoint by

$$\bar\psi\equiv\psi^\dagger\gamma^0,$$

where the gamma matrices obey

$$\{\gamma^\mu,\gamma^\nu\}=2\eta^{\mu\nu}.$$

The free Dirac Lagrangian density is

$$\mathcal L_{\mathrm D,free}
=\bar\psi(i\gamma^\mu\partial_\mu-m)\psi.$$

The fields $\psi$ and $A_\mu$ will now be varied independently. Matter produces the electromagnetic field, and the electromagnetic field acts back on matter.

## 8. From global phase symmetry to local gauge symmetry

The free Dirac Lagrangian is invariant under a constant phase change,

$$\psi\longrightarrow e^{-ie\chi}\psi,$$

when $\chi$ is constant. This is a global $U(1)$ symmetry. Here $e$ is the signed electric charge carried by the field; for an electron, $e<0$. Keeping $e$ signed makes the formulas below independent of a separate charge-sign convention.

If $\chi$ is allowed to depend on spacetime, differentiating $\psi$ also differentiates the phase. The ordinary derivative then fails to transform in the same way as $\psi$. To restore a local symmetry, introduce the covariant derivative

$$\boxed{D_\mu\equiv\partial_\mu+ieA_\mu.}$$

Under the simultaneous transformations

$$\boxed{
\psi\longrightarrow\psi'=e^{-ie\chi(x)}\psi,
\qquad
A_\mu\longrightarrow A'_\mu=A_\mu+\partial_\mu\chi,
}$$

the covariant derivative transforms like the matter field itself:

$$D'_\mu\psi'=e^{-ie\chi(x)}D_\mu\psi.$$

This is the local $U(1)$ gauge symmetry. The same gauge transformation of $A_\mu$ that appeared in classical electromagnetism is now tied to a spacetime-dependent phase transformation of charged matter.

## 9. The QED Lagrangian

The locally gauge-invariant Lagrangian density is

$$\boxed{
\mathcal L_{\mathrm{QED}}
=-\frac14F_{\mu\nu}F^{\mu\nu}
+\bar\psi(i\gamma^\mu D_\mu-m)\psi.
}$$

Expanding the covariant derivative makes its three pieces visible:

$$\mathcal L_{\mathrm{QED}}
=\underbrace{-\frac14F_{\mu\nu}F^{\mu\nu}}_{\text{electromagnetic field}}
+\underbrace{\bar\psi(i\gamma^\mu\partial_\mu-m)\psi}_{\text{Dirac matter}}
-\underbrace{e\bar\psi\gamma^\mu\psi\,A_\mu}_{\text{interaction}}.$$

Define the matter current

$$\boxed{j^\mu=e\bar\psi\gamma^\mu\psi.}$$

The interaction is then $-j^\mu A_\mu$, exactly the same form as the classical source coupling $-J^\mu A_\mu$. The difference is that $j^\mu$ is made from a field whose dynamics are included in the same action.

## 10. The coupled Maxwell--Dirac equations

Varying the QED action with respect to $\bar\psi$ gives the Dirac equation in an electromagnetic field:

$$\boxed{(i\gamma^\mu D_\mu-m)\psi=0.}$$

Varying with respect to $A_\nu$ gives Maxwell's sourced equation:

$$\boxed{
\partial_\mu F^{\mu\nu}=j^\nu
=e\bar\psi\gamma^\nu\psi.
}$$

As before, the definition of $F_{\mu\nu}$ supplies the Bianchi identity,

$$\boxed{
\partial_\lambda F_{\mu\nu}
+\partial_\mu F_{\nu\lambda}
+\partial_\nu F_{\lambda\mu}=0.
}$$

These are the coupled Maxwell--Dirac equations. The Dirac field generates a current that sources $A_\mu$, while $A_\mu$, through $D_\mu$, influences the evolution of the Dirac field. They display the mutual interaction in a closed set of classical field equations.

## 11. Conserved current

The global subgroup of the $U(1)$ phase symmetry leads, through Noether's theorem, to the conserved current $j^\mu$. Using the Dirac equation and its adjoint gives

$$\boxed{\partial_\mu j^\mu=0.}$$

The associated conserved charge is

$$Q=\int d^3x\,j^0.$$

The same conservation law is also required by the Maxwell equation: applying $\partial_\nu$ to $\partial_\mu F^{\mu\nu}=j^\nu$ again makes the left-hand side vanish identically. Gauge structure, equations of motion, and charge conservation fit together rather than appearing as separate assumptions.

## 12. The classical-to-QED parallel

| Classical electrodynamics with an external source | Maxwell--Dirac theory underlying QED                           |
|---------------------------------------------------|----------------------------------------------------------------|
| Electromagnetic variable $A_\mu$                  | The same variable $A_\mu$                                      |
| Field tensor $F_{\mu\nu}$                         | The same field tensor $F_{\mu\nu}$                             |
| Gauge change $A_\mu\to A_\mu+\partial_\mu\chi$    | The same change, accompanied by $\psi\to e^{-ie\chi}\psi$      |
| Prescribed conserved current $J^\mu$              | Dynamical conserved current $j^\mu=e\bar\psi\gamma^\mu\psi$    |
| Coupling $-J^\mu A_\mu$                           | Coupling $-j^\mu A_\mu$ generated by $D_\mu$                   |
| $\partial_\mu F^{\mu\nu}=J^\nu$                   | $\partial_\mu F^{\mu\nu}=j^\nu$, coupled to the Dirac equation |

This parallel is the central conceptual bridge. Local phase symmetry does not merely tolerate the electromagnetic potential; it tells us how the potential must enter the matter equation through $D_\mu$. Conversely, the resulting interaction identifies the Dirac field's conserved current as the source of the electromagnetic field.

# The beginning of QED

The expression conventionally called the QED Lagrangian has now been introduced, but everything done so far can still be read as a classical theory of coupled fields. The spinor nature of $\psi$ anticipates quantum physics, yet writing the Lagrangian and deriving the Maxwell--Dirac equations does not by itself quantize either field.

Genuine quantum electrodynamics begins when $A_\mu$ and $\psi$ are treated as quantum fields and the theory is given a quantum interpretation. Proceeding further requires additional machinery---for example canonical quantization or path integrals, quantum states and Fock space, and usually perturbation theory. Those ideas are important, but they no longer have a simple one-to-one parallel with the classical derivation above.

This is therefore the natural stopping point for an undergraduate first pass:

$$\boxed{
\text{The QED Lagrangian is the bridge; quantizing its fields is the beginning of QED.}
}$$

## Final summary

Both theories are organized by the same action-based language. The potential $A_\mu$ builds the gauge-invariant field strength $F_{\mu\nu}$; varying the electromagnetic action gives the sourced Maxwell equations; and the definition of $F_{\mu\nu}$ gives the homogeneous equations. In the QED Lagrangian, a local $U(1)$ phase symmetry introduces the covariant derivative and fixes the form of the electromagnetic interaction. The external classical source is replaced by the conserved current of a dynamical Dirac field, producing the coupled Maxwell--Dirac equations. Quantization is the next chapter.
