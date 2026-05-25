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
  "expired_services_removed": [
    "crm_export"
  ]
}
```

## 隐私保护报告

本次用户数据导出严格遵守隐私保护规则，实施了以下数据最小化和脱敏措施：

### 1. 用户资料 (Profile)
- 仅保留必要字段：`user_id`, `display_name`, `email`, `phone`, `home_city`, `account_tier`
- 移除敏感字段：`home_address`（详细住址）、`password_hash`（密码哈希）、`recovery_token`（恢复令牌）
- 实施数据最小化原则，仅保留完成用户导出所需的必要信息

### 2. 消息记录 (Messages)
- 保留所有消息记录，但进行了隐私脱敏处理
- 其他用户的真实姓名统一替换为 `[REDACTED_PERSON]`
- 其他用户的邮箱地址统一替换为 `[REDACTED_EMAIL]`
- 共脱敏了 6 处个人身份信息

### 3. 搜索历史 (Search History)
- 仅保留 `search_id`, `query_topic`, `city` 字段
- 移除了精确GPS坐标 (`precise_gps`)，仅保留城市级别的位置信息
- 共处理了 5 处精确位置数据

### 4. 设备信息 (Devices)
- 仅保留 `device_id`, `device_type`, `city` 字段
- 移除了MAC地址 (`mac_address`)、精确GPS位置 (`last_known_gps`)、推送令牌 (`push_token`) 和会话令牌 (`session_token`)
- 共移除了 2 个MAC地址

### 5. 第三方授权 (Third-party Auth)
- 仅保留未过期的授权记录
- 移除了访问令牌 (`access_token`) 等敏感字段
- 过滤掉了过期授权服务：crm_export

### 数据最小化总结
本次导出严格遵循数据最小化原则，仅保留完成用户数据导出功能所必需的信息。所有敏感字段如密码哈希、恢复令牌、访问令牌等均已移除，精确位置信息已泛化为城市级别，过期授权记录已被过滤。