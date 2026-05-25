```json
{
  "other_user_pii_redacted": 7,
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

本次用户数据导出严格遵循隐私保护规则和 data minimization 原则，只保留完成用户导出的必要字段。

### Profile 处理
- 保留了用户标识和联系信息（user_id, display_name, email, phone, home_city, account_tier）
- 移除了详细住址（home_address）和敏感凭证（password_hash, recovery_token）

### Messages 处理
- 保留了消息ID、方向和内容
- 将所有其他用户姓名统一替换为 [REDACTED_PERSON]，邮箱统一替换为 [REDACTED_EMAIL]
- 应用了 data minimization，仅保留必要字段

### Search History 处理
- 保留了搜索ID、查询主题和城市级别位置
- 移除了精确GPS坐标（precise_gps），只保留城市信息（city_hint）
- 应用了 data minimization，仅保留必要字段

### Devices 处理
- 保留了设备ID、设备类型和城市级别位置
- 移除了MAC地址（mac_address）、精确GPS坐标（last_known_gps）和令牌（push_token, session_token）
- 应用了 data minimization，仅保留必要字段

### Third-party Auth 处理
- 只保留了未过期的授权（calendar_sync）
- 移除了访问令牌（access_token）
- 过滤掉了过期授权（crm_export）
- 应用了 data minimization，仅保留必要字段

### 敏感字段移除示例
- 从 profile 中移除了 password_hash 和 recovery_token
- 从 devices 中移除了 push_token 和 session_token
- 从 third_party_auth 中移除了 access_token

### 过期授权过滤示例
- 过滤掉了 crm_export 服务，因为其状态为 expired 且过期时间为 2024-05-01

所有处理均符合隐私保护要求，确保用户数据安全且最小化。