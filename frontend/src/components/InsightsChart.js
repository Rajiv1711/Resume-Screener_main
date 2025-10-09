import React, { useEffect, useState } from "react";
import { getInsights } from "../services/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const InsightsChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    getInsights().then((res) => setData(res.data));
  }, []);

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
