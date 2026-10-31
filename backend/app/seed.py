"""First-run seed: concept graph, question bank, 10 fake students."""
import random

from sqlalchemy.orm import Session

from .models import Concept, ConceptEdge, Mastery, Question, Student, utcnow

CONCEPTS = [
    dict(id="electric_current", name="Electric Current & Potential Difference", topic="Electricity",
         summary="Current is the rate of flow of charge; potential difference is the work done per unit charge that drives it.",
         key_ideas=["I = Q/t, measured in amperes", "V = W/Q, measured in volts",
                    "Ammeter goes in series, voltmeter in parallel", "Conventional current flows from + to − terminal"]),
    dict(id="ohms_law", name="Ohm's Law", topic="Electricity",
         summary="At constant temperature, the current through a conductor is proportional to the potential difference across it.",
         key_ideas=["V = IR", "V–I graph of an ohmic conductor is a straight line through the origin",
                    "Resistance is the ratio V/I", "Holds only at constant temperature"]),
    dict(id="resistance_factors", name="Resistance & Resistivity", topic="Electricity",
         summary="A conductor's resistance depends on its length, cross-section area, material and temperature.",
         key_ideas=["R = ρL/A", "Resistance rises with length and falls with area",
                    "Resistivity depends on material and temperature, not on dimensions",
                    "Alloys have higher resistivity than pure metals"]),
    dict(id="series_parallel", name="Series & Parallel Circuits", topic="Electricity",
         summary="How resistors combine and how current and voltage split in series and parallel arrangements.",
         key_ideas=["Series: R = R1 + R2 + …, same current everywhere", "Parallel: 1/R = 1/R1 + 1/R2 + …, same voltage across each branch",
                    "Parallel equivalent is smaller than the smallest resistor", "Household wiring is parallel"]),
    dict(id="electric_power", name="Electric Power & Energy", topic="Electricity",
         summary="Rate at which electrical energy is consumed, and the heating effect of current.",
         key_ideas=["P = VI = I²R = V²/R", "Energy = P × t; 1 kWh = 3.6 × 10^6 J",
                    "Heating effect H = I²Rt", "Appliance rating gives power at its rated voltage"]),
    dict(id="reflection", name="Reflection of Light", topic="Light: Reflection & Refraction",
         summary="Laws of reflection and image formation by plane mirrors.",
         key_ideas=["Angle of incidence = angle of reflection, both measured from the normal",
                    "Incident ray, reflected ray and normal lie in one plane",
                    "Plane mirror image: virtual, erect, same size, laterally inverted, as far behind as the object is in front"]),
    dict(id="spherical_mirrors", name="Spherical Mirrors", topic="Light: Reflection & Refraction",
         summary="Concave and convex mirrors: focal length, mirror formula, magnification, ray diagrams.",
         key_ideas=["f = R/2", "1/v + 1/u = 1/f", "m = −v/u = h'/h",
                    "Distances measured from the pole; concave mirror has negative f",
                    "Image nature depends on object position relative to F and C"]),
    dict(id="refraction", name="Refraction of Light", topic="Light: Reflection & Refraction",
         summary="Bending of light when it passes between media; refractive index and Snell's law.",
         key_ideas=["Light bends towards the normal entering a denser medium", "n = sin i / sin r (Snell's law)",
                    "n = c / v", "Denser medium: higher n, lower speed of light"]),
    dict(id="lenses", name="Lenses & Lens Power", topic="Light: Reflection & Refraction",
         summary="Image formation by convex and concave lenses, lens formula and power.",
         key_ideas=["1/v − 1/u = 1/f", "m = v/u", "P = 1/f with f in metres; unit dioptre",
                    "Convex lens converges, concave lens diverges; concave power is negative"]),
    dict(id="magnetic_effect", name="Magnetic Effect of Current", topic="Magnetic Effects of Electric Current",
         summary="Magnetic field produced by a current and the force on a current-carrying conductor in a field.",
         key_ideas=["Oersted: a current produces a magnetic field", "Right-hand thumb rule gives field direction",
                    "Fleming's left-hand rule gives force direction on a conductor",
                    "Field strength falls with distance from the wire"]),
]

# (prerequisite, concept)
EDGES = [
    ("electric_current", "ohms_law"), ("ohms_law", "resistance_factors"), ("ohms_law", "series_parallel"),
    ("series_parallel", "electric_power"), ("electric_current", "magnetic_effect"),
    ("reflection", "spherical_mirrors"), ("reflection", "refraction"),
    ("refraction", "lenses"), ("spherical_mirrors", "lenses"),
]

# diagnostic_order set => part of the 5-question diagnostic. Others are the offline fallback bank.
QUESTIONS = [
    dict(concept_id="ohms_law", difficulty=0.25, diagnostic_order=1,
         stem="A conductor has a potential difference of 12 V across it and carries a current of 3 A. What is its resistance?",
         options=["36 Ω", "4 Ω", "0.25 Ω", "9 Ω"], correct_index=1,
         explanation="R = V / I = 12 V / 3 A = 4 Ω."),
    dict(concept_id="reflection", difficulty=0.4, diagnostic_order=2,
         stem="A ray strikes a plane mirror with an angle of incidence of 30°. What is the angle between the incident ray and the reflected ray?",
         options=["30°", "60°", "90°", "120°"], correct_index=1,
         explanation="Angle of reflection is also 30°, both measured from the normal, so the angle between the two rays is 30° + 30° = 60°."),
    dict(concept_id="series_parallel", difficulty=0.5, diagnostic_order=3,
         stem="Resistors of 6 Ω and 3 Ω are connected in parallel. The equivalent resistance is:",
         options=["9 Ω", "4.5 Ω", "2 Ω", "18 Ω"], correct_index=2,
         explanation="1/R = 1/6 + 1/3 = 1/2, so R = 2 Ω. A parallel combination is always smaller than the smallest resistor."),
    dict(concept_id="electric_power", difficulty=0.65, diagnostic_order=4,
         stem="A 100 W bulb and a 60 W bulb are both rated 220 V. Which has the higher resistance when working normally?",
         options=["The 100 W bulb", "The 60 W bulb", "Both are the same", "It cannot be determined"], correct_index=1,
         explanation="R = V²/P at the same voltage, so lower power means higher resistance. The 60 W bulb has the higher resistance."),
    dict(concept_id="refraction", difficulty=0.8, diagnostic_order=5,
         stem="Light passes from air into glass of refractive index 1.5 (speed of light in air is 3 × 10^8 m/s). Which statement is correct?",
         options=["Speed falls to 2 × 10^8 m/s and the ray bends towards the normal",
                  "Speed falls to 2 × 10^8 m/s and the ray bends away from the normal",
                  "Speed rises to 4.5 × 10^8 m/s and the ray bends towards the normal",
                  "Speed stays the same and the ray bends towards the normal"], correct_index=0,
         explanation="v = c/n = 3 × 10^8 / 1.5 = 2 × 10^8 m/s. Entering a denser medium, light slows down and bends towards the normal."),
    # --- fallback bank (used when NVIDIA is unavailable) ---
    dict(concept_id="electric_current", difficulty=0.2,
         stem="A current of 2 A flows through a wire for 10 s. How much charge passes through it?",
         options=["5 C", "20 C", "0.2 C", "12 C"], correct_index=1,
         explanation="Q = I × t = 2 A × 10 s = 20 C."),
    dict(concept_id="resistance_factors", difficulty=0.5,
         stem="A wire's length is doubled and its cross-sectional area is also doubled (same material). Its resistance:",
         options=["doubles", "halves", "stays the same", "becomes four times"], correct_index=2,
         explanation="R = ρL/A. Doubling L doubles R, doubling A halves it, so R is unchanged."),
    dict(concept_id="spherical_mirrors", difficulty=0.55,
         stem="An object is placed at the centre of curvature of a concave mirror. The image formed is:",
         options=["real, inverted, same size, at C", "virtual, erect, magnified",
                  "real, inverted, magnified, beyond C", "real, inverted, diminished, between F and C"], correct_index=0,
         explanation="For an object at C, the image is also at C: real, inverted and the same size (m = −1)."),
    dict(concept_id="lenses", difficulty=0.7,
         stem="A lens has a power of −2.5 D. What kind of lens is it and what is its focal length?",
         options=["Convex, 40 cm", "Concave, 40 cm", "Concave, 2.5 cm", "Convex, 2.5 cm"], correct_index=1,
         explanation="Negative power means a concave lens. f = 1/P = 1/(−2.5) m = −0.4 m, so the magnitude is 40 cm."),
    dict(concept_id="magnetic_effect", difficulty=0.4,
         stem="In Fleming's left-hand rule, the thumb points in the direction of:",
         options=["the current", "the magnetic field", "the force (motion) on the conductor", "the induced current"], correct_index=2,
         explanation="Forefinger = magnetic field, middle finger = current, thumb = force on the conductor."),
]

DEMO_NAMES = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Ananya", "Ishaan", "Saanvi", "Vihaan", "Tara"]

# Class-wide averages are planted so the teacher chart tells a story:
# refraction, lenses and series-parallel are weak across the class.
CLASS_MEANS = {
    "electric_current": 0.78, "ohms_law": 0.70, "resistance_factors": 0.56, "series_parallel": 0.38,
    "electric_power": 0.50, "reflection": 0.74, "spherical_mirrors": 0.46, "refraction": 0.33,
    "lenses": 0.28, "magnetic_effect": 0.62,
}


def seed_if_empty(db: Session) -> None:
    if db.query(Concept).count() > 0:
        return

    for i, c in enumerate(CONCEPTS):
        db.add(Concept(position=i, **c))
    for pre, con in EDGES:
        db.add(ConceptEdge(prerequisite_id=pre, concept_id=con))
    for q in QUESTIONS:
        db.add(Question(source="seed", **q))

    rng = random.Random(7)
    now = utcnow()
    for name in DEMO_NAMES:
        student = Student(name=name, is_demo=True)
        db.add(student)
        db.flush()
        ability = rng.gauss(0, 0.08)  # some students are stronger overall
        for c in CONCEPTS:
            score = min(0.98, max(0.04, CLASS_MEANS[c["id"]] + ability + rng.gauss(0, 0.12)))
            attempts = rng.randint(4, 12)
            db.add(Mastery(student_id=student.id, concept_id=c["id"], score=round(score, 3),
                           attempts=attempts, correct_count=round(score * attempts),
                           last_practiced=now, interval_days=1.0, due_at=now))
    db.commit()
