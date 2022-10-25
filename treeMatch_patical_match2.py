import errno
import itertools
import os
import sys
# pip install pptree
import pptree
from statistics import mean
import operator

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
        self.path_belonged=[]

    def __repr__(self):
        return self.name

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def get_leaf(self):
        result=[]
        if self.children:
            for c in self.children:
                if c.is_leaf():
                    result.extend([c])
                else:
                    result.extend(c.get_leaf())
            return result


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

    def get_children(self, n):
        return n.children

    def insert(self, node, parent):
        if parent is not None:
            parent.add_child(node)
        else:
            if self.root is None:
                self.root = node
        self.nodes.append(node)

    def get_leaf_num(self):
        count = 0
        for n in self.nodes:
            if n.is_leaf():
                count+=1
        return count

    def getLevel(self):
        dep = 0
        for N in self.nodes:
            temp = N.depth()
            if temp > dep:
                dep = temp
        return dep

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
        self.depth_score_list=[]
        self.longest_submatch={}
        self.temp_depth=0
        self.matchingNodes = []
        self.ranking = []
        #         Tq would be one level. such as q= a, then Ta = {a1, a2, a3 .. an} and all would only have one ancestor or parent
        #         Tq, list of sorted occurrences of q. represented by a triplet, (start,end,level)

    def insertNodeToTree(self, tree, data, parent):
        # insert the current data
        name = data.tag
        if '}' in name:
            name = data.tag.split("}", 1)[1] # ignore anything in the {}
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
        if 'math' in root.tag and len(root)==1:
            root = root[0]
        # data, start, end, parent, children
        tree = self.insertNodeToTree(tree, root, None)
        return tree

    def run(self, targetFile, dataset):
        matchingFile = {}
        self.numFiles = len(dataset)
        try:
            self.targetTree = newTree.makeATree(targetFile)
            # self.targetTree.root.display()
            # print("targetTree")
            # print(len(self.targetTree.nodes))
        except:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), targetFile)
        for f in dataset:
            try:
                self.candidateTree = newTree.makeATree(f)
                # self.candidateTree.root.display()
                # print("candidate 8")
                # print(len(self.candidateTree.nodes))

            except:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f)
            self.depth_score_list=[]
            self.longest_submatch={}
            self.matchingNodes = []
            self.matchingDepth = 0
            result = self.treeMatch(self.targetTree.root)
            targetNodesNames = [x.name for x in self.targetTree.nodes]
            candidateNodesNames = [x.name for x in self.candidateTree.nodes]
            union= len(targetNodesNames) + len(candidateNodesNames)
            # TODO: final score
            # print(self.matchingNodes)
            score = [sum(self.depth_score_list)/len(self.depth_score_list), len(self.matchingNodes)/union]
            print(score)
        #     if result:
        #         self.ranking.append((f, score))
        #     else:
        #         matchingFile[f] = score
        # # Result, if the matchingFile is empty means we did not find a matching file
        # ranked_file = sorted(matchingFile.items(), key=lambda x: mean(x[1]), reverse=True)
        # self.ranking.extend(ranked_file)
        # for i in self.ranking:
        #     print(i)
        # with open(r'result_1.txt', 'a') as fp:
        #     fp.write(f"Target File: {targetFile}\n")
        #     # for item in self.ranking:
        #     #     # write each item on a new line
        #     #     fp.write(f"{str(item)}\n")
        #     fp.writelines([str(x)+"\n" for x in self.ranking])
        #     fp.write("\n")
        #     print('Done')

    '''
       Tree match algorithm based off the paper by Yao
       @param q the root node of the sub tree we are trying to match
       '''
    def treeMatch(self, q):
        # Exact or Subtree matching
        tq = self.candidateTree.searchNode(q.name) #(list)Tq are occurrences of the pattern node q in data source.
        for tqi in tq:
            if(self.find(q,tqi)):
                return True
        self.particalTreeMatch(tq, q)
        return False

    def particalTreeMatch(self, tq, q):
        if q.is_leaf():
            if (not q in self.longest_submatch) or (1 > self.longest_submatch[q]):
                if tq:
                    if not q in self.matchingNodes:
                        self.matchingNodes.append(q)
                    self.longest_submatch[q] = 1
                else:
                    self.longest_submatch[q] = 0
            self.depth_score_list.append(self.longest_submatch[q]/q.depth())
            # print(q.name, self.longest_submatch[q], q.depth())
        else:
            for tqi in tq:
                result = self.find_partical(q,tqi, q.depth())
            for child in q.children:
                tq = self.candidateTree.searchNode(child.name)  # (list)Tq are occurrences of the pattern node q in data source.
                self.particalTreeMatch(tq, child)
        return False

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
    def find_partical(self, q, tq, currentDepth):
        if q.is_leaf():
            if not q in self.matchingNodes:
                self.matchingNodes.append(q)
            temp_depth = q.depth() - currentDepth
            if (not q in self.longest_submatch) or (temp_depth > self.longest_submatch[q]):
                self.longest_submatch[q] = temp_depth
            return True
        numOfChildren = len(q.children)
        i = 0 #q_i(i = 0, 1, 2, ... n-1) are q's children

        partialSolution = False
        if q.name =='mi':

            if not q in self.matchingNodes:
                self.matchingNodes.append(q)
                self.matchingNodes.append(q.children[0])

            temp_depth = q.depth()+1 - currentDepth
            value = q.children[0]
            if (not value in self.longest_submatch) or (temp_depth > self.longest_submatch[value]):
                self.longest_submatch[value] = temp_depth
            return True
        tq_i = self.candidateTree.searchInChildren(tq,q.children[i].name)
        while partialSolution or tq_i:
            if (not tq_i) or (tq_i[0].start > tq.end):
                if(partialSolution):
                    i=i+1
                    partialSolution = False
                    if i != numOfChildren:
                        tq_i = self.candidateTree.searchInChildren(tq, q.children[i].name)
                if i==numOfChildren:
                    # self.temp_depth = q.depth() - currentDepth
                    return True
            else:
                if tq_i[0].start >= tq.start:
                    if self.find_partical(q.children[i],tq_i[0],currentDepth):
                        if not q in self.matchingNodes:
                            self.matchingNodes.append(q)
                        partialSolution = True
                tq_i.pop(0)

        temp_depth = q.depth() - currentDepth
        for l in q.get_leaf():
            if (not l in self.longest_submatch) or (temp_depth > self.longest_submatch[l]):
                self.longest_submatch[l] = temp_depth
        if i < numOfChildren-1:
            i=i+1
            tq_i = self.candidateTree.searchInChildren(tq, q.children[i].name)
            if tq_i:
                if self.find_partical(q.children[i], tq_i[0], currentDepth):
                    if not q in self.matchingNodes:
                        self.matchingNodes.append(q)
        return False

    def find(self, q, tq):
        if q.is_leaf():
            return True
        numOfChildren = len(q.children)
        i = 0 #q_i(i = 0, 1, 2, ... n-1) are q's children
        partialSolution = False
        if q.name =='mi':
            return True
        tq_i = self.candidateTree.searchInChildren(tq,q.children[i].name)
        while partialSolution or tq_i:
            if (not tq_i) or (tq_i[0].start > tq.end):
                if(partialSolution):
                    i=i+1
                    partialSolution = False
                if i==numOfChildren:
                    return True
                tq_i = self.candidateTree.searchInChildren(tq, q.children[i].name)
            else:
                if tq_i[0].start >= tq.start:
                    if self.find(q.children[i],tq_i[0]):
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
    #folder = "candidate"
    # folder = "candidate/madelynnTests"
    # for f in os.listdir(folder):
    #     files.append(folder+'/'+f)
    files.append("candidate/madelynnTests/candidate_8.xml")
    newTree.run("old_target/target_2.xml", files)
