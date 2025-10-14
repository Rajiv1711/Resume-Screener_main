import React from "react";

export const Skeleton = ({ width = "100%", height = 16, radius = 8, className = "" }) => {
  return (
    <div
      className={className}
      style={{
        width,
        height,
        borderRadius: radius,
        background: "linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.12), rgba(255,255,255,0.06))",
        backgroundSize: "200% 100%",
        animation: "skeleton-shimmer 1.2s ease-in-out infinite",
      }}
    />
  );
};

export const SkeletonRow = () => (
  <div className="d-flex align-items-center justify-content-between w-100" style={{ gap: 12 }}>
    <Skeleton width={40} height={40} radius={20} />
    <Skeleton width={"25%"} height={16} />
    <Skeleton width={80} height={16} />
    <Skeleton width={"35%"} height={16} />
  </div>
);

export default Skeleton;


