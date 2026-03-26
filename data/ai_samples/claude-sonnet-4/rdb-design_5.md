# リレーショナルデータベース設計の基本：効率的なシステムを支えるテーブル設計手法

## はじめに

リレーショナルデータベース（RDB）は、現代のアプリケーション開発において欠かせない技術の一つです。しかし、適切な設計なしにテーブル構造を作成すると、パフォーマンスの低下やデータの整合性の問題、保守性の悪化につながる可能性があります。

本記事では、効率的で保守性の高いデータベースを構築するための基本的な設計原則と実践的な手法について解説します。

## データベース設計の重要性

データベース設計は、システム全体の性能と品質を左右する重要な要素です。適切に設計されたデータベースは以下のメリットをもたらします：

- **データの整合性確保**：重複や矛盾のないデータ管理
- **パフォーマンス向上**：効率的なクエリ実行
- **保守性の向上**：変更に強い柔軟な構造
- **開発効率の向上**：直感的で理解しやすいテーブル構造

## 正規化の原則

### 第一正規形（1NF）
各列に原子値（分割できない値）のみを格納し、同一の値の型を持つことを保証します。

**悪い例：**
```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    colors VARCHAR(200)  -- 'red,blue,green' のように複数値を格納
);
```

**良い例：**
```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE product_colors (
    product_id INT,
    color VARCHAR(50),
    PRIMARY KEY (product_id, color),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### 第二正規形（2NF）
1NFを満たし、かつ主キーに部分従属する列が存在しないことを保証します。

**悪い例：**
```sql
CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- product_idのみに依存
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);
```

**良い例：**
```sql
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

### 第三正規形（3NF）
2NFを満たし、かつ推移従属関係を排除します。

**悪い例：**
```sql
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    department_id INT,
    department_name VARCHAR(100)  -- department_idから推移従属
);
```

**良い例：**
```sql
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

## テーブル設計のベストプラクティス

### 1. 適切な主キーの選択

主キーは以下の条件を満たすべきです：
- **一意性**：重複しない値
- **不変性**：値が変更されない
- **シンプルさ**：できるだけ単純な構造

```sql
-- サロゲートキー（推奨）
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- 自動生成される一意のID
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50)
);

-- 自然キー（注意が必要）
CREATE TABLE countries (
    country_code CHAR(2) PRIMARY KEY,  -- ISO国コード
    country_name VARCHAR(100)
);
```

### 2. 適切なデータ型の選択

データの性質に応じて最適なデータ型を選択することで、ストレージ効率とパフォーマンスを向上させます。

```sql
CREATE TABLE user_profiles (
    user_id INT,
    birth_date DATE,                    -- 日付にはDATE型
    is_active BOOLEAN,                  -- 真偽値にはBOOLEAN型
    balance DECIMAL(10,2),              -- 金額にはDECIMAL型
    description TEXT,                   -- 長文にはTEXT型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. インデックス戦略

頻繁に検索される列にインデックスを作成し、クエリパフォーマンスを向上させます。

```sql
-- よく検索される列にインデックス
CREATE INDEX idx_email ON users(email);

-- 複合インデックス（検索条件の組み合わせに応じて）
CREATE INDEX idx_user_status ON users(user_id, status);

-- 部分インデックス（条件付きインデックス）
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;
```

## 実践的な設計例：ECサイトの商品管理

以下は、ECサイトの商品管理システムを例とした実践的なテーブル設計です：

```sql
-- カテゴリテーブル
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- 商品テーブル
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_category (category_id),
    INDEX idx_price (price)
);

-- 商品画像テーブル
CREATE TABLE product_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
```

## まとめ

リレーショナルデータベース設計の基本は、正規化の原則を理解し、適切なテーブル構造を設計することです。以下のポイントを意識して設計を進めることで、効率的で保守性の高いデータベースを構築できます：

1. **正規化の適切な適用**：データの整合性と重複の排除
2. **主キーとインデックスの戦略的設計**：パフォーマンスの最適化
3. **データ型の適切な選択**：ストレージ効率の向上
4. **外部キー制約の活用**：データの整合性確保

データベース設計は一度決めると後から変更が困難な場合が多いため、初期の段階で十分な検討を行うことが重要です。要件の変化に対応できる柔軟性も考慮しながら、バランスの取れた設計を心がけましょう。