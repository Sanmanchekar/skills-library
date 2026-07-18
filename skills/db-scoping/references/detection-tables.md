# Detection tables — db-scoping

Read this file when Step 2 (Build the table inventory) or Step 3 (Classify + find migration evidence) needs to sweep the service.

You're auditing ONE service and resolving everything to **physical table names**.

## Raw SQL (any language — string literals + `.sql` files)
| Signal | Patterns to grep | Access |
|---|---|---|
| Read | `FROM\s+[\`"'\[]?(\w+)`, `JOIN\s+[\`"'\[]?(\w+)` | R |
| Insert | `INSERT\s+INTO\s+[\`"'\[]?(\w+)`, `INTO\s+(\w+)\s*\(` | W |
| Update | `UPDATE\s+[\`"'\[]?(\w+)\s+SET` | W |
| Delete | `DELETE\s+FROM\s+[\`"'\[]?(\w+)` | W |
| Upsert | `ON\s+CONFLICT`, `ON\s+DUPLICATE\s+KEY`, `MERGE\s+INTO\s+(\w+)`, `REPLACE\s+INTO\s+(\w+)` | W |
| Exec entry points | `cursor.execute`, `session.execute(text(`, `db.query`, `conn.exec`, `.raw(`, `knex.raw`, `sequelize.query` | (parse the SQL) |

## ORM model → physical table (declaration = potential ownership; query = access)
| Stack | Model declaration | Physical table name source | Query/write verbs |
|---|---|---|---|
| Django | `class X(models.Model)` | `Meta.db_table` else `<applabel>_<classname_lower>` | `.objects.filter/get/all` (R); `.save/.create/.update/.delete/.bulk_create` (W) |
| SQLAlchemy (declarative) | `class X(Base)` | `__tablename__` | `session.query/select` (R); `session.add/.merge/.delete`, `Model()` + commit (W) |
| SQLAlchemy (core) | `Table('name', metadata, …)` | first arg | `.select()` (R); `.insert()/.update()/.delete()` (W) |
| Prisma | `model X {` in `schema.prisma` | `@@map("name")` else model name | `.findMany/.findUnique` (R); `.create/.update/.upsert/.delete` (W) |
| TypeORM | `@Entity('name')` / `@Entity({name:…})` | arg | `.find/.findOne/QueryBuilder` (R); `.save/.insert/.update/.delete` (W) |
| Sequelize | `sequelize.define('name'`, `@Table` | `tableName` else pluralized model | `.findAll/.findByPk` (R); `.create/.update/.destroy` (W) |
| ActiveRecord (Rails) | `class X < ApplicationRecord` | `self.table_name=` else `pluralize(X)` | `.where/.find` (R); `.save/.create/.update/.destroy` (W) |
| GORM (Go) | struct + `func (X) TableName()` | return value else `pluralize(snake(X))` | `.Find/.First` (R); `.Create/.Save/.Update/.Delete` (W) |
| JPA/Hibernate | `@Entity` + `@Table(name=…)` | `@Table.name` else class name | `find/JPQL/criteria` (R); `persist/merge/remove` (W) |
| Mongoose (Mongo) | `mongoose.model('X', schema)` | collection = pluralized `X` | `.find` (R); `.create/.updateOne/.deleteOne` (W) |
| Ecto (Elixir) | `schema "name"` | arg | `Repo.all/.get` (R); `Repo.insert/.update/.delete` (W) |

## Migrations (ownership evidence — who CREATEs the table)
| Stack | Signal |
|---|---|
| Any SQL | `CREATE TABLE`, `ALTER TABLE`, `V<n>__*.sql` (Flyway), Liquibase changesets |
| Django | `migrations/` dir, `migrations.CreateModel`, `AlterField` |
| Alembic | `alembic/versions/`, `op.create_table` |
| Rails | `db/migrate/`, `create_table` |
| Prisma | `prisma/migrations/`, `CREATE TABLE` in `migration.sql` |
| TypeORM | `@migration`, `queryRunner.createTable` |

## Shared / generated all-tables models module (the ambient-access anti-pattern)
| Signal | Patterns to grep |
|---|---|
| Giant generated models file | a single models file far larger than the service's own tables (e.g. `sqlacodegen`/`inspectdb` output); count declared tables vs. tables the service actually queries |
| Broad import | `from <shared_models> import *`, `import { * } from './models'`, one module re-exporting hundreds of entities |
| Signal to compute | `declared_tables` (in the module) − `queried_tables` (actually used) = ambient surface to shed |

## Cross-context coupling smells (severity)
| Smell | Detect | Severity |
|---|---|---|
| `foreign-write` | INSERT/UPDATE/DELETE/upsert on a table with no local migration + outside owned domain | 🔴 CRITICAL |
| `cross-domain-txn` | a foreign write (or read-for-update) inside the same `transaction`/`atomic`/`BEGIN…COMMIT` as an owned write | 🔴 CRITICAL |
| `cross-context-join` | a single SQL `JOIN` (or ORM relation traversal) between an owned table and a foreign table | 🟠 HIGH |
| `ambient-schema-import` | service imports an all-tables shared models module (no bounded context) | 🟠 HIGH |
| `foreign-column-read` | SELECT of specific columns of a foreign table (silent break when owner alters schema) | 🟠 HIGH |
| `foreign-fk` | FK / ORM relationship constraint pointing at a foreign table (hard DB coupling; blocks independent deploy/shard) | 🟡 MEDIUM |
| `shared-reference-read` | direct read of a central config/reference table | 🟡 MEDIUM |
| `ambient-unused` | table reachable via import but never queried | 🟢 LOW |

## Ownership inference (single-service audit)

You cannot see the other services, so infer ownership from evidence, weakest claim to strongest:

1. **Migration evidence (strongest)** — if the service's own migrations `CREATE TABLE`/`CreateModel`/`create_table` it, that's a strong `owned` signal. A table queried with **no** local migration touching it is likely foreign.
2. **Write asymmetry** — writing a table you created ⇒ owned. Writing a table you did NOT create ⇒ `foreign-write` (the red flag). Reading only ⇒ at most `foreign-read`.
3. **Domain-name mapping** — apply user-supplied `domain_map` if given; else use naming heuristics (prefixes/roots) and mark `inferred`.
4. **Shared models module** — a large generated models file exposing the whole DB means the service has *ambient* access to everything. Only the subset it actually queries counts; of that subset, anything it doesn't own is a real dependency, the rest is `ambient`.

Always tag inferred ownership as `inferred: true` and list it under "Confirm with architecture" — mirror the discipline of not adjudicating org ownership yourself.
