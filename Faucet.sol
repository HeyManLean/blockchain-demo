pragma solidity ^0.4.19;
// Our first contract is a faucet!
contract Faucet {

    // Give out ether to anyone who asks
    function withdraw(uint withdrawAmount) public {

        // Limit withdrawal amount
        require(withdrawAmount <= 100000000000000000);

        // Send the amount to the address that requested it
        msg.sender.transfer(withdrawAmount);
    }

    // Accept any incoming amount
    function a() public payable {}

}