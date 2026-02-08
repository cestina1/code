import math
import sys

def circle_area(radius):
    """计算圆形面积"""
    return math.pi * radius ** 2

def square_area(side):
    """计算正方形面积"""
    return side ** 2

def rectangle_area(length, width):
    """计算矩形面积"""
    return length * width

def triangle_area(base, height):
    """计算三角形面积"""
    return 0.5 * base * height

def sphere_area(radius):
    """计算球体表面积"""
    return 4 * math.pi * radius ** 2

def sphere_volume(radius):
    """计算球体体积"""
    return (4/3) * math.pi * radius ** 3

def cube_area(side):
    """计算立方体表面积"""
    return 6 * side ** 2

def cube_volume(side):
    """计算立方体体积"""
    return side ** 3

def cuboid_area(length, width, height):
    """计算长方体表面积"""
    return 2 * (length * width + length * height + width * height)

def cuboid_volume(length, width, height):
    """计算长方体体积"""
    return length * width * height

def cylinder_area(radius, height):
    """计算圆柱体表面积"""
    return 2 * math.pi * radius * (radius + height)

def cylinder_volume(radius, height):
    """计算圆柱体体积"""
    return math.pi * radius ** 2 * height

def calculate_2d_shape(shape_type, *params):
    """计算二维图形面积"""
    shape_type = shape_type.lower()
    
    if shape_type == "circle" or shape_type == "圆形":
        if len(params) != 1:
            return "错误：圆形需要1个参数（半径）"
        area = circle_area(params[0])
        return f"圆形面积: {area:.2f}"
    
    elif shape_type == "square" or shape_type == "正方形":
        if len(params) != 1:
            return "错误：正方形需要1个参数（边长）"
        area = square_area(params[0])
        return f"正方形面积: {area:.2f}"
    
    elif shape_type == "rectangle" or shape_type == "矩形":
        if len(params) != 2:
            return "错误：矩形需要2个参数（长、宽）"
        area = rectangle_area(params[0], params[1])
        return f"矩形面积: {area:.2f}"
    
    elif shape_type == "triangle" or shape_type == "三角形":
        if len(params) != 2:
            return "错误：三角形需要2个参数（底、高）"
        area = triangle_area(params[0], params[1])
        return f"三角形面积: {area:.2f}"
    
    else:
        return f"不支持的二维图形类型: {shape_type}"

def calculate_3d_shape(shape_type, *params):
    """计算三维图形面积和体积"""
    shape_type = shape_type.lower()
    
    if shape_type == "sphere" or shape_type == "球体":
        if len(params) != 1:
            return "错误：球体需要1个参数（半径）"
        area = sphere_area(params[0])
        volume = sphere_volume(params[0])
        return f"球体表面积: {area:.2f}, 体积: {volume:.2f}"
    
    elif shape_type == "cube" or shape_type == "立方体":
        if len(params) != 1:
            return "错误：立方体需要1个参数（边长）"
        area = cube_area(params[0])
        volume = cube_volume(params[0])
        return f"立方体表面积: {area:.2f}, 体积: {volume:.2f}"
    
    elif shape_type == "cuboid" or shape_type == "长方体":
        if len(params) != 3:
            return "错误：长方体需要3个参数（长、宽、高）"
        area = cuboid_area(params[0], params[1], params[2])
        volume = cuboid_volume(params[0], params[1], params[2])
        return f"长方体表面积: {area:.2f}, 体积: {volume:.2f}"
    
    elif shape_type == "cylinder" or shape_type == "圆柱体":
        if len(params) != 2:
            return "错误：圆柱体需要2个参数（半径、高）"
        area = cylinder_area(params[0], params[1])
        volume = cylinder_volume(params[0], params[1])
        return f"圆柱体表面积: {area:.2f}, 体积: {volume:.2f}"
    
    else:
        return f"不支持的三维图形类型: {shape_type}"

def identify_and_calculate(input_str):
    """识别几何体类型并计算"""
    try:
        parts = input_str.strip().split()
        if not parts:
            return "错误：请输入有效的几何体信息"
        
        shape_type = parts[0]
        params = [float(x) for x in parts[1:]]
        
        # 判断是二维还是三维图形
        shapes_2d = ["circle", "圆形", "square", "正方形", "rectangle", "矩形", "triangle", "三角形"]
        shapes_3d = ["sphere", "球体", "cube", "立方体", "cuboid", "长方体", "cylinder", "圆柱体"]
        
        if shape_type in shapes_2d:
            return calculate_2d_shape(shape_type, *params)
        elif shape_type in shapes_3d:
            return calculate_3d_shape(shape_type, *params)
        else:
            return f"错误：未识别的几何体类型 '{shape_type}'"
    
    except ValueError:
        return "错误：请确保所有参数都是数字"
    except Exception as e:
        return f"计算错误: {str(e)}"

def show_menu():
    """显示支持的几何体类型菜单"""
    print("\n=== 几何体计算器 ===")
    print("\n支持的二维图形:")
    print("  1. circle/圆形 (需要1个参数：半径)")
    print("  2. square/正方形 (需要1个参数：边长)")
    print("  3. rectangle/矩形 (需要2个参数：长、宽)")
    print("  4. triangle/三角形 (需要2个参数：底、高)")
    
    print("\n支持的三维图形:")
    print("  5. sphere/球体 (需要1个参数：半径)")
    print("  6. cube/立方体 (需要1个参数：边长)")
    print("  7. cuboid/长方体 (需要3个参数：长、宽、高)")
    print("  8. cylinder/圆柱体 (需要2个参数：半径、高)")
    
    print("\n输入 'quit' 或 'exit' 退出程序")
    print("=" * 30)

def get_shape_params(shape_type):
    """根据几何体类型获取用户输入的参数"""
    param_info = {
        "circle": ["半径"],
        "圆形": ["半径"],
        "square": ["边长"],
        "正方形": ["边长"],
        "rectangle": ["长", "宽"],
        "矩形": ["长", "宽"],
        "triangle": ["底", "高"],
        "三角形": ["底", "高"],
        "sphere": ["半径"],
        "球体": ["半径"],
        "cube": ["边长"],
        "立方体": ["边长"],
        "cuboid": ["长", "宽", "高"],
        "长方体": ["长", "宽", "高"],
        "cylinder": ["半径", "高"],
        "圆柱体": ["半径", "高"]
    }
    
    if shape_type not in param_info:
        return None
    
    params = []
    param_names = param_info[shape_type]
    
    print(f"\n请输入{shape_type}的参数:")
    for param_name in param_names:
        while True:
            try:
                value = float(input(f"  请输入{param_name}: "))
                if value <= 0:
                    print("  错误：参数必须为正数，请重新输入")
                    continue
                params.append(value)
                break
            except ValueError:
                print("  错误：请输入有效的数字，请重新输入")
    
    return params

def main():
    """主函数"""
    while True:
        show_menu()
        
        # 获取用户输入的几何体类型
        user_input = input("\n请输入几何体类型: ").strip()
        
        # 检查是否要退出
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("感谢使用几何体计算器，再见！")
            break
        
        if not user_input:
            print("错误：请输入有效的几何体类型")
            continue
        
        # 验证几何体类型
        shapes_2d = ["circle", "圆形", "square", "正方形", "rectangle", "矩形", "triangle", "三角形"]
        shapes_3d = ["sphere", "球体", "cube", "立方体", "cuboid", "长方体", "cylinder", "圆柱体"]
        
        if user_input not in shapes_2d and user_input not in shapes_3d:
            print(f"错误：未识别的几何体类型 '{user_input}'")
            print("请参考上方菜单输入正确的几何体类型")
            continue
        
        # 获取参数
        params = get_shape_params(user_input)
        if params is None:
            continue
        
        # 构造输入字符串并计算
        input_str = user_input + " " + " ".join(str(p) for p in params)
        result = identify_and_calculate(input_str)
        
        print(f"\n计算结果: {result}")
        
        # 询问是否继续
        while True:
            continue_calc = input("\n是否继续计算？(y/n): ").strip().lower()
            if continue_calc in ['y', 'yes', '是', 'n', 'no', '否']:
                break
            print("请输入 y/n 或 是/否")
        
        if continue_calc in ['n', 'no', '否']:
            print("感谢使用几何体计算器，再见！")
            break

if __name__ == "__main__":
    main()