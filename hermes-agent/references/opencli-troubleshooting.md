# opencli Troubleshooting

opencli is a CLI tool for scraping data from websites (Bilibili, Jike, etc.). When sites change layout or environment shifts, things break.

## Common Failures

### 1. CSS selector失效 (Selector not found)

**Symptom**: `opencli <site> feed` returns empty array or `Selector not found`

**Fix**:
1. Update opencli: `npm install -g @jackwener/opencli`
2. Check login: `opencli auth status --site <site> --full`
3. Try foreground mode: `opencli <site> feed -f json --window foreground`
4. Verify Chrome is logged into the target site

**Known issues**: Jike selectors `[class*="_post_"]` break on site redesigns. Bilibili selectors change periodically.

### 2. Login state lost

**Symptom**: `opencli auth status --site <site> --full` shows `not_logged_in`

**Fix**: Open Chrome, log into the site, use `--site-session persistent` for persistence.

### 3. Cronjob model drift

**Symptom**: cronjob reports `Skipped to prevent unintended spend: global inference config drifted`

**Cause**: Model version changed (e.g. mimo-v2.5 → mimo-v2.5-pro). System pauses to prevent unexpected spend.

**Fix**: Update the cronjob's pinned model:
```bash
hermes cron edit <job_id>
```

### 4. WeChat rate limiting

**Symptom**: `Weixin send failed: iLink sendmessage rate limited`

**Cause**: Multiple cronjobs triggered in quick succession.

**Fix**: Wait a few minutes. Space out cronjob schedules to avoid hitting limits.

## Best Practices

1. Keep opencli updated — sites redesign frequently
2. Use `--site-session persistent` for login-required sites
3. Check `opencli auth status` periodically
4. Space cronjob intervals to avoid platform rate limits
