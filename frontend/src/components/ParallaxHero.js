import React from "react";
import { motion, useScroll, useTransform } from "framer-motion";

const ParallaxHero = ({ title, subtitle }) => {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 400], [0, -40]);
  const y2 = useTransform(scrollY, [0, 400], [0, -80]);

  return (
    <div className="position-relative overflow-hidden" style={{ minHeight: 220 }}>
      <motion.div style={{ y: y2, position: "absolute", inset: 0, opacity: 0.35, pointerEvents: "none" }}>
        <svg width="100%" height="100%">
          <defs>
            <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity="0.6" />
              <stop offset="100%" stopColor="var(--accent-secondary)" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <circle cx="15%" cy="40%" r="180" fill="url(#g1)" />
          <circle cx="85%" cy="30%" r="140" fill="url(#g1)" />
        </svg>
      </motion.div>
      <motion.div style={{ y: y1 }} className="text-center py-5">
        <h1 className="display-5 fw-bold" style={{ color: 'var(--text-primary)' }}>{title}</h1>
        {subtitle && (
          <p className="lead" style={{ color: 'var(--text-secondary)' }}>{subtitle}</p>
        )}
      </motion.div>
    </div>
  );
};

export default ParallaxHero;


