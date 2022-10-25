import zss
from zss import simple_distance, Node
from treeMatch_patical_match2 import *
try:
    from editdist import distance as strdist
except ImportError:
    def strdist(a, b):
        if a == b:
            return 0
        else:
            return 1


def run():
    TreeObj = FastTreeMatch()
    try:
        targetTree = TreeObj.makeATree('old_target/target_2.xml')
        targetTree.root.display()
        candidateTree = TreeObj.makeATree('candidate/madelynnTests/candidate_8.xml')
        candidateTree.root.display()

    except:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), "make a tree failed")
    result = zss.simple_distance(targetTree.root, candidateTree.root, get_children, get_label, dist)
    return result

def get_children(node):
    return node.children
def dist(node1, node2):
    strdist(node1, node2)

def get_label(node):
    return node.name
def insert_cost(node):
    return 0.1
def remove_cost(node):
    return 0.1
def update_cost(node1, node2):
    return 0.1


if __name__ == "__main__":
    print(run())


