# Okada's Conjectures 9.63, 9.64 and 9.66

This package proves Conjectures 9.63 and 9.64 and specific slices of Conjecture 9.66 in
arXiv:2003.02112v2, Section 9.8.3, pp. 96–97.

## Mathematical content

For natural tuples `0 <= a1 < ... < a_mu <= b1 < ... < b_mu`, let

`P(q) = product_i [b_i choose a_i]_q - product_i [b_i choose a_(mu+1-i)]_q`.

- At every width `mu >= 3`, the nonzero coefficient list of `P` is not a
  palindrome: its second coefficient exceeds its penultimate coefficient by one.
- At width two, that list is palindromic exactly when
  `min(a2-a1, b2-b1) = 1`.
- At fixed `b2 = lambda >= 2`, the non-almost-palindromic proportion is
  `(lambda-2)(lambda-3)/(lambda*(lambda+1))`. It increases strictly from
  `lambda = 3` and tends to one.

The exact posing source is
https://arxiv.org/abs/2003.02112v2, Conjectures 9.63 and 9.64, pp. 96–97.
The three preceding statements have degree shift zero and unit weights and
base shifts. They also hold at every constant positive integral base shift,
with the base-shift factors in Definition 9.4 included explicitly.

Further written consequences in Section 3 are:

- For every width at least two and constant integral weight at least two,
  the degree-shift-zero determinant is not almost palindromic.
- Example 9.65 extends to a family: for `a=(0,1)`, `b=(1,n)`, `n>=4`, and degree
  shift one, the determinant is almost palindromic exactly at base shift one.
  At `n=4` the two coefficient lists, including zeros, are
  `[1,0,1,1]` and `[1,1,2,4,4,5,6,6,5,5,4,2,2,1]` for base shifts one and two.
- If `G` is the direct-minus-reversed degree gap, symmetry under replacing
  the degree shift `e` by `G-e` proves the classification also at `e=G`;
  at even `G` the midpoint `e=G/2` is always reciprocal. For widths at least
  three, the determinants at `e=1` and `e=G-1` are not almost palindromic.
  This proves these slices of Conjecture 9.66, but not its remaining cases.
- At fixed final upper index `lambda`, the count at width `mu>=3` is
  `binomial(lambda+1,2*mu-1)`; all these determinants are non-almost-palindromic.

These are the historically numbered v2 statements. The author's manuscript
dated November 2, 2026 reorganizes the conjectures; its Section 11 concerns
unimodality and log-concavity, which are not established in general here.

## Files and PDF build

- `note.tex`: complete mathematical text, references, and license statement.
- `metadata.json`: bibliographic identity, creators, problem ID, and license.
- `verify.py`: finite integer-polynomial checks; Python 3.9 or later, standard library only.

Build with Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a LaTeX installation containing the standard packages
listed in `note.tex`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

References are included directly in `note.tex`; BibTeX and external figures
are unnecessary. Font and PDF metadata differences may change PDF bytes
between TeX installations without changing the mathematical text.

## Finite checks

```sh
python3 verify.py > checked-results.json
```

The default computation compares 66 Gaussian polynomials with subset
enumeration, checks all 1,486 fitting pairs of widths three through six with
maximum upper index ten, and checks all 4,845 width-two pairs with final upper
index at most eighteen. It verifies the endpoint formulas, the width-two
classification, the polynomial identity for a unit tuple gap, and the
counts for each final upper index. The all-parameter proofs are in `note.tex`.
Additional checks use all 99 fitting tuples of widths two through four and
maximum upper index six, at constant base shifts one through three (297 cases),
weights two and three (594 cases), and every degree shift from zero through
the degree gap (1,497 reciprocity comparisons). The counterexample family is
checked for `4<=n<=12`, base shifts one through four (36 cases), and 66
explicit constant-sequence unimodal examples are checked.

The output is deterministic JSON and records all finite ranges and case counts.

## Lean statement coverage

The declaration `D5.S3.Combinatorics.GaussianQuotient.OkadaPreMergedNonPalindromic.result`
in the following pinned file proves the non-almost-palindromicity statement
for every natural width at least three and all fitting tuples:

https://github.com/the-omega-institute/trureturing/blob/0b3d3a2945e69db04f778eb6fea96ee6a8030a45/D5/S3/Combinatorics/GaussianQuotient/OkadaPreMergedNonPalindromic.lean

Its `preMerged` is the displayed polynomial, and `IsAlmostPalindromic`
tests the coefficient list on support sorted by increasing degree.
The lemmas `low_end` and `high_end` supply the endpoint formulas.
The width-two classification and counting formula have written proofs in
Section 2. All constant-base, constant-weight, degree-shift and counterexample
conclusions have written proofs in Section 3 and the finite checks specified above;
they are not additional conclusions of the pinned Lean declaration.

## Creators and license

1. Haobo Ma — ChronoAI Pte Ltd, Singapore.
2. Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

CC BY 4.0 (`cc-by-4.0`):
https://creativecommons.org/licenses/by/4.0/.
