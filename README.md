# peer_tools

コマンドラインからピアノードの情報を取得する。  
以下の Rest と同等の機能が使用できます。

- /chain/info
- /node/info
- /node/peers
- /node/unlockedaccount

## 準備

### SymbolSDK 等必要なパッケージをインストール

```
pip install symbol-sdk-python pyopenssl zenlog
```

### peer-tools と certtool をクローン

```
git clone https://github.com/ccHarvestasya/peer-tools.git
git clone https://github.com/ccHarvestasya/symbol-node-configurator.git
```

### CA プライベートキー生成

```
cd peer-tools
openssl genpkey -algorithm ed25519 -outform PEM -out ca.key.pem
```

### 証明書の生成

```
python ../symbol-node-configurator/certtool.py --working cert --name-ca "my cool CA" --name-node "my cool node name" --ca ca.key.pem
cat cert/node.crt.pem cert/ca.crt.pem > cert/node.full.crt.pem
```

## Peer ノードの設定を変更

### trustedHosts に許可する IP を設定

trustedHosts はカスタムプリセットに設定すれば良いかと思います。  
空にすると、全ての IP に対して有効となり、**セキュリティ的に良くない**ので空にならないようにしてください。  
symbol-bootstrap での Peer なら 172.20.0.1 を許可すれば良いです。  
複数指定する場合は、カンマ区切りで IP を指定してください。

```
trustedHosts:  172.20.0.1
```

「どの IP を許可すれば分からないよ！！」という場合は、一度実行してみてノードログを見ましょう。  
`ignoring unknown packet of type Unlocked_Accounts`を探し出して、表示されてる IP を許可すれば良いです。

```
<warning> (net::ChainedSocketReader.cpp@71) D4794B69B5683348F0A1BDF8ACF052CA84C2598E7050FDD9234789A9197FE6F2 @ 203.135.231.85 read completed with error: Malformed_Data
<warning> (ionet::SocketReader.cpp@75) D4794B69B5683348F0A1BDF8ACF052CA84C2598E7050FDD9234789A9197FE6F2 @ 203.135.231.85 ignoring unknown packet of type Unlocked_Accounts
<warning> (ionet::PacketHandlers.cpp@115) rejecting packet Unlocked_Accounts with size 8 from 203.135.231.85
```

### extension.diagnostics を有効化

extension.diagnostics は symbol-bootstrap ならデフォルトで有効だと思います。  
(target/nodes/dhealth-peer-node/server-config/resources/config-extensions-server.properties)

## 実行

```
python peer_tools.py chainInfo symbol02.harvestasya.com
python peer_tools.py nodeInfo symbol02.harvestasya.com
python peer_tools.py nodePeers symbol02.harvestasya.com
python peer_tools.py nodeUnlockedaccount symbol02.harvestasya.com
```

### 通信ポート変更されている場合

引数にポート番号を指定

```
python peer-tools.py nodeInfo 03.symbol-node.com 7913
```

# peer_simple_rest

peer_tools の機能を Web から確認できるようにしたものです。  
peer_tools と同じく、以下の機能が使用できます。

- /chain/info
- /node/info
- /node/peers
- /node/unlockedaccount

## 追加で必要なパッケージをインストール

```
pip install flask waitress --user
```

## 実行

```
waitress-serve --port=3000 peer_simple_rest:app
```

以下の感じでバックグラウンドで実行すると良いかと思います。

```
nohup waitress-serve --port=3000 peer_simple_rest:app > waitress-serve.log 2>&1 &
```

終了は waitress-serve を kill して。

```
$ ps -A | grep waitress-serve
 261858 ?        00:00:01 waitress-serve
$ kill 261858
```

## 確認

- http://symbol02.harvestasya.com:3000/chain/info
- http://symbol02.harvestasya.com:3000/node/info
- http://symbol02.harvestasya.com:3000/node/peers
- http://symbol02.harvestasya.com:3000/node/unlockedaccount

# 参考

- [Chatting with Peers for Fun and Profit - Symbol Blog](https://symbolblog.com/developer-guides/chatting-with-peers-for-fun-and-profit/)
