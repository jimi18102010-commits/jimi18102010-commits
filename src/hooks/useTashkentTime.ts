import { useState, useEffect } from 'react';

export function useTashkentTime() {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Tashkent is UTC+5
      const options: Intl.DateTimeFormatOptions = {
        timeZone: 'Asia/Tashkent',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      };
      setTime(new Intl.DateTimeFormat('en-US', options).format(now));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  return time;
}
