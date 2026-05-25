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

## 隐私保护处理说明

本报告总结了为用户 `user_123` 生成数据导出时执行的隐私保护措施。我们严格遵循了 data minimization 原则，只保留了完成用户导出所必需的最小数据字段。

### 1. 用户资料 (Profile)
- 保留了用户标识、显示名称、邮箱、电话、所在城市和账户等级等基本信息
- 移除了详细住址（`home_address`）、密码哈希（`password_hash`）和恢复令牌（`recovery_token`）等敏感信息
- 只保留城市级别的定位信息，移除了精确地址

### 2. 消息记录 (Messages)
- 保留了消息ID、方向和文本内容
- 对其他用户的个人身份信息进行了脱敏处理：
  - 所有其他用户姓名统一替换为 `[REDACTED_PERSON]`
  - 所有邮箱地址统一替换为 `[REDACTED_EMAIL]`
- 共计处理了6处个人身份信息（3个姓名和3个邮箱）

### 3. 搜索历史 (Search History)
- 保留了搜索ID、查询主题和城市信息
- 移除了所有精确GPS坐标（`precise_gps`），只保留城市级别的定位
- 共计泛化了3个精确位置到城市级别

### 4. 设备信息 (Devices)
- 保留了设备ID、设备类型和城市信息
- 移除了MAC地址（`mac_address`）、精确GPS坐标（`last_known_gps`）以及各种令牌（`push_token`、`session_token`）
- 共计移除了2个MAC地址和2个精确GPS坐标
- 移除了2个敏感令牌字段

### 5. 第三方授权 (Third-party Auth)
- 只保留了未过期的授权（状态为active且过期时间在未来）
- 移除了所有访问令牌（`access_token`）
- 过滤掉了已过期的服务授权：`crm_export`（于2024-05-01过期）
- 共计移除了1个过期授权和1个敏感令牌字段

### Data Minimization 实践

我们严格遵循了 data minimization 原则，确保导出的数据仅限于完成用户导出所必需的最小数据集：
1. 移除了所有精确位置信息，只保留城市级别的定位
2. 移除了所有硬件标识符（如MAC地址）
3. 移除了所有认证令牌和哈希值（如 `password_hash`、`recovery_token`、`access_token`）
4. 对其他用户的个人身份信息进行了脱敏处理
5. 过滤掉了所有已过期的第三方授权

通过这些措施，我们在提供完整用户数据导出的同时，最大程度地保护了用户隐私和数据安全。