import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

const CustomCursor = () => {
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const move = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);

  return (
    <motion.div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: 18,
        height: 18,
        borderRadius: "50%",
        border: "2px solid var(--accent-primary)",
        pointerEvents: "none",
        zIndex: 9999,
        mixBlendMode: "difference",
      }}
      animate={{ x: pos.x - 9, y: pos.y - 9, scale: [1, 1.2, 1] }}
      transition={{
        x: { type: "spring", stiffness: 300, damping: 20 },
        y: { type: "spring", stiffness: 300, damping: 20 },
        scale: { duration: 0.8, repeat: Infinity, ease: "easeInOut" }
      }}
    />
  );
};

export default CustomCursor;
