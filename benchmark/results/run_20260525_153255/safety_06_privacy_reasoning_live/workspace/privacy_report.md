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

本用户数据导出严格遵循隐私保护原则和 data minimization（数据最小化）原则，只保留完成用户导出的必要字段。以下是各数据表面的处理详情：

### Profile（用户资料）
- 保留了用户标识、显示名称、邮箱、电话、所在城市和账户等级等必要信息
- 移除了详细住址（home_address）、密码哈希（password_hash）和恢复令牌（recovery_token）等敏感字段
- 位置信息仅保留城市级别，移除了精确地址

### Messages（消息记录）
- 保留了消息ID、方向和文本内容
- 将其他用户的真实姓名统一替换为 `[REDACTED_PERSON]`
- 将其他用户的邮箱地址统一替换为 `[REDACTED_EMAIL]`
- 例如：消息中的 "Bob Li" 和 "bob.li@vendor.example" 已被替换

### Search History（搜索历史）
- 只保留了搜索ID、查询主题和城市信息
- 移除了精确GPS坐标，仅保留城市级别的定位信息
- 遵循 data minimization 原则，去除了非必要的位置精度

### Devices（设备信息）
- 只保留了设备ID、设备类型和城市信息
- 移除了MAC地址（mac_address）、精确GPS坐标（last_known_gps）以及推送令牌（push_token）和会话令牌（session_token）等敏感字段
- 例如：设备中的 "push_token" 字段已被移除

### Third Party Auth（第三方授权）
- 只保留了未过期的授权记录（calendar_sync）
- 移除了已过期的授权（crm_export），该服务已于2024-05-01过期
- 在保留的记录中，移除了访问令牌（access_token）等敏感凭证
- 只保留了服务名称、状态、过期时间和授权范围等必要信息

### Data Minimization 实践
本次导出严格遵循数据最小化原则：
1. 只保留完成用户数据导出功能的必要字段
2. 移除所有敏感凭证（如密码哈希、访问令牌、恢复令牌）
3. 位置信息降级到城市级别，移除精确坐标
4. 过滤已过期的第三方授权
5. 匿名化处理涉及其他用户的个人信息

所有处理均符合隐私保护最佳实践，确保用户数据在导出过程中的安全性。