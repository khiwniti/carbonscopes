import { useEffect, useRef, useState } from 'react';

/**
 * Hook for detecting when an element enters the viewport
 * @param threshold - Intersection threshold (0-1). Default: 0.1
 * @returns [ref, isVisible] - Ref to attach to element and visibility state
 */
export function useInView(threshold: number = 0.1): [React.RefObject<HTMLDivElement>, boolean] {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    observer.observe(el);

    return () => observer.disconnect();
  }, [threshold]);

  return [ref, isVisible];
}
