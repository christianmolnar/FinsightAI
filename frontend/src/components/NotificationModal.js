import React, { useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

const NotificationModal = ({ 
  isOpen, 
  onClose, 
  title, 
  message, 
  type = 'success', // 'success', 'error', 'warning', 'info'
  autoClose = true,
  autoCloseDuration = 3000
}) => {
  useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, autoCloseDuration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, autoCloseDuration, onClose]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case 'info':
        return <Info className="w-6 h-6 text-blue-500" />;
      default:
        return <CheckCircle className="w-6 h-6 text-green-500" />;
    }
  };

  const getBorderColor = () => {
    switch (type) {
      case 'success':
        return 'border-l-4 border-green-500';
      case 'error':
        return 'border-l-4 border-red-500';
      case 'warning':
        return 'border-l-4 border-yellow-500';
      case 'info':
        return 'border-l-4 border-blue-500';
      default:
        return 'border-l-4 border-green-500';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 animate-slideIn">
      <div className={`bg-white rounded-lg shadow-lg max-w-md w-full ${getBorderColor()}`}>
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getIcon()}
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-gray-900">
                {title}
              </h3>
              {message && (
                <div className="mt-1 text-sm text-gray-600">
                  {message}
                </div>
              )}
            </div>
            <button
              onClick={onClose}
              className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationModal;
