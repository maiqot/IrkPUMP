# IrkPUMP - Инженерный калькулятор ЭЦН

Электронное приложение для расчета и подбора электроцентробежных насосов (ЭЦН).

## Возможности

- Расчет параметров скважины и флюида
- Подбор оптимального насоса
- Визуализация характеристик насоса
- Темная/светлая тема

## Установка и запуск

### Требования
- Node.js 16+ 
- npm

### Установка зависимостей (Node)
```bash
npm install
```

### Запуск в режиме разработки
```bash
npm start
```

### Сборка приложения

#### macOS
```bash
npm run dist
```

#### Windows
```bash
npm run dist:win
```

#### Все платформы
```bash
npm run dist:all
```

## Python (альтернатива Electron)

### Требования
- Python 3.9+

### Установка зависимостей
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Запуск
```bash
make run
```

### Сборка (PyInstaller)
```bash
make build-mac   # macOS .app в dist/
make build-win   # Windows .exe (на Windows)
```

## Структура проекта

- `main.js` - основной процесс Electron
- `preload.js` - скрипт предзагрузки
- `IrkPUMP v6.html` - интерфейс приложения
- `package.json` - конфигурация проекта

## Сборка

Приложение собирается с помощью electron-builder и поддерживает:
- macOS (.dmg)
- Windows (.exe)
- Linux (.AppImage)

## Лицензия

ISC