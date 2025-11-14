

class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def bst_insert(root, value):
    if root is None:
        return BSTNode(value)
    if value < root.value:
        root.left = bst_insert(root.left, value)
    else:
        root.right = bst_insert(root.right, value)
    return root

def bst_inorder(root, out_list):
    if root is None:
        return
    bst_inorder(root.left, out_list)
    out_list.append(root.value)
    bst_inorder(root.right, out_list)

def binary_tree_sort(seq):
    root = None
    for x in seq:
        root = bst_insert(root, x)

    result = []
    bst_inorder(root, result)
    return result
