import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const variants = {
  initial: { y: 20, opacity: 0, scale: 0.95 },
  animate: { y: 0, opacity: 1, scale: 1 },
  exit: { y: 10, opacity: 0, scale: 0.97 },
};

export const Toast = ({ id, title, message, type = "success", onClose }) => {
  useEffect(() => {
    const t = setTimeout(() => onClose(id), 3500);
    return () => clearTimeout(t);
  }, [id, onClose]);

  const bg = type === 'success' ? 'var(--accent-success)' : type === 'warning' ? 'var(--accent-warning)' : 'var(--accent-danger)';

  return (
    <motion.div
      className="glass p-3 mb-2"
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ borderLeft: `4px solid ${bg}` }}
    >
      <div className="d-flex align-items-start">
        <div className="me-2" style={{ color: bg }}>✔</div>
        <div className="flex-grow-1">
          <div className="fw-semibold" style={{ color: 'var(--text-primary)' }}>{title}</div>
          {message && (
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{message}</div>
          )}
        </div>
        <button className="btn btn-sm" onClick={() => onClose(id)} style={{ color: 'var(--text-secondary)' }}>✕</button>
      </div>
    </motion.div>
  );
};

const ToastContainer = ({ toasts, onClose }) => {
  return (
    <div style={{ position: 'fixed', right: 16, top: 16, zIndex: 2000, width: 320 }}>
      <AnimatePresence>
        {toasts.map(t => (
          <Toast key={t.id} {...t} onClose={onClose} />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ToastContainer;


