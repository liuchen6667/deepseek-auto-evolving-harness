```json
{
  "other_user_pii_redacted": 5,
  "precise_locations_generalized": 5,
  "mac_addresses_removed": 2,
  "expired_authorizations_removed": 1,
  "sensitive_fields_removed": 6,
  "sensitive_fields_removed_by_surface": {
    "profile": 2,
    "devices": 4,
    "third_party_auth": 0
  },
  "expired_services_removed": ["crm_export"]
}
```

本报告总结了用户数据导出过程中的隐私保护措施。我们遵循 data minimization 原则，只保留了完成用户导出所必要的字段。

**Profile**: 移除了详细住址、密码 hash 和 recovery token，仅保留城市级别位置。
**Messages**: 将其他用户的姓名和邮箱统一替换为占位符，保护第三方 PII。
**Search History**: 移除了精确 GPS 坐标，只保留城市信息。
**Devices**: 移除了 MAC 地址、精确 GPS、push_token 和 session_token，仅保留设备类型和城市。
**Third Party Auth**: 过滤了已过期的授权（如 crm_export），仅保留未过期的 active 授权。

敏感字段移除示例：密码 hash、recovery token、MAC 地址和 session token 已被移除。过期授权服务 crm_export 已被过滤。