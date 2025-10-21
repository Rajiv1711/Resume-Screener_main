import React, { useEffect, useState } from "react";
import { getInsights } from "../services/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const InsightsChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getInsights();
        // API returns { status: 'success', insights: { skills_distribution: [...] } }
        const apiData = res?.data || {};
        const skills = apiData?.insights?.skills_distribution || apiData?.skills_distribution || [];
        setData(Array.isArray(skills) ? skills : []);
      } catch (e) {
        setError("Failed to load insights");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-secondary)' }}>Loading insights...</div>;
  }
  if (error) {
    return <div style={{ color: 'var(--accent-danger)' }}>{error}</div>;
  }
  if (!data || data.length === 0) {
    return <div style={{ color: 'var(--text-secondary)' }}>No insights available yet. Rank resumes to generate analytics.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="skill" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#82ca9d" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default InsightsChart;
