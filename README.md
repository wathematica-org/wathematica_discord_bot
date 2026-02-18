# Wathematica Discord Bot

## 概要

WathematicaのDiscordサーバ上でゼミやロールの管理を行うBotです。
SlashCommandを実装しており、Discordサーバ上で補完付きのコマンド入力が可能です。

Pythonによって実装されています。

## 導入方法

### discordトークンの取得
1. https://discord.com/developers/docs/intro　にアクセス
2. botの作成
3. botタブをひらいてPrivileged Gateway Intets を全てonにする
4. botタブでtokenを発行してコピーして保存しておく
5. Oauth2タブに移動してbotを選択し、権限をAdministratorにする
6. URLを発行して導入したいサーバーにbotを入れる



### docker-compose によるローカル環境での起動
1. このレポジトリをクローン
2. config下に、設定用のjsonファイルを作成する。
3. dev内に.discord_tokenという名前のファイルを作成してコピーしておいたtokenを貼り付ける
4. 起動して動作を確認する `docker compose up` 

### fly.ioへのデプロイ
初回以外は、 `fly.toml` があるパスと同じ場所から `fly deploy` と実行すればよい。
初回（machine 作成時）にはデータベース用の volume を確保するために以下のような手順で行う：

1. `fly launch --ha=halse --secret discord_token={DISCORD_TOKEN} --no-deploy` を実行して app を作成
2. `fly volumes create data_volume --region iad --size` によって作成した app に紐づく volume を確保
3. `fly deploy` を実行してデプロイ

### データの移行
本 Bot では SQLite を用いてデータを管理しており、 `database.db` というファイルに全てのデータが書き込まれている。
Fly volume で永続的なストレージを確保していなかった場合や、ローカルでのデータベースファイルなどをデプロイ先のアプリから参照したいという場合には、 flyctl の `sftp` を用いるのが便利である。

#### Fly.io 上の VM のファイルをローカルにダウンロード
```shell
> fly sftp get {VM 上の path} {ローカルマシンでの保存先の path}
```
例：
```shell
> fly sftp get /data/database.db ~/Downloads/database-tmp.db
```

#### Fly.io 上にローカルのファイルをアップロード
```shell
> fly sftp put {ローカルマシンのファイルの path} {VM 上のアップロード先}
```
例：
```shell
> fly sftp put ~/Downloads/database-tmp.db /data/database.db
```


