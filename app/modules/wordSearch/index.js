require('babel-core/register');
var pt = require('periodic-table');
var exports = module.exports = {};

exports.rand = function(wordList){
	var word = wordList.list[Math.floor(Math.random()*wordList.length)]
	var wordObj = []
	for (let symbol of word){
		let symbolString = symbol[0].toUpperCase() + symbol.slice(1)
		let element = pt.symbols[symbolString]
		wordObj.push({"name" : element.name, "symbol" : element.symbol, "atomicNumber" : element.atomicNumber, "atomicMass" : element.atomicMass})
	}
	return wordObj
}