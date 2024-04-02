import { Link, Node } from './data';

export const RADIUS = 10;

export const drawNetwork = (
  context: CanvasRenderingContext2D,
  width: number,
  height: number,
  nodes: Node[],
  links: Link[],
  highlightNode: Node | null // this is the additional parameter
) => {
  context.clearRect(0, 0, width, height);

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
    context.fillStyle = (highlightNode && node.id === highlightNode.id) ? 'red' : 'gray';
    context.fill();
    context.strokeStyle = 'white';
    context.lineWidth = 2;
    context.stroke();
  });
};