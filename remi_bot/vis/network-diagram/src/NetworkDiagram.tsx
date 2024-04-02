import * as d3 from 'd3';
import { useEffect, useRef, useState } from 'react';
import { Data, Link, Node } from './data';

const RADIUS = 8;

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
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(50))
      .force('collide', d3.forceCollide().radius(RADIUS))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2));

    const drawNetwork = () => {
      context.fillStyle = '#333'; // Set the background color
      context.fillRect(0, 0, dimensions.width, dimensions.height);

      links.forEach(link => {
        context.beginPath();
        context.moveTo(link.source.x, link.source.y);
        context.lineTo(link.target.x, link.target.y);
        context.strokeStyle = '#999';
        context.lineWidth = 1;
        context.stroke();

        // // Calculate the midpoint of the link
        // const midX = (link.source.x + link.target.x) / 2;
        // const midY = (link.source.y + link.target.y) / 2;
        // // Offset for the control points
        // const offsetX = (link.target.y - link.source.y) * 0.1; // Adjust the 0.1 as needed
        // const offsetY = (link.target.x - link.source.x) * 0.1; // Adjust the 0.1 as needed

        // context.beginPath();
        // context.moveTo(link.source.x, link.source.y);
        // // Create a quadratic curve with the control point offset from the midpoint
        // context.quadraticCurveTo(midX + offsetX, midY - offsetY, link.target.x, link.target.y);
      });

      nodes.forEach(node => {
        context.beginPath();
        context.arc(node.x!, node.y!, RADIUS, 0, Math.PI * 2);
        context.fillStyle = '#7f27ff';
        context.fill();
        context.strokeStyle = '#ffffff';
        context.lineWidth = 1;
        context.stroke();
      });
    };

    simulation.on('tick', drawNetwork);

    const drag = d3.drag<HTMLCanvasElement, Node>()
      .container(canvas!)
      .subject(event => {
        const node = simulation.find(event.x, event.y, RADIUS) as Node | null;
        return node ?? { x: event.x, y: event.y };
      })
      .on('start', (event) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      })
      .on('drag', (event) => {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      })
      .on('end', (event) => {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      });

    d3.select(canvas).call(drag as any);

    canvas.addEventListener('mousemove', function (event) {
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      context.clearRect(0, 0, dimensions.width, dimensions.height);
      drawNetwork();

      nodes.forEach(node => {
        if (Math.hypot(node.x! - mouseX, node.y! - mouseY) < RADIUS) {
          console.log("highlight......")
          context.beginPath();
          context.arc(node.x!, node.y!, RADIUS, 0, 2 * Math.PI);
          context.fillStyle = '#15f5ba';
          context.fill();

          context.fillStyle = '#ffffff'; // White color for the text
          context.font = '16px sans-serif'; // Increase font size here as needed
          context.fillText(node.id, node.x! + 2 * RADIUS, node.y! + 2 * RADIUS);
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