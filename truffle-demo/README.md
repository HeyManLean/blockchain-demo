```
let account0;
let account1;
web3.eth.getAccounts().then( function(s){account0=s[0]; account1=s[1];});
Wrestling.deployed().then(inst => {WrestlingInstance = inst});
WrestlingInstance.wrestler1.call();
WrestlingInstance.registerAsAnOpponent({from:account1});

WrestlingInstance.wrestler2.call()
WrestlingInstance.wrestle({from: account0, value: web3.utils.toWei('2', "ether")});

WrestlingInstance.wrestle({from: account1, value: web3.utils.toWei('3', "ether")});

WrestlingInstance.wrestle({from: account0, value: web3.utils.toWei('5', "ether")});
WrestlingInstance.wrestle({from: account1, value: web3.utils.toWei('20', "ether")})

WrestlingInstance.withdraw({from:account1});
```