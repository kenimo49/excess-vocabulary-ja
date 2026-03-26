# リレーショナルデータベース設計の基本：正規化から実装まで

## はじめに

リレーショナルデータベース（RDB）は、現代のWebアプリケーション開発において欠かせない技術です。適切なデータベース設計は、システムのパフォーマンス、保守性、拡張性に大きく影響します。本記事では、RDB設計の基本概念から実践的な設計手法まで、エンジニアが知っておくべき重要なポイントを解説します。

## リレーショナルデータベースとは

リレーショナルデータベースは、データを表（テーブル）形式で管理し、表同士の関係（リレーション）を定義することで、複雑なデータ構造を表現できるデータベースシステムです。

### 基本用語

- **テーブル（表）**: データを格納する基本単位
- **レコード（行）**: テーブル内の1件のデータ
- **カラム（列）**: データの属性を表す項目
- **主キー（Primary Key）**: レコードを一意に識別する列
- **外部キー（Foreign Key）**: 他のテーブルとの関連を表す列

## 正規化の重要性

正規化は、データの重複を排除し、データの整合性を保つための設計手法です。

### 第1正規形（1NF）
繰り返し項目を排除し、各セルに原子的な値を格納します。

```sql
-- 正規化前
CREATE TABLE orders_bad (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- "商品A,商品B,商品C"のような形式
);

-- 正規化後
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

### 第2正規形（2NF）
部分関数従属を排除します。非キー属性は主キー全体に従属する必要があります。

### 第3正規形（3NF）
推移的関数従属を排除します。非キー属性間の依存関係を取り除きます。

```sql
-- 正規化前
CREATE TABLE employees_bad (
    employee_id INT PRIMARY KEY,
    department_id INT,
    department_name VARCHAR(100)  -- department_idに従属
);

-- 正規化後
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

## リレーションシップの種類

### 1対1（One-to-One）
各レコードが相手側の1つのレコードと対応します。

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50)
);

CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    avatar_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 1対多（One-to-Many）
1つのレコードが相手側の複数のレコードと対応します。

```sql
CREATE TABLE authors (
    author_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title VARCHAR(200),
    author_id INT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
```

### 多対多（Many-to-Many）
中間テーブルを使用して関係を表現します。

```sql
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);

CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    enrollment_date DATE,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

## インデックス設計

適切なインデックス設計は、クエリのパフォーマンスを大幅に向上させます。

### インデックスを作成すべきケース

1. **検索条件によく使用される列**
```sql
CREATE INDEX idx_users_email ON users(email);
```

2. **結合条件に使用される列**
```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

3. **ソートに使用される列**
```sql
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

### 複合インデックス
複数の列を組み合わせたインデックスは、特定のクエリパターンに効果的です。

```sql
CREATE INDEX idx_users_name_created ON users(last_name, first_name, created_at);
```

## 実践的な設計のポイント

### 1. 命名規則の統一
- テーブル名：複数形（users, orders）
- カラム名：スネークケース（user_id, created_at）
- 主キー：`テーブル名_id`
- 外部キー：`参照テーブル名_id`

### 2. 適切なデータ型の選択
```sql
CREATE TABLE products (
    product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT UNSIGNED DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 制約の活用
```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status ENUM('pending', 'processing', 'completed', 'cancelled') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## まとめ

リレーショナルデータベースの設計は、システム全体の品質を左右する重要な工程です。正規化による冗長性の排除、適切なリレーションシップの定義、パフォーマンスを考慮したインデックス設計など、基本原則を理解し実践することで、保守性が高く拡張可能なデータベースを構築できます。

設計段階で十分な検討を行い、将来の要件変更にも対応できる柔軟な構造を目指しましょう。また、実際の運用においては、パフォーマンスとのバランスを考慮し、必要に応じて意図的な非正規化を行うことも重要です。