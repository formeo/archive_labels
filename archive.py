from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
import os

# Регистрируем шрифт с поддержкой кириллицы
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
    print("✅ Шрифты DejaVu загружены")
except:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    print("⚠️  Шрифты DejaVu не найдены. Используем стандартные.")


class DocumentBox:
    def __init__(self, owner, doc_type, start_year, end_year, contents, box_number, style="modern"):
        self.owner = owner
        self.doc_type = doc_type
        self.start_year = start_year
        self.end_year = end_year
        self.contents = contents
        self.box_number = box_number
        self.style = style


def create_modern_label(pdf, box, x, y):
    """Создает современную этикетку"""
    width = 95 * mm  # Уменьшили ширину для 2 этикеток в ряд
    height = 65 * mm  # Уменьшили высоту для 4 этикеток на странице

    # Фон и рамка
    pdf.setFillColorRGB(0.94, 0.97, 1.0)  # Светло-голубой
    pdf.setStrokeColorRGB(0.18, 0.52, 0.67)  # Синий
    pdf.setLineWidth(0.5)
    pdf.roundRect(x, y, width, height, 3 * mm, stroke=1, fill=1)

    # Заголовок с цветным фоном
    pdf.setFillColorRGB(0.18, 0.52, 0.67)  # Синий
    pdf.setStrokeColorRGB(0.18, 0.52, 0.67)
    pdf.roundRect(x, y + height - 12 * mm, width, 12 * mm, 3 * mm, stroke=1, fill=1)

    pdf.setFillColorRGB(1, 1, 1)  # Белый текст
    pdf.setFont(FONT_BOLD, 10)
    pdf.drawCentredString(x + width / 2, y + height - 9 * mm, "АРХИВ")
    pdf.setFillColorRGB(0, 0, 0)  # Черный текст

    # Содержимое (уменьшенные шрифты)
    pdf.setFont(FONT_NAME, 8)
    pdf.drawString(x + 5 * mm, y + height - 20 * mm, "Владелец:")
    pdf.setFont(FONT_BOLD, 9)
    pdf.drawString(x + 22 * mm, y + height - 20 * mm, _truncate_text(box.owner, 20))

    pdf.setFont(FONT_NAME, 8)
    pdf.drawString(x + 5 * mm, y + height - 27 * mm, "Тип:")
    pdf.setFont(FONT_BOLD, 8)
    pdf.drawString(x + 22 * mm, y + height - 27 * mm, _truncate_text(box.doc_type, 25))

    pdf.setFont(FONT_NAME, 8)
    pdf.drawString(x + 5 * mm, y + height - 34 * mm, "Период:")
    pdf.setFont(FONT_BOLD, 8)
    period = f"{box.start_year}-{box.end_year}"
    pdf.drawString(x + 22 * mm, y + height - 34 * mm, period)

    pdf.setFont(FONT_NAME, 7)
    pdf.drawString(x + 5 * mm, y + height - 41 * mm, "Содержание:")

    # Многострочное содержимое
    contents_text = _truncate_text(box.contents, 40)
    lines = _wrap_text(contents_text, pdf, FONT_NAME, 7, width - 10 * mm)
    for i, line in enumerate(lines[:3]):  # Максимум 3 строки
        pdf.drawString(x + 5 * mm, y + height - (48 + i * 4) * mm, line)

    # Номер коробки
    pdf.setFont(FONT_BOLD, 9)
    pdf.drawRightString(x + width - 5 * mm, y + 3 * mm, f"№{box.box_number}")


def create_classic_label(pdf, box, x, y):
    """Создает классическую этикетку (компактную)"""
    width = 95 * mm
    height = 65 * mm

    # Рамка
    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.setLineWidth(0.3)
    pdf.rect(x, y, width, height)

    # Заголовок
    pdf.setFont(FONT_BOLD, 12)
    pdf.drawCentredString(x + width / 2, y + height - 8 * mm, "АРХИВ")

    # Линия под заголовком
    pdf.line(x + 5 * mm, y + height - 10 * mm, x + width - 5 * mm, y + height - 10 * mm)

    # Содержимое
    pdf.setFont(FONT_NAME, 8)
    pdf.drawString(x + 5 * mm, y + height - 18 * mm, "Владелец:")
    pdf.setFont(FONT_BOLD, 8)
    pdf.drawString(x + 25 * mm, y + height - 18 * mm, _truncate_text(box.owner, 18))

    pdf.setFont(FONT_NAME, 7)
    pdf.drawString(x + 5 * mm, y + height - 25 * mm, "Тип документов:")
    pdf.setFont(FONT_BOLD, 7)
    pdf.drawString(x + 5 * mm, y + height - 30 * mm, _truncate_text(box.doc_type, 30))

    pdf.setFont(FONT_NAME, 7)
    pdf.drawString(x + 5 * mm, y + height - 37 * mm, "Период:")
    pdf.setFont(FONT_BOLD, 7)
    period = f"{box.start_year}-{box.end_year}"
    pdf.drawString(x + 22 * mm, y + height - 37 * mm, period)

    # Содержание (кратко)
    pdf.setFont(FONT_NAME, 6)
    contents = _truncate_text(box.contents, 35)
    pdf.drawString(x + 5 * mm, y + height - 44 * mm, "Содержание:")
    pdf.drawString(x + 5 * mm, y + height - 49 * mm, _truncate_text(contents, 40))

    # Номер коробки
    pdf.setFont(FONT_NAME, 8)
    pdf.drawString(x + 5 * mm, y + 3 * mm, f"Коробка №{box.box_number}")


def _truncate_text(text, max_length):
    """Обрезает текст если он слишком длинный"""
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def _wrap_text(text, pdf, font_name, font_size, max_width):
    """Разбивает текст на несколько строк"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if pdf.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def generate_pdf_compact(boxes, filename):
    """Генерирует PDF с 4 этикетками на странице"""
    pdf = canvas.Canvas(filename, pagesize=A4)
    page_width, page_height = A4

    # Параметры сетки (2x2 этикетки на странице)
    labels_per_row = 2
    labels_per_column = 2
    labels_per_page = labels_per_row * labels_per_column

    label_width = 95 * mm
    label_height = 65 * mm

    # Отступы от краев страницы
    margin_x = (page_width - (labels_per_row * label_width)) / 2
    margin_y = (page_height - (labels_per_column * label_height)) / 2

    for i, box in enumerate(boxes):
        # Если страница заполнена, создаем новую
        if i > 0 and i % labels_per_page == 0:
            pdf.showPage()

        # Вычисляем позицию этикетки в сетке
        page_index = i % labels_per_page
        row = page_index // labels_per_row
        col = page_index % labels_per_row

        x = margin_x + (col * label_width)
        y = margin_y + ((labels_per_column - 1 - row) * label_height)  # Сверху вниз

        # Создаем этикетку в зависимости от стиля
        if box.style == "classic":
            create_classic_label(pdf, box, x, y)
        else:
            create_modern_label(pdf, box, x, y)

    pdf.save()
    print(f"✅ PDF успешно создан: {filename}")
    print(f"📄 Всего страниц: {(len(boxes) + labels_per_page - 1) // labels_per_page}")
    print(f"🏷️  Всего этикеток: {len(boxes)}")


def main():
    # Данные для этикеток - можно добавить сколько угодно!
    boxes = [
        DocumentBox(owner="Ваня", doc_type="Школьные документы",
                    start_year=2015, end_year=2023,
                    contents="Табели, дипломы олимпиад, творческие работы",
                    box_number=1, style="modern"),

        DocumentBox(owner="Степа", doc_type="Медицинские карты",
                    start_year=2010, end_year=2022,
                    contents="Карты из поликлиники, прививочный сертификат",
                    box_number=2, style="classic"),

        DocumentBox(owner="Семейные", doc_type="Финансовые документы",
                    start_year=2018, end_year=2024,
                    contents="Квитанции ЖКХ, налоговые декларации",
                    box_number=3, style="modern"),

        DocumentBox(owner="Мария", doc_type="Личные документы",
                    start_year=2005, end_year=2023,
                    contents="Паспорт, дипломы, трудовая книжка",
                    box_number=4, style="modern"),

        DocumentBox(owner="Работа", doc_type="Рабочие документы",
                    start_year=2018, end_year=2023,
                    contents="Договоры, отчеты, служебные записки",
                    box_number=5, style="classic"),

        DocumentBox(owner="Дача", doc_type="Дачные документы",
                    start_year=2015, end_year=2023,
                    contents="Договор аренды, квитанции, схемы",
                    box_number=6, style="modern"),

        DocumentBox(owner="Авто", doc_type="Автомобильные документы",
                    start_year=2019, end_year=2024,
                    contents="СТС, ОСАГО, талоны ТО",
                    box_number=7, style="classic"),

        DocumentBox(owner="Фото", doc_type="Фотографии и альбомы",
                    start_year=2000, end_year=2023,
                    contents="Семейные фото, альбомы, негативы",
                    box_number=8, style="modern"),
    ]

    generate_pdf_compact(boxes, "archive_labels_compact.pdf")


if __name__ == "__main__":
    main()
