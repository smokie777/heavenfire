import './index.scss';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom';
import { ControlPanel } from './ControlPanel';
import { Overlay } from './Overlay';

const router = createBrowserRouter([
  {
    path: '/',
    element: <ControlPanel />,
  },
  {
    path: '/overlay',
    element: <Overlay />
  }
]);

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <RouterProvider router={router} />
);
