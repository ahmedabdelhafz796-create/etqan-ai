import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mockuplib import *
import matplotlib.pyplot as plt

# ============================================================ 3.2 Store dashboard mockup
def fig_03_01_dashboard():
    fig, ax = new_canvas(w=10.4, h=6.2)
    x, cy, w, ch = browser_window(ax, 0.2, 0.2, 10.0, 5.8, url="admin.mystore.com/dashboard")

    # sidebar
    sidebar_w = 2.0
    ax.add_patch(Rectangle((x, cy), sidebar_w, ch, facecolor=NAVY_DEEP, edgecolor="none", zorder=2))
    items = ["الرئيسية", "الطلبات", "المنتجات", "العملاء", "التحليلات", "الإعدادات"]
    item_h = ch / (len(items) + 1)
    for i, label in enumerate(items):
        sidebar_item(ax, x, cy + ch - item_h * (i + 2), sidebar_w, item_h * 0.8, label, active=(i == 0))

    # top stat cards
    card_y = cy + ch - 1.3
    card_w = (w - sidebar_w - 0.6) / 3
    stats = [("إجمالي المبيعات", "48,250 ر.س", GREEN), ("الطلبات الجديدة", "132", GOLD),
             ("زوار اليوم", "2,840", BLUE)]
    for i, (label, value, color) in enumerate(stats):
        cx = x + sidebar_w + 0.2 + i * (card_w + 0.2)
        rounded_box(ax, cx, card_y, card_w, 1.1, color="#F9FAFB", edge=LIGHT_GREY, radius=0.08, zorder=3)
        ax.text(cx + 0.2, card_y + 0.8, label, fontsize=9, color=GREY, ha="left", zorder=4)
        ax.text(cx + 0.2, card_y + 0.35, value, fontsize=15, color=color, fontweight="bold", ha="left", zorder=4)

    # simple order table
    table_x = x + sidebar_w + 0.2
    table_y = cy + 0.3
    table_w = w - sidebar_w - 0.6
    table_h = card_y - 0.2 - table_y
    rounded_box(ax, table_x, table_y, table_w, table_h, color="#F9FAFB", edge=LIGHT_GREY, radius=0.06, zorder=3)
    ax.text(table_x + 0.2, table_y + table_h - 0.3, "أحدث الطلبات", fontsize=11, color=NAVY,
            fontweight="bold", ha="left", zorder=4)
    rows = [("#1042", "أحمد سالم", "قيد الشحن", GOLD), ("#1041", "منى خالد", "تم التسليم", GREEN),
            ("#1040", "سعيد فهد", "قيد المعالجة", BLUE)]
    row_h = (table_h - 0.6) / len(rows)
    for i, (oid, name, status, color) in enumerate(rows):
        ry = table_y + table_h - 0.7 - i * row_h
        ax.text(table_x + 0.2, ry, oid, fontsize=9.5, color=NAVY, ha="left", zorder=4)
        ax.text(table_x + 1.6, ry, name, fontsize=9.5, color=NAVY, ha="left", zorder=4)
        ax.text(table_x + table_w - 0.3, ry, status, fontsize=9.5, color=color, fontweight="bold",
                ha="right", zorder=4)
    save(fig, "fig-03-01-dashboard")


# ============================================================ 3.3 Product page mockup
def fig_03_02_product_page():
    fig, ax = new_canvas(w=10.4, h=6.4)
    x, cy, w, ch = browser_window(ax, 0.2, 0.2, 10.0, 6.0, url="mystore.com/product/watch-01")

    # image gallery (left in RTL = right visually, but keep simple LTR box layout)
    img_w = w * 0.42
    rounded_box(ax, x + 0.3, cy + ch - 3.6, img_w, 3.1, color="#F3F4F6", edge=LIGHT_GREY, radius=0.06, zorder=3)
    ax.text(x + 0.3 + img_w / 2, cy + ch - 2.05, "صورة المنتج", fontsize=10, color=GREY, ha="center", zorder=4)
    thumb_w = (img_w - 0.3) / 4
    for i in range(4):
        rounded_box(ax, x + 0.3 + i * (thumb_w + 0.1), cy + ch - 4.05, thumb_w, 0.35,
                    color="#E5E7EB", edge=LIGHT_GREY, radius=0.05, zorder=3)

    # details column
    details_x = x + 0.3 + img_w + 0.4
    details_w = w - img_w - 1.0
    ax.text(details_x, cy + ch - 0.5, "ساعة يد كلاسيكية — طراز 2026", fontsize=13, color=NAVY,
            fontweight="bold", ha="left", zorder=4)
    ax.text(details_x, cy + ch - 0.95, "★★★★★  (312 تقييم)", fontsize=9.5, color=GOLD, ha="left", zorder=4)
    ax.text(details_x, cy + ch - 1.5, "349 ر.س", fontsize=16, color=GREEN, fontweight="bold", ha="left", zorder=4)
    desc = "تصميم أنيق يناسب الإطلالة اليومية والمناسبات معًا، بضمان استبدال\nكامل خلال 30 يومًا دون أي تعقيد."
    for i, line in enumerate(desc.split("\n")):
        ax.text(details_x, cy + ch - 2.0 - i * 0.3, line, fontsize=9.5, color="#4B5563", ha="left", zorder=4)
    button(ax, details_x, cy + ch - 3.35, details_w * 0.85, 0.55, "أضف إلى السلة", color=GOLD)
    ax.text(details_x, cy + ch - 3.75, "دفع آمن  •  شحن خلال 3 أيام  •  إرجاع مجاني", fontsize=8.5,
            color=GREY, ha="left", zorder=4)

    annotate_point(ax, details_x + details_w * 0.2, cy + ch - 3.08, "زر شراء بارز وواضح",
                   details_x + details_w + 0.3, cy + ch - 2.6, color=RED, ha="left")
    annotate_point(ax, details_x + 2.0, cy + ch - 0.95, "دليل اجتماعي (تقييمات)",
                   details_x + details_w + 0.3, cy + ch - 0.6, color=RED, ha="left")
    save(fig, "fig-03-02-product-page")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("fig_")]
    for fn in fns:
        fn()
        print("generated", fn.__name__)
    print(f"\nTotal figures: {len(fns)}")
