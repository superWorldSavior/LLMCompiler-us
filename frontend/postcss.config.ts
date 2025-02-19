import type { Config } from 'postcss'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'

export default {
  plugins: {
    tailwindcss,
    autoprefixer,
  },
} satisfies Config
