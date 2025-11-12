import type { Config } from 'tailwindcss';
import { tokens } from './src/lib/tokens';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        // Monotone palette from tokens (UI chrome only)
        'bg-primary': tokens.colors.bg.primary,
        'bg-secondary': tokens.colors.bg.secondary,
        'bg-tertiary': tokens.colors.bg.tertiary,
        'bg-inverse': tokens.colors.bg.inverse,
        'text-primary': tokens.colors.text.primary,
        'text-secondary': tokens.colors.text.secondary,
        'text-tertiary': tokens.colors.text.tertiary,
        'text-inverse': tokens.colors.text.inverse,

        // Semantic colors from tokens (data/status only)
        success: {
          DEFAULT: tokens.colors.semantic.success,
          foreground: 'hsl(142 76% 95%)',
        },
        warning: {
          DEFAULT: tokens.colors.semantic.warning,
          foreground: 'hsl(38 92% 95%)',
        },
        error: {
          DEFAULT: tokens.colors.semantic.error,
          foreground: 'hsl(0 72% 95%)',
        },
        neutral: {
          DEFAULT: tokens.colors.semantic.neutral,
          foreground: 'hsl(0 0% 95%)',
        },

        // ShadCN compatibility layer (keep for existing components)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      spacing: tokens.space,
      borderRadius: {
        none: tokens.radii.none,
        sm: tokens.radii.sm,
        md: tokens.radii.md,
        lg: tokens.radii.lg,
        xl: tokens.radii.xl,
        pill: tokens.radii.pill,
        // Keep ShadCN compatibility
        DEFAULT: 'var(--radius)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
      fontFamily: {
        sans: tokens.typography.families.sans.split(',').map((f) => f.trim()),
        mono: tokens.typography.families.mono.split(',').map((f) => f.trim()),
      },
      fontSize: {
        h1: tokens.typography.scale.h1,
        h2: tokens.typography.scale.h2,
        h3: tokens.typography.scale.h3,
        h4: tokens.typography.scale.h4,
        body: tokens.typography.scale.body,
        small: tokens.typography.scale.small,
        tiny: tokens.typography.scale.tiny,
      },
      fontWeight: {
        normal: tokens.typography.weights.normal.toString(),
        medium: tokens.typography.weights.medium.toString(),
        semibold: tokens.typography.weights.semibold.toString(),
        bold: tokens.typography.weights.bold.toString(),
      },
      transitionDuration: {
        instant: tokens.motion.duration.instant,
        fast: tokens.motion.duration.fast,
        base: tokens.motion.duration.base,
        slow: tokens.motion.duration.slow,
        slower: tokens.motion.duration.slower,
      },
      transitionTimingFunction: {
        'ease-default': tokens.motion.easing.ease,
        'ease-spring': tokens.motion.easing.spring,
      },
      boxShadow: {
        ...tokens.elevation,
      },
      zIndex: tokens.zIndex,
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
