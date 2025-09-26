import random
import numpy as np
import os


def clear_console():
    """清屏函数，提升交互体验"""
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_target_correlation(first_round):
    """生成目标相关系数，第一轮决定正负性，后续按正态分布"""
    if first_round:
        # 第一轮：随机决定正负性，强度中等
        sign = random.choice([-1, 1])
        magnitude = round(random.uniform(0.3, 0.7), 2)
        return sign * magnitude
    else:
        # 后续轮次：按正态分布生成(均值0.5，标准差0.2)，超出(0,1)范围则重新取值
        while True:
            magnitude = round(np.random.normal(0.5, 0.2), 2)
            if 0 < magnitude < 1:  # 确保在(0,1)范围内
                sign = random.choice([-1, 1])
                return sign * magnitude


def generate_scatter_plot(X, Y, Z, first_round):
    """生成指定相关系数的散点图，返回散点图字符串、点数据、目标相关系数、相关趋势类型"""
    # 生成目标相关系数
    target_corr = generate_target_correlation(first_round)
    correlation_type = "正" if target_corr > 0 else "负"

    # 生成具有指定相关系数的二维正态分布数据
    mean = [0, 0]
    cov = [[1, target_corr], [target_corr, 1]]
    points = np.random.multivariate_normal(mean, cov, Z)

    # 归一化数据到画布尺寸
    x_values = points[:, 0]
    y_values = points[:, 1]

    # 归一化到 [0,1] 范围
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)

    # 防止除零错误
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1

    normalized_x = [(x - x_min) / x_range for x in x_values]
    normalized_y = [(y - y_min) / y_range for y in y_values]

    # 映射到画布坐标
    canvas_points = []
    for x, y in zip(normalized_x, normalized_y):
        canvas_x = int(x * (X - 1))
        canvas_y = int(y * (Y - 1))
        canvas_points.append((canvas_x, canvas_y))

    # 创建画布 (原点在左下角)
    plot_width = Y + 2  # 列数 + 2（左右边框）
    plot_height = X + 2  # 行数 + 2（上下边框）
    canvas = [[chr(9633) for _ in range(plot_width)] for _ in range(plot_height)]

    # 绘制边框
    for x in range(plot_width):
        canvas[0][x] = '—'
        canvas[plot_height - 1][x] = '—'
    for y in range(1, plot_height - 1):
        canvas[y][0] = '丨'
        canvas[y][plot_width - 1] = '丨'

    # 绘制坐标轴
    for x in range(2, plot_width - 1):
        canvas[plot_height - 2][x] = '—'
    for y in range(1, plot_height - 2):
        canvas[y][1] = '丨'

    # 标记原点
    canvas[plot_height - 2][1] = '○'

    # 标记散点
    for x, y in canvas_points:
        canvas_row = plot_height - 3 - y
        canvas_col = x + 2
        if 1 <= canvas_row < plot_height - 2 and 2 <= canvas_col < plot_width - 1:
            canvas[canvas_row][canvas_col] = chr(9632)

    # 转换为字符串
    plot_str = '\n'.join(''.join(row) for row in canvas)

    return plot_str, canvas_points, target_corr, correlation_type


def calculate_correlation(points):
    """计算实际相关系数"""
    if not points or len(points) < 2:
        return None

    x_values = [p[0] for p in points]
    y_values = [p[1] for p in points]

    corr_matrix = np.corrcoef(x_values, y_values)
    return corr_matrix[0, 1]


def guess_correlation(actual_corr, correlation_type, plot_str, X, Y, Z):
    """处理相关系数猜测逻辑，按原有功能实现"""
    history = [f"提示：散点图呈现{correlation_type}相关趋势"]
    input_options = "[输入数值猜测] | [a=显示答案] | [q=退出]"

    while True:
        clear_console()
        print("=== 散点图相关系数猜测游戏 ===")
        print(f"当前配置：X={X}, Y={Y}, Z={Z}")
        print("\n生成的散点图如下：")
        print(plot_str)
        print("\n历史记录：")
        for item in history:
            print(f"- {item}")

        user_input = input(f"\n{input_options}: ").strip().lower()

        if user_input == 'a':
            answer_str = f"答案为{actual_corr:.4f}"
            history.append(answer_str)
            clear_console()
            print("=== 散点图相关系数猜测游戏 ===")
            print(f"当前配置：X={X}, Y={Y}, Z={Z}")
            print("\n生成的散点图如下：")
            print(plot_str)
            print("\n历史记录：")
            for item in history:
                print(f"- {item}")
            input("按回车键继续...")
            return False, "答案已显示"

        elif user_input == 'q':
            return False, "退出游戏"

        try:
            guess = float(user_input)
            if not (-1 <= guess <= 1):
                history.append("请输入-1到1之间的数值")
                continue

            diff = abs(guess - actual_corr)

            if diff <= 0.05:
                praise = "完美无缺！" if diff < 0.01 else "相差无几！"
                result = f"太棒了！你猜测的 {guess:.4f} 与实际值 {actual_corr:.4f} {praise}"
                history.append(result)
                clear_console()
                print("=== 散点图相关系数猜测游戏 ===")
                print(f"当前配置：X={X}, Y={Y}, Z={Z}")
                print("\n生成的散点图如下：")
                print(plot_str)
                print("\n历史记录：")
                for item in history:
                    print(f"- {item}")
                input("按回车键继续...")
                return True, "猜测正确"
            elif diff <= 0.2:
                history.append("额，差了一些，再试试？")
            elif diff <= 0.7:
                history.append("差得远，多试试吧")
            else:
                history.append("你在逗我？")

        except ValueError:
            history.append("无效输入，请输入数字、'a' 或 'q'")


def main():
    first_round = True
    current_config = None

    print("=== 散点图相关系数猜测游戏 ===")

    while True:
        try:
            if current_config is None:
                X = int(input("\n请输入画布的宽度 X: "))
                Y = int(input("请输入画布的高度 Y: "))
                Z = int(input("请输入散点的数量 Z: "))
                current_config = (X, Y, Z)

            X, Y, Z = current_config
            if X <= 0 or Y <= 0 or Z < 0:
                print("错误：X、Y 必须是正整数，Z 必须是非负整数。")
                current_config = None
                continue

            if Z > X * Y:
                print(f"警告：散点数量过多，已自动调整为 {X * Y}")
                Z = X * Y
                current_config = (X, Y, Z)

            plot_str, points, target_corr, corr_type = generate_scatter_plot(X, Y, Z, first_round)
            actual_corr = calculate_correlation(points)

            print("\n请根据散点图猜测X和Y的相关系数（范围：-1 到 1）")
            success, message = guess_correlation(actual_corr, corr_type, plot_str, X, Y, Z)

            clear_console()
            print("=== 散点图相关系数猜测游戏 ===")
            print(f"当前配置：X={X}, Y={Y}, Z={Z}")
            print("\n生成的散点图如下：")
            print(plot_str)
            print(f"\n{message}")

            if message == "退出游戏":
                print("\n感谢游玩，再见！")
                break

            choice = input("\n[m=继续游玩] | [n=新配置游玩] | [q=退出]: ").strip().lower()
            if choice == 'm':
                first_round = False
            elif choice == 'n':
                first_round = False
                current_config = None
            elif choice == 'q':
                print("\n感谢游玩，再见！")
                break
            else:
                print("无效输入，将使用新配置重新开始")
                first_round = False
                current_config = None

        except ValueError:
            print("错误：请输入有效的整数。")
            current_config = None
        except Exception as e:
            print(f"发生错误: {e}")
            break


if __name__ == "__main__":
    main()
