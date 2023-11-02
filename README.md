# peer-tools

ピアノードの情報を取得する。

# 注意

Unlockedaccount を取得するには、以下の条件が必要です。

- 実行するマシンの IP/Host をノードの trustedHosts に設定する必要があります（許可されたマシンにしか応答しません）。
- extension.diagnostics が有効になっている必要があります。

trustedHosts はカスタムプリセットに設定すれば良いかと思います。  
空にすることで、全ての IP に対して有効となります **（セキュリティ的に良くない!!）** 。  
symbol-bootstrap での Peer なら 172.20.0.1 を許可すれば良いです。多分。

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

extension.diagnostics は symbol-bootstrap ならデフォルトで有効だと思います。  
(target/nodes/dhealth-peer-node/server-config/resources/config-extensions-server.properties)

# 準備

## SymbolSDK をインストール

```
pip install symbol-sdk-python pyopenssl zenlog
```

## peer-tools と certtool をクローン

```
git clone https://github.com/ccHarvestasya/peer-tools.git
git clone https://github.com/ccHarvestasya/symbol-node-configurator.git
```

## CA プライベートキー生成

```
cd peer-tools
openssl genpkey -algorithm ed25519 -outform PEM -out ca.key.pem
```

## 証明書の生成

```
python ../symbol-node-configurator/certtool.py --working cert --name-ca "my cool CA" --name-node "my cool node name" --ca ca.key.pem
cat cert/node.crt.pem cert/ca.crt.pem > cert/node.full.crt.pem
```

# 実行

```
python peer-tools.py nodeInfo 11.dusanjp.com
```

## 通信ポート変更されている場合

引数にポート番号を指定

```
python peer-tools.py nodeInfo 03.symbol-node.com 7913
```

# 参考

- [Chatting with Peers for Fun and Profit - Symbol Blog](https://symbolblog.com/developer-guides/chatting-with-peers-for-fun-and-profit/)
