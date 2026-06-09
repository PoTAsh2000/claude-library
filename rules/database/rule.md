---
description: SQL database design standards covering normalization, key design, index policy, naming conventions, data types, constraints, and schema documentation requirements.
alwaysApply: true
---

# Database Design Standards

## Normalization

- Always design normalized schemas. Default target is Fourth Normal Form (4NF): atomic values, no partial dependencies, no transitive dependencies, no independent multi-valued facts about the same entity.
- Never denormalize speculatively. Denormalization is a deliberate, documented performance decision made after profiling — not a shortcut taken during initial design.
- When intentional denormalization is chosen, add a comment to the table or column explaining the reason, what normal form was relaxed, and what read pattern justifies the tradeoff.

## Primary Keys

- Every table must have a primary key. No exceptions.
- Use surrogate keys (auto-increment integer or UUID) as the physical primary key by default. Natural keys may serve as unique constraints, not as primary keys, unless the natural key is truly immutable, globally unique, and never null.
- Use UUIDs when records are exposed in URLs, shared across distributed systems, or when insertion order must not be inferable by clients. Use auto-increment integers for internal-only tables where sequential IDs are acceptable.
- Never use composite primary keys except in pure join tables (many-to-many associations with no additional attributes). If a join table gains any non-key columns, give it a surrogate primary key.

## Foreign Keys

- Declare foreign key constraints for every relationship between tables. Do not rely on application code to enforce referential integrity.
- Define explicit cascade behavior for every foreign key: `ON DELETE CASCADE`, `ON DELETE SET NULL`, `ON DELETE RESTRICT`, or `ON DELETE NO ACTION`. Never leave cascade behavior implicit.
- Never delete parent records that have child records without first deciding and documenting the intended cascade behavior.
- Never drop columns or tables without first confirming the data is no longer needed.

## Index Policy

- Apply a conservative index policy: only create an index when a clear query pattern demands it and the table is expected to grow beyond a few hundred rows.
- Always discuss and document each index: which query it serves, which columns it covers, whether it is a covering index, and the write-overhead tradeoff accepted.
- The primary key is always indexed automatically — do not duplicate it.
- Add indexes on foreign key columns — most databases do not create these automatically, and unindexed foreign keys cause full-table scans on joins.
- Add indexes on columns used in frequent `WHERE`, `ORDER BY`, or `JOIN ON` clauses where table size warrants it.
- Never add speculative indexes "just in case." Measure query plans before adding indexes on existing tables.
- Remove unused indexes. Every index slows writes and consumes storage.

## Naming Conventions

- Use `snake_case` for all identifiers: tables, columns, indexes, constraints, sequences.
- Use plural nouns for table names: `orders`, `line_items`, `users`, `product_categories`.
- Use `id` as the primary key column name on every table.
- Name foreign key columns as `[referenced_table_singular]_id` (e.g., `order_id` on `line_items`).
- Name join tables as `[table_a]_[table_b]` in alphabetical order (e.g., `products_tags`).
- Name indexes as `idx_[table]_[columns]` (e.g., `idx_orders_user_id`).
- Name unique constraints as `uq_[table]_[columns]` (e.g., `uq_users_email`).
- Name check constraints as `chk_[table]_[description]` (e.g., `chk_line_items_quantity_positive`).
- Name foreign key constraints as `fk_[table]_[referenced_table]` (e.g., `fk_line_items_orders`).
- Never use reserved SQL keywords as identifiers. Never abbreviate — spell out column names in full.

## Data Types

- Choose the most specific type that accurately represents the data: `BOOLEAN` not `TINYINT`, `DATE` not `VARCHAR`, `DECIMAL` for monetary values not `FLOAT`.
- Never use `FLOAT` or `DOUBLE` for monetary or financial values. Use `DECIMAL(precision, scale)` with explicit precision.
- Store timestamps as `TIMESTAMP WITH TIME ZONE` (or database equivalent). Never store dates as strings or epoch integers unless interfacing with a system that requires it — document the reason.
- Use `TEXT` for variable-length strings with no meaningful maximum. Use `VARCHAR(n)` only when a maximum length is a genuine business constraint. Do not use `VARCHAR(255)` as a default — choose the length intentionally.
- Use `JSONB` (or equivalent) only for genuinely schemaless supplementary data. Do not store relational data in JSON columns to avoid proper table design.

## Constraints and Validation

- Enforce data integrity at the database level, not only in application code. Constraints are the last line of defense.
- Add `NOT NULL` constraints on every column that must always have a value. Nullable columns must have a clear business reason for accepting nulls.
- Add `UNIQUE` constraints for any column or combination that must be unique by business rules. Example: `CONSTRAINT uq_users_email UNIQUE (email)`
- Add `CHECK` constraints for domain rules expressible as predicates. Example: `CONSTRAINT chk_line_items_quantity_positive CHECK (quantity > 0)`
- Email format example: `CONSTRAINT chk_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')`
- Never seed production data in migration files — use dedicated seed files.
- Never use raw SQL when the ORM/migration tool provides a method for the operation.

## Schema Documentation

- Every table must have a comment describing its purpose, the entity it represents, and any non-obvious design decisions.
- Every non-obvious column must have a comment. Self-explanatory columns do not need comments — avoid noise.
- Document every intentional deviation from normalization inline at the point of deviation.
- Each migration file must include a comment block stating: what schema change it makes, why it is needed, and whether it is reversible.
- Update documentation whenever database changes are made.
