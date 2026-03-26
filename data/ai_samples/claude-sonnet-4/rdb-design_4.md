# リレーショナルデータベース設計の基本：実践的なアプローチ

データベース設計は、システム開発において最も重要な工程の一つです。適切に設計されたデータベースは、アプリケーションのパフォーマンス、保守性、拡張性に大きな影響を与えます。本記事では、リレーショナルデータベース設計の基本的な概念と実践的な手法について解説します。

## 1. データベース設計の基本原則

### 1.1 データの整合性を保つ

データベース設計において最も重要なのは、データの整合性を保つことです。これには以下の要素が含まれます：

- **エンティティ整合性**: 主キーの一意性とNULLでないことを保証
- **参照整合性**: 外部キーによる関連データの存在を保証
- **ドメイン整合性**: カラムの値が適切な範囲内であることを保証

### 1.2 冗長性の最小化

不要なデータの重複を避けることで、データの不整合や更新異常を防ぎます。これは正規化によって実現されます。

## 2. 正規化の基本

正規化は、データの冗長性を排除し、整合性を保つための手法です。

### 2.1 第1正規形（1NF）

各セルに単一の値のみを格納し、繰り返しグループを排除します。

```sql
-- 非正規化（悪い例）
CREATE TABLE orders_bad (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- カンマ区切りで複数商品
);

-- 第1正規形（良い例）
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

### 2.2 第2正規形（2NF）

第1正規形かつ、非キー属性が主キー全体に完全従属していることを要求します。

```sql
-- 第2正規形違反（悪い例）
CREATE TABLE order_details_bad (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- product_idのみに従属
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- 第2正規形（良い例）
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100)
);

CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### 2.3 第3正規形（3NF）

第2正規形かつ、非キー属性間の推移的従属を排除します。

```sql
-- 第3正規形違反（悪い例）
CREATE TABLE employees_bad (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100)  -- department_idから推移的に従属
);

-- 第3正規形（良い例）
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100)
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
```

## 3. 実践的な設計手法

### 3.1 エンティティ関係図（ER図）の活用

データベース設計では、まずER図を作成してエンティティ間の関係を明確にします。

```
顧客 (1) ←→ (N) 注文 (N) ←→ (M) 商品
     ↑              ↑              ↑
customer_id    order_id      product_id
name           customer_id   name
email          order_date    price
```

### 3.2 インデックス設計

クエリパフォーマンスを向上させるため、適切なインデックスを設計します。

```sql
-- 主キーには自動的にインデックスが作成される
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- よく検索される列にインデックスを追加
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 複合インデックスの活用
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

## 4. パフォーマンスを考慮した設計

### 4.1 適切なデータ型の選択

```sql
-- 効率的なデータ型の選択例
CREATE TABLE user_profiles (
    user_id INT UNSIGNED,           -- 負の値が不要な場合はUNSIGNED
    status TINYINT,                -- 小さな整数値
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,              -- 長いテキスト用
    age TINYINT UNSIGNED           -- 0-255の範囲で十分
);
```

### 4.2 非正規化の適切な活用

読み取り性能が重要な場合、意図的な非正規化も検討します。

```sql
-- 集計値を事前計算して保存（非正規化の例）
CREATE TABLE user_statistics (
    user_id INT PRIMARY KEY,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    last_order_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 5. 実際の設計例

ECサイトの簡単な例を示します：

```sql
-- ユーザーテーブル
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品テーブル
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0
);

-- 注文テーブル
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 注文詳細テーブル
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## まとめ

リレーショナルデータベース設計は、以下のポイントを押さえることが重要です：

1. **正規化を基本とする**: データの整合性を保ち、冗長性を排除
2. **適切な制約の設定**: 主キー、外部キー、一意制約の活用
3. **インデックス戦略**: クエリパフォーマンスを考慮した設計
4. **将来の拡張性**: ビジネス要件の変化に対応できる柔軟な設計

良いデータベース設計は、アプリケーション全体の品質向上につながります。要件を十分に理解し、段階的に設計を進めることで、保守性と性能を両立したデータベースを構築できます。