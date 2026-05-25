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

## 隐私处理说明

本次用户数据导出严格遵循 **data minimization** 原则，只保留完成用户导出的必要字段。以下是各数据模块的处理详情：

### Profile（用户资料）
- 移除了详细住址（"home_address"），只保留城市级别信息（"home_city"）
- 移除了敏感字段：`password_hash` 和 `recovery_token`
- 保留了用户标识、显示名称、联系方式等必要信息

### Messages（消息记录）
- 其他用户的真实姓名统一替换为 `[REDACTED_PERSON]`
- 其他用户的邮箱地址统一替换为 `[REDACTED_EMAIL]`
- 共处理了 3 条消息中的 6 个 PII 元素

### Search History（搜索历史）
- 移除了精确 GPS 坐标（"precise_gps"）
- 只保留城市级别位置信息（"city"）
- 保留了搜索主题和城市信息

### Devices（设备信息）
- 移除了 MAC 地址（"mac_address"）
- 移除了精确 GPS 坐标（"last_known_gps"），只保留城市级别信息（"city"）
- 移除了敏感 token 字段：`push_token` 和 `session_token`

### Third Party Auth（第三方授权）
- 过滤掉了过期授权服务 "crm_export"
- 只保留了未过期的 "calendar_sync" 服务
- 移除了 `access_token` 敏感字段

## 关键移除项示例

- **敏感字段**：如 `password_hash`、`recovery_token`、`push_token`、`session_token` 和 `access_token` 等 token/hash 类字段已全部移除
- **过期授权**：服务 "crm_export" 因已过期（expires_at: 2024-05-01）而被过滤

所有处理均符合隐私保护规则，确保用户数据最小化且安全。
