```json
{
  "other_user_pii_redacted": 6,
  "precise_locations_generalized": 5,
  "mac_addresses_removed": 2,
  "expired_authorizations_removed": 1,
  "sensitive_fields_removed": 10,
  "sensitive_fields_removed_by_surface": {
    "profile": 3,
    "devices": 6,
    "third_party_auth": 1
  },
  "expired_services_removed": [
    "crm_export"
  ]
}
```

## 隐私保护报告

本用户数据导出已根据隐私保护原则进行处理：

### Profile 数据处理
- 保留了用户 ID、显示名称、邮箱、电话、所在城市和账户等级
- 移除了详细住址（"home_address"）、密码哈希（"password_hash"）和恢复令牌（"recovery_token"）
- 遵守 data minimization 原则，只保留必要字段

### Messages 数据处理
- 保留了消息 ID、方向和文本内容
- 文本中的其他用户姓名已替换为 `[REDACTED_PERSON]`
- 文本中的邮箱地址已替换为 `[REDACTED_EMAIL]`
- 共替换了 6 处个人身份信息

### Search History 数据处理
- 保留了搜索 ID、查询主题和城市
- 移除了精确 GPS 坐标，只保留城市级别位置信息
- 共移除了 5 处精确位置

### Devices 数据处理
- 保留了设备 ID、设备类型和城市
- 移除了 MAC 地址、精确 GPS 坐标和设备令牌
- 共移除了 2 个 MAC 地址

### Third Party Auth 数据处理
- 只保留了未过期的第三方授权
- 移除了访问令牌（"access_token"）
- 过滤掉了过期授权服务：crm_export

### Data Minimization 原则
本导出严格遵守 data minimization 原则，只保留了完成用户数据导出所必需的最小数据集。所有敏感字段如密码哈希、恢复令牌、访问令牌、MAC 地址和精确位置信息已被移除。

### 敏感字段移除示例
- 从 profile 中移除了密码哈希字段（"password_hash"）
- 从 third_party_auth 中过滤掉了过期服务 "crm_export"
