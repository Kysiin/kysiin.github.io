# LAB1
![[Pasted image 20261104154341.png]]
```MATLAB
% 1. 定义自变量 n，范围从 -10 到 10，步长为 1
n = -10:1:10;

% 2. 生成离散正弦序列 x1(n) 和余弦序列 x2(n)
x1 = 3 * sin(0.2 * pi * n + 2 * pi / 3);
x2 = 3 * cos(0.2 * pi * n + 2 * pi / 3);

% 3. 计算序列的相加和点乘
x_add = x1 + x2;
x_mul = x1 .* x2;

% 4. 绘制图形
figure;

% 子图1：绘制 x1(n)
subplot(2, 2, 1);
stem(n, x1, 'filled');
title('离散正弦序列 x_1(n)');
xlabel('n'); ylabel('x_1(n)');
grid on;

% 子图2：绘制 x2(n)
subplot(2, 2, 2);
stem(n, x2, 'filled');
title('离散余弦序列 x_2(n)');
xlabel('n'); ylabel('x_2(n)');
grid on;

% 子图3：绘制 x1(n) + x2(n)
subplot(2, 2, 3);
stem(n, x_add, 'filled');
title('序列相加 x_1(n) + x_2(n)');
xlabel('n'); ylabel('x_1(n) + x_2(n)');
grid on;

% 子图4：绘制 x1(n) .* x2(n)
subplot(2, 2, 4);
stem(n, x_mul, 'filled');
title('序列相乘 x_1(n) \cdot x_2(n)');
xlabel('n'); ylabel('x_1(n) \cdot x_2(n)');
grid on;
```
![[Pasted image 20261104154555.png|498]]
![[Pasted image 20261104154621.png]]
```MATLAB
% 1. 定义两个序列的数值
x = [5, 6, 11, 0, -3, 1, 7];
y = [7, -3, 1, 0, -2, 4];

% 2. 定义两个序列的时间索引范围
nx = -3:3;
ny = -1:4;

% 3. 计算卷积数值
z = conv(x, y);

% 4. 计算卷积后序列的时间索引范围
nz_start = nx(1) + ny(1);      % 起始索引：-3 + (-1) = -4
nz_end = nx(end) + ny(end);    % 结束索引：3 + 4 = 7
nz = nz_start : nz_end;        % 生成索引向量 [-4, -3, ..., 7]

% 5. 打印结果到命令行窗口
disp('卷积结果 z(n) 的数值为：');
disp(z);
disp('对应的索引 n 为：');
disp(nz);

% 6. 绘图展示
figure;
subplot(3,1,1);
stem(nx, x, 'filled'); title('序列 x(n)'); xlabel('n'); ylabel('x(n)'); grid on;
subplot(3,1,2);
stem(ny, y, 'filled'); title('序列 y(n)'); xlabel('n'); ylabel('y(n)'); grid on;
subplot(3,1,3);
stem(nz, z, 'filled', 'r'); title('卷积结果 z(n) = x(n) * y(n)'); xlabel('n'); ylabel('z(n)'); grid on;
```
![[Pasted image 20261104154734.png|487]]
![[Pasted image 20261104155210.png]]
```MATLAB
% 1. 定义基本参数
n16 = 0:15; % N=16 的索引
n8 = 0:7;   % N=8 的索引

% 2. 生成序列
x1_16 = exp(1j * (pi/8) * n16);
x1_8  = exp(1j * (pi/8) * n8);

x2_16 = cos((pi/8) * n16);
x2_8  = cos((pi/8) * n8);

% 3. 计算 DFT
X1_16 = fft(x1_16, 16);
X1_8  = fft(x1_8, 8);

X2_16 = fft(x2_16, 16);
X2_8  = fft(x2_8, 8);

% 4. 绘制幅频特性曲线
figure('Name', 'DFT幅频特性');

% 绘制 x1 的幅频特性
subplot(2,2,1);
k16 = 0:15;
stem(k16, abs(X1_16), 'filled'); title('x_1(n) 幅频特性 (N=16)');
xlabel('k'); ylabel('|X_1(k)|'); grid on;

subplot(2,2,2);
k8 = 0:7;
stem(k8, abs(X1_8), 'filled'); title('x_1(n) 幅频特性 (N=8)');
xlabel('k'); ylabel('|X_1(k)|'); grid on;

% 绘制 x2 的幅频特性
subplot(2,2,3);
stem(k16, abs(X2_16), 'filled'); title('x_2(n) 幅频特性 (N=16)');
xlabel('k'); ylabel('|X_2(k)|'); grid on;

subplot(2,2,4);
stem(k8, abs(X2_8), 'filled'); title('x_2(n) 幅频特性 (N=8)');
xlabel('k'); ylabel('|X_2(k)|'); grid on;


% 5. 使用 IDFT 恢复 x2 信号
% 分别对 N=16 和 N=8 的频域结果进行 IFFT
x2_rec_16 = ifft(X2_16, 16);
x2_rec_8  = ifft(X2_8, 8);

% 取实部
x2_rec_16 = real(x2_rec_16);
x2_rec_8  = real(x2_rec_8);

% 绘制恢复信号对比图
figure('Name', 'IDFT恢复信号对比');

subplot(2,1,1);
stem(n16, x2_16, 'b', 'LineWidth', 1.5); hold on;
stem(n16, x2_rec_16, 'r--o', 'LineWidth', 1.5);
title('N=16 时，原始 x_2(n) 与 IDFT 恢复信号对比');
legend('原始信号', '恢复信号'); xlabel('n'); ylabel('幅度'); grid on;

subplot(2,1,2);
stem(n8, x2_8, 'b', 'LineWidth', 1.5); hold on;
stem(n8, x2_rec_8, 'r--o', 'LineWidth', 1.5);
title('N=8 时，原始 x_2(n) 与 IDFT 恢复信号对比');
legend('原始信号', '恢复信号'); xlabel('n'); ylabel('幅度'); grid on;

% 计算恢复误差
disp('N=16 时的恢复误差最大绝对值:');
disp(max(abs(x2_16 - x2_rec_16)));
disp('N=8 时的恢复误差最大绝对值:');
disp(max(abs(x2_8 - x2_rec_8)));
```
![[Pasted image 20261104155230.png|465]]
![[Pasted image 20261104155244.png|468]]
两种DFT有差别，因为N越大，DFT的频率分辨率越高，N=16能分辨出 π/8的频率成分，而N=8分辨不出。且当信号频率不在 DFT 的采样点上时，就会发生“栅栏效应”，导致能量向周围频点扩散，产生泄露，N=8时产生了频谱泄露。

IDFT恢复得到的信号与原信号一致。