import React from "react";

const AnimatedBackground = () => {
  return (
    <div
      aria-hidden
      style={{
        position: "fixed",
        inset: 0,
        pointerEvents: "none",
        zIndex: -1,
        background:
          "radial-gradient(600px 300px at 20% 10%, rgba(79,209,197,0.08), transparent 60%)," +
          "radial-gradient(500px 250px at 80% 20%, rgba(124,58,237,0.08), transparent 60%)," +
          "radial-gradient(400px 200px at 50% 90%, rgba(251,146,60,0.06), transparent 60%)," +
          "radial-gradient(400px 200px at 10% 80%, rgba(52,211,153,0.06), transparent 60%)",
      }}
    />
  );
};

export default AnimatedBackground;


