import React from 'react';
import logo from '../assets/logo.png';
import { apiClient } from '../utils/apiClient';
import ChangePasswordModal from './ChangePasswordModal';

const Navbar = ({ onRefresh, onLogout, user }) => {
  const [lastUpdate, setLastUpdate] = React.useState(new Date());
  const [showSettings, setShowSettings] = React.useState(false);
  const [alertStatus, setAlertStatus] = React.useState(null); // null | 'sending' | 'sent' | 'error'
  const [showChangePassword, setShowChangePassword] = React.useState(false);
  const settingsRef = React.useRef(null);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (e) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target)) {
        setShowSettings(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleTestAlert = async () => {
    setAlertStatus('sending');
    try {
      await apiClient.post('/api/alerts/test');
      setAlertStatus('sent');
    } catch (err) {
      setAlertStatus('error');
    } finally {
      setTimeout(() => setAlertStatus(null), 3000);
    }
  };

  const handleRefresh = () => {
    onRefresh();
    setLastUpdate(new Date());
  };

  return (
    <>
      <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src={logo} alt="f.Insight.AI" className="h-12" />
            </div>
          </div>

          {/* Status and controls */}
          <div className="flex items-center space-x-4">
            {/* Live indicator */}
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Live</span>
            </div>

            {/* Last update */}
            <div className="hidden sm:block text-sm text-gray-500">
              Updated {lastUpdate.toLocaleTimeString()}
            </div>

            {/* Refresh button */}
            <button
              onClick={handleRefresh}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span className="hidden sm:inline">Refresh</span>
            </button>

            {/* User + logout */}
            {user && (
              <div className="flex items-center space-x-2">
                <span className="hidden sm:inline text-sm text-gray-500">{user.username || user.email}</span>
                <button
                  onClick={onLogout}
                  title="Sign out"
                  className="text-gray-400 hover:text-red-500 p-2 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            )}
            <div className="relative" ref={settingsRef}>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`p-2 rounded-lg transition-colors ${showSettings ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
                title="Settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>

              {showSettings && (
                <div className="absolute right-0 mt-2 w-60 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Settings</p>
                  </div>
                  <div className="p-2">
                    <button
                      onClick={handleTestAlert}
                      disabled={alertStatus === 'sending'}
                      className="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-3 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="text-lg">
                        {alertStatus === 'sending' ? '⏳' : alertStatus === 'sent' ? '✅' : alertStatus === 'error' ? '❌' : '🔔'}
                      </span>
                      <span className={alertStatus === 'sent' ? 'text-green-600' : alertStatus === 'error' ? 'text-red-600' : 'text-gray-700'}>
                        {alertStatus === 'sending' ? 'Sending...' : alertStatus === 'sent' ? 'Alert sent!' : alertStatus === 'error' ? 'Send failed' : 'Send Test Alert'}
                      </span>
                    </button>
                    <button
                      onClick={() => { setShowSettings(false); setShowChangePassword(true); }}
                      className="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-3 hover:bg-gray-50 text-gray-700"
                    >
                      <span className="text-lg">🔑</span>
                      <span>Change Password</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
      {showChangePassword && (
        <ChangePasswordModal onClose={() => setShowChangePassword(false)} />
      )}
    </>
  );
};

export default Navbar;
