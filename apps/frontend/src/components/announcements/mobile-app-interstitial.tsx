'use client';

import { X } from 'lucide-react';
import { useEffect, useState } from 'react';

export function MobileAppInterstitial() {
  const [isVisible, setIsVisible] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent));
    };
    checkMobile();
  }, []);

  if (!isMobile || !isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-sm w-full">
        <button
          onClick={() => setIsVisible(false)}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">CarbonScope Mobile App</h2>
          <p className="text-gray-600 mb-4">
            Get the best experience with our mobile app
          </p>
        </div>
      </div>
    </div>
  );
}
