# Обработка смазанного фото по референсу

Исходник: сильный motion blur ночного кадра.  
Референс: ночная long-exposure эстетика (глубокий чёрный, золотые блики, cyan-трейлы).

## Запуск

```bash
python3 process_photo.py
```

## Результат

| Файл | Описание |
|------|----------|
| `output/processed_full.jpg` | Полный размер (3024×4032) |
| `output/processed_web.jpg` | Уменьшенная версия для просмотра |
| `output/before_after.jpg` | Сравнение до/после |

Пайплайн: EXIF-ориентация → подтяжка экспозиции → мягкий LAB match к референсу → bilateral sharpen → night curve → teal/orange grade → bloom трейлов → виньетка → зерно.
