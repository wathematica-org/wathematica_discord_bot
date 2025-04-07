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
3. Dockerfileと同じ階層に.discord_tokenという名前のファイルを作成してコピーしておいたtokenを貼り付ける
4. 起動して動作を確認する

### fly.ioへのデプロイ
1. fly laucn --no-deploy　をローカルレポジトリ内で行う
2. fly secrets set discord_token=[発行したトークン] を同様に行う
3. fly deploy --ha=false を実行してデプロイする


