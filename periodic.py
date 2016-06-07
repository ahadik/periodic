import unittest
import pickle
import copy
import sys
import json
import argparse

class TestSymbolMethods(unittest.TestCase):

    def test_equal(self):
		symbol = Symbol('a')
		symbolPrime = Symbol('a')
		self.assertEqual(symbol, symbolPrime)
		self.assertEqual(symbol, 'a')
		self.assertEqual(symbol, symbolPrime.symbol)
		self.assertEqual(symbol, ['a'])

		symbol = Symbol('ab')
		symbolPrime = Symbol('ab')
		self.assertEqual(symbol, symbolPrime)
		self.assertEqual(symbol, 'ab')
		self.assertEqual(symbol, symbolPrime.symbol)
		self.assertEqual(symbol, ['a','b'])

    def test_unequal(self):
		symbol = Symbol('a')
		symbolPrime = Symbol('x')
		self.assertNotEqual(symbol, symbolPrime)
		self.assertNotEqual(symbol, 'x')
		self.assertNotEqual(symbol, symbolPrime.symbol)
		self.assertNotEqual(symbol, ['x'])

		symbol = Symbol('ab')
		symbolPrime = Symbol('xy')
		self.assertNotEqual(symbol, symbolPrime)
		self.assertNotEqual(symbol, 'xy')
		self.assertNotEqual(symbol, symbolPrime.symbol)
		self.assertNotEqual(symbol, ['x','y'])


class Symbol:
	def __init__(self, symbol):
		self.symbol = list(symbol)

	def __eq__(self, other):
		if (''.join(self.symbol) == other):
			return True
		try:
			if self.symbol == other:
				return True
			elif self.symbol == other.symbol:
				return True
		except AttributeError:
			pass

		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		return str(self.symbol)

	def __str__(self):
		return str(self.symbol)

class Node(Symbol):
	def __init__(self, char, parents):
		self.symbol = list(char)
		self.parents = parents
		self.children = []
		self.iteration = 0
		self.visitedFrom = []
		self.isDeleted = False
		if parents:
			for parent in parents:
				if not self in parent.children:
					parent.children.append(self)

	def setChildren(self, *args):
		self.children = args[0]
		if len(self.children):
			for child in self.children:
				if not self in child.parents:
					child.parents.append(self)

	def delete(self):
		self.isDeleted = True
		if self.parents:
			for parent in self.parents:
				try:
					if self in parent.children:
						parent.children.remove(self)
					if not len(parent.children):
						parent.delete()
				except ValueError:
					print self.symbol
					print parent.symbol
					for child in parent.children:
						print '-'+str(child.symbol)
					print "exiting..."
					exit()
			for child in self.children:
				if self in child.parents:
					child.parents.remove(self)
	def __repr__(self):
		return str(self.symbol)+':'+str(self.children)

	def __str__(self):
		return str(self.symbol)+':'+str(self.children)


class WordTree:
	def __init__(self):
		self.root = Node('$', None)
		self.leaves = 0
		self.iteration = 0

	def addWord(self, wordSuffix, currNode=None):
		if not currNode:
			currNode = self.root
		if len(wordSuffix):
			nextSymbol = Symbol([wordSuffix[0]])
			wordSuffix = wordSuffix[1:]
			if nextSymbol in currNode.children:
				self.addWord(wordSuffix, currNode=currNode.children[currNode.children.index(nextSymbol)])
			else:
				child = Node(''.join(nextSymbol.symbol), [currNode])
				if child not in currNode.children:
					currNode.children.append(child)
				self.addWord(wordSuffix, currNode=child)
		else:
			child = Node('#', [currNode])
			self.leaves+=1
			if child not in currNode.children:
				currNode.children.append(child)
				

	def makeTree(self, wordFile):
		words = wordFile.readlines()
		for word in words:
			self.addWord(word.rstrip())

	def exportWords(self, wordFile):
		def traverseProcess(node, treeRecur):
			nodeWord = node.symbol
			if len(node.children):
				tempList = []
				for child in node.children:
					suffixes = traverseProcess(child, None)
					for suffix in suffixes:
						tempList += [''.join(nodeWord)+''.join(suffix)]
				if tempList:
					nodeWord = tempList
			return nodeWord
		words = traverseProcess(self.root, None)
		while len(words):
			word = words.pop()
			if (word not in words):
				wordFile.write(word[1:-1]+"\n")
		

	def exportTree(self, treeFile):
		def traverseProcess(node, treeRecur):
			nodeString = "{\n\"name\": \""+''.join(node.symbol)+"\""
			if len(node.children):
				nodeString += ",\n\"children\": ["
				tempString = ""
				for child in node.children:
					tempString += traverseProcess(child, None)
				if tempString:
					nodeString += tempString[:-1]
				nodeString+="]"
			nodeString += "\n},"
			return nodeString
		treeString = traverseProcess(self.root, None)
		treeFile.write(treeString[:-1])

def makeElementList(elementFile):
	elements = elementFile.readlines()
	return [Symbol(element.lower().rstrip()) for element in elements]

def treeTracer(elementList, node, iteration):
	queue = [node]
	node.iteration = iteration
	while len(queue):
		current = queue.pop(0)
		index = 0
		while True:
			if index >= len(current.children):
				break
			else:
				child = current.children[index]
				index+=1
			if child.iteration < iteration:
				child.iteration = iteration
				isFoundFlag = False
				for element in elementList:
					if child == element:
						isFoundFlag = True
					if (len(element.symbol) > len(child.symbol)):
						tempElem = Symbol(element.symbol[0])
						if child == tempElem:
							for childPrime in child.children:
								if childPrime.children != []:
									tempChild = Node(child.symbol+childPrime.symbol, copy.copy(child.parents))
									tempChild.setChildren(copy.copy(childPrime.children))
									for parent in tempChild.parents:
										if not tempChild in parent.children:
											parent.children.append(tempChild)
				if (not isFoundFlag) and (child.symbol != ['#']):
						child.delete()
						index-=1
				else:
					queue.append(child)

def treeExport(wordTree, fileName):
	nodes = []
	links = []
	index = 0
	def treeRecur(node, parentObj, nodes):
		nodeObj = {'label' : ''.join(node.symbol)}
		nodeObj['id'] = id(nodeObj)
		nodes.append(nodeObj)
		if parentObj:
			links.append({'source':nodes.index(parentObj), 'target':nodes.index(nodeObj)})
		for child in node.children:
			treeRecur(child, nodeObj, nodes)
	treeRecur(wordTree.root, None, nodes)

	
	with open(fileName, 'w') as f:
		f.write('{\n')
		f.write('"nodes" : '+json.dumps(nodes)+',\n')
		f.write('"links" : '+json.dumps(links)+'\n')
		f.write('}')


def main(args):
	wordFilePath = args.wordFile
	elementFilePath = args.symbolsFile
	fullPicklePath = args.fullPickle
	prunedPicklePath = args.prunedPickle

	#Build the element list with the provided file path
	with open(elementFilePath, 'r') as f:
		elementList = makeElementList(f)

	#if no filepath was provided for the pruned pickle, 
	#we must either load an unpruned tree from a pickle, 
	#or compute a new one
	if not prunedPicklePath:
		#if no pickle was provided for the full tree, we must recompute it
		if not fullPicklePath:
			with open(wordFilePath, 'r') as f:
				#Instantiate and build the word tree
				wordTree = WordTree()
				wordTree.makeTree(f)
				#After building the word tree, export it as a pickle if the fullPickle flag was set without an argument
				if fullPicklePath == None:
					pickle.dump( wordTree, open( "tree.p", "wb" ))
		#if a pickle path was provided, we load the unpruned tree from disk
		else:
			wordTree = pickle.load(open(fullPicklePath, 'rb'))
			
		#if the exportFullTree flag was set, we export the tree either to a default file name, or a provided one
		if args.exportFullTree != False:
			if args.exportFullTree == None:
				fullTreeExportPath = 'tree.json'
			else:
				fullTreeExportPath = args.exportFullTree
			#export the full tree to the determined file path
			with open(fullTreeExportPath, 'wb') as f:
				wordTree.exportTree(f)

		#increment the wordTree iteration by 1
		wordTree.iteration+=1
		#prune the wordTree by removing invalid paths
		treeTracer(elementList, wordTree.root, wordTree.iteration)

		if prunedPicklePath == None:
			pickle.dump( wordTree, open( "tree_pruned.p", "wb" ))
	#if the prunedPicklePath was set
	else:
		#Load the already pruned tree from disk
		wordTree = pickle.load(open(prunedPicklePath, 'rb'))
	#if the exportPrunedTree flag was set export the pruned tree to JSON format
	if args.exportPrunedTree != False:
		if args.exportPrunedTree == None:
			prunedTreeExportPath = 'pruned_tree.json'
		else:
			prunedTreeExportPath = args.exportPrunedTree
		with open(prunedTreeExportPath, 'wb') as f:
				wordTree.exportTree(f)
	#if the exportWords flag was set, export the word list to a text file
	if args.exportWords != False:
		if args.exportWords == None:
			wordExportFilePath = 'treeWords.txt'
		else:
			wordExportFilePath = args.exportWords
		with open(wordExportFilePath, 'wb') as f:
			wordTree.exportWords(f)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Generate a tree of all words that can be made from a list of symbols.')
	parser.add_argument('wordFile', metavar='wordFile', type=str, nargs='?',
                    help='file path to the list of possible words')
	parser.add_argument('symbolsFile', metavar='symbolFile', type=str, nargs='?',
                    help='file path to the list of possible symbols')
	parser.add_argument('--fullPickle', '-fp', default=False,  nargs='?', dest='fullPickle', help='load a pickle of the full prefix tree instead of recomputing')
	parser.add_argument('--prunedPickle', '-pp', default=False,  nargs='?', dest='prunedPickle', help='load a pickle of the pruned prefix tree instead of recomputing')
	parser.add_argument('--exportFullTree', '-eft', dest='exportFullTree', nargs='?', default=False, help='export the full tree to JSON (default: False)')
	parser.add_argument('--exportPrunedTree', '-ept', dest='exportPrunedTree', nargs='?', default=False, help='export the pruned tree to JSON (default: False)')
	parser.add_argument('--exportWords', '-ew', dest='exportWords', nargs='?', default=False, help='export the words found in the pruned tree (default: False)')

	args = parser.parse_args()
	#unittest.main()
	main(args)