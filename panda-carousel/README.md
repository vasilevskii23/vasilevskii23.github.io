# Lifotronic · креативная карусель

5 слайдов Instagram **1080×1350 (4:5)** про плюшевую панду в худи Lifotronic.

| # | Файл | Концепт |
|---|------|---------|
| 01 | `slides/carousel_01.jpg` | Hero — **LIFOTRONIC / PAIR PROGRAMMER** |
| 02 | `slides/carousel_02.jpg` | Макро — **DEBUG BUDDY** |
| 03 | `slides/carousel_03.jpg` | Профиль — вертикаль **CODE** |
| 04 | `slides/carousel_04.jpg` | **ON CALL / watching the build** |
| 05 | `slides/carousel_05.jpg` | Lockup — **Soft mascot. Serious tools.** |

Превью всех слайдов: `slides/carousel_preview.jpg`

## Viewer

```bash
cd panda-carousel && python3 -m http.server 8765
```

Открыть http://127.0.0.1:8765/ — свайп, кнопки, точки, стрелки.

## Пересборка

```bash
python3 build_slides.py
```

Исходники: `assets/src-0*.jpg` · шрифты: `fonts/`
