from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule


def and_(left, right):
    return ConjunctionFormula(left, right)


def not_(formula):
    return NegationFormula(formula)


p1 = Predicate("p1", 1)
q1 = Predicate("q1", 1)
r1 = Predicate("r1", 1)
s1 = Predicate("s1", 1)
t1 = Predicate("t1", 1)

p2 = Predicate("p2", 2)
q2 = Predicate("q2", 2)
r2 = Predicate("r2", 2)

x = Variable("x")
y = Variable("y")
z = Variable("z")

a = Constant("a")

px = Atom(p1, x)
py = Atom(p1, y)
qx = Atom(q1, x)
rx = Atom(r1, x)
sx = Atom(s1, x)
tx = Atom(t1, x)

pxy = Atom(p2, x, y)
pyz = Atom(p2, y, z)
pxx = Atom(p2, x, x)
qxy = Atom(q2, x, y)
qxx = Atom(q2, x, x)
rxy = Atom(r2, x, y)
rxx = Atom(r2, x, x)

pzy = Atom(p2, z, y)
pyy = Atom(p2, y, y)
qzy = Atom(q2, z, y)

Rpx_qx = Rule(px, qx, label="Rpx_qx")
Rpx_py = Rule(px, py, label="Rpx_py")
Rqx_rxy = Rule(qx, rxy, label="Rqx_rxy")
Rpxy_qzy = Rule(pxy, qzy, label="Rpxy_qzy")
Rquv_pwv = Rule(qxy, pzy, label="Rquv_pwv")
Rpxy_pyz = Rule(pxy, pyz, label="Rpxy_pyz")
Rpxy_pyy = Rule(pxy, pyy, label="Rpxy_pyy")
Rpxnotqx_rx = Rule(and_(px, not_(qx)), rx, label="Rpxnotqx_rx")
Rsx_qx = Rule(sx, qx, label="Rsx_qx")
Rpxnotqx_qx = Rule(and_(px, not_(qx)), qx, label="Rpxnotqx_qx")
Rpxnotrx_qx = Rule(and_(px, not_(rx)), qx, label="Rpxnotrx_qx")
Rpxynotqxy_rxy = Rule(and_(pxy, not_(qxy)), rxy, label="Rpxynotqxy_rxy")
Rpxxnotrxx_qxx = Rule(and_(pxx, not_(rxx)), qxx, label="Rpxxnotrxx_qxx")
Rpxy_qxy = Rule(pxy, qxy, label="Rpxy_qxy")
Rqxxnotpxx_rx = Rule(and_(qxx, not_(pxx)), rx, label="Rqxxnotpxx_rx")
Rqxxnotrxx_sx = Rule(and_(qxx, not_(rxx)), sx, label="Rqxxnotrxx_sx")
Rpxnotrx_sx = Rule(and_(px, not_(rx)), sx, label="Rpxnotrx_sx")
Rpxnotsx_tx = Rule(and_(px, not_(sx)), tx, label="Rpxnotsx_tx")
Rqx_rx = Rule(qx, rx, label="Rqx_rx")
Rrx_sx = Rule(rx, sx, label="Rrx_sx")
Rqxx_sx = Rule(qxx, sx, label="Rqxx_sx")
Rtxnotsx_pxx = Rule(and_(tx, not_(sx)), pxx, label="Rtxnotsx_pxx")

__all__ = [
    "Rpx_qx",
    "Rpx_py",
    "Rqx_rxy",
    "Rpxy_qzy",
    "Rquv_pwv",
    "Rpxy_pyz",
    "Rpxy_pyy",
    "Rpxnotqx_rx",
    "Rsx_qx",
    "Rpxnotqx_qx",
    "Rpxnotrx_qx",
    "Rpxynotqxy_rxy",
    "Rpxxnotrxx_qxx",
    "Rpxy_qxy",
    "Rqxxnotpxx_rx",
    "Rqxxnotrxx_sx",
    "Rpxnotrx_sx",
    "Rpxnotsx_tx",
    "Rqx_rx",
    "Rrx_sx",
    "Rqxx_sx",
    "Rtxnotsx_pxx",
]
