import * as d3 from 'd3';
import { useEffect, useRef, useState } from 'react';
import { RADIUS } from './drawNetwork';
import { Data, Link, Node } from './data';

type NetworkDiagramProps = {
  data: Data;
};

export const NetworkDiagram = ({ data }: NetworkDiagramProps) => {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    function handleResize() {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize(); // Set initial size

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const context = canvas.getContext('2d');
    if (!context) {
      return;
    }

    // Adjust canvas size
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    // Prepare nodes and links from data
    const nodes = data.nodes.map(d => ({ ...d }));
    const links = data.links.map(d => ({ ...d }));
    if (!nodes || !links) {
      return;
    }

    // Initialize D3 force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2));

      const drawNetwork = () => {
        context.clearRect(0, 0, dimensions.width, dimensions.height);
      
        links.forEach(link => {
          context.beginPath();
          context.moveTo(link.source.x, link.source.y);
          context.lineTo(link.target.x, link.target.y);
          context.strokeStyle = '#999';
          context.stroke();
        });
      
        nodes.forEach(node => {
          context.beginPath();
          context.arc(node.x!, node.y!, RADIUS, 0, Math.PI * 2);
          context.fillStyle = 'gray';
          context.fill();
          context.strokeStyle = 'white';
          context.lineWidth = 2;
          context.stroke();
        });
      };

    simulation.on('tick', drawNetwork);

    canvas.addEventListener('mousemove', function(event) {
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      context.clearRect(0, 0, dimensions.width, dimensions.height);
      drawNetwork();

      nodes.forEach(node => {
        if (Math.hypot(node.x! - mouseX, node.y! - mouseY) < RADIUS) {
          context.beginPath();
          context.arc(node.x!, node.y!, RADIUS, 0, 2 * Math.PI);
          context.fillStyle = 'red';
          context.fill();
        }
      });
    });

    return () => {
      simulation.stop();
      canvas.removeEventListener('mousemove', drawNetwork);
    };
  }, [data, dimensions]);

  return (
    <div>
      <canvas ref={canvasRef} />
    </div>
  );
};