# リレーショナルデータベース設計の基本

## はじめに

アプリケーション開発において、データベース設計は成功の鍵を握る重要な要素です。適切に設計されたデータベースは、アプリケーションのパフォーマンス向上、保守性の確保、データの整合性維持に大きく貢献します。本記事では、リレーショナルデータベース設計の基本的な概念と実践的なアプローチについて解説します。

## データベース設計の重要性

データベース設計が不適切だと、以下のような問題が発生する可能性があります：

- **パフォーマンスの低下**: 非効率なクエリの増加
- **データの整合性問題**: 重複や矛盾したデータの発生
- **保守性の悪化**: スキーマ変更の困難さ
- **拡張性の制限**: システムの成長に対応できない構造

## 正規化の基本概念

### 第1正規形（1NF）

第1正規形では、各セルに単一の値を格納し、繰り返し項目を排除します。

**良くない例:**
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    skills VARCHAR(500)  -- 'Java,Python,SQL' のような形式
);
```

**改善後:**
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employee_skills (
    employee_id INT,
    skill VARCHAR(100),
    PRIMARY KEY (employee_id, skill),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

### 第2正規形（2NF）

第2正規形では、非主キー属性が主キー全体に完全関数従属している必要があります。

**良くない例:**
```sql
CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- product_idのみに依存
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);
```

**改善後:**
```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### 第3正規形（3NF）

第3正規形では、非主キー属性間の推移的関数従属を排除します。

**良くない例:**
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100)  -- department_idに推移的に依存
);
```

**改善後:**
```sql
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## エンティティ関係（ER）モデリング

### 基本的な関係性

1. **1対1関係（One-to-One）**
   ```sql
   CREATE TABLE users (
       id INT PRIMARY KEY,
       username VARCHAR(100)
   );
   
   CREATE TABLE user_profiles (
       user_id INT PRIMARY KEY,
       bio TEXT,
       FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```

2. **1対多関係（One-to-Many）**
   ```sql
   CREATE TABLE categories (
       id INT PRIMARY KEY,
       name VARCHAR(100)
   );
   
   CREATE TABLE articles (
       id INT PRIMARY KEY,
       title VARCHAR(200),
       category_id INT,
       FOREIGN KEY (category_id) REFERENCES categories(id)
   );
   ```

3. **多対多関係（Many-to-Many）**
   ```sql
   CREATE TABLE students (
       id INT PRIMARY KEY,
       name VARCHAR(100)
   );
   
   CREATE TABLE courses (
       id INT PRIMARY KEY,
       title VARCHAR(200)
   );
   
   CREATE TABLE enrollments (
       student_id INT,
       course_id INT,
       enrollment_date DATE,
       PRIMARY KEY (student_id, course_id),
       FOREIGN KEY (student_id) REFERENCES students(id),
       FOREIGN KEY (course_id) REFERENCES courses(id)
   );
   ```

## インデックス設計の基本

### 主キーと外部キーのインデックス

```sql
-- 主キーには自動的にインデックスが作成される
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    -- 外部キーにはインデックスを作成することを推奨
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date)
);
```

### 複合インデックスの活用

```sql
-- 検索条件に応じた複合インデックス
CREATE INDEX idx_customer_date ON orders (customer_id, order_date);

-- このクエリで効果的に使用される
SELECT * FROM orders 
WHERE customer_id = 123 
AND order_date >= '2024-01-01';
```

## パフォーマンス考慮事項

### クエリ最適化を意識した設計

1. **適切なデータ型の選択**
   ```sql
   -- 効率的なデータ型を選択
   CREATE TABLE events (
       id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
       event_type ENUM('login', 'logout', 'purchase') NOT NULL,
       user_id INT UNSIGNED NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       INDEX idx_user_type_time (user_id, event_type, created_at)
   );
   ```

2. **非正規化の検討**
   ```sql
   -- 読み取りパフォーマンス向上のための意図的な非正規化
   CREATE TABLE order_summaries (
       id INT PRIMARY KEY,
       customer_id INT,
       total_amount DECIMAL(10,2),
       item_count INT,  -- 計算可能だが、頻繁にアクセスされるため保存
       order_date DATE,
       INDEX idx_customer_date (customer_id, order_date)
   );
   ```

## 実践的な設計プロセス

### 1. 要件分析
- ビジネス要件の理解
- データの種類と関係性の特定
- パフォーマンス要件の確認

### 2. 概念設計
- エンティティとその属性の特定
- 関係性の明確化
- ERダイアグラムの作成

### 3. 論理設計
- 正規化の実施
- 主キー・外部キーの定義
- 制約条件の設定

### 4. 物理設計
- インデックスの設計
- パーティショニングの検討
- ストレージエンジンの選択

## まとめ

適切なリレーショナルデータベース設計は、以下のポイントを押さえることが重要です：

- **正規化の原則を理解し、適切に適用する**
- **エンティティ間の関係性を正確にモデリングする**
- **パフォーマンスと保守性のバランスを考慮する**
- **インデックス戦略を事前に計画する**

データベース設計は一度作成して終わりではありません。アプリケーションの成長に合わせて継続的に見直し、最適化を行うことで、長期的に安定したシステムを維持できます。

初期設計の段階で時間をかけて検討することで、後の開発フェーズでの問題を大幅に減らすことができます。ぜひ本記事の内容を参考に、堅牢で効率的なデータベース設計を心がけてください。