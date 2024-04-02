import { createRoot } from 'react-dom/client';
import { data } from './data'; // Ensure `data` has a defined TypeScript type
import { NetworkDiagram } from './NetworkDiagram'; // Ensure NetworkDiagram accepts typed props

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = createRoot(rootElement); // createRoot needs to be called on the container
  root.render(
    <NetworkDiagram data={data}/>
  );
}
