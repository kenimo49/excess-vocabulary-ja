# リレーショナルデータベース設計の基本

## はじめに

リレーショナルデータベース（RDB）は、現代のアプリケーション開発において欠かせない技術です。適切なデータベース設計は、システムのパフォーマンス、保守性、拡張性に大きく影響します。本記事では、RDB設計の基本的な概念と実践的な設計手法について解説します。

## リレーショナルデータベースとは

リレーショナルデータベースは、データを「テーブル（表）」形式で管理し、テーブル間の関係（リレーション）を定義することでデータを体系的に整理するデータベースです。各テーブルは行（レコード）と列（カラム）で構成され、SQLを使用してデータの操作を行います。

## 正規化の重要性

### 正規化とは

正規化は、データの重複を排除し、データの整合性を保つためのプロセスです。主に以下の目的があります：

- データの重複を最小限に抑える
- 更新時の異常を防ぐ
- データの整合性を保つ
- ストレージの効率的な利用

### 主要な正規形

**第1正規形（1NF）**
```sql
-- 非正規形の例
CREATE TABLE orders_bad (
    order_id INT,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- "商品A,商品B,商品C"のような形式
);

-- 第1正規形の例
CREATE TABLE orders (
    order_id INT,
    customer_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_name VARCHAR(100)
);
```

**第2正規形（2NF）**
- 第1正規形を満たし、部分関数従属を排除
- 複合主キーの一部だけに依存する属性を別テーブルに分離

**第3正規形（3NF）**
- 第2正規形を満たし、推移的関数従属を排除
- 非キー属性間の依存関係を解消

## 主キーと外部キー

### 主キー（Primary Key）

主キーは、テーブル内の各レコードを一意に識別するための列または列の組み合わせです。

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL
);
```

### 外部キー（Foreign Key）

外部キーは、他のテーブルの主キーを参照し、テーブル間の関係を定義します。

```sql
CREATE TABLE posts (
    post_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(200),
    content TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

## テーブル間の関係

### 1対1の関係
```sql
-- ユーザーとプロフィールの関係
CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    avatar_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 1対多の関係
```sql
-- 部署と従業員の関係
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100)
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);
```

### 多対多の関係
```sql
-- 学生と講座の関係
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);

-- 中間テーブル
CREATE TABLE student_courses (
    student_id INT,
    course_id INT,
    enrollment_date DATE,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

## 設計のベストプラクティス

### 1. 命名規則の統一

```sql
-- 良い例
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 避けるべき例
CREATE TABLE tbl_Users (
    UserId INT PRIMARY KEY,
    createdDate TIMESTAMP,
    ModifiedTime TIMESTAMP
);
```

### 2. 適切なデータ型の選択

```sql
CREATE TABLE products (
    product_id INT UNSIGNED PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,  -- 金額は DECIMAL 型
    stock_quantity INT UNSIGNED DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. インデックスの活用

```sql
-- 検索頻度の高いカラムにインデックスを作成
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_created_at ON posts(created_at);

-- 複合インデックス
CREATE INDEX idx_user_created ON posts(user_id, created_at);
```

### 4. 制約の適切な設定

```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status ENUM('pending', 'processing', 'completed', 'cancelled') 
        DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## まとめ

リレーショナルデータベース設計は、システム開発の基礎となる重要なスキルです。正規化を適切に行い、主キー・外部キーを正しく設定し、テーブル間の関係を明確に定義することで、保守性が高く拡張しやすいデータベースを構築できます。

ただし、過度な正規化はパフォーマンスの低下を招く可能性があるため、実際の使用パターンやパフォーマンス要件を考慮しながら、適切なバランスを保つことが重要です。

継続的な学習と実践を通じて、より洗練されたデータベース設計スキルを身につけていきましょう。