```json
{
  "other_user_pii_redacted": 6,
  "precise_locations_generalized": 5,
  "mac_addresses_removed": 2,
  "expired_authorizations_removed": 1,
  "sensitive_fields_removed": 5,
  "sensitive_fields_removed_by_surface": {
    "profile": 2,
    "devices": 2,
    "third_party_auth": 1
  },
  "expired_services_removed": ["crm_export"]
}
```

## 隐私保护报告

本报告总结了为用户 `user_123` 生成数据导出时应用的隐私保护措施。我们严格遵守了 data minimization 原则，只保留了完成用户导出的必要字段。

### Profile 数据
- 保留了用户标识符、显示名称、邮箱、电话、城市和账户等级等基本信息
- 移除了详细住址（`home_address`）、密码哈希（`password_hash`）和恢复令牌（`recovery_token`）等敏感信息
- 位置数据仅保留城市级别（`home_city`）

### Messages 数据
- 保留了所有消息的ID、方向和文本内容
- 应用了PII脱敏：其他用户姓名统一替换为 `[REDACTED_PERSON]`，邮箱统一替换为 `[REDACTED_EMAIL]`
- 共脱敏了6处其他用户的个人身份信息（3个姓名和3个邮箱）

### Search History 数据
- 保留了搜索ID、查询主题和城市信息
- 移除了精确GPS坐标（`precise_gps`），仅保留城市级别的定位数据
- 共泛化了3个精确位置到城市级别

### Devices 数据
- 保留了设备ID、设备类型和城市信息
- 移除了MAC地址（`mac_address`）、精确GPS位置（`last_known_gps`）和设备令牌（`push_token`、`session_token`）
- 共移除了2个MAC地址和2个设备令牌
- 泛化了2个精确位置到城市级别

### Third-Party Auth 数据
- 仅保留了未过期的第三方授权（`calendar_sync`）
- 移除了已过期的授权（`crm_export`）
- 在保留的授权中移除了访问令牌（`access_token`）
- 应用了 data minimization：只保留服务名称、状态、过期时间和权限范围

### Data Minimization 实践
我们严格遵循了 data minimization 原则，确保：
1. 只保留完成用户导出的必要字段
2. 移除所有敏感字段，如密码哈希、恢复令牌、访问令牌、MAC地址等
3. 位置数据仅保留城市级别，移除精确GPS坐标
4. 过滤掉已过期的第三方授权（如 `crm_export`）
5. 脱敏其他用户的个人身份信息

### 敏感字段移除示例
- **hash/token类字段**：`password_hash`、`recovery_token`、`push_token`、`session_token`、`access_token` 等字段已被移除
- **过期授权**：`crm_export` 服务因已过期（2024-05-01）而被过滤掉

这些措施确保了用户数据导出既完整又安全，最大程度地保护了用户隐私。