import React, { useState, useEffect } from 'react';
import { Radar } from 'react-chartjs-2';
import 'chart.js/auto';
import './EmotionScoreChart.css';

const EmotionScoreChart = () => {
  const [chartData, setChartData] = useState({
    labels: ['Anger', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise', 'Angry'],
    datasets: [
      {
        label: 'Emotion Scores',
        data: [],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgb(75, 192, 192)',
        borderWidth: 1,
      },
    ],
  });

  const updateChartData = (jsonData) => {
    setChartData({
      ...chartData,
      datasets: [
        {
          ...chartData.datasets[0],
          data: [
            jsonData.emotion_score.anger,
            jsonData.emotion_score.disgust,
            jsonData.emotion_score.fear,
            jsonData.emotion_score.happy,
            jsonData.emotion_score.neutral,
            jsonData.emotion_score.sad,
            jsonData.emotion_score.surprise,
            jsonData.emotion_score.angry
          ],
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
      <h1>Emotion Score Radar Chart</h1>
      <div className="chart-wrapper">
        <Radar data={chartData} options={{ maintainAspectRatio: false }} />
      </div>
    </div>
  );
};

export default EmotionScoreChart;
