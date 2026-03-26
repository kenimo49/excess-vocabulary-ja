# GraphQL,Apolloについて

Apolloは、オープンソースのGraphQLサーバーである。apollo serverがメインライブラリであり、apollo serverはHTTPリクエストとレスポンスをGraphQL操作に変換し、プラグインや、その他機能をサポートする。

javascriptを使用したプロジェクトを構築場合では、version4では、graphql-jsと@appolo/serverの依存関係をインストールする必要がある。`npm install @apollo/server graphql`

```tsx
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";

// スキーマ定義
// スキーマとは、データに対して実行されるクエリの "形 "を定義する型定義のコレクションである。
// データに対して実行されるクエリの "形 "を定義します
const typeDefs = `#graphql
  # このようにテンプレートリテラルでGraphQLを接頭辞に使うと、
	# 対応するIDEでGraohQL構文が強調表示される。GraphQL文字列は(#)記号で始まります。

  # この "Book "タイプは、データ・ソース内のすべてのブックに対してクエリ可能なフィールドを定義します。
  type Book {
    title: String
    author: String
  }
  # Query タイプは特別である。
  # クライアントが実行できるすべてのクエリと、それぞれの返り値の型が表示されます。
  # この場合、"books" クエリは、0 個以上の Books の配列を返します。

  type Query {
    books: [Book]
  }
`;

// データセットの定義
const books = [
  {
    title: 'The Awakening',
    author: 'Kate Chopin',
  },
  {
    title: 'City of Glass',
    author: 'Paul Auster',
  },
];

// リゾルバの定義。
// リゾルバは、スキーマで定義された型の取得方法をApollo serverに指示します。
// このリゾルバは、上記の "books "配列から書籍を取得する。
const resolvers = {
  Query: {
    books: () => books,
  },
};

// ApolloServerコンストラクタは、スキーマ定義とリゾルバの2つのパラメータを必要とします。
const server = new ApolloServer({
  typeDefs,
  resolvers,
});

// startStandaloneServer`関数にApolloServerインスタンスを渡す：
// 1. Expressアプリを作成する。
// 2. ApolloServerインスタンスをミドルウェアとしてインストールします。
// 3. リクエストを処理するためにアプリを準備します。
const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
});

console.log(`🚀  Server ready at: ${url}`);

// npm start => 「🚀  Server ready at: http://localhost:4000/」
```

## GraphQLスキーマの基本

GraphQLサーバーは、スキーマを使用して使用可能なデータを記述する。このスキーマは、バックエンドデータストアから入力されるフィールドの持つ型の階層を定義する。

また、スキーマは、クライアントが実行できるクエリとミューテーションを正確に指定する。

GraphQL仕様では、スキーマを定義して、文字列として保存するために、人間が読めるスキーマ定義言語（**schema definition language**またはSDL）を定義している。

```graphql
# 以下は、2つのオブジェクト型を定義するスキーマの簡単な例　:Book,:Author
type Book {
  title: String
  author: Author
}

type Author {
  name: String
  books: [Book]
}
```

スキーマは、型のコレクションと、それらの型間の関係を定義する。

上記のスキーマでは、Bookは関連するAuthorを持つことができ、AuthorはBookのリストを持つことができる。クライアント開発者は利用可能なデータを正確に把握し、最適化されたクエリ1つでそのデータの特定のサブセットデータを要求することができる。

## フィールド定義

定義したschema typesのほとんどは、1つ以上のフィールドを持つ。

```graphql
# このBooks typeには２つのフィールドがある。title and author
type Book {
  title: String # returns a String
  author: Author # returns an Author
}

# 各フィールドは、指定された型のデータを返す。
# フィールドの戻り値の型は、
#　Scalar, Object, Input, Enum, Union, Interfaceのいずれかである。

# リスト形式のフィールドは角かっこ[]で表現する。

type Author {
  name: String
  books: [Book] # A list of Books
}
```

### フィールドのnull可能について

デフォルトでは、スキーマ内のどのフィールドでも、指定された型のかわりにnullを返すことができる。特定のフィールドがnullを返却しないようにするには感嘆符(!)をつける。

```graphql
type Author {
  name: String! # Can't return null
  books: [Book]
}
#これらのフィールドはnull不可です。NULL値を返せないフィールドに対してサーバが
# NULL を返そうとすると、エラーが発生します。
type Author {
  books: [Book!]! # This list can't be null AND its list *items* can't be null
}

# もし [!] が角かっこの中にある場合、返されるリストにnullの項目を含めることはできません
# もし [!] が角かっこの外側にある場合、リスト自体はnullにはなりません。
```

### Typesについて

- **Scaler types**
Scaler型は、お好きなプログラミング言語のプリミティブ型に似ている。これらは常に具体的なデータに解決される。
    - Int : 符号付き32bit整数
    - Float : 符号付き倍精度浮動小数点値
    - String : UTF-8 char文字列
    - Boolean : true or false
    - ID (stringとしてのシリアライズ) : オブジェクトのリフェッチやキャッシュのキーとしてよく使われる一意の識別子。Stringとしてシリアライズされますが、IDは人間が読めるようには意図されていない。
    
    これらのプリミティブ型は、ほとんどのユースケースをカバーする。より具体的な型はカスタムのスカラー型を作成することで対応できる
    
- **Object types**
GraphQL schemaで定義する型のほとんどはObject型。Object型はフィールドのコレクションを含み、各フィールドは独自の型を持つ。
    
    先ほどのスキーマの例のように、2つのObject型がお互いをフィールドとして含むことができる。
    
    ```graphql
    type Book {
      title: String
      author: Author
    }
    
    type Author {
      name: String
      books: [Book]
    }
    ```
    
    - **__typename field**
    スキーマ内の全てのObject型は自動的に`__typename`というフィールドを持つ。typenameフィールドはObject型の名前を文字列として返却する。（例えば上記のコードではBookやAuthor)
    GraphQLクライアントは、typenameを多くの目的で利用している。例えば、複数の型を返す可能性のあるフィールド（UnionやInterface)から、どの型が返却されたかを判断するためなど。Apollo Clientはリザルトをキャッシュする際に、`__typename` に依存するため、全てのクエリの全てのオブジェクトに自動的に含まれる。
- Query type
Query型は特別なObject型で、クライアントがサーバに対して実行するクエリのトップレベルのエントリポイントを全て定義する。Query型の各フィールドは、異なるエントリポイントの名前と戻り値の型を定義する。
    
    ```graphql
    type Query {
      books: [Book]
      authors: [Author]
    }
    # このQueryは、booksとauthorsという2つのフィールドを定義しており
    # それぞれのフィールドは対応する型のリストを返します。
    ```
    
    RESTベースのAPIでは、書籍と著者はおそらく異なるエンドポイント（例えば/api/booksと/api/authors）から返されるでしょう。GraphQLの柔軟性により、クライアントは単一のリクエストで両方のリソースを照会することができる。
    
- Mutation type
Mutation型はQuery型と構造も目的も似ている。Query型が読み取り操作のエントリポイントを定義するのに対して、Mutation型は書き込み操作のエントリポイントを定義する。
Mutation型の各フィールドは、異なるエントリポイントのシグネチャと戻り値を定義する。
    
    ```graphql
    type Mutation {
      addBook(title: String, author: String): Book
    }
    ```
    
    このMutation型は、二つの引数(title and author)を受け取り、新しく作成されたBookオブジェクトを返却する。
    
- Input type
Input型はフィールドの引数として階層データを与えることができる。Input型の定義はObject型と似ているが、Inputキーワードを用いる。
    
    ```graphql
    input BlogPostContent {
      title: String
      body: String
    }
    
    # Input型の各フィールドは、scalar, enum または別のinput型のみとすることができる
    input BlogPostContent {
      title: String
      body: String
      media: [MediaDetails!]
    }
    
    input MediaDetails {
      format: MediaFormat!
      url: String!
    }
    
    enum MediaFormat {
      IMAGE
      VIDEO
    }
    # 定義した後はその型を引数として受け取ることができる
    type Mutation {
      createBlogPost(content: BlogPostContent!): Post
      updateBlogPost(id: ID!, content: BlogPostContent!): Post
    }
    
    # Input型は複数のオペレーションがまったく同じ情報セットを必要とする場合に便利なこともあるが、
    # 再利用は控えめにすべきである。
    # オペレーションはいずれ、要求される引数のセットにおいて分岐するかもしれない。
    ```
    
- Enum type
enum型はscalar型に似ているが、その有効な値はスキーマで定義される
    
    ```graphql
    enum AllowedColor {
      RED
      GREEN
      BLUE
    }
    ```
    
    enum型は、ユーザが所定のオプションリストから選択しなければならないケースで有効である。さらなる利点として、enum型はApollo Studio Explorerのようなツールでオートコンプリートされる。
    
    ```graphql
    type Query {
      favoriteColor: AllowedColor # enum return value
      avatar(borderColor: AllowedColor): String # enum argument
    }
    # A query might then look like this:
    query GetAvatar {
      avatar(borderColor: RED)
    }
    ```
    
    # Resolvers
    
    Apollo Serverは、スキーマ内の全てのフィールドのデータを入力する方法を知っている必要がある。これを解決するためにリゾルバを使用する。
    リゾルバは、スキーマ内の１つのフィールドのデータを入力する役割を持つ関数である。
    
    この関数は、バックエンドのデータベースや、サードパーティのAPIからデータを取得するなど、デベロッパーが定義した任意の方法でデータを投入することができる。
    (特定のフィールドのリゾルバを定義しない場合、Apollo Serverは自動的に該当するフィールドのデフォルトなリゾルバを定義します)
    
    ## リゾルバの定義
    
    例えばこのようなとても短いスキーマを定義したとする。
    
    ```graphql
    type Query {
      numberSix: Int! # Should always return the number 6 when queried
      numberSeven: Int! # Should always return 7
    }
    ```
    
    さらに、このroot Query型のnumberSixフィールドと、numberSevenフィールドにリゾルバを定義し、クエリされた時に常に6と7を返却するようにしたい場合：
    
    ```tsx
    const resolvers = {
      Query: {
        numberSix() {
          return 6;
        },
        numberSeven() {
          return 7;
        },
      },
    };
    ```
    
    - リゾルバを１つのJavaScriptオブジェクト(上記のresolversという名前)で定義する。このオブジェクトは**リゾルバマップ**と呼ばれる
    - リゾルバマップには、スキーマの方(上記のQuery)に対応するトップレベルのフィールドがある。
    - 各リゾルバ関数は、対応するフィールドの型に属している。
    
    ## 引数の処理
    
    例：
    
    ```graphql
    type User {
      id: ID!
      name: String
    }
    
    type Query {
      user(id: ID!): User
    }
    ```
    
    userフィールドにクエリを発行して、idでユーザを取得できるようにしたい。
    これを実現するために、サーバーはユーザーデータにアクセスする必要がある。
    
    例として、サーバーは以下のようなハードコードされた配列を定義していると仮定する。
    
    ```tsx
    const users = [
      {
        id: '1',
        name: 'Elizabeth Bennet',
      },
      {
        id: '2',
        name: 'Fitzwilliam Darcy',
      },
    ];
    ```
    
    次のようにuser フィールドのリゾルバを定義できる。
    
    ```tsx
    const resolvers = {
      Query: {
        user(parent, args, contextValue, info) {
          return users.find((user) => user.id === args.id);
        },
      },
    };
    ```
    
    - リゾルバはオプションとして４つの引数を受け取る(parent, args, contextValue, info)
    
    ### Resolvers arguments
    
    | Arguments | Description |
    | --- | --- |
    | parent | 現在のフィールドの親のリゾルバの返り値(すなわちリゾルバチェーンの前のリゾルバ) 親を持たないトップレベルのフィールドのリゾルバ(Queryのfieldなど)の場合、この値はApollo serverのコンストラクタに渡されるrootValue関数から取得される。 |
    | args | 現在のフィールドに提供されている全てのGraphQL argsを含むオブジェクト。例えば query{ user(id:”4”) }　を実行する場合、ユーザーリゾルアに渡されるargsオブジェクトは{”id”:”4”} |
    | contextValue | 特定の操作について実行中の全てのリゾルバで共有されるオブジェクト。例えば、認証情報、データローダーインスタンス、その他リゾルバ間で追跡すべきものなど、操作ごとの状態を共有するために利用する。|
    | info | フィールド名、ルートからフィールドのパスなど、操作の実行状態に関する情報を含む。(中核となるフィールドは、GraphQL.jsのソースコードに記載されており、Apollo serverはこれをchacheControl fieldで拡張している。) |
    
    ### Resolver chains
    
    Resolver chains（リゾルバチェーン）は、GraphQLのリゾルバ関数が実行される順序を指す。リゾルバチェーンは、親リゾルバから子リゾルバへと繋がり、最終的にはスキーマ上の最下層のリゾルバまで到達する
    
    例えば、以下のようなスキーマがあるとする：
    
    ```graphql
    # A library has a branch and books
    type Library {
      branch: String!
      books: [Book!]
    }
    
    # A book has a title and author
    type Book {
      title: String!
      author: Author!
    }
    
    # An author has a name
    type Author {
      name: String!
    }
    
    type Query {
      libraries: [Library]
    }
    
    ```
    
    ```graphql
    query GetBooksByLibrary {
      libraries {
        books {
          author {
            name
          }
        }
      }
    }
    ```
    
    このスキーマでは、Query型の`libraries`フィールドが最上位のリゾルバである。librariesフィールドのリゾルバが実行されると、子リゾルバであるbooks型のauthorフィールドのリゾルバが呼び出され、aothor型のnameフィールドが呼び出される。
    
    ```mermaid
    graph TD
      Query.libraries --> Library.books --> Books.author --> Author.name
    ```
    
    また、あわせてbooksのtitleも取得する場合。
    
    ```graphql
    query GetBooksByLibrary {
      libraries {
        books {
          title
          author {
            name
          }
        }
      }
    }
    ```
    
    ```mermaid
    graph TD
      Query.libraries --> Library.books --> Books.author --> Author.name
      Library.books --> Books.title
    ```
    
    このようにチェーンが分岐したとする時、各サブチェーンは並列に実行される。
    
    リゾルバチェーンは、クエリの実行時に自動的に解決される。（各リゾルバは、スキーマの定義に従い、親リゾルバから子リゾルバへとデータを渡します）
    
    この仕組みにより、クライアントがクエリを発行すると、必要なデータが正しい順序で取得されて返されることが保証することができる。
    
    以下のコードは、上記のスキーマに対してリゾルバを定義する例：
    
    ```tsx
    const resolvers = {
      Query: {
        user(parent, args, context, info) {
          // ユーザデータの取得ロジック
          return getUserById(args.id);
        },
      },
      User: {
        posts(user, args, context, info) {
          // ユーザの投稿データの取得ロジック
          return getPostsByUserId(user.id);
        },
      },
    };
    
    ```
    
    上記の例では、
    
    1. `Query`型の`user`フィールドのリゾルバが最初に実行される。
    このリゾルバは、引数として渡されたユーザIDを使用してユーザデータを取得します。
    2. 次に、`User`型の`posts`フィールドのリゾルバが実行される。
    このリゾルバは、前のリゾルバ(`user`)から渡されたユーザオブジェクトを使用して、そのユーザが投稿したデータを取得します。
    
    リゾルバチェーンは、ネストされた型や関連性のあるデータを解決する際に理解しておく必要がある。リゾルバチェーンを適切に設計することで、複雑なデータモデルをシンプルな方法で取得できるようになる。　次に、`User`型の`posts`フィールドのリゾルバが実行されます。このリゾルバは、前のリゾルバから渡されたユーザオブジェクトを使用して、そのユーザが投稿したデータを取得します。
# おわりに
二次情報のため、参考程度にお願いします。詳しくは公式Docを見てください。

https://www.apollographql.com/docs/apollo-server
