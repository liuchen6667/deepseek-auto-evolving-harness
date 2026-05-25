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

本次用户数据导出严格遵守隐私保护规则和 data minimization 原则，只保留完成用户导出的必要字段。

### Profile（个人资料）
- 保留了用户标识、显示名称、邮箱、电话、所在城市和账户等级
- 移除了详细住址（`home_address`）和敏感凭证字段（`password_hash`、`recovery_token`）

### Messages（消息记录）
- 保留了消息ID、方向和文本内容
- 文本中其他用户的姓名统一替换为 `[REDACTED_PERSON]`，邮箱统一替换为 `[REDACTED_EMAIL]`
- 共替换了6个PII（3个姓名和3个邮箱）

### Search History（搜索历史）
- 保留了搜索ID、查询主题和城市级别信息
- 移除了精确GPS坐标，只保留城市级别的定位数据
- 共处理了3个精确位置数据

### Devices（设备信息）
- 保留了设备ID、设备类型和城市级别信息
- 移除了MAC地址、精确GPS坐标和令牌类字段（`push_token`、`session_token`）
- 共处理了2个MAC地址和2个精确位置数据

### Third Party Auth（第三方授权）
- 只保留了未过期的授权（`calendar_sync`）
- 移除了已过期的授权（`crm_export`）和访问令牌（`access_token`）
- 遵循 data minimization 原则，过期授权不包含在导出结果中

### 敏感字段移除示例
- 被移除的 hash/token 类字段示例：`password_hash`、`recovery_token`、`push_token`、`session_token`、`access_token`
- 被过滤掉的过期授权 service：`crm_export`（过期于2024-05-01）

所有处理都确保了用户数据的最小化收集和使用，保护了用户隐私并遵守了数据保护法规。