'use client';

import { ThemeToggle } from '@/components/home/theme-toggle';
import { siteConfig } from '@/lib/site-config';
import { cn } from '@/lib/utils';
import { X, Menu } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import Link from 'next/link';
import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '@/components/AuthProvider';
import { useRouter, usePathname } from 'next/navigation';
import { CarbonScopeLogoSimple } from '@/components/brand/carbonscope-logo-simple';
import { useTranslations } from 'next-intl';
import { trackCtaSignup } from '@/lib/analytics/gtm';
import { AppDownloadQR } from '@/components/common/app-download-qr';
import { isMobileDevice } from '@/lib/utils/is-mobile-device';

// Apple logo SVG
function AppleLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
    </svg>
  );
}

// Play icon SVG
function PlayIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 406 455" fill="currentColor">
      <path d="M382.634 187.308C413.301 205.014 413.301 249.277 382.634 266.983L69.0001 448.06C38.3334 465.765 3.84111e-05 443.633 3.9959e-05 408.222L5.57892e-05 46.0689C5.73371e-05 10.6581 38.3334 -11.4738 69.0001 6.23166L382.634 187.308Z"/>
    </svg>
  );
}

// Scroll threshold with hysteresis to prevent flickering
const SCROLL_THRESHOLD_DOWN = 50;
const SCROLL_THRESHOLD_UP = 20;

const overlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

const drawerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.2,
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.15 },
  },
};

const drawerMenuContainerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
    },
  },
};

const drawerMenuVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut" as const,
    },
  },
};

interface NavbarProps {
  isAbsolute?: boolean;
}

export function Navbar({ isAbsolute = false }: NavbarProps) {
  const [hasScrolled, setHasScrolled] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');
  const [isMobile, setIsMobile] = useState(false);
  const { user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const t = useTranslations('common');
  const lastScrollY = useRef(0);

  const filteredNavLinks = siteConfig.nav.links;

  // Detect if user is on an actual mobile device (iOS/Android)
  // Mobile users clicking "Try Free" will be redirected to /app which then redirects to app stores
  useEffect(() => {
    setIsMobile(isMobileDevice());
  }, []);

  // Get the appropriate CTA link based on device type
  const ctaLink = isMobile ? '/app' : '/auth';

  // Single unified scroll handler with hysteresis
  const handleScroll = useCallback(() => {
    const currentScrollY = window.scrollY;
    
    // Hysteresis: different thresholds for scrolling up vs down
    if (!hasScrolled && currentScrollY > SCROLL_THRESHOLD_DOWN) {
      setHasScrolled(true);
    } else if (hasScrolled && currentScrollY < SCROLL_THRESHOLD_UP) {
      setHasScrolled(false);
    }

    // Update active section
    const sections = filteredNavLinks.map((item) => item.href.substring(1));
    for (const section of sections) {
      const element = document.getElementById(section);
      if (element) {
        const rect = element.getBoundingClientRect();
        if (rect.top <= 150 && rect.bottom >= 150) {
          setActiveSection(section);
          break;
        }
      }
    }

    lastScrollY.current = currentScrollY;
  }, [hasScrolled, filteredNavLinks]);

  useEffect(() => {
    // Use passive listener for better scroll performance
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  const toggleDrawer = () => setIsDrawerOpen((prev) => !prev);
  const handleOverlayClick = () => setIsDrawerOpen(false);

  return (
    <header style={{
      display: 'flex',
      justifyContent: 'center',
      paddingLeft: '1.5rem',
      paddingRight: '1.5rem',
      paddingTop: '1rem',
      position: isAbsolute ? 'relative' : 'sticky',
      top: 0,
      zIndex: 50,
      background: hasScrolled ? 'rgba(11, 17, 32, 0.8)' : 'transparent',
      backdropFilter: hasScrolled ? 'blur(20px)' : 'none',
      borderBottom: hasScrolled ? '1px solid rgba(30, 41, 59, 0.5)' : 'none',
      transition: 'background 0.3s ease, backdrop-filter 0.3s ease, border-bottom 0.3s ease',
    }}>
      <div style={{ width: '100%', maxWidth: '56rem' }}>
        <div style={{
          marginLeft: 'auto',
          marginRight: 'auto',
          borderRadius: '1rem',
          background: 'transparent',
        }}>
          <div style={{
            position: 'relative',
            display: 'flex',
            height: '56px',
            alignItems: 'center',
            paddingTop: '0.5rem',
            paddingBottom: '0.5rem',
          }}>
            {/* Left Section - Logo */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-start',
              flexShrink: 0,
            }}>
              <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
                {/* CarbonScope Logo */}
                <CarbonScopeLogoSimple size={28} />
                {/* CarbonScope Wordmark */}
                <span style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '-0.02em', color: '#F1F5F9' }}>
                  Carbon<span style={{ color: '#10B981' }}>Scope</span>
                </span>
              </Link>
            </div>

            {/* Center Section - Nav Links (absolutely centered) */}
            <nav style={{
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.25rem',
              position: 'absolute',
              left: '50%',
              transform: 'translateX(-50%)',
            }} className="hidden md:flex">
              {filteredNavLinks.map((item) => (
                <Link
                  key={item.id}
                  href={item.href}
                  style={{
                    paddingLeft: '0.75rem',
                    paddingRight: '0.75rem',
                    paddingTop: '0.375rem',
                    paddingBottom: '0.375rem',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                    borderRadius: '0.5rem',
                    color: pathname === item.href ? '#E2E8F0' : '#94A3B8',
                    textDecoration: 'none',
                    transition: 'color 0.2s ease',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.color = '#34D399'}
                  onMouseLeave={(e) => e.currentTarget.style.color = pathname === item.href ? '#E2E8F0' : '#94A3B8'}
                >
                  {item.name}
                </Link>
              ))}

              {/* Mobile App Download with QR Popover */}
              <div style={{ position: 'relative' }}>
                <Link
                  href="/app"
                  style={{
                    paddingLeft: '0.75rem',
                    paddingRight: '0.75rem',
                    paddingTop: '0.375rem',
                    paddingBottom: '0.375rem',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                    borderRadius: '0.5rem',
                    color: pathname === '/app' ? '#E2E8F0' : '#94A3B8',
                    textDecoration: 'none',
                    transition: 'color 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#34D399';
                    const popover = e.currentTarget.nextElementSibling as HTMLElement;
                    if (popover) {
                      popover.style.opacity = '1';
                      popover.style.visibility = 'visible';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = pathname === '/app' ? '#E2E8F0' : '#94A3B8';
                    const popover = e.currentTarget.nextElementSibling as HTMLElement;
                    if (popover) {
                      popover.style.opacity = '0';
                      popover.style.visibility = 'hidden';
                    }
                  }}
                >
                  Mobile
                </Link>

                {/* QR Code Popover - appears on hover */}
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    paddingTop: '0.5rem',
                    zIndex: 50,
                    opacity: 0,
                    visibility: 'hidden',
                    transition: 'opacity 0.2s ease, visibility 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.visibility = 'visible';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '0';
                    e.currentTarget.style.visibility = 'hidden';
                  }}
                >
                  <div style={{
                    position: 'relative',
                    background: '#162032',
                    borderRadius: '1rem',
                    border: '1px solid #1E293B',
                    padding: '1rem',
                    minWidth: '200px',
                  }}>
                    <div style={{
                      borderRadius: '0.75rem',
                      padding: '0.75rem',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    }}>
                      <AppDownloadQR size={160} logoSize={24} />
                    </div>
                    <p style={{
                      fontSize: '0.75rem',
                      color: '#64748B',
                      textAlign: 'center',
                      marginTop: '0.75rem',
                      fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                    }}>
                      Scan to download
                    </p>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.375rem',
                      marginTop: '0.375rem',
                    }}>
                      <AppleLogo className="h-3 w-3 text-slate-500/60" />
                      <PlayIcon className="h-2.5 w-2.5 text-slate-500/60" />
                    </div>
                  </div>
                </div>
              </div>
            </nav>

            {/* Right Section - Actions */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: '0.5rem',
              marginLeft: 'auto',
            }}>
              {user ? (
                <Link
                  href="/dashboard"
                  className="luxury-transition luxury-shimmer"
                  style={{
                    height: '2rem',
                    paddingLeft: '1rem',
                    paddingRight: '1rem',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                    borderRadius: '0.5rem',
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: '#FFFFFF',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textDecoration: 'none',
                    boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #059669 0%, #047857 100%)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                    e.currentTarget.style.transform = 'scale(1.05) translateY(-1px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #10B981 0%, #059669 100%)';
                    e.currentTarget.style.boxShadow = '0 4px 14px rgba(16, 185, 129, 0.3)';
                    e.currentTarget.style.transform = 'scale(1) translateY(0)';
                  }}
                >
                  Dashboard
                </Link>
              ) : (
                <Link
                  href={ctaLink}
                  onClick={() => trackCtaSignup()}
                  className="luxury-transition luxury-shimmer"
                  style={{
                    height: '2rem',
                    paddingLeft: '1rem',
                    paddingRight: '1rem',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                    borderRadius: '0.5rem',
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: '#FFFFFF',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textDecoration: 'none',
                    boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #059669 0%, #047857 100%)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                    e.currentTarget.style.transform = 'scale(1.05) translateY(-1px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #10B981 0%, #059669 100%)';
                    e.currentTarget.style.boxShadow = '0 4px 14px rgba(16, 185, 129, 0.3)';
                    e.currentTarget.style.transform = 'scale(1) translateY(0)';
                  }}
                  suppressHydrationWarning
                >
                  {t('tryFree')}
                </Link>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={toggleDrawer}
                style={{
                  padding: '0.5rem',
                  borderRadius: '0.5rem',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'background 0.2s ease',
                  display: 'none',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#162032'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                className="md:!block"
                aria-label="Open menu"
              >
                <Menu style={{ width: '1.25rem', height: '1.25rem', color: '#94A3B8' }} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Drawer - Full Screen */}
      <AnimatePresence>
        {isDrawerOpen && (
          <motion.div
            style={{
              position: 'fixed',
              inset: 0,
              background: '#0B1120',
              zIndex: 50,
              display: 'flex',
              flexDirection: 'column',
              paddingTop: '1rem',
            }}
            initial="hidden"
            animate="visible"
            exit="exit"
            variants={drawerVariants}
          >
            {/* Header - matches navbar positioning */}
            <div style={{
              display: 'flex',
              height: '56px',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingLeft: '1.5rem',
              paddingRight: '1.5rem',
              paddingTop: '0.5rem',
              paddingBottom: '0.5rem',
            }}>
              <Link
                href="/"
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}
                onClick={() => setIsDrawerOpen(false)}
              >
                {/* cBIM Mark Logo */}
                <svg viewBox="0 0 24 24" width="24" height="24" style={{ display: 'block' }}>
                  <path
                    d="M11.52,3.84 A8.64,8.64 0 1,1 11.52,20.16"
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="1.92"
                    strokeLinecap="round"
                  />
                  <line
                    x1="13.25"
                    y1="4.42"
                    x2="13.25"
                    y2="11.78"
                    stroke="#10B981"
                    strokeWidth="1.15"
                    strokeLinecap="round"
                  />
                </svg>
                {/* cBIM Text */}
                <span style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '-0.02em', color: '#F1F5F9' }}>
                  <span style={{ color: '#10B981' }}>c</span>BIM
                </span>
              </Link>
              <button
                onClick={toggleDrawer}
                style={{
                  border: '1px solid #1E293B',
                  borderRadius: '0.5rem',
                  padding: '0.5rem',
                  cursor: 'pointer',
                  background: 'transparent',
                  transition: 'background 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#162032'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                aria-label="Close menu"
              >
                <X style={{ width: '1.25rem', height: '1.25rem', color: '#94A3B8' }} />
              </button>
            </div>

            {/* Navigation Links - Big Typography, Left Aligned */}
            <motion.nav
              style={{
                flex: 1,
                paddingLeft: '1.5rem',
                paddingRight: '1.5rem',
                paddingTop: '2rem',
              }}
              variants={drawerMenuContainerVariants}
            >
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {filteredNavLinks.map((item) => (
                  <motion.li
                    key={item.id}
                    variants={drawerMenuVariants}
                  >
                    <a
                      href={item.href}
                      onClick={(e) => {
                        if (!item.href.startsWith('#')) {
                          setIsDrawerOpen(false);
                          return;
                        }
                        e.preventDefault();
                        if (pathname !== '/') {
                          router.push(`/${item.href}`);
                          setIsDrawerOpen(false);
                          return;
                        }
                        const element = document.getElementById(item.href.substring(1));
                        element?.scrollIntoView({ behavior: 'smooth' });
                        setIsDrawerOpen(false);
                      }}
                      style={{
                        display: 'block',
                        paddingTop: '0.75rem',
                        paddingBottom: '0.75rem',
                        fontSize: '2.25rem',
                        fontWeight: 500,
                        fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                        letterSpacing: '-0.025em',
                        color: (item.href.startsWith('#') && pathname === '/' && activeSection === item.href.substring(1)) || (item.href === pathname)
                          ? '#E2E8F0'
                          : '#94A3B8',
                        textDecoration: 'none',
                        transition: 'color 0.2s ease',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#E2E8F0'}
                      onMouseLeave={(e) => {
                        const isActive = (item.href.startsWith('#') && pathname === '/' && activeSection === item.href.substring(1)) || (item.href === pathname);
                        e.currentTarget.style.color = isActive ? '#E2E8F0' : '#94A3B8';
                      }}
                    >
                      {item.name}
                    </a>
                  </motion.li>
                ))}
                {/* Mobile App Link */}
                <motion.li variants={drawerMenuVariants}>
                  <Link
                    href="/app"
                    onClick={() => setIsDrawerOpen(false)}
                    style={{
                      display: 'block',
                      paddingTop: '0.75rem',
                      paddingBottom: '0.75rem',
                      fontSize: '2.25rem',
                      fontWeight: 500,
                      fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                      letterSpacing: '-0.025em',
                      color: pathname === '/app' ? '#E2E8F0' : '#94A3B8',
                      textDecoration: 'none',
                      transition: 'color 0.2s ease',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#E2E8F0'}
                    onMouseLeave={(e) => e.currentTarget.style.color = pathname === '/app' ? '#E2E8F0' : '#94A3B8'}
                  >
                    Mobile
                  </Link>
                </motion.li>
              </ul>
            </motion.nav>

            {/* Footer Actions */}
            <div style={{
              paddingLeft: '1.5rem',
              paddingRight: '1.5rem',
              paddingBottom: '2rem',
              marginTop: 'auto',
            }}>
              <motion.div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.3 }}
              >
                {user ? (
                  <Link
                    href="/dashboard"
                    onClick={() => setIsDrawerOpen(false)}
                    style={{
                      width: '100%',
                      height: '3.5rem',
                      fontSize: '1.125rem',
                      fontWeight: 500,
                      fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                      borderRadius: '0.75rem',
                      background: '#059669',
                      color: '#FFFFFF',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      textDecoration: 'none',
                      transition: 'background 0.2s ease',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#047857'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#059669'}
                  >
                    Dashboard
                  </Link>
                ) : (
                  <Link
                    href={ctaLink}
                    onClick={() => {
                      trackCtaSignup();
                      setIsDrawerOpen(false);
                    }}
                    style={{
                      width: '100%',
                      height: '3.5rem',
                      fontSize: '1.125rem',
                      fontWeight: 500,
                      fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                      borderRadius: '0.75rem',
                      background: '#059669',
                      color: '#FFFFFF',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      textDecoration: 'none',
                      transition: 'background 0.2s ease',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#047857'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#059669'}
                    suppressHydrationWarning
                  >
                    {t('tryFree')}
                  </Link>
                )}

                {/* Theme Toggle */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}>
                  <ThemeToggle />
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

