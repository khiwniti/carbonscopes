/**
 * Cloudflare Pages preparation script
 * Copies workspace dependencies to node_modules before build
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..', '..');
const frontendNodeModules = path.join(__dirname, '..', 'node_modules');
const sharedSource = path.join(rootDir, 'packages', 'shared');
const sharedDest = path.join(frontendNodeModules, '@agentpress', 'shared');

// Ensure @agentpress directory exists
const agentpressDir = path.join(frontendNodeModules, '@agentpress');
if (!fs.existsSync(agentpressDir)) {
  fs.mkdirSync(agentpressDir, { recursive: true });
}

// Copy shared package
if (fs.existsSync(sharedSource)) {
  if (fs.existsSync(sharedDest)) {
    fs.rmSync(sharedDest, { recursive: true });
  }
  copyDir(sharedSource, sharedDest);
  console.log('✓ Copied @agentpress/shared to node_modules');
} else {
  console.log('⚠ @agentpress/shared not found, assuming already installed');
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

console.log('✓ Cloudflare preparation complete');