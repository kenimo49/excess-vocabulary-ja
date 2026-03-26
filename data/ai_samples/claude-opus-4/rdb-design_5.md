# リレーショナルデータベース設計の基本

## はじめに

リレーショナルデータベース（RDB）は、多くのWebアプリケーションやシステムの中核を担う重要な技術です。適切なデータベース設計は、システムのパフォーマンス、保守性、拡張性に大きく影響します。本記事では、RDB設計の基本的な概念と実践的なポイントについて解説します。

## リレーショナルデータベースとは

リレーショナルデータベースは、データを表（テーブル）形式で管理し、テーブル間の関係（リレーション）を定義することでデータを整理・管理するデータベースシステムです。

### 主な特徴
- **構造化データの管理**: 行と列からなるテーブル形式でデータを格納
- **SQL言語**: 標準化されたクエリ言語でデータを操作
- **ACID特性**: トランザクションの信頼性を保証

## 正規化の重要性

データベース設計において最も重要な概念の一つが「正規化」です。正規化により、データの重複を排除し、整合性を保つことができます。

### 第1正規形（1NF）
各カラムが単一の値を持つようにする。

```sql
-- 悪い例
CREATE TABLE orders (
    order_id INT,
    products VARCHAR(255) -- "商品A,商品B,商品C"
);

-- 良い例
CREATE TABLE orders (
    order_id INT PRIMARY KEY
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

### 第2正規形（2NF）
部分関数従属を排除する。

```sql
-- 悪い例
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100), -- product_idに依存
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- 良い例
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### 第3正規形（3NF）
推移的関数従属を排除する。

```sql
-- 悪い例
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    department_id INT,
    department_name VARCHAR(100) -- department_idに依存
);

-- 良い例
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100)
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
```

## 主キーと外部キー

### 主キー（Primary Key）
- テーブル内の各レコードを一意に識別
- NULL値を許可しない
- 自動的にインデックスが作成される

### 外部キー（Foreign Key）
- テーブル間の関係を定義
- 参照整合性を保証

```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

## インデックス設計

インデックスは検索性能を大幅に向上させますが、適切に設計しないと逆効果になることもあります。

### インデックス設計のポイント

1. **検索条件によく使用されるカラムに設定**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at);
```

2. **カーディナリティの高いカラムを優先**
   - 値の種類が多いカラムほど効果的

3. **複合インデックスは左端から利用される**
```sql
-- idx_posts_user_created インデックスは以下のクエリで有効
SELECT * FROM posts WHERE user_id = 1;
SELECT * FROM posts WHERE user_id = 1 AND created_at > '2024-01-01';

-- 以下のクエリでは効果がない
SELECT * FROM posts WHERE created_at > '2024-01-01';
```

## 設計のベストプラクティス

### 1. 命名規則の統一
```sql
-- テーブル名: 複数形
users, posts, comments

-- カラム名: スネークケース
user_id, created_at, is_active

-- 主キー: テーブル名_id
user_id, post_id
```

### 2. 適切なデータ型の選択
```sql
CREATE TABLE products (
    product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(10, 2), -- 金額は DECIMAL
    stock_quantity INT UNSIGNED, -- 在庫数は負にならない
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 制約の活用
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INT CHECK (age >= 0 AND age <= 150),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active'
);
```

## パフォーマンスを考慮した非正規化

場合によっては、パフォーマンスのために意図的に非正規化することもあります。

```sql
-- 正規化された設計
SELECT COUNT(*) FROM posts WHERE user_id = 1;

-- 非正規化: ユーザーテーブルに投稿数を保持
ALTER TABLE users ADD COLUMN post_count INT DEFAULT 0;

-- トリガーで自動更新
DELIMITER $$
CREATE TRIGGER update_post_count_on_insert
AFTER INSERT ON posts
FOR EACH ROW
BEGIN
    UPDATE users SET post_count = post_count + 1 
    WHERE user_id = NEW.user_id;
END$$
DELIMITER ;
```

## まとめ

リレーショナルデータベース設計は、システム全体の品質を左右する重要な要素です。正規化を基本としながら、実際の使用状況やパフォーマンス要件に応じて柔軟に設計を調整することが大切です。

設計時のチェックリスト：
- [ ] 適切に正規化されているか
- [ ] 主キー・外部キーが正しく設定されているか
- [ ] 必要なインデックスが設定されているか
- [ ] 命名規則が統一されているか
- [ ] データ型が適切に選択されているか
- [ ] 必要な制約が設定されているか

これらの基本を押さえることで、保守性が高く、パフォーマンスの良いデータベースを設計することができます。