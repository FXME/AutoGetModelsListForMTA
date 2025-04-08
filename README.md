# IDE Files Processor

![GUI Screenshot](https://i.imgur.com/wJhnwbv.png)

## 📌 Назначение

**IDE Files Processor** — это специализированная утилита для разработчиков модификаций игр серии GTA (San Andreas, Vice City и др.).  
Она автоматизирует работу с `.ide` файлами — важнейшими конфигурационными файлами, содержащими данные об игровых объектах.

### Основные функции:
- 🔍 Рекурсивный парсинг всех `.ide` файлов в указанной директории и подпапках
- 📤 Экспорт данных в 3 форматах:
  - `CModelNames.txt` — для использования в массиве `bigFOTable` (файл: `Client\mods\deathmatch\logic\CModelNames.cpp`)
  - `objects.xml` — для ресурса editor_gui (файл: `\client\browser\objects.xml`)
  - `editor_main.txt` — для ресурса editor_main (файл: `\server\getObjectNameFromModel.lua`)
- 🖥 Удобный графический интерфейс с отображением прогресса и логов

---

## 🛠 Установка source кода

### Требования:
- Python **3.6+**
- Библиотека `tkinter` (входит в стандартную поставку Python)

Видео-инструкция по использованию - https://youtu.be/r-49PEifDaY
