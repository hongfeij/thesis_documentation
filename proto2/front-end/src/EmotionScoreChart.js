import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import './EmotionScoreChart.css';

const EmotionScoreChart = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Emotion Score',
        data: [],
        fill: false,
        backgroundColor: 'rgb(75, 192, 192)',
        borderColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  });

  const updateChartData = (jsonData) => {
    setChartData({
      labels: jsonData.map((data) => data.id.toString()),
      datasets: [
        {
          ...chartData.datasets[0],
          data: jsonData.map((data) => data.emotion_score),
        },
      ],
    });
  };

  const fetchChartData = () => {
    fetch('http://localhost:5000/get_emotion_score')
      .then((response) => response.json())
      .then((jsonData) => {
        updateChartData(jsonData);
      })
      .catch((error) => {
        console.error('Error fetching chart data:', error);
      });
  };

  useEffect(() => {
    fetchChartData(); // Fetch on initial load

    const intervalId = setInterval(() => {
      fetchChartData(); // Fetch every 3 seconds
    }, 3000);

    return () => clearInterval(intervalId); // Clean up on unmount
  }, []);

  return (
    <div className="chart-container">
      <h1>Emotion Score Over Time</h1>
      <div className="chart-wrapper">
        <Line data={chartData} options={{ maintainAspectRatio: false }} />
      </div>
    </div>
  );
};

export default EmotionScoreChart;
