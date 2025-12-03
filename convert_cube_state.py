# convert_cube_state.py
import twophase.solver as sv

def parse_cube_state_from_file(filename='cube_results/cube_state.txt'):
    """
    从cube_state.txt文件中解析魔方状态
    """
    cube_state = {}

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_face = None
    face_data = []

    for line in lines:
        line = line.strip()

        # 检测面开始
        if '上面 (UP' in line:
            current_face = 'U'
            face_data = []
        elif '右面 (RIGHT' in line:
            current_face = 'R'
            face_data = []
        elif '前面 (FRONT' in line:
            current_face = 'F'
            face_data = []
        elif '下面 (DOWN' in line:
            current_face = 'D'
            face_data = []
        elif '左面 (LEFT' in line:
            current_face = 'L'
            face_data = []
        elif '后面 (BACK' in line:
            current_face = 'B'
            face_data = []

        # 解析颜色行
        elif line.startswith("['") and current_face:
            # 提取颜色列表，例如: "['red', 'orange', 'blue']"
            colors_str = line.replace("'", "").replace("[", "").replace("]", "")
            colors = [color.strip() for color in colors_str.split(',')]
            face_data.extend(colors)

            # 如果收集到9个颜色，保存这个面
            if len(face_data) == 9:
                cube_state[current_face] = face_data.copy()
                face_data = []

    return cube_state


def convert_to_kociemba_format(cube_state):
    """
    将解析的魔方状态转换为kociemba格式
    """
    # 颜色映射到kociemba字符
    color_mapping = {
        'white': 'U',   # 上
        'yellow': 'D',  # 下
        'red': 'F',     # 前
        'orange': 'B',  # 后
        'blue': 'R',    # 右
        'green': 'L'    # 左
    }

    # kociemba要求的顺序：U, R, F, D, L, B
    kociemba_order = ['U', 'R', 'F', 'D', 'L', 'B']
    kociemba_string = ""

    for face in kociemba_order:
        if face in cube_state:
            colors = cube_state[face]
            for color in colors:
                if color in color_mapping:
                    kociemba_string += color_mapping[color]
                else:
                    print(f"⚠️ 警告: 未知颜色 '{color}' 在面 {face}")
                    kociemba_string += '?'  # 未知颜色占位符
        else:
            print(f"❌ 错误: 缺少面 {face} 的数据")

    return kociemba_string


def validate_kociemba_state(kociemba_string):
    """
    验证kociemba状态字符串的有效性
    """
    if len(kociemba_string) != 54:
        return False, f"长度错误: 需要54个字符，实际得到{len(kociemba_string)}个"

    # 检查每个面的中心块是否正确
    centers = {
        'U': kociemba_string[4],  # U面的中心应该是U
        'R': kociemba_string[13],  # R面的中心应该是R
        'F': kociemba_string[22],  # F面的中心应该是F
        'D': kociemba_string[31],  # D面的中心应该是D
        'L': kociemba_string[40],  # L面的中心应该是L
        'B': kociemba_string[49]  # B面的中心应该是B
    }

    expected_centers = {'U': 'U', 'R': 'R', 'F': 'F', 'D': 'D', 'L': 'L', 'B': 'B'}

    for face, actual in centers.items():
        if actual != expected_centers[face]:
            return False, f"面{face}的中心应该是{expected_centers[face]}，但检测到{actual}"

    return True, "状态有效"


def main():
    """
    主函数：读取文件并生成kociemba编码
    """
    try:
        # 1. 从文件解析魔方状态
        print("📖 正在解析cube_state.txt文件...")
        cube_state = parse_cube_state_from_file('cube_results/cube_state.txt')

        # 显示解析结果
        print("\n🔍 解析到的魔方状态:")
        for face, colors in cube_state.items():
            print(f"  {face}面: {colors}")

        # 2. 转换为kociemba格式
        print("\n🔄 正在转换为kociemba格式...")
        kociemba_string = convert_to_kociemba_format(cube_state)
        print(f"✅ kociemba编码: {kociemba_string}")

        # 3. 验证状态
        print("\n🔍 验证状态有效性...")
        is_valid, message = validate_kociemba_state(kociemba_string)
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")

        # 4. 保存结果
        output_filename = 'cube_results/kociemba_state.txt'
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(kociemba_string)
        print(f"\n💾 kociemba编码已保存到: {output_filename}")

        # 5. 显示求解命令
        print(f"\n🎯 求解命令:")
        print(f"python -c \"import two_phase.solver as sv; print(sv.solve('{kociemba_string}', 20, 2))\"")

        return kociemba_string

    except FileNotFoundError:
        print("❌ 错误: 找不到cube_state.txt文件")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


if __name__ == "__main__":
    kociemba_code = main()

    # 如果转换成功，可以直接求解
    if kociemba_code and len(kociemba_code) == 54:
        try:
            solution = sv.solve(kociemba_code, 20, 2)
            # 清理格式
            solution = solution.replace("\n", "").strip()
            print(f"\n🎉 求解结果: {solution}")
        except Exception as e:
            print(f"\n❌ 求解失败: {e}")
