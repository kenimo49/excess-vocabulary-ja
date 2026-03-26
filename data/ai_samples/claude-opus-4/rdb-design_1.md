# リレーショナルデータベース設計の基本 - 良い設計のための原則とテクニック

## はじめに

リレーショナルデータベース（RDB）は、現代のアプリケーション開発において欠かせない技術です。しかし、適切に設計されていないデータベースは、パフォーマンスの低下、データの不整合、メンテナンスの困難さなど、様々な問題を引き起こします。

本記事では、RDB設計の基本原則と実践的なテクニックについて解説します。

## データベース設計の重要性

データベース設計は、システム開発の初期段階で行われる重要な作業です。一度運用が始まってしまうと、設計の変更は困難かつリスクが高くなります。そのため、初期設計の段階で以下の点を考慮することが重要です：

- **拡張性**: 将来的な機能追加やデータ量の増加に対応できるか
- **パフォーマンス**: クエリが効率的に実行できるか
- **整合性**: データの一貫性が保たれるか
- **保守性**: 理解しやすく、メンテナンスしやすい構造か

## 正規化の基本

### 第一正規形（1NF）

各カラムには単一の値のみを格納し、繰り返しグループを排除します。

**悪い例:**
```sql
-- 注文テーブル
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- "商品A,商品B,商品C"のように格納
);
```

**良い例:**
```sql
-- 注文テーブル
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

-- 注文明細テーブル
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

### 第二正規形（2NF）

主キーの一部に対する部分関数従属を排除します。

### 第三正規形（3NF）

推移的関数従属を排除し、非キー属性が主キーに直接依存するようにします。

```sql
-- 顧客テーブル（3NF）
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    prefecture_id INT,
    FOREIGN KEY (prefecture_id) REFERENCES prefectures(prefecture_id)
);

-- 都道府県マスタ
CREATE TABLE prefectures (
    prefecture_id INT PRIMARY KEY,
    prefecture_name VARCHAR(50),
    region VARCHAR(50)
);
```

## 実践的な設計テクニック

### 1. 適切な主キーの選択

主キーは以下の特性を持つべきです：

- **一意性**: 絶対に重複しない
- **不変性**: 一度設定したら変更されない
- **非NULL**: 必ず値が存在する

```sql
-- サロゲートキー（推奨）
CREATE TABLE users (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);
```

### 2. インデックスの活用

頻繁に検索条件として使用されるカラムにはインデックスを設定します：

```sql
-- 複合インデックスの例
CREATE INDEX idx_orders_customer_date 
ON orders(customer_id, order_date);

-- カバリングインデックスの例
CREATE INDEX idx_products_category_price 
ON products(category_id, price, product_name);
```

### 3. 制約の適切な使用

データの整合性を保つため、制約を積極的に活用します：

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0),
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
```

### 4. 命名規則の統一

一貫性のある命名規則を採用することで、可読性と保守性が向上します：

- テーブル名: 複数形（users, products, orders）
- カラム名: スネークケース（user_id, created_at）
- 主キー: テーブル名の単数形 + _id（user_id, product_id）
- 外部キー: 参照先テーブル名の単数形 + _id（customer_id, category_id）

## アンチパターンと対策

### 1. EAV（Entity-Attribute-Value）パターンの乱用

柔軟性を求めるあまり、すべてをkey-value形式で格納すると、クエリが複雑になります。

### 2. 過度な正規化

パフォーマンスを考慮し、適度な非正規化も検討すべきです：

```sql
-- 集計結果を保持するテーブル（非正規化の例）
CREATE TABLE order_summaries (
    order_id INT PRIMARY KEY,
    total_amount DECIMAL(10, 2),
    item_count INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

## まとめ

リレーショナルデータベース設計は、システムの基盤となる重要な作業です。正規化の原則を理解し、実践的なテクニックを適用することで、拡張性が高く、保守しやすいデータベースを構築できます。

重要なのは、教科書的な理論だけでなく、実際のユースケースやパフォーマンス要件を考慮して、バランスの取れた設計を行うことです。設計段階で十分な時間をかけることで、将来的な技術的負債を大幅に削減できるでしょう。

## 参考リンク

- [MySQL公式ドキュメント - インデックスの使用](https://dev.mysql.com/doc/refman/8.0/ja/mysql-indexes.html)
- [PostgreSQL公式ドキュメント - データベース設計](https://www.postgresql.org/docs/current/tutorial.html)