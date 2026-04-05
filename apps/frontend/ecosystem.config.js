module.exports = {
  apps: [{
    name: 'frontend',
    script: '../../node_modules/.bin/next',
    args: 'dev --port 3003',
    cwd: '/teamspace/studios/this_studio/carbonscope/suna-init/apps/frontend',
    node_args: '--max-old-space-size=8192',
    env: {
      NODE_ENV: 'development'
    }
  }]
};
