# リレーショナルデータベース設計の基本

リレーショナルデータベース（RDB）は、情報を表（テーブル）に格納し、キーで結びつけることで複雑なデータ構造を扱うための強力な基盤です。設計を誤るとパフォーマンス低下やデータ不整合が発生しやすくなるため、以下の基本概念を押さえて設計を進めましょう。

## 1. エンティティ・リレーション図（ER図）で可視化

まずは業務上の「エンティティ（実体）」を洗い出し、それらの関係を図に落とし込みます。  
- **1対1（One‑to‑One）**：主キーと外部キーが同一  
- **1対多（One‑to‑Many）**：親テーブルの主キーが子テーブルの外部キーになる  
- **多対多（Many‑to‑Many）**：中間テーブル（Junction Table）を作成し、両テーブルの主キーを外部キーに持たせる  

ER図は設計段階の「共通語言」であり、チーム間のコミュニケーションを円滑にします。

## 2. 正規化とデータ冗長のバランス

データを無駄に重複させないために正規化（Normalization）を実施します。一般的には次の3つまでが推奨です。

| 正規形 | 主な目的 |
|------|--------|
| 1NF | 各列が原子値（Atomic）である |
| 2NF | 主キーに完全従属する属性だけを持つ |
| 3NF | 推論可能な非キー属性を除外する |

**例**  
```sql
-- 非正規化例
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(50), -- 重複データ
    ...
);
```
**正規化例**  
```sql
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(50)
);
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);
```

正規化を進めすぎると結合が頻繁に発生しパフォーマンスが低下する場合があるため、**テーブル設計のバランス**を取ることも重要です。

## 3. 主キー・外部キー・ユニーク制約

- **主キー（Primary Key）**  
  - テーブル内で行を一意に識別する。NULLを許容しない。  
  - 連番 (`SERIAL`, `BIGSERIAL`) や UUID などが典型的。  
- **外部キー（Foreign Key）**  
  - 参照整合性を保つ。`ON DELETE CASCADE` や `ON UPDATE CASCADE` を適切に設定。  
- **ユニーク制約（Unique Constraint）**  
  - ある列の値が重複しないことを保証。メールアドレスなどで使用。  

```sql
ALTER TABLE Orders
ADD CONSTRAINT fk_customer
FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
ON DELETE RESTRICT;
```

## 4. インデックス設計

検索性能を向上させるためにインデックスを設計しますが、書き込み性能を犠牲にしないよう注意が必要です。

| シナリオ | 推奨インデックス |
|------|------------------|
| 主キー検索 | 自動でインデックスが作成 |
| 外部キー検索 | 外部キー列にインデックス |
| 複数列検索 | コンポジットインデックス（順序に注意） |
| 頻繁にソート | `ORDER BY` で使う列にインデックス |

**ヒント**  
- **SELECT **（全列）でなく、必要な列だけを選択する。  
- **EXPLAIN** で実際のクエリ計画を確認し、不要なフルテーブルスキャンを防ぐ。

## 5. トランザクションとACID

データの一貫性を保証するため、**ACID**（Atomicity, Consistency, Isolation, Durability）を満たすトランザクションを活用します。  
```sql
BEGIN;
UPDATE Accounts SET balance = balance - 100 WHERE id = 1;
UPDATE Accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```
ロック競合が起きた場合は **ロックレベル**（行ロック vs テーブルロック）を確認し、必要に応じて **Isolation Level**（例：`READ COMMITTED`, `SERIALIZABLE`）を調整します。

## 6. データベース設計のベストプラクティス

| 項目 | 実践例 |
|------|--------|
| **命名規則** | `snake_case`（テーブル、カラム）で統一 |
| **コメント** | `COMMENT ON COLUMN` で意味を明示 |
| **データ型選択** | `VARCHAR(255)` ではなく、実際に必要な長さを設定 |
| **マイグレーション管理** | `Flyway`, `Liquibase` などでバージョン管理 |
| **監査テーブル** | 変更履歴を保持（`created_at`, `updated_at`） |

## 7. まとめ

- **ER図で全体像を可視化** → **正規化でデータ重複を排除** → **主キー・外部キーで整合性確保**  
- インデックスは **読み書きバランス** を考慮して設計  
- **トランザクション** で一貫性を保ちつつ、**ACID** 原則を遵守  

設計段階でこれらのポイントを抑えておけば、後々のパフォーマンスチューニングや保守が格段に楽になります。まずは小さく始め、必要に応じてデータモデルを進化させていく「反復的設計」を心がけましょう。

> **Q&A**  
> **Q**：多対多リレーションは必ず中間テーブルを作るべきですか？  
> **A**：はい。中間テーブルを使うことで、両テーブルの主キーを安全に管理でき、拡張性も高くなります。  

これでリレーショナルデータベース設計の基本を押さえた上で、実務に活かす準備が整いました。次のステップは「実際にテーブルを作り、データを投入してテスト走査してみる」ことです。Happy Design! 🚀