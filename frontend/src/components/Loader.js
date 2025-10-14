import React from "react";
import { motion } from "framer-motion";

const Loader = ({ size = 40 }) => {
  const dot = {
    width: size / 5,
    height: size / 5,
    borderRadius: "50%",
    background: "var(--accent-primary)",
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: size / 6 }}>
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          style={dot}
          animate={{ y: [0, -8, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.12 }}
        />
      ))}
    </div>
  );
};

export default Loader;
