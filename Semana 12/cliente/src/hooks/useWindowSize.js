import { useEffect, useState } from 'react';

export function useWindowSize() {
  const [width, setWidth] = useState(() => window.innerWidth);
  useEffect(() => {
    function resize() { setWidth(window.innerWidth); }
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);
  return width;
}
