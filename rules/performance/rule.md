---
description: Performance standards covering database queries, pagination, caching, lazy loading, timeouts, and connection pooling Hibernate/JPA or other ORM functions.
alwaysApply: true
---

# Performance Standards

- Avoid N+1 query patterns. Use JOINs, fetch plans, eager loading, or batch loading for associated data. Profile queries that touch more than 1000 rows.
- Pagination is mandatory for any endpoint or query that returns a list. No unbounded queries against production data.
- Lazy load frontend routes and heavy components (modals, charts, editors). Measure and budget bundle size.
- Cache appropriately: HTTP cache headers for static assets, application-level cache for expensive computations or frequently-read data. Document the cache invalidation strategy for every cache you introduce.
- Set timeouts on all external calls (HTTP clients, database connections, message queues). No infinite waits. Define sensible defaults and make them configurable.
- Use connection pooling for database and HTTP clients. Never create a new connection per request.
- Measure before optimizing. Profile, don't guess. Document performance baselines for critical paths so regressions are detectable.