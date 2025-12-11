class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BSTSorter:
    """Класс-обёртка для сортировки бинарным деревом."""

    @staticmethod
    def _insert(root, value):
        if root is None:
            return BSTNode(value)
        if value < root.value:
            root.left = BSTSorter._insert(root.left, value)
        else:
            root.right = BSTSorter._insert(root.right, value)
        return root

    @staticmethod
    def _inorder(root, out_list):
        if root is None:
            return
        BSTSorter._inorder(root.left, out_list)
        out_list.append(root.value)
        BSTSorter._inorder(root.right, out_list)

    @staticmethod
    def binary_tree_sort(seq):
        root = None
        for x in seq:
            root = BSTSorter._insert(root, x)

        result = []
        BSTSorter._inorder(root, result)
        return result


# Старое API сохранено
def binary_tree_sort(seq):
    return BSTSorter.binary_tree_sort(seq)
