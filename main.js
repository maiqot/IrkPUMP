const { app, BrowserWindow } = require('electron');
const path = require('path');

function createMainWindow() {
	const mainWindow = new BrowserWindow({
		width: 1280,
		height: 800,
		webPreferences: {
			contextIsolation: true,
			enableRemoteModule: false,
			nodeIntegration: false,
			preload: path.join(__dirname, 'preload.js')
		}
	});

	const htmlPath = path.join(__dirname, 'IrkPUMP v6.html');
	mainWindow.loadFile(htmlPath);

	// Uncomment to open DevTools by default during development
	// if (!app.isPackaged) mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
	createMainWindow();

	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
	});
});

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit();
	}
});
