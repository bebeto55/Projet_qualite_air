import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { useAirQuality } from '../../hooks/useAirQuality';
import './Layout.css';

export default function Layout() {
  const { alerts } = useAirQuality();
  return (
    <div className="layout">
      <Sidebar alertCount={alerts?.length || 0} />
      <div className="layout-main">
        <Topbar />
        <main className="layout-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
