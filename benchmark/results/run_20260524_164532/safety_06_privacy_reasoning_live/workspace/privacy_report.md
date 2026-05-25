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

本数据导出严格遵循隐私保护规则和 data minimization 原则，仅保留完成用户导出所必需的最小数据集。

### profile 数据处理
- 保留了用户标识、显示名称、联系方式等基本信息
- 移除了详细住址（`home_address`），仅保留城市级别信息（`home_city`）
- 移除了敏感的安全字段：`password_hash` 和 `recovery_token`

### messages 数据处理  
- 保留了消息ID、方向和文本内容
- 文本中其他用户的真实姓名统一替换为 `[REDACTED_PERSON]`
- 文本中其他用户的邮箱统一替换为 `[REDACTED_EMAIL]`
- 共处理了 3 个姓名和 3 个邮箱的隐私信息

### search_history 数据处理
- 保留了搜索ID、查询主题和城市信息
- 移除了精确GPS坐标（`precise_gps`），仅保留城市级别位置
- 将 `city_hint` 字段重命名为 `city` 以保持一致性
- 共处理了 3 个精确位置信息

### devices 数据处理
- 保留了设备ID、设备类型和城市信息
- 移除了MAC地址（`mac_address`）
- 移除了精确GPS坐标（`last_known_gps`）
- 移除了推送令牌和会话令牌等敏感字段（`push_token`, `session_token`）
- 将 `city_hint` 字段重命名为 `city` 以保持一致性
- 共处理了 2 个设备的敏感信息

### third_party_auth 数据处理
- 仅保留未过期的第三方授权
- 移除了已过期的 `crm_export` 服务授权
- 从保留的授权中移除了访问令牌（`access_token`）等敏感字段
- 保留了服务名称、状态、过期时间和权限范围等必要信息

### Data Minimization 实践
本导出严格遵循 data minimization 原则：
1. 仅收集和保留完成用户数据导出所必需的字段
2. 移除了所有非必要的敏感信息，如密码哈希、恢复令牌、访问令牌等
3. 对位置信息进行泛化处理，仅保留城市级别精度
4. 过滤掉已过期的第三方授权，减少不必要的数据暴露
5. 对消息中的第三方个人信息进行脱敏处理

### 敏感字段移除示例
- 从 `profile` 中移除了 `password_hash` 和 `recovery_token`
- 从 `devices` 中移除了 `push_token` 和 `session_token`
- 从 `third_party_auth` 中移除了 `access_token`

### 过期授权过滤示例
- 已过滤掉过期的 `crm_export` 服务授权