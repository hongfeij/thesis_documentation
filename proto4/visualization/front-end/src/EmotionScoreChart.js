import React, { useState, useEffect } from 'react';
import { Radar } from 'react-chartjs-2';
import 'chart.js/auto';
import './EmotionScoreChart.css';

const EmotionScoreChart = () => {
  const [chartData, setChartData] = useState({
    labels: ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise'],
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

  const updateChartData = (latestData) => {
    console.log(latestData);
    setChartData({
      ...chartData,
      datasets: [
        {
          ...chartData.datasets[0],
          data: [
            latestData.emotion_score.angry,
            latestData.emotion_score.disgust,
            latestData.emotion_score.fear,
            latestData.emotion_score.happy,
            latestData.emotion_score.neutral,
            latestData.emotion_score.sad,
            latestData.emotion_score.surprise,
          ],
        },
      ],
    });
  };

  const fetchChartData = () => {
    fetch('http://localhost:5000/get_emotion_score')
      .then((response) => response.json())
      .then((jsonData) => {
        const latestData = jsonData[jsonData.length - 1]; // Get the last element
        updateChartData(latestData);
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
