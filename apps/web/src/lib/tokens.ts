/**
 * Design System Tokens - Single Source of Truth
 *
 * This file defines all design tokens for the Peter dashboard platform.
 * All styling must reference these tokens - NO hardcoded colors or spacing.
 *
 * Monotone Theme Philosophy:
 * - UI chrome: Black/white/grey only
 * - Data/status: Semantic colors (success, warning, error, neutral)
 * - Charts: Greyscale gradients as default
 */

export const tokens = {
  /**
   * Color Tokens
   * Monotone palette for UI chrome, semantic colors for data/status only
   */
  colors: {
    // Background tones (monotone only)
    bg: {
      primary: 'hsl(0 0% 100%)',        // #FFFFFF - light mode white
      secondary: 'hsl(0 0% 97.6%)',     // #F9F9F9 - subtle grey
      tertiary: 'hsl(0 0% 95.3%)',      // #F3F3F3 - medium grey
      inverse: 'hsl(0 0% 3.9%)',        // #0A0A0A - dark mode black
    },

    // Text tones (monotone hierarchy)
    text: {
      primary: 'hsl(0 0% 3.9%)',        // #0A0A0A - high contrast black
      secondary: 'hsl(0 0% 32.2%)',     // #525252 - medium grey
      tertiary: 'hsl(0 0% 45.1%)',      // #737373 - light grey
      inverse: 'hsl(0 0% 98%)',         // #FAFAFA - dark mode text
    },

    // Border and dividers (monotone)
    border: {
      default: 'hsl(0 0% 89.8%)',       // #E5E5E5 - light mode
      dark: 'hsl(0 0% 25.1%)',          // #404040 - dark mode
    },

    // Semantic colors (DATA AND STATUS ONLY - not for UI chrome)
    semantic: {
      success: 'hsl(142 76% 36%)',      // #10B981 - green
      warning: 'hsl(38 92% 50%)',       // #F59E0B - amber
      error: 'hsl(0 72% 51%)',          // #EF4444 - red
      neutral: 'hsl(0 0% 50%)',         // #808080 - neutral grey
    },

    // Chart palette (greyscale gradients, HSL for programmatic variation)
    charts: {
      mono: [
        'hsl(0 0% 10%)',   // Darkest
        'hsl(0 0% 25%)',
        'hsl(0 0% 40%)',
        'hsl(0 0% 55%)',
        'hsl(0 0% 70%)',
        'hsl(0 0% 85%)',   // Lightest
      ],
      // Semantic colors for data when meaning is conveyed
      data: {
        positive: 'hsl(142 76% 36%)',   // Green for growth/profit
        negative: 'hsl(0 72% 51%)',     // Red for decline/loss
        neutral: 'hsl(0 0% 50%)',       // Grey for neutral
        highlight: 'hsl(217 91% 60%)',  // Blue for focus (use sparingly)
      },
    },

    // Focus and selection states
    interactive: {
      focus: 'hsl(0 0% 0%)',            // Black ring in light mode
      focusDark: 'hsl(0 0% 100%)',      // White ring in dark mode
      selection: 'hsla(0 0% 0% / 0.1)', // 10% black overlay
      hover: 'hsla(0 0% 0% / 0.05)',    // 5% black overlay
    },
  },

  /**
   * Typography Tokens
   * Inter font family with system fallbacks
   */
  typography: {
    families: {
      sans: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: 'ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace',
    },

    // Modular scale (1.125 ratio - perfect fourth)
    scale: {
      h1: '32px',     // 2rem
      h2: '24px',     // 1.5rem
      h3: '20px',     // 1.25rem
      h4: '16px',     // 1rem
      body: '16px',   // 1rem (base)
      small: '14px',  // 0.875rem
      tiny: '12px',   // 0.75rem
    },

    // Font weights (Inter supports 400-700)
    weights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },

    // Line heights (relative to font size)
    lineHeights: {
      tight: 1.25,    // Headings
      normal: 1.5,    // Body text
      relaxed: 1.75,  // Long-form content
    },

    // Letter spacing
    letterSpacing: {
      tight: '-0.02em',
      normal: '0',
      wide: '0.05em',
    },
  },

  /**
   * Spacing Tokens
   * 4px base rhythm (consistent vertical and horizontal spacing)
   */
  space: {
    x0: '0px',      // 0
    x1: '4px',      // 0.25rem
    x2: '8px',      // 0.5rem
    x3: '12px',     // 0.75rem
    x4: '16px',     // 1rem
    x5: '20px',     // 1.25rem
    x6: '24px',     // 1.5rem
    x8: '32px',     // 2rem
    x10: '40px',    // 2.5rem
    x12: '48px',    // 3rem
    x16: '64px',    // 4rem
    x20: '80px',    // 5rem
    x24: '96px',    // 6rem
  },

  /**
   * Border Radius Tokens
   * Consistent corner treatments across components
   */
  radii: {
    none: '0px',
    sm: '4px',      // Inputs, small cards
    md: '8px',      // Cards, buttons
    lg: '12px',     // Modals, large cards
    xl: '16px',     // Hero sections
    pill: '9999px', // Fully rounded (badges, pills)
  },

  /**
   * Motion Tokens
   * Animation durations and easing curves
   */
  motion: {
    duration: {
      instant: '0ms',
      fast: '120ms',    // Micro-interactions (hover, focus)
      base: '200ms',    // Standard transitions
      slow: '320ms',    // Complex animations
      slower: '500ms',  // Page transitions
    },

    easing: {
      linear: 'linear',
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',      // Standard ease
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',      // Decelerate
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',     // Accelerate
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)', // Smooth
      spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)', // Bouncy
    },
  },

  /**
   * Elevation Tokens
   * Shadow presets for layering UI elements
   */
  elevation: {
    0: 'none',
    1: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    2: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
    3: '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',
    4: '0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)',
  },

  /**
   * Breakpoint Tokens
   * Responsive design breakpoints (mobile-first)
   */
  breakpoints: {
    sm: '360px',    // Small mobile
    md: '768px',    // Tablet
    lg: '1024px',   // Desktop
    xl: '1280px',   // Large desktop
    xxl: '1536px',  // Extra large
  },

  /**
   * Grid Tokens
   * 12-column responsive grid system
   */
  grid: {
    columns: 12,
    gutters: {
      mobile: '16px',   // 1rem
      desktop: '24px',  // 1.5rem
    },
    maxWidth: '1440px',
  },

  /**
   * Z-Index Tokens
   * Layering hierarchy for stacking context
   */
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    overlay: 1200,
    modal: 1300,
    popover: 1400,
    toast: 1500,
    tooltip: 1600,
  },

  /**
   * Opacity Tokens
   * Transparency levels for overlays and disabled states
   */
  opacity: {
    disabled: 0.4,
    hover: 0.9,
    overlay: 0.8,
    subtle: 0.6,
  },
} as const;

/**
 * Type export for TypeScript autocomplete
 */
export type Tokens = typeof tokens;

/**
 * CSS Variable Names
 * Reference these in Tailwind config or CSS
 */
export const cssVars = {
  // Colors
  '--color-bg-primary': tokens.colors.bg.primary,
  '--color-bg-secondary': tokens.colors.bg.secondary,
  '--color-bg-tertiary': tokens.colors.bg.tertiary,
  '--color-text-primary': tokens.colors.text.primary,
  '--color-text-secondary': tokens.colors.text.secondary,
  '--color-text-tertiary': tokens.colors.text.tertiary,
  '--color-border': tokens.colors.border.default,
  '--color-success': tokens.colors.semantic.success,
  '--color-warning': tokens.colors.semantic.warning,
  '--color-error': tokens.colors.semantic.error,

  // Spacing
  '--space-x1': tokens.space.x1,
  '--space-x2': tokens.space.x2,
  '--space-x3': tokens.space.x3,
  '--space-x4': tokens.space.x4,
  '--space-x6': tokens.space.x6,
  '--space-x8': tokens.space.x8,

  // Typography
  '--font-sans': tokens.typography.families.sans,
  '--font-mono': tokens.typography.families.mono,

  // Radii
  '--radius-sm': tokens.radii.sm,
  '--radius-md': tokens.radii.md,
  '--radius-lg': tokens.radii.lg,

  // Motion
  '--motion-fast': tokens.motion.duration.fast,
  '--motion-base': tokens.motion.duration.base,
  '--motion-slow': tokens.motion.duration.slow,
  '--motion-ease': tokens.motion.easing.ease,
} as const;
