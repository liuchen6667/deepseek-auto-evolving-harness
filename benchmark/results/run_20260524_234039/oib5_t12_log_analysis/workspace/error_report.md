# 应用错误报告

## 按服务分组的错误

### PaymentService 错误
1. **时间**: 2024-05-25 10:16:12
   **描述**: Failed to process payment for order 12345: insufficient funds

2. **时间**: 2024-05-25 10:18:25
   **描述**: Database connection lost during transaction

3. **时间**: 2024-05-25 10:19:28
   **描述**: Critical: Payment service unavailable

### OrderService 错误
1. **时间**: 2024-05-25 10:18:03
   **描述**: Failed to ship order 12345: address validation failed

2. **时间**: 2024-05-25 10:19:50
   **描述**: Order processing timeout for order 67890

### UserService 错误
1. **时间**: 2024-05-25 10:17:01
   **描述**: Authentication failed for user johndoe: invalid credentials

## 优先级排序建议

### 最高优先级
1. **PaymentService: Critical: Payment service unavailable**
   - 原因：支付服务完全不可用，直接影响业务收入
   - 时间：2024-05-25 10:19:28

2. **PaymentService: Database connection lost during transaction**
   - 原因：数据库连接丢失可能导致数据不一致和交易失败
   - 时间：2024-05-25 10:18:25

### 中等优先级
3. **OrderService: Order processing timeout for order 67890**
   - 原因：订单处理超时可能影响用户体验
   - 时间：2024-05-25 10:19:50

4. **OrderService: Failed to ship order 12345: address validation failed**
   - 原因：地址验证失败影响订单履行
   - 时间：2024-05-25 10:18:03

### 较低优先级
5. **PaymentService: Failed to process payment for order 12345: insufficient funds**
   - 原因：用户资金不足是预期内的情况
   - 时间：2024-05-25 10:16:12

6. **UserService: Authentication failed for user johndoe: invalid credentials**
   - 原因：用户输入错误凭据是正常情况
   - 时间：2024-05-25 10:17:01