// Blueprint-style physics drawings behind the app. Purely decorative.
// One moment of motion: the ray paths trace themselves in once on load.
const d = (s) => ({ "--d": s });

export default function Backdrop() {
  return (
    <svg className="bd" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      {/* Refraction at an interface (top left) */}
      <path d="M40 190 H480" pathLength={1} className="draw" style={d("0s")} />
      <path d="M260 60 V320" className="dash" />
      <path d="M120 70 L260 190 L318 300" pathLength={1} className="draw ray" style={d("0.3s")} />
      <text x="168" y="130">θ₁</text>
      <text x="282" y="262">θ₂</text>
      <text x="50" y="228">n₁</text>
      <text x="50" y="268">n₂</text>
      <text x="40" y="360" className="formula">n₁ sin θ₁ = n₂ sin θ₂</text>

      {/* Convex lens with converging rays (top right) */}
      <path d="M900 300 H1560" className="dash" />
      <path d="M1250 170 Q1310 300 1250 430 Q1190 300 1250 170Z" pathLength={1} className="draw" style={d("0.2s")} />
      <path d="M900 236 H1250 L1480 300" pathLength={1} className="draw ray" style={d("0.5s")} />
      <path d="M900 364 H1250 L1480 300" pathLength={1} className="draw ray" style={d("0.8s")} />
      <path d="M900 268 H1250 L1480 300" pathLength={1} className="draw ray" style={d("1.1s")} />
      <circle cx="1480" cy="300" r="4" className="dot" />
      <text x="1470" y="334">F</text>
      <text x="1236" y="470" className="formula">1/v − 1/u = 1/f</text>

      {/* Wave (bottom left) */}
      <path d="M40 820 q60 -90 120 0 t120 0 t120 0 t120 0 t120 0 t120 0" pathLength={1} className="draw" style={d("0.6s")} />
      <path d="M40 820 H760" className="dash" />
      <path d="M40 905 H160 M40 895 V915 M160 895 V915" />
      <text x="84" y="940">λ</text>

      {/* Simple circuit (bottom right) */}
      <path d="M1050 720 H1170 l12 -26 l24 52 l24 -52 l24 52 l24 -52 l12 26 H1480 V920 H1050 V860 M1030 860 H1070 M1042 836 H1058 M1050 836 V720"
        pathLength={1} className="draw" style={d("0.9s")} />
      <text x="1250" y="680">R</text>
      <text x="1000" y="800">V</text>
      <text x="1494" y="830">I</text>
      <text x="1090" y="975" className="formula">V = IR</text>
    </svg>
  );
}
