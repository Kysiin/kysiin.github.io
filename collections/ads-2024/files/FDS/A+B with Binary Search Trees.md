# A+B with Binary Search Trees

# 2024.3.28

## Introduction

The Binary Search Tree (BST) Pair Finder program is designed to efficiently identify pairs of elements from two binary search trees whose sum equals a specified target value. This functionality has various applications, including in computational finance, data analysis, and algorithmic problem solving where pair matching based on numerical values is essential.

## Algorithm Specification

The program implements the following algorithmic steps:

1. **Node Creation and Tree Construction:**

   - Nodes are created with a specified key value and pointers to left and right children initialized to NULL.
   - The `createTree` function builds two BSTs from input data, linking nodes based on parent-child relationships.

   ```c
   TreeNode* createTree(int n) {
       if (n == 0) return NULL;

       TreeNode *nodes[n];  // Array to store the nodes
       int keys[n];  // Array to store keys
       int parentIndices[n];  // Array to store parent indices

       // Read the input and create nodes
       for (int i = 0; i < n; i++) {
           scanf("%d %d", &keys[i], &parentIndices[i]);  // Read key and parent index
           nodes[i] = createNode(keys[i]);  // Create a node for each key
       }

       TreeNode *root = NULL;  // Initialize the root of the tree
       // Construct the tree based on the parent-child relationships
       for (int i = 0; i < n; i++) {
           if (parentIndices[i] == -1) {  // Identify the root node
               root = nodes[i];
           } else {  // Set the appropriate child for each parent node
               TreeNode *parent = nodes[parentIndices[i]];
               if (keys[i] < parent->key) {
                   parent->left = nodes[i];
               } else {
                   parent->right = nodes[i];
               }
           }
       }
       return root;  // Return the constructed tree
   }
   ```



2. **Finding Pairs:**

   - Utilizes two pointers, one for each tree, traversing in opposite directions (inorder for T1 and reverse-inorder for T2).
   - Uses a stack for each tree to manage traversal, ensuring no pair is missed.

   ```c
   void findPair(TreeNode *root1, TreeNode *root2, int target) {
       if (!root1 || !root2) return;  // If either tree is empty, return immediately

       TreeNode *stack1[1000], *stack2[1000];  // Stacks to store nodes during traversal
       int top1 = 0, top2 = 0;  // Stack pointers
       TreeNode *curr1 = root1, *curr2 = root2;  // Current nodes for traversals
       int found = 0;  // Flag to indicate if a pair has been found

       // Start the process to find pairs
       while (1) {
           // Traverse to the leftmost node of the current subtree in T1
           while (curr1) {
               stack1[top1++] = curr1;
               curr1 = curr1->left;
           }
           // Traverse to the rightmost node of the current subtree in T2
           while (curr2) {
               stack2[top2++] = curr2;
               curr2 = curr2->right;
           }
           // If either stack is empty, stop the process
           if (top1 == 0 || top2 == 0) break;

           curr1 = stack1[top1 - 1];  // Get the next node from stack1
           curr2 = stack2[top2 - 1];  // Get the next node from stack2

           int sum = curr1->key + curr2->key;  // Calculate the sum of the two nodes' keys
           // Check if the sum equals the target
           if (sum == target) {
               if (!found) {
                   printf("true\n");
                   found = 1;
               }
               printf("%d = %d + %d\n", target, curr1->key, curr2->key);  // Print the pair
               curr1 = stack1[--top1];  // Move to the next node in T1
               curr1 = curr1->right;
               curr2 = stack2[--top2];  // Move to the next node in T2
               curr2 = curr2->left;
           } else if (sum < target) {  // If the sum is less than the target, move right in T1
               curr1 = stack1[--top1];
               curr1 = curr1->right;
               curr2 = NULL;
           } else {  // If the sum is more than the target, move left in T2
               curr2 = stack2[--top2];
               curr2 = curr2->left;
               curr1 = NULL;
           }
       }
   ```



3. **Preorder Traversal:**

   - For output verification, performs a preorder traversal of each tree, displaying the structure and correctness of tree construction.

   ```c
   void preorderTraversal(TreeNode *root, int n) {
       if (root != NULL) {  // If the current node is not null, process it
           printf("%d", root->key);  // Print the current node's key
           if (--n > 0) printf(" ");  // Print space if more nodes are to be printed
           preorderTraversal(root->left, n);  // Recursively traverse the left subtree
           preorderTraversal(root->right, n);  // Recursively traverse the right subtree
       }
   }
   ```

   ## Testing Results

   ### Test case 1

   input:

   ```
   8
   12 2
   16 5
   13 4
   18 5
   15 -1
   17 4
   14 2
   18 3
   7
   20 -1
   16 0
   25 0
   13 1
   18 1
   21 2
   28 2
   36
   ```

   expected output:

   ```
   true
   36 = 15 + 21
   36 = 16 + 20
   36 = 18 + 18
   15 13 12 14 17 16 18 18
   20 16 13 18 25 21 28
   ```

   actual output:

   <img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\10b36cd77532cb19dfc00676e863333.png" alt="10b36cd77532cb19dfc00676e863333" style="zoom: 67%;" />

   ### Test case 2:

   input

   ```
   5
   10 -1
   5 0
   15 0
   2 1
   7 1
   3
   15 -1
   10 0
   20 0
   40
   ```

   expected output

   ```
   false
   10 5 2 7 15
   15 10 20
   ```

   actual output:

   <img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\77359f562bde49f5ffe2bd7301c9f1b.png" alt="77359f562bde49f5ffe2bd7301c9f1b" style="zoom: 67%;" />



   ## Analysis and Comments

   - **Efficiency:** The algorithm is efficient in terms of time complexity, performing traversal in O(n) time for each tree, resulting in an overall O(n) complexity for balanced BSTs.
   - **Scalability:** The program handles dynamic input sizes, although the stack size in `findPair` is statically defined, which could be improved for very large trees.
   - **Maintainability:** Comments and clear structuring of the program enhance maintainability and readability.

### Time Complexity

1. **Tree Construction (`createTree` function):**
   - For each of the n nodes, the function assigns parent-child relationships in a loop.
   - The time complexity is O(n) since each node is visited once.
2. **Finding Pairs (`findPair` function):**
   - This function involves traversing both trees simultaneously, with each tree having potentially �*n* nodes.
   - In the worst case, each node in both trees is visited once, leading to a time complexity of O(n+m), where n and m are the numbers of nodes in the two trees, respectively.
3. **Preorder Traversal (`preorderTraversal` function):**
   - The preorder traversal visits each node exactly once, resulting in O(n) time complexity for each tree traversal.

Combining these operations, the total time complexity of the program is O(n+m), where n and m are the sizes of the two trees, assuming the traversal and pair finding are the dominant operations.

### Space Complexity

1. **Tree Storage:**
   - The space required to store the trees is O(n+m), considering all nodes in both trees.
2. **Stack for Traversal (`findPair` function):**
   - In the worst case, the stack could grow proportionally to the height of the tree. For balanced trees, the height is O($log{n}$) or (O($log{m}$) respectively, but for skewed trees, it could be O(n) or O(m).
   - However, since we traverse both trees simultaneously and store nodes in stacks, the combined space complexity for the stacks would be O(n+m) in the worst case of skewed trees.
3. **Auxiliary Space:**
   - This includes space for variables and function call stack during recursion (preorder traversal), which would be O(h) for each tree, where ℎ*h* is the height of the tree.

Given these points, the overall space complexity is O(n+m) due to the storage of nodes and stack space in the worst case of skewed trees.

In conclusion, the program has a time complexity of O(n+m) and a space complexity of O(n+m), where n and m are the number of nodes in the two binary search trees, respectively.

## Declaration

I hereby declare that all the work done in this project titled " Exponentiations Performance Measurement" is of my independent effort.

## Appendix

```c
#include <stdio.h>
#include <stdlib.h>

// Define a structure for tree nodes
typedef struct TreeNode {
    int key;
    struct TreeNode *left, *right;
} TreeNode;

// Function to create a new tree node with a given key
TreeNode* createNode(int key) {
    TreeNode* node = (TreeNode *)malloc(sizeof(TreeNode));  // Allocate memory for a new node
    node->key = key;  // Set the key value of the node
    node->left = node->right = NULL;  // Initialize left and right children as NULL
    return node;
}

// Function to insert a node with a given key into the BST
TreeNode* insert(TreeNode *root, int key) {
    if (!root) {  // If the tree is empty, create the root node with the key
        root = (TreeNode *)malloc(sizeof(TreeNode));
        root->key = key;
        root->left = root->right = NULL;
    } else if (key < root->key) {  // If the key is less than the root's key, insert it into the left subtree
        root->left = insert(root->left, key);
    } else {  // If the key is greater than or equal to the root's key, insert it into the right subtree
        root->right = insert(root->right, key);
    }
    return root;  // Return the (possibly new) root of the subtree
}

// Function to perform a preorder traversal of the tree and print its elements
void preorderTraversal(TreeNode *root, int n) {
    if (root != NULL) {  // If the current node is not null, process it
        printf("%d", root->key);  // Print the current node's key
        if (--n > 0) printf(" ");  // Print space if more nodes are to be printed
        preorderTraversal(root->left, n);  // Recursively traverse the left subtree
        preorderTraversal(root->right, n);  // Recursively traverse the right subtree
    }
}

// Function to find and print pairs of nodes from two BSTs that sum up to a target value
void findPair(TreeNode *root1, TreeNode *root2, int target) {
    if (!root1 || !root2) return;  // If either tree is empty, return immediately

    TreeNode *stack1[1000], *stack2[1000];  // Stacks to store nodes during traversal
    int top1 = 0, top2 = 0;  // Stack pointers
    TreeNode *curr1 = root1, *curr2 = root2;  // Current nodes for traversals
    int found = 0;  // Flag to indicate if a pair has been found

    // Start the process to find pairs
    while (1) {
        // Traverse to the leftmost node of the current subtree in T1
        while (curr1) {
            stack1[top1++] = curr1;
            curr1 = curr1->left;
        }
        // Traverse to the rightmost node of the current subtree in T2
        while (curr2) {
            stack2[top2++] = curr2;
            curr2 = curr2->right;
        }
        // If either stack is empty, stop the process
        if (top1 == 0 || top2 == 0) break;

        curr1 = stack1[top1 - 1];  // Get the next node from stack1
        curr2 = stack2[top2 - 1];  // Get the next node from stack2

        int sum = curr1->key + curr2->key;  // Calculate the sum of the two nodes' keys
        // Check if the sum equals the target
        if (sum == target) {
            if (!found) {
                printf("true\n");
                found = 1;
            }
            printf("%d = %d + %d\n", target, curr1->key, curr2->key);  // Print the pair
            curr1 = stack1[--top1];  // Move to the next node in T1
            curr1 = curr1->right;
            curr2 = stack2[--top2];  // Move to the next node in T2
            curr2 = curr2->left;
        } else if (sum < target) {  // If the sum is less than the target, move right in T1
            curr1 = stack1[--top1];
            curr1 = curr1->right;
            curr2 = NULL;
        } else {  // If the sum is more than the target, move left in T2
            curr2 = stack2[--top2];
            curr2 = curr2->left;
            curr1 = NULL;
        }
    }

    if (!found) printf("false\n");  // If no pair was found, print "false"
}

// Function to create a BST from the given input format
TreeNode* createTree(int n) {
    if (n == 0) return NULL;

    TreeNode *nodes[n];  // Array to store the nodes
    int keys[n];  // Array to store keys
    int parentIndices[n];  // Array to store parent indices

    // Read the input and create nodes
    for (int i = 0; i < n; i++) {
        scanf("%d %d", &keys[i], &parentIndices[i]);  // Read key and parent index
        nodes[i] = createNode(keys[i]);  // Create a node for each key
    }

    TreeNode *root = NULL;  // Initialize the root of the tree
    // Construct the tree based on the parent-child relationships
    for (int i = 0; i < n; i++) {
        if (parentIndices[i] == -1) {  // Identify the root node
            root = nodes[i];
        } else {  // Set the appropriate child for each parent node
            TreeNode *parent = nodes[parentIndices[i]];
            if (keys[i] < parent->key) {
                parent->left = nodes[i];
            } else {
                parent->right = nodes[i];
            }
        }
    }
    return root;  // Return the constructed tree
}

int main() {
    int n1, n2, N;
    scanf("%d", &n1);  // Read the number of nodes in T1
    TreeNode *T1 = createTree(n1);  // Create T1 tree
    scanf("%d", &n2);  // Read the number of nodes in T2
    TreeNode *T2 = createTree(n2);  // Create T2 tree
    scanf("%d", &N);  // Read the target sum

    findPair(T1, T2, N);  // Find and print pairs that sum up to N

    preorderTraversal(T1, n1);  // Print the preorder traversal of T1
    printf("\n");
    preorderTraversal(T2, n2);  // Print the preorder traversal of T2
    printf("\n");

    return 0;
}
```

