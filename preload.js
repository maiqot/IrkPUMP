// Intentionally minimal preload to keep renderer isolated from Node.
// You can expose safe APIs via contextBridge here if needed later.
const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('appInfo', {
	version: '1.0.0'
});
