import * as d3 from 'd3';
import { useEffect, useRef, useState } from 'react';
import { RADIUS, drawNetwork } from './drawNetwork';
import { Data, Link, Node } from './data';

type NetworkDiagramProps = {
  data: Data;
};

export const NetworkDiagram = ({ data }: NetworkDiagramProps) => {
  // State for keeping track of the dimensions of the network diagram
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const [links, setLinks] = useState<Link[]>(data.links.map(d => ({ ...d })));
  const [nodes, setNodes] = useState<Node[]>(data.nodes.map(d => ({ ...d })));
  const [highlightNode, setHighlightNode] = useState<Node | null>(null);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    function handleResize() {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize(); // Set the initial size

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const context = canvas?.getContext('2d');
    if (!context) {
      return;
    }

    // Set the canvas dimensions
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id))
      .force('collide', d3.forceCollide().radius(RADIUS))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .on('tick', () => drawNetwork(context, dimensions.width, dimensions.height, nodes, links, highlightNode));

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

    const handleMouseMove = (event: MouseEvent) => {
      const mouse = d3.pointer(event);
      const mouseX = mouse[0];
      const mouseY = mouse[1];
  
      let foundNode = null;
      
      for (const node of nodes) {
        const dx = mouseX - node.x!;
        const dy = mouseY - node.y!;
        if (dx * dx + dy * dy < RADIUS * RADIUS) {
          foundNode = node;
          break;
        }
      }
  
      setHighlightNode(foundNode);
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    return () => {
      simulation.stop();
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, [dimensions, nodes, links, highlightNode]);

  return (
    <div>
      <canvas
        ref={canvasRef}
        style={{
          width: dimensions.width,
          height: dimensions.height,
        }}
      />
    </div>
  );
};