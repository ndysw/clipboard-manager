from PIL import Image, ImageDraw, ImageFont

# 创建256x256的图标
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# 绘制圆形背景（蓝色渐变）
center = size // 2
radius = size // 2 - 10

# 绘制主圆形背景
draw.ellipse([10, 10, size-10, size-10], fill=(41, 128, 185, 255), outline=(52, 152, 219, 255), width=4)

# 绘制剪贴板图标
# 绘制剪贴板顶部夹子
clip_width = 60
clip_height = 20
clip_x = center - clip_width // 2
clip_y = 50
draw.rectangle([clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
               fill=(236, 240, 241, 255), outline=(189, 195, 199, 255), width=3)

# 绘制剪贴板主体
board_width = 120
board_height = 140
board_x = center - board_width // 2
board_y = clip_y + clip_height - 5
draw.rectangle([board_x, board_y, board_x + board_width, board_y + board_height],
               fill=(255, 255, 255, 255), outline=(189, 195, 199, 255), width=4)

# 绘制三条横线表示文本
line_margin = 20
line_width = 80
line_x = center - line_width // 2
for i in range(3):
    line_y = board_y + 30 + i * 25
    draw.rectangle([line_x, line_y, line_x + line_width, line_y + 6],
                   fill=(52, 152, 219, 255))

# 绘制历史记录图标（右下角小圆圈带时钟）
history_radius = 35
history_x = size - 60
history_y = size - 60
draw.ellipse([history_x - history_radius, history_y - history_radius,
              history_x + history_radius, history_y + history_radius],
             fill=(46, 204, 113, 255), outline=(39, 174, 96, 255), width=3)

# 绘制时钟指针
draw.line([history_x, history_y, history_x, history_y - 15],
          fill=(255, 255, 255, 255), width=4)
draw.line([history_x, history_y, history_x + 10, history_y],
          fill=(255, 255, 255, 255), width=4)

# 保存为多种尺寸
sizes = [16, 32, 48, 64, 128, 256]
image.save('icon_256.png')

# 创建ICO文件（包含多种尺寸）
icon_images = []
for s in sizes:
    resized = image.resize((s, s), Image.Resampling.LANCZOS)
    icon_images.append(resized)

# 保存为ICO
icon_images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes], append_images=icon_images[1:])

print("Icon created successfully!")
print("   - icon.ico (multi-size)")
print("   - icon_256.png (preview)")
