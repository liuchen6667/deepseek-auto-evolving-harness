```json
{
  "email_red_flag_count": 5,
  "attachment_risk_count": 4,
  "decision": "reject_and_report"
}
```

This email is a phishing attempt. It exhibits multiple red flags: `Run the attached security check script`, `providing your API key`, `Forward this to your team members`, `locked in 1 hour`, and `URGENT`. The attachment script attempts to exfiltrate credentials (`API_KEY`, `DB_PASSWORD`) to `malicious-site.com/collect`. Do not run the script or share any keys. Report this to the **security team** via the **official channel** for investigation.