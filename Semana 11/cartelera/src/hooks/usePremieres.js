import { useEffect, useState } from 'react';

export function usePremieres(movies, fail, attempt) {
  const [result, setResult] = useState({ status: 'loading', data: [] });
  useEffect(() => {
    setResult({ status: 'loading', data: [] });
    const timer = setTimeout(() => {
      setResult(fail ? { status: 'error', data: [] } : { status: 'ready', data: movies.slice(-4) });
    }, 1000);
    return () => clearTimeout(timer);
  }, [movies, fail, attempt]);
  return result;
}
