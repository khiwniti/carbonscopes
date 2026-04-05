// app/fonts/instrument-serif.ts
// CarbonScope Display Font - Geological/Strata Metaphor
import { Instrument_Serif } from 'next/font/google';

export const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  variable: '--font-instrument',
  display: 'swap',
  weight: '400', // Only 400 available for Instrument Serif
});
