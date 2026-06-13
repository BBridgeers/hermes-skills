# Never-Run Job Patterns in Hermes Cron System

## Definition
A never-run job is defined as:
- `last_run_at: null`
- `repeat.completed: 0` 
- Created >24 hours ago
- `next_run_at` in the future

## Common Causes
1. **Scheduling mismatch**: Job created with future start time that hasn't arrived yet
2. **Dependency issues**: Job requires external conditions not yet met
3. **Configuration errors**: Invalid schedule expression or missing required parameters
4. **Toolset issues**: Job missing required `enabled_toolsets` configuration
5. **Provider/model misconfiguration**: Job references unavailable models/providers

## Investigation Procedure
1. Check job age: `created_at` vs current time
2. Verify schedule expression validity
3. Check for missing dependencies (external services, files, etc.)
4. Validate `enabled_toolsets` is not null
5. Confirm model/provider configuration is valid
6. Check if job was paused or disabled upon creation

## Resolution Paths
- If scheduling mismatch: Wait for `next_run_at` to arrive or adjust schedule
- If dependency issues: Resolve missing dependencies
- If configuration errors: Fix schedule expression or missing parameters
- If toolset issues: Add required toolsets configuration
- If model/provider misconfiguration: Update to valid alternatives
- If intentionally paused: Determine if pause should be lifted

## Prevention
- Validate job configuration at creation time
- Use `cronjob(action='create')` with proper parameters
- Test schedule expressions with cron expression validators
- Ensure all required toolsets are specified
- Verify model/provider availability before job creation

## Related References
- `references/cron-jobs-json-schema.md` - Field definitions
- `references/cron-job-analysis-patterns.md` - Failure pattern classification
- `references/null-toolsets-fix.md` - Diagnosing and fixing null toolsets bug