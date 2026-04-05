import { useEffect, useState } from 'react';

/**
 * Hook for animating number count-up effect
 * @param end - Target number to count up to
 * @param duration - Animation duration in milliseconds. Default: 1200ms
 * @param trigger - Whether to trigger the animation. Default: true
 * @returns Current animated value
 */
export function useCountUp(end: number, duration: number = 1200, trigger: boolean = true): number {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!trigger) {
      setValue(0);
      return;
    }

    let start = 0;
    const step = end / (duration / 16);

    const timer = setInterval(() => {
      start += step;
      if (start >= end) {
        setValue(end);
        clearInterval(timer);
      } else {
        setValue(Math.round(start));
      }
    }, 16);

    // Cleanup function clears interval when dependencies change or unmount
    return () => clearInterval(timer);
  }, [end, duration, trigger]);

  return value;
}
