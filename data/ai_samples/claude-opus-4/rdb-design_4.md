# リレーショナルデータベース設計の基本

## はじめに

リレーショナルデータベース（RDB）は、多くのアプリケーションにおいてデータ管理の中核を担っています。適切なデータベース設計は、システムのパフォーマンス、拡張性、保守性に直接影響を与えるため、エンジニアにとって必須のスキルです。

本記事では、リレーショナルデータベース設計の基本概念と実践的な設計手法について解説します。

## リレーショナルモデルの基本概念

### テーブル（リレーション）
リレーショナルデータベースの基本単位はテーブルです。テーブルは行（レコード）と列（カラム）で構成され、各行は一意のデータエントリを表します。

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 主キー（Primary Key）
主キーは、テーブル内の各行を一意に識別するための列または列の組み合わせです。主キーには以下の特徴があります：

- NULL値を含まない
- 重複する値を持たない
- 一度設定されると変更されない

### 外部キー（Foreign Key）
外部キーは、別のテーブルの主キーを参照する列です。これによりテーブル間の関係性を定義します。

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 正規化の重要性

正規化は、データの重複を最小限に抑え、データの整合性を保つための設計手法です。

### 第1正規形（1NF）
- 各カラムの値は原子的（これ以上分割できない）
- 繰り返しグループが存在しない

**悪い例：**
```
| order_id | products          |
|----------|-------------------|
| 1        | りんご,みかん,バナナ |
```

**良い例：**
```
| order_id | product  |
|----------|----------|
| 1        | りんご    |
| 1        | みかん    |
| 1        | バナナ    |
```

### 第2正規形（2NF）
- 第1正規形を満たす
- 非キー属性が主キーに完全関数従属

### 第3正規形（3NF）
- 第2正規形を満たす
- 非キー属性間に推移的関数従属が存在しない

## ER図を使った設計プロセス

### 1. エンティティの識別
システムで管理すべき主要な概念やオブジェクトを識別します。

例：ECサイトの場合
- ユーザー
- 商品
- 注文
- カテゴリー

### 2. 属性の定義
各エンティティが持つ属性を定義します。

```
ユーザー：
- ユーザーID
- 名前
- メールアドレス
- 登録日時

商品：
- 商品ID
- 商品名
- 価格
- 在庫数
```

### 3. リレーションシップの定義
エンティティ間の関係を明確にします。

- 1対1：ユーザーとユーザープロフィール
- 1対多：ユーザーと注文
- 多対多：注文と商品

## 実践的な設計のベストプラクティス

### 1. 適切なデータ型の選択
```sql
-- 良い例
CREATE TABLE products (
    id BIGINT UNSIGNED PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER UNSIGNED DEFAULT 0
);

-- 避けるべき例
CREATE TABLE products (
    id VARCHAR(255) PRIMARY KEY,  -- 文字列のIDは避ける
    name TEXT,                     -- 不必要に大きなデータ型
    price FLOAT                    -- 金額にFLOATは不適切
);
```

### 2. インデックスの活用
頻繁に検索条件として使用される列にはインデックスを作成します。

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id_date ON orders(user_id, order_date);
```

### 3. 制約の適切な使用
データの整合性を保つため、適切な制約を設定します。

```sql
ALTER TABLE orders
ADD CONSTRAINT chk_order_amount CHECK (total_amount >= 0);

ALTER TABLE products
ADD CONSTRAINT uq_product_code UNIQUE (product_code);
```

## パフォーマンスを考慮した設計

### 非正規化の検討
読み取りパフォーマンスが重要な場合、あえて非正規化することもあります。

```sql
-- 正規化された設計
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- 非正規化（カウンターカラムの追加）
ALTER TABLE users ADD COLUMN order_count INTEGER DEFAULT 0;
```

### パーティショニング
大量のデータを扱う場合、テーブルを論理的に分割します。

```sql
CREATE TABLE orders_2024 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## まとめ

リレーショナルデータベース設計は、以下のポイントを押さえることが重要です：

1. **基本概念の理解**：主キー、外部キー、正規化の概念をしっかり理解する
2. **適切な正規化**：データの整合性を保ちつつ、パフォーマンスを考慮した設計
3. **将来の拡張性**：ビジネス要件の変化に対応できる柔軟な設計
4. **パフォーマンスの考慮**：インデックスや非正規化を適切に活用

優れたデータベース設計は、アプリケーションの品質と開発効率を大きく向上させます。基本をしっかり押さえ、実践を通じてスキルを磨いていくことが大切です。