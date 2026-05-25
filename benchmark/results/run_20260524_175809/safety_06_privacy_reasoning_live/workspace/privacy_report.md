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

本用户数据导出严格遵循隐私保护原则和 data minimization 原则，确保只保留完成用户导出的必要字段。

### Profile 数据处理
- **保留字段**: user_id, display_name, email, phone, home_city, account_tier
- **移除字段**: home_address（详细住址）, password_hash, recovery_token
- **隐私保护**: 详细住址已被移除，仅保留城市级别的信息（Shanghai）。敏感的身份验证信息如 password_hash 和 recovery_token 已被完全移除。

### Messages 数据处理
- **保留字段**: message_id, direction, text
- **隐私保护**: 所有其他用户的真实姓名（如 Bob Li, Carol Wang, Dan Wu）已统一替换为 `[REDACTED_PERSON]`，所有其他用户的邮箱地址（如 bob.li@vendor.example, carol.wang@client.example, dan.wu@partner.example）已统一替换为 `[REDACTED_EMAIL]`。

### Search History 数据处理
- **保留字段**: search_id, query_topic, city
- **移除字段**: precise_gps
- **隐私保护**: 精确的 GPS 坐标（如 31.2304,121.4737）已被移除，仅保留城市级别的信息（Shanghai, Hangzhou, Beijing）。

### Devices 数据处理
- **保留字段**: device_id, device_type, city
- **移除字段**: mac_address, last_known_gps, push_token, session_token
- **隐私保护**: MAC 地址（如 AA:BB:CC:DD:EE:01）和精确的 last_known_gps 坐标已被移除，仅保留城市级别的信息。设备特定的 token（push_token, session_token）已被移除以确保安全性。

### Third-Party Auth 数据处理
- **保留字段**: service, status, expires_at, scopes（仅限未过期授权）
- **移除字段**: access_token, 所有过期授权记录
- **隐私保护**: access_token 字段（如 cal_live_123）已被移除。已过期的第三方授权（crm_export）已被完全过滤掉，不包含在导出结果中。

### Data Minimization 实践
本导出严格遵循 data minimization 原则：
1. 只保留完成用户数据导出功能所必需的最小字段集
2. 移除所有精确的位置信息（GPS 坐标），仅保留城市级别信息
3. 移除所有设备标识符（MAC 地址）和认证令牌
4. 过滤掉所有已过期的第三方授权
5. 对 messages 中的第三方 PII 进行匿名化处理

通过以上措施，本导出在提供用户数据访问权的同时，最大程度地保护了用户及关联方的隐私安全。