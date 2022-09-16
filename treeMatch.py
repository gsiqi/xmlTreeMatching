import errno
import itertools
import os
import sys
# pip install pptree
import pptree

# To make the start,end line working, put this line of code before importing ElementTree
sys.modules['_elementtree'] = None
import xml.etree.ElementTree as ET


# To make this working, use python 3.8 or older version
class LineNumberingParser(ET.XMLParser):
    def _start(self, *args, **kwargs):
        # Here we assume the default XML parser which is expat
        # and copy its element position attributes into output Elements
        element = super(self.__class__, self)._start(*args, **kwargs)
        element._start_line_number = self.parser.CurrentLineNumber
        element._start_column_number = self.parser.CurrentColumnNumber
        element._start_byte_index = self.parser.CurrentByteIndex
        return element

    def _end(self, *args, **kwargs):
        element = super(self.__class__, self)._end(*args, **kwargs)
        element._end_line_number = self.parser.CurrentLineNumber
        element._end_column_number = self.parser.CurrentColumnNumber
        element._end_byte_index = self.parser.CurrentByteIndex
        return element


class Node:
    def __init__(self, data='', start=0, end=0, parent=None):
        self.start = start
        self.end = end
        self.parent = parent
        self.children = []
        self.name = data

    def __repr__(self):
        return self.name

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def depth(self):
        if self.is_root():
            return 0
        else:
            return 1 + self.parent.depth()

    def display(self):
        pptree.print_tree(self, 'children', 'name', True)

    def add_child(self, node):
        node.parent = self
        self.children.append(node)


class Tree:
    def __init__(self):
        self.root = None
        self.level = 0
        self.nodes = []

    def insert(self, node, parent):
        if parent is not None:
            parent.add_child(node)
        else:
            if self.root is None:
                self.root = node
        self.nodes.append(node)

    def searchIndex(self, name):
        occurrences = []
        for i, N in enumerate(self.nodes):
            if N.name == name:
                occurrences.append(i)
        return occurrences

    def searchNode(self, name):
        occurrences=[]
        for N in self.nodes:
            if N.name == name:
                occurrences.append(N)
        return occurrences

    def searchInChildren(self,q,name):
        occurrences = []
        for i, N in enumerate(q.children):
            if N.name == name:
                occurrences.append(N)
        return occurrences

    def getNode(self, index):
        return self.nodes[index]

    def root(self):
        return self.root


class FastTreeMatch:
    def __init__(self):
        self.numFiles = 0
        self.docNumber = 0
        self.targetTree = Tree()
        self.candidateTree = Tree()
        self.listOfStack={}
        #         Tq would be one level. such as q= a, then Ta = {a1, a2, a3 .. an} and all would only have one ancestor or parent
        #         Tq, list of sorted occurrences of q. represented by a triplet, (start,end,level)

    def insertNodeToTree(self, tree, data, parent):
        # insert the current data
        name = data.tag.split("}", 1)[1]  # ignore anything in the {}
        parentNode = Node(name, data._start_line_number, data._end_line_number, parent)
        tree.insert(parentNode, parent)
        childNode = Node()
        # if the current tag has value, then insert value as a child
        if data.text.strip():
            lineNumber = (data._end_line_number - data._start_line_number) // 2 + data._start_line_number
            children = [data.text]
            childNode = Node(data.text, lineNumber, lineNumber, parentNode)
            # parentNode.add_child(childNode)
            tree.insert(childNode, parentNode)

        for child in data:
            if data.text.strip():
                self.insertNodeToTree(tree, child, childNode)
            else:
                self.insertNodeToTree(tree, child, parentNode)
        return tree

    def makeATree(self, fileName):
        parser = LineNumberingParser()
        root = ET.parse(fileName, parser=parser).getroot()
        tree = Tree()
        # data, start, end, parent, children
        tree = self.insertNodeToTree(tree, root, None)
        return tree

    def run(self, targetFile, dataset):
        matchingFile = []
        self.numFiles = len(dataset)
        try:
            self.targetTree = newTree.makeATree(targetFile)
        except:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), targetFile)
        for f in dataset:
            try:
                self.candidateTree = newTree.makeATree(f)
            except:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f)
            result = self.treeMatch(self.targetTree.root)
            if result:
                matchingFile.append(f)
        # Result, if the matchingFile is empty means we did not find a matching file
        print("These files are matching to the equation:", matchingFile)

    '''
       Tree match algorithm based off the paper by Yao
       @param q the root node of the sub tree we are trying to match
       '''
    def treeMatch(self, q):
        result = False
        tq = self.candidateTree.searchNode(q.name) #(list)Tq are occurrences of the pattern node q in data source.
        for qi in tq:
            if(self.find(q,qi)):
                result = True
        return result

    '''
    determines whether the current occurrence Tq→current is a partial solution.
    @param q is the node in the target tree
    @param tq Tq→current is a partial solution means matchings of
    sub-tree patterns rooted by q have been found and encoded
    in the stacks and these matchings are possibly extended to
    final results
    @return If Tq→current is false/ not a partial solution,
    function CleanStack() is called to remove the recoded
    nodes that are its descendants.
    returns true if the list is not empty, the end is bigger than the start, and i = N;
    '''
    def find(self, q, tq):
        if tq.is_leaf():
            return True
        numOfChildren = len(tq.children)
        i = 0 #q_i(i = 0, 1, 2, ... n-1) are q's children
        stack_i = []
        partialSolution = False
        if q.name =='mi':
            return True
        tq_i = self.candidateTree.searchInChildren(tq,q.children[i].name)
        while partialSolution or tq_i:
            if (not tq_i) or (tq_i[0].start > tq.end):
                if(partialSolution):
                    i=i+1
                    partialSolution = False
                else:
                    j=0
                    while j < i:
                        self.cleanStack(q.children[j])
                        j += 1
                    return False
                if i==numOfChildren:
                    return True
                tq_i = self.candidateTree.searchInChildren(tq, q.children[i].name)
            else:
                if tq_i[0].start >= tq.start:
                    if self.find(q.children[i],tq_i[0]):
                        stack_i.append([tq_i[0], tq])
                        self.listOfStack[q.children[i]] = stack_i
                        partialSolution = True
                tq_i.pop(0)
        return False

    '''
    * Function GenerateSolution() and GenerateSolution2()
     * produce two varieties of explicit representation
     * of the final result
     * @param q
    '''
    def generateSolution(self,q):
        n = len(q.children)
        i = 0
        while i < n:
            self.generateSolution(q.children[i])
            self.listOfStack[q].extend(self.listOfStack[q.children[i]])
            self.listOfStack[q] = [ [y[0] for y in g] + [i] for i, g in itertools.groupby(self.listOfStack[q], key = lambda x: x[-1])]
            # print(self.listOfStack[q])
            # print('@'*50)
            i += 1


    def cleanStack(self,q):
        n = q.numChildren
        i = 0
        while i < n:
            self.cleanStack(q.children[i])
            i+=1

        parentNode = self.listOfStack[q][-1].parent
        while(self.listOfStack[q]) and (self.listOfStack[q][-1].parent == parentNode):
            self.listOfStack[q].pop()

# Run this as a main function
if __name__ == "__main__":
    newTree = FastTreeMatch()
    files = []
    folder = "candidate"
    for f in os.listdir(folder):
        files.append(folder+'/'+f)
    newTree.run("target.xml", files)
