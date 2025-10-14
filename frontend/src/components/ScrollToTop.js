import React, { useEffect, useState } from "react";

const ScrollToTop = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 300);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  if (!visible) return null;

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      className="btn"
      style={{
        position: 'fixed',
        right: 20,
        bottom: 20,
        background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))',
        color: '#0b1220',
        border: 'none',
        borderRadius: 999,
        padding: '10px 14px',
        boxShadow: '0 8px 24px rgba(124,58,237,0.25)',
        zIndex: 1000
      }}
      aria-label="Scroll to top"
    >
      ↑
    </button>
  );
};

export default ScrollToTop;


