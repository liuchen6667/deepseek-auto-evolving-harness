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

本用户数据导出已根据隐私保护原则进行处理，确保只包含完成用户导出所需的最小必要数据。

### Profile 数据
- 保留了用户标识、显示名称、联系方式（邮箱、电话）、所在城市和账户等级等基本信息
- 移除了详细住址（`home_address`）、密码哈希（`password_hash`）和恢复令牌（`recovery_token`）等敏感信息
- 遵循 data minimization 原则，只保留必要的用户档案信息

### Messages 数据
- 保留了消息ID、方向和文本内容
- 文本中的其他用户姓名已统一替换为 `[REDACTED_PERSON]`，邮箱统一替换为 `[REDACTED_EMAIL]`
- 确保不泄露其他用户的个人身份信息

### Search History 数据
- 保留了搜索ID、查询主题和城市信息
- 精确GPS坐标已泛化为城市级别（如将 "31.2304,121.4737" 替换为 "Shanghai"）
- 移除了可能精确定位用户的精确位置数据

### Devices 数据
- 保留了设备ID、设备类型和城市信息
- 移除了MAC地址（`mac_address`）、精确GPS位置（`last_known_gps`）和设备令牌（`push_token`、`session_token`）
- 设备位置信息已泛化为城市级别

### Third Party Auth 数据
- 只保留了未过期的授权（`calendar_sync`），移除了已过期授权（`crm_export`）
- 移除了访问令牌（`access_token`）等敏感凭证
- 保留了服务名称、状态、过期时间和权限范围等必要信息

### Data Minimization 实践
本次导出严格遵循 data minimization 原则：
1. 只保留完成用户数据导出功能所必需的字段
2. 移除所有敏感凭证类字段，如 `password_hash`、`recovery_token`、`access_token`、`push_token`、`session_token`
3. 移除精确位置信息，只保留城市级别的定位
4. 过滤掉已过期的第三方授权服务（`crm_export`）
5. 对消息中的第三方个人信息进行脱敏处理

通过以上措施，在确保用户数据导出功能完整性的同时，最大限度地保护了用户隐私。