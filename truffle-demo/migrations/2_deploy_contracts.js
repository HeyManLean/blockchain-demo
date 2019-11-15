const Wrestling = artifacts.require("./Wrestling");

module.exports = function(deployer) {
    deployer.deploy(Wrestling);
};