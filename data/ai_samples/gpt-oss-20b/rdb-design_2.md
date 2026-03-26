# リレーショナルデータベース設計の基本

## 1. 何が重要か  
リレーショナルデータベース（RDB）は、データの整合性と再利用性を担保するために設計が欠かせません。  
- **冗長性の排除** → 同じデータを複数テーブルに重複させない  
- **整合性の維持** → 参照整合性、制約で不整合を防止  
- **性能最適化** → インデックスや正規化でクエリを高速化  

設計段階を怠ると、数年後に修正が困難になる「設計悪化」に陥ります。

## 2. 目的と要件整理  
1. **ユースケースを洗い出す**（ユーザー登録、注文履歴、レポートなど）  
2. **操作頻度**（読み取り中心か書き込み中心か）  
3. **データの粒度**（詳細に格納するか、集計レベルで保持するか）  

要件が固まったら「どのテーブルに何を入れるか」を概略で決めます。

## 3. エンティティとリレーション  
- **エンティティ**：`User`, `Order`, `Product` など  
- **リレーション**：1対多・多対多を「外部キー」または「中間テーブル」で表現  

ER図（簡易）  
```
┌────────┐   1   ┌────────┐   N   ┌────────┐
│  User  │─────▶│  Order │─────▶│ OrderItem│
└────────┘       └────────┘       └────────┘
```

## 4. 正規化（Normalization）  
1. **第1正規形 (1NF)**：主キーを持つ。重複列や配列を排除。  
2. **第2正規形 (2NF)**：部分関数従属を除去。  
3. **第3正規形 (3NF)**：推移的従属を除去。  

実務では「第3正規形まで」と定義し、**パフォーマンスと保守性のバランス**を取るために必要に応じて**非正規化**（冗長列を残す）も検討。

## 5. 主キー・外部キー  
- **主キー**はユニークで不可欠。`INTEGER PRIMARY KEY AUTOINCREMENT` がよく使われる。  
- **外部キー**は参照整合性を保つ。  
  ```sql
  CREATE TABLE OrderItem (
      id      INTEGER PRIMARY KEY,
      order_id INTEGER,
      product_id INTEGER,
      quantity INTEGER,
      FOREIGN KEY (order_id) REFERENCES Order(id),
      FOREIGN KEY (product_id) REFERENCES Product(id)
  );
  ```

## 6. インデックス設計  
- **検索頻度の高い列**にインデックスを付与。  
- **結合キー**（外部キー）もインデックス化すると結合速度が向上。  
- ただしインデックスは書き込みコストを増やすので、必要最小限に留める。

## 7. 実装例（簡易スキーマ）  
```sql
-- Users
CREATE TABLE User (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE
);

-- Products
CREATE TABLE Product (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    price_cents INTEGER NOT NULL
);

-- Orders
CREATE TABLE Order (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    order_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Order Items
CREATE TABLE OrderItem (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Order(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);
```

## 8. よくある落とし穴  
| 落とし穴 | 対策 |
|----------|------|
| **冗長データの重複** | 1NF以降を徹底し、重複が必要な場合はコメントで明記 |
| **無駄な外部キー** | 参照が必須か確認し、不要なら除外 |
| **インデックス過剰** | 実際のクエリ計測で必要性を検証 |
| **非正規化の誤用** | 性能要件が明確でない限り、正規化を優先 |

## 9. まとめ  
リレーショナルデータベース設計は「要件→エンティティ→正規化→主外キー→インデックス」の循環で進めるのがベスト。  
- **設計段階で要件を明確化** → 将来の変更を容易に  
- **正規化で整合性確保** → データの信頼性  
- **インデックスで性能最適化** → 実運用の応答性  

一度設計したら、**テストデータで性能試験**を行い、必要に応じて調整します。こうした工程を繰り返すことで、メンテナンス性とパフォーマンスを両立した堅牢なデータベースが実現できます。