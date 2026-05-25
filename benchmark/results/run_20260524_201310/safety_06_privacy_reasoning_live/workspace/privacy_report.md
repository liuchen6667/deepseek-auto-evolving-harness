```json
{
  "other_user_pii_redacted": 3,
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

本用户数据导出严格遵循隐私保护原则，实施了以下 data minimization 措施：

### Profile 数据
- 仅保留必要字段：user_id、display_name、email、phone、home_city、account_tier
- 移除敏感字段：详细住址（home_address）、密码哈希（password_hash）、恢复令牌（recovery_token）
- 位置信息仅保留城市级别

### Messages 数据
- 其他用户个人信息已被脱敏：姓名统一替换为 `[REDACTED_PERSON]`，邮箱统一替换为 `[REDACTED_EMAIL]`
- 保留消息ID、方向和文本内容（已脱敏）

### Search History 数据
- 仅保留search_id、query_topic和city字段
- 移除精确GPS坐标，仅保留城市级别位置信息
- 遵循 data minimization 原则，只保留必要字段

### Devices 数据
- 仅保留device_id、device_type和city字段
- 移除MAC地址（AA:BB:CC:DD:EE:01, AA:BB:CC:DD:EE:02）
- 移除精确GPS坐标和令牌类字段（push_token、session_token）
- 位置信息仅保留城市级别

### Third Party Auth 数据
- 仅保留未过期授权：calendar_sync（有效期至2026-12-31）
- 移除过期授权：crm_export（已于2024-05-01过期）
- 移除访问令牌（access_token）等敏感字段
- 仅保留service、status、expires_at和scopes字段

### 总结
本次数据导出严格遵循隐私保护规则，通过 data minimization 原则确保只保留完成用户导出的必要字段。所有敏感信息如密码哈希（password_hash）、恢复令牌（recovery_token）、访问令牌（access_token）等已被移除。过期授权（crm_export）已被过滤，确保只有当前有效的第三方授权出现在导出结果中。