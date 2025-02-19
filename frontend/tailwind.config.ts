import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'
import daisyui from 'daisyui'

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace']
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(59, 130, 246, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)' }
        }
      },
      animation: {
        glow: 'glow 2s ease-in-out infinite'
      }
    }
  },
  plugins: [
    typography,
    daisyui
  ],
  daisyui: {
    themes: [
      {
        industrial: {
          "primary": "#00ff9f",          // Vert néon
          "primary-content": "#000000",
          "secondary": "#0891b2",        // Cyan
          "accent": "#ff00ff",          // Rose néon
          "neutral": "#171717",         // Gris très foncé
          "base-100": "#0a0a0a",        // Noir profond
          "base-200": "#171717",        // Gris foncé
          "base-300": "#262626",        // Gris moyen
          "base-content": "#e5e7eb",    // Texte clair
          "info": "#00ffff",            // Cyan néon
          "success": "#00ff9f",         // Vert néon
          "warning": "#ffff00",         // Jaune néon
          "error": "#ff0000",           // Rouge néon
          
          // Personnalisation du thème
          "--rounded-box": "0.25rem",
          "--rounded-btn": "0.25rem",
          "--rounded-badge": "0.25rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.2s",
          "--btn-text-case": "uppercase",
          "--border-btn": "2px",
          "--tab-border": "2px",
          "--tab-radius": "0.25rem",
        },
        professional: {
          "primary": "#2563eb",          // Bleu professionnel
          "primary-content": "#ffffff",
          "secondary": "#475569",        // Gris slate
          "accent": "#0891b2",          // Cyan
          "neutral": "#f8fafc",         // Gris très clair
          "base-100": "#ffffff",        // Blanc
          "base-200": "#f8fafc",        // Gris très clair
          "base-300": "#f1f5f9",        // Gris clair
          "base-content": "#0f172a",    // Texte foncé
          "info": "#3b82f6",            // Bleu info
          "success": "#10b981",         // Vert
          "warning": "#f59e0b",         // Orange
          "error": "#ef4444",           // Rouge
          
          // Personnalisation du thème
          "--rounded-box": "0.5rem",
          "--rounded-btn": "0.375rem",
          "--rounded-badge": "0.375rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.2s",
          "--btn-text-case": "uppercase",
          "--border-btn": "1px",
          "--tab-border": "1px",
          "--tab-radius": "0.375rem",
        }
      }
    ],
    darkTheme: "industrial",
  }
} satisfies Config
