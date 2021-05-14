# Nguyên Liệu Thô
cr = [1150, 33, 13]  # Giá mua 1 đơn vị nguyên liệu thô (đ/unit)
M = [1, 1, 1]  # Tỷ lệ nguyên liệu thô để sản xuất 1 sản phẩm (đ/unit)
# Chi phí lưu kho 1 đơn vị nguyên liệu thô phía nhà sản xuất (đ/unit)
H_r = [6, 1, 0.6]
n = [5, 1, 1]  # Chi kỳ nhập nguyên liệu thô (ngày)

# Thành phẩm
# Chi phí setup
# Chi phí cố định thiết lập vận chuyển từ nơi sản xuất đến kho lưu trữ thành phẩm (đ/setup)
S_p = 500000
# Chi phí cố định thiết lập vận chuyển từ kho lưu trữ thành phẩm đến các nhà bán lẻ (đ/setup)
S_b = [500000, 600000, 700000]
L_b = [800000, 1000000, 1200000]  # Chi phí cố định backoder cost (đ/setup)
b_rate = 0.05  # Tỷ lệ nhận backoder cost

# Chi phí vận chuyển
# Chi phí vận chuyển trên từng sản phẩm từ nơi sản xuất đến kho lưu trữ thành phẩm (đ/unit)
T_p = 20
# Chi phí vận chuyển trên từng sản phẩm từ kho lưu trữ thành phẩm đến nhà bán lẻ (đ/unit)
T_b = [35, 35, 45]

# Chi phí lưu kho
H_p = 10  # Chi phí lưu kho phía nơi sản xuất (đ/unit)
H_b = 12  # Chi phí lưu kho phía kho lưu trữ (đ/unit)
# Chi phí quản lý sản phẩm của các nhà bán lẻ trả cho nhà sản xuất (đ/unit)
uc = [50, 60, 65]

# Giá sản phẩm
p = 2100  # Giá bán sản phẩm cố định đến người tiêu dùng

# Thông số
P = 80000  # Công xuất tối đa của nhà sản xuất (ngày)
K = [32000, 28000, 24000]  # Quy mô thị trường của các nhà bán lẻ
AS = 0.3  # Tỉ lệ chi phí quảng cáo trên doanh thu (A/S)
NUM_OF_MATERIALS = len(M)  # Số lượng nguyên liệu thô cấu thành sản xuất
NUM_OF_RETAILERS = len(K)  # Số lượng nhà bán lẻ
# Chi phí quảng cáo tối đa trên mỗi đơn vị sản phẩm phía nhà sản xuất (đ/unit)
MAX_A = int((p - sum(cr)) * AS)
# Chi phí quảng cáo tối đa trên đơn vị sản phẩm phía nhà bán lẻ (đ/unit)
MAX_a = int(p * AS)


class TXC:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
