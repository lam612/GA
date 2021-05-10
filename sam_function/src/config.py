# -*- coding: utf-8 -*-
P = 2000000  # Công suất nhà sản xuất
H_p = 25  # Chi phí giữ hàng phía nhà sản xuất
S_p = 0  # Chi phí thiết lập sản xuất của nhà sản xuất ($/setup)
cm = 134 + 15  # Chi phí sản xuất 1 sản phẩm ($/unit)


cr = [1274]  # Chi phí mua 1 đơn vị nguyên liệu thô ($/unit)
H_r = [18]  # Chi phí giữ nguyên liệu thô j ($/unit/time)
M = [1]  # Số nguyên liệu thô để sản xuất 1 sản phầm j
S_r = [12]  # Chi phí mua nguyên liệu thô cố định ($/order)


K = [1000000, 800000, 500000]  # Quy mô thị trường của nhà bán lẻ i
phi = [25, 30, 45]  # Chi phí vận chuyển cho nhà bán lẻ i
# Nhà sản xuất quản lý hàng tồn kho của nhà bán lẻ i và lấy chi phí uci với mỗi sản phẩm
uc = [10, 12, 15]
# Giá bán 1 sản phẩm cho nhà bán lẻ thứ iz
cp = [1750, 1800, 1850]
# p = [2085, 2120, 2210]  # Giá bán sản phẩm của nhà bán lẻ i
p = 2100
S_b = [5, 4.5, 5.4]  # Chi phí cố định bổ sung cho nhà bán lẻ i
H_b = [4.5, 4.8, 4.2]  # Chi phí giữ hàng phía nhà bán lẻ i
L_b = [1.1, 1.2, 1.3]  # Backorder cost của nhà bán lẻ i
a_r = 0.5
p_l = 7

M_len = len(M)
R_len = len(K)

MAX_A = int((min(cp) - sum(cr)) * a_r)
MAX_a = [(p - cp[i]) * a_r for i in range(R_len)]
MIN_cp = sum(cr)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
