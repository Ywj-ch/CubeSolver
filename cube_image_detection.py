# convert_cube_state.py
import cv2
import numpy as np
import os

class CubeDetector:
    def __init__(self):
        # 创建结果文件夹
        self.results_dir = 'cube_results'
        os.makedirs(self.results_dir, exist_ok=True)

        # 定义魔方六个面的标准颜色
        self.color_names = ['white', 'yellow', 'red', 'orange', 'blue', 'green']

        # 中心颜色到面名称的映射（根据你的命名）
        self.center_to_face = {
            'white': 'U',   # 上面
            'yellow': 'D',  # 下面
            'red': 'F',     # 前面
            'orange': 'B',   # 后面
            'blue': 'R',    # 左面
            'green': 'L'    # 右面
        }

    # TODO：识别算法目前不是很稳定，后序可以在这里提升优化
    @staticmethod
    def hsv_to_color(h, s, v):
        """根据HSV值判断颜色"""
        # 白色检测：低饱和度 + 高亮度
        if s < 50 and v > 150:
            return 'white'

        # 黄色检测
        elif 20 <= h <= 35 and s > 100:
            return 'yellow'

        # 橙色检测
        elif 10 <= h < 20 and s > 100:
            return 'orange'

        # 红色检测（注意红色在HSV环的两端）
        elif (h < 10 or h > 170) and s > 100:
            return 'red'

        # 绿色检测
        elif 35 <= h < 85 and s > 100:
            return 'green'

        # 蓝色检测
        elif 85 <= h < 130 and s > 100:
            return 'blue'

        else:
            return 'unknown'

    def detect_face_colors(self, image_path):
        """检测单个魔方面的9个颜色"""
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ 无法读取图像: {image_path}")
            return None

        # 预处理
        img = cv2.resize(img, (400, 400))
        img_blur = cv2.GaussianBlur(img, (5, 5), 0)
        hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

        # 检测3x3网格
        detected_face = []
        cell_size = 120
        margin = 20

        for i in range(3):
            row_colors = []
            for j in range(3):
                # 计算取样区域
                center_x = margin + j * cell_size + cell_size // 2
                center_y = margin + i * cell_size + cell_size // 2

                sample_size = 30
                x1 = max(0, center_x - sample_size // 2)
                y1 = max(0, center_y - sample_size // 2)
                x2 = min(400, center_x + sample_size // 2)
                y2 = min(400, center_y + sample_size // 2)

                sample_region = hsv[y1:y2, x1:x2]

                if sample_region.size == 0:
                    row_colors.append('unknown')
                    continue

                # 计算平均HSV
                avg_hsv = np.mean(sample_region, axis=(0, 1))
                h, s, v = avg_hsv

                # 检测颜色
                detected_color = self.hsv_to_color(h, s, v)
                row_colors.append(detected_color)

                # 在图像上标记
                cv2.putText(img, detected_color, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)

            detected_face.append(row_colors)

        return detected_face, img

    def detect_all_faces(self):
        """检测所有六个面"""
        images_dir = 'images'
        cube_state = {}

        print("=== 开始检测魔方六个面 ===")

        for color_name in self.color_names:
            img_path = os.path.join(images_dir, f"{color_name}.png")

            if not os.path.exists(img_path):
                print(f"❌ 图像不存在: {img_path}")
                continue

            print(f"\n🎯 检测 {color_name}.png (中心块: {color_name})")

            # 检测这个面的颜色
            face_colors, marked_img = self.detect_face_colors(img_path)

            if face_colors:
                # 根据中心块颜色确定面名称
                face_name = self.center_to_face[color_name]
                cube_state[face_name] = face_colors

                # 保存到结果文件夹
                result_path = os.path.join(self.results_dir, f'result_{face_name}_{color_name}.jpg')
                cv2.imwrite(result_path, marked_img)
                print(f"✅ {face_name}面结果保存: {result_path}")
                print(f"   检测结果: {face_colors}")

        return cube_state

    @staticmethod
    def display_cube_state(cube_state):
        """显示魔方状态"""
        print("\n" + "=" * 60)
        print("                 魔方六面状态报告")
        print("=" * 60)

        face_descriptions = {
            'U': '上面 (UP - 白色中心)',
            'R': '右面 (RIGHT - 蓝色中心)',
            'F': '前面 (FRONT - 红色中心)',
            'D': '下面 (DOWN - 黄色中心)',
            'L': '左面 (LEFT - 绿色中心)',
            'B': '后面 (BACK - 橙色中心)'
        }

        for face_name in ['U', 'R', 'F', 'D', 'L', 'B']:
            if face_name in cube_state:
                colors = cube_state[face_name]
                print(f"\n{face_descriptions[face_name]}:")
                for i, row in enumerate(colors):
                    print(f"  行{i + 1}: {row}")
            else:
                print(f"\n❌ 缺少 {face_descriptions[face_name]} 的数据")

        print("\n" + "=" * 60)

    def save_cube_state(self, cube_state, filename='cube_state.txt'):
        """保存魔方状态到文件"""
        # 保存到结果文件夹
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("魔方六面状态识别结果\n")
            f.write("=" * 50 + "\n\n")

            face_descriptions = {
                'U': '上面 (UP - 白色中心)',
                'R': '右面 (RIGHT - 蓝色中心)',
                'F': '前面 (FRONT - 红色中心)',
                'D': '下面 (DOWN - 黄色中心)',
                'L': '左面 (LEFT - 绿色中心)',
                'B': '后面 (BACK - 橙色中心)'
            }

            for face_name in ['U', 'R', 'F', 'D', 'L', 'B']:
                if face_name in cube_state:
                    f.write(f"{face_descriptions[face_name]}:\n")
                    for row in cube_state[face_name]:
                        f.write(f"  {row}\n")
                    f.write("\n")

        print(f"✅ 魔方状态已保存到: {filename}")


def main():
    """主函数 - 六面魔方识别"""
    detector = CubeDetector()

    # 直接检测images目录下的6张图片
    cube_state = detector.detect_all_faces()

    if len(cube_state) == 6:
        # 显示结果
        detector.display_cube_state(cube_state)

        # 保存结果
        detector.save_cube_state(cube_state)

        print("🎉 魔方六面识别完成！")
        print("📁 每个面的标记图像已保存为 result_面名_中心颜色.jpg")
    else:
        print(f"❌ 识别不完整，只识别了 {len(cube_state)}/6 个面")
        if cube_state:
            detector.display_cube_state(cube_state)


if __name__ == "__main__":
    main()
