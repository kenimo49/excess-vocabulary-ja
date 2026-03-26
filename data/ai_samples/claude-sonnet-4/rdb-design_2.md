# リレーショナルデータベース設計の基本：正規化とパフォーマンスのバランス

## はじめに

リレーショナルデータベース設計は、アプリケーション開発における重要な要素の一つです。適切なデータベース設計により、データの整合性を保ち、保守性の高いシステムを構築できます。本記事では、リレーショナルデータベース設計の基本原則と実践的なアプローチについて解説します。

## 正規化の基本

### 正規化とは

正規化は、データの冗長性を排除し、データの整合性を保つためのプロセスです。主に以下の3つの正規形について理解しておく必要があります。

#### 第1正規形（1NF）
- 各属性が原子値（分割できない値）であること
- 繰り返しグループが存在しないこと

```sql
-- ❌ 非正規化状態
CREATE TABLE employees_bad (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    phone_numbers VARCHAR(200) -- "090-1111-1111,090-2222-2222"
);

-- ✅ 第1正規形
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE employee_phones (
    employee_id INT,
    phone_number VARCHAR(15),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

#### 第2正規形（2NF）
- 第1正規形を満たし、かつ完全関数従属であること
- 主キーの一部の属性のみに依存する属性を別テーブルに分離

```sql
-- ❌ 第2正規形違反
CREATE TABLE order_items_bad (
    order_id INT,
    product_id INT,
    product_name VARCHAR(50), -- product_idのみに依存
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- ✅ 第2正規形
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

#### 第3正規形（3NF）
- 第2正規形を満たし、かつ推移関数従属が存在しないこと

```sql
-- ❌ 第3正規形違反（部署名が部署IDに推移的に依存）
CREATE TABLE employees_bad (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    department_id INT,
    department_name VARCHAR(50) -- 推移的依存
);

-- ✅ 第3正規形
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## 実践的な設計原則

### 1. 適切なデータ型の選択

データ型の選択は、ストレージ効率とパフォーマンスに大きく影響します。

```sql
-- 整数型の適切な選択
CREATE TABLE users (
    id BIGINT PRIMARY KEY,        -- 大量のレコードが予想される場合
    age TINYINT UNSIGNED,         -- 0-255の範囲で十分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文字列型の適切な選択
CREATE TABLE articles (
    id INT PRIMARY KEY,
    title VARCHAR(255),           -- 可変長、インデックス効率を考慮
    slug VARCHAR(100) UNIQUE,     -- URLスラグ、適切な長さ制限
    content TEXT                  -- 長文コンテンツ
);
```

### 2. インデックス設計

クエリパフォーマンスを向上させるために、適切なインデックスを設計します。

```sql
-- 単一カラムインデックス
CREATE INDEX idx_users_email ON users(email);

-- 複合インデックス（順序が重要）
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 部分インデックス（条件付きインデックス）
CREATE INDEX idx_orders_pending ON orders(created_at) 
WHERE status = 'pending';
```

### 3. 外部キー制約

データの整合性を保つために外部キー制約を適切に設定します。

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## パフォーマンス考慮事項

### 非正規化の判断

高いパフォーマンスが要求される場合、意図的な非正規化を検討することがあります。

```sql
-- 読み取りパフォーマンス重視の場合
CREATE TABLE order_summary (
    id INT PRIMARY KEY,
    user_id INT,
    user_name VARCHAR(50),        -- 非正規化：JOIN回避
    total_amount DECIMAL(10, 2),
    item_count INT,               -- 非正規化：集計値の保存
    created_at TIMESTAMP
);
```

### パーティショニング

大量のデータを扱う場合、テーブルパーティショニングを検討します。

```sql
-- 日付によるパーティショニング例（MySQL 8.0）
CREATE TABLE access_logs (
    id BIGINT,
    user_id INT,
    action VARCHAR(50),
    created_at DATE
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

## 設計時のベストプラクティス

### 1. 命名規則の統一

```sql
-- 一貫した命名規則の例
CREATE TABLE user_profiles (          -- テーブル名：複数形、スネークケース
    id INT PRIMARY KEY,               -- 主キー：id
    user_id INT NOT NULL,            -- 外部キー：参照テーブル名_id
    first_name VARCHAR(50),          -- カラム名：スネークケース
    last_name VARCHAR(50),
    created_at TIMESTAMP,            -- 作成日時：created_at
    updated_at TIMESTAMP             -- 更新日時：updated_at
);
```

### 2. ドキュメント化

```sql
-- コメントによるドキュメント化
CREATE TABLE products (
    id INT PRIMARY KEY COMMENT '商品ID',
    sku VARCHAR(50) UNIQUE COMMENT '商品コード（Stock Keeping Unit）',
    name VARCHAR(255) NOT NULL COMMENT '商品名',
    price DECIMAL(10, 2) COMMENT '価格（税抜）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '販売中フラグ'
) COMMENT = '商品マスタテーブル';
```

## まとめ

リレーショナルデータベース設計では、正規化によるデータの整合性確保と、パフォーマンス要件のバランスを取ることが重要です。基本的な正規化原則を理解した上で、アプリケーションの特性に応じて適切な設計判断を行いましょう。

また、設計段階で将来の拡張性を考慮し、一貫した命名規則や適切なドキュメント化を行うことで、保守性の高いデータベースを構築できます。継続的な監視と最適化により、長期的に安定したシステムの運用が可能になります。