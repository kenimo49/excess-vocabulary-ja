# はじめに

### OpenAPI Generator とは
まず、そもそも OpenAPI とは「OpenAPI Spesification」の略で REST API の定義を記述するための規格です。
OpenAPI Generator は、OAS（OpenAPI Spesification）の定義に基づいてコードを生成することができるツールです。

スキーマ駆動開発では、定義したAPIスキーマをもとにバックエンド (API) とフロントエンド (画面) の開発を並行して行います。そのため、API の実装としては定義に即したリクエスト/レスポンスになっていることが前提です。
OpenAPI Generator では OAS に基づいてコードが生成されるため、挙動が仕様に準拠していることが保証されるというメリットがあります。

### 使用ツール

- [**VSCode**](https://code.visualstudio.com/)： エディタ
- [**Stoplight Studio**](https://stoplight.io/solutions)： OAS 設計
- [**Postman**](https://www.postman.com/)： API テスト

### 環境

バージョンによっては、OpenApi Generator の実行でエラーになってしまいました。エラーの詳細については [#バージョンによるエラー](#バージョンによるエラー) に記載しています。
今回は、最終的に下記のバージョンになりました。

- **Gradle** (version 7.6.3)
- **OpenApi Generator** (version 6.3.0)
- **Java** (version 21)
- **Spring Boot** (version 2.7.18)

# OAS を作成する
OAS（OpenAPI Specification）は、JSON または YAML 形式で記述します。

Stoplight Studio を使って OAS を作成します。
Stoplight Studio は、OAS の作成を支援してくれるツールです。
画像のように、GUI で操作しながら API の仕様を定義することができます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1560824/567b2ce6-d97b-1dc8-5c75-7316dfe03168.png)

```yaml:sample.yaml
openapi: 3.1.0
x-stoplight:
  id: z93blvmmi7luc
info:
  title: Sample-Api
  version: '1.0'
servers:
  - url: 'http://localhost:3000'
paths:
  /users/{userId}:
    parameters:
      - schema:
          type: integer
          minimum: 1
          maximum: 2147483647
        name: userId
        in: path
        required: true
        description: ユーザID
    get:
      summary: ユーザ情報を取得する
      tags:
        - user
      responses:
        '200':
          description: User Found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Bad Request
      operationId: get-user
      description: ユーザ情報を取得します
components:
  schemas:
    User:
      title: User
      type: object
      x-stoplight:
        id: bspfe2osvcdoc
      properties:
        id:
          type: integer
          description: Unique identifier for the given user.
          x-stoplight:
            id: 7vckvz1gosoku
        firstName:
          type: string
          x-stoplight:
            id: cm6rccn4h1qg1
        lastName:
          type: string
          x-stoplight:
            id: ekivdt3u7bpvc
        email:
          type: string
          format: email
          x-stoplight:
            id: e5jvwyaji360n
      required:
        - id
        - firstName
        - lastName
        - email
```

# API を実装する

### プロジェクト構成
```
Project
 ├─ .gradle
 ├─ .vscode
 ├─ bin
 ├─ build
 ├─ gradle/wrapper
   ├─ gradle-wrapper.jar
   └─ gradle-wrapper.properties

 ├─ src
   ├─ main
     ├─ java
       └─ com/app
         ├─ component
         ├─ gen // OpenAPI Generator によって配下にコードが生成されます
         └─ MyApplication.java

     └─ resources

 ├─ specs
   └─ sample.yaml // OAS を格納します

 ├─ test
 ├─ gitignore
 ├─ build.gradle
 ├─ gradlew
 ├─ gradlew.bat
 └─ settings.gradle
```

### Gradle の設定
```gradle:build.gradle
plugins {
  id 'java'
  id 'org.springframework.boot' version '2.7.18'
  id 'io.spring.dependency-management' version '1.1.4'
  // 追加：OpenAPI Generator プラグインの宣言
  id 'org.openapi.generator' version '6.3.0'
  id 'application'
}

group = 'com.app'
version = '0.0.1-SNAPSHOT'

java {
  sourceCompatibility = '21'
}

configurations {
  compileOnly {
    extendsFrom annotationProcessor
  }
}

repositories {
  mavenCentral()
}

dependencies {
  implementation 'org.springframework.boot:spring-boot-starter-web'
  compileOnly 'org.projectlombok:lombok'
  annotationProcessor 'org.projectlombok:lombok'
  testImplementation 'org.springframework.boot:spring-boot-starter-test'
  // 追加：生成されるコードで使用する ライブラリ
  implementation 'org.openapitools:jackson-databind-nullable:0.2.2'
  // 追加：生成されるコードで使用する ライブラリ
  implementation 'io.swagger.core.v3:swagger-annotations:2.1.10'
  // 追加：生成されるコードで使用する ライブラリ
  implementation 'org.springframework.boot:spring-boot-starter-validation'
}

tasks.named('test') {
  useJUnitPlatform()
}

// OpenAPI Generator の設定
openApiGenerate {
  generatorName = "spring"
  // OAS ファイルのパスを指定
  inputSpec = "$rootDir/src/specs/sample.yaml".toString()
  // 出力先のディレクトリを指定
  outputDir = "$rootDir".toString()
  // 生成されるインターフェースのパッケージパスを指定
  apiPackage = "com.app.gen.api"
  // 生成されるモデル（リクエスト、レスポンス）のパッケージパスを指定
  modelPackage = "com.app.gen.model"
  invokerPackage = "com.app.gen.invoker"
  generateApiDocumentation = false
  generateModelDocumentation = false
  configOptions = [
    dateLibrary: "java8",
    // インターフェースのみ生成するかどうか
    interfaceOnly : "true",
    // Java8インターフェースのデフォルト実装の生成をスキップするかどうか
    skipDefaultInterface : "true",
    // OpenAPI Jackson Nullable ライブラリを有効にするかどうか
    openApiNullable: 'false',
    // ※1. インターフェイスとコントローラーのクラス名の作成にタグを使用するかどうか
    useTags: "true"
  ]
}
```
<font color="red">**※1.**</font> OAS でタグを定義することで複数の API がタグでまとめられて、1つのインターフェースを生成してくれます

### OpenAPI Gnerator の実行

build.gradle と同じ階層で ```gradle OpenApiGenerate``` コマンドを実行するか、もしくは VSCode の gradle タブ Tasks/openapi tools/openApiGenerate から OpenAPI Generator を実行します。
![無題.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1560824/2e119e4c-4b7d-f1b7-844e-48b276e0f6d8.png)



実行後、build.gradle で定義したパス先にファイルが作成されます。
OAS で定義した API のエンドポイント、バリデーション、リクエスト、レスポンス等にそってコードが記述されています。

```java:UserApi.java
/**
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.3.0).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
package com.app.gen.api;

import com.app.gen.model.User;
import io.swagger.v3.oas.annotations.ExternalDocumentation;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;
import javax.validation.constraints.*;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import javax.annotation.Generated;

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2023-12-16T17:31:15.909979900+09:00[Asia/Tokyo]")
@Validated
@Tag(name = "User", description = "the User API")
public interface UserApi {

    /**
     * GET /users/{userId} : ユーザ情報を取得する
     * ユーザ情報を取得します
     *
     * @param userId ユーザID (required)
     * @return User Found (status code 200)
     *         or Bad Request (status code 400)
     */
    @Operation(
        operationId = "getUser",
        summary = "ユーザ情報を取得する",
        description = "ユーザ情報を取得します",
        tags = { "user" },
        responses = {
            @ApiResponse(responseCode = "200", description = "User Found", content = {
                @Content(mediaType = "application/json", schema = @Schema(implementation = User.class))
            }),
            @ApiResponse(responseCode = "400", description = "Bad Request")
        }
    )
    @RequestMapping(
        method = RequestMethod.GET,
        value = "/users/{userId}",
        produces = { "application/json" }
    )
    ResponseEntity<User> getUser(
        @Min(1) @Max(2147483647) @Parameter(name = "userId", description = "ユーザID", required = true, in = ParameterIn.PATH) @PathVariable("userId") Integer userId
    );

}
```

生成されたインターフェースを継承し、OAS 定義に準拠したバックエンドの実装を行います。

```java:UserController.java
package com.app.component.presentation.user;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import com.example.gen.api.UserApi;
import com.example.gen.model.User;

@RestController
public class UserController implements UserApi {

  @Override
  public ResponseEntity<User> getUser(Integer userId) {

    User response = new User()//
        .id(userId)//
        .firstName("太郎")//
        .lastName("山田")//
        .email("taro.yamada@xxx.com");

    return new ResponseEntity<>(response, HttpStatus.OK);
  }

}
```

# 動作確認
Postman で ```/users/{userId}``` エンドポイントのAPIを呼んでみます。
↓ OAS で定義したレスポンスが返ってきました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1560824/43a90498-869d-de71-8822-e572168c8b21.png)

バリエーションチェックも OAS で定義した内容で実施されているようです。
userId の桁数超過で 400 が返されました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1560824/f86e28b5-cd52-3cdd-42d0-47f903075dc4.png)


# バージョンによるエラー

### Spring Boot
Sprig Boot 2.7 から 3.0 へのアップデートによって javax というパッケージを jakarta に変更することになりました。
しかし、OpenApi Generator によってコードを生成した場合、javax でインポートされてしまいます。
よって、Spring Boot のバージョンは 2.7 を指定することにしました。

### Gradle
2023/12/16 時点では Gradle v8.5 が最新ですが、v8.5 では outputDir に \\$rootDir を指定すると次のエラーが出てしまいました。
```
Execution failed for task ':openApiGenerate'.
> Cannot access output property 'outputDir' of task ':openApiGenerate'. Accessing unreadable inputs or outputs is not supported. Declare the task as untracked by using Task.doNotTrackState(). For more information, please refer to https://docs.gradle.org/8.5/userguide/incremental_build.html#disable-state-tracking in the Gradle documentation.
   > Failed to create MD5 hash for file content.
```
いろいろと試してみましたが、残念ながら v8.5 では \\$rootDir を指定する方法が見つかりませんでした。

**対応案 1**

１つ目の対応案は、素直に \\$rootDir の指定をあきらめる方法です。例えば \\$buildDir などを指定します。
ただし build ディレクトリ配下にコードを生成した場合、ディレクトリの構成上インタフェースを継承することができなくなってしまいます。
なので、下記のように build.gradle にビルドパスを追加します。
```
sourceSets {
  main {
    java {
      srcDir "${openApiGenerate.outputDir.get()}/src/main/java"
    }
  }
}
```

**対応案 2**

2つ目の対応案は、Gradle のバージョンを v7.6.3 に変更する方法です。
バージョンを下げることで特に困ることもなかったので、今回はこちらの方法で実装しました。

# 終わりに
OpenAPI Generator は便利だと思います。
ただ、生成したコードを見ればわかりますが余分な import が大量に記載されてしまいます。
これをどうにかする方法を知っている方がいましたら教えてほしいです。。
