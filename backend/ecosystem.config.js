module.exports = {
  apps: [{
    name: 'backend',
    script: 'api.py',
    interpreter: '/teamspace/studios/this_studio/carbonscope/suna-init/backend/.venv/bin/python',
    cwd: '/teamspace/studios/this_studio/carbonscope/suna-init/backend',
    env: {
      PYTHONPATH: '/teamspace/studios/this_studio/carbonscope/suna-init/backend'
    }
  }]
};
