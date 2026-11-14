# Recover the Design

>Group 18

## Chapter1 : Introduction

The problem presents a garden design recovery task. A garden is laid out in a grid pattern with connectors that indicate where fences can connect. The connectors are placed at grid intersections and have a value (from 1 to 4) representing the number of fences that must connect to it. The original design, which showed the full layout of the fences, is lost, and the goal is to reconstruct this layout using the connectors as a guide.

We need to implement a function that takes the garden's dimensions (n x m) and a matrix of connector values. This function should determine where to place horizontal and vertical fences so that the number of fences connected to each connector matches its value. The fences cannot bend or cross without a connector, and corners are formed only at connectors.

## Chapter2 : Data Structure/Algorithm Specification

### Data Structure

```c
typedef struct node
{
    int row, col;  // row and colum of the node
    int connect;   // number of connections to the node
    int direct[4]; // four directions of the node, in the order of 'up down left right'
    int cross;     // number of intersections of nodes
} node;
```

### Algorithm Specification

* `print`

```pseudocode
FUNCTION print(graph[ ], row, col)
    putn ← 0
    FOR i FROM 0 TO row * col - 1
        IF graph[i] is connected
            putn ← putn + 1
            PRINT all information of graph[i]
        ENDIF
    ENDFOR
    IF putn = 0
        PRINT "No Solution"
    ENDIF
    RETURN 0
END FUNCTION
```

Takes an array of `node` structures and the garden's dimensions. It outputs the connection status of nodes where it has a connection. If no such nodes exist, it prints "No Solution".

* `judge`

```pseudocode
FUNCTION judge(graph[], row, col)
    FOR every node before [row,col] in the graph
        Count the number of connections of all direction of this node
    ENDFOR
    IF the number of connections of all direction equal to each other
        IF printed = 0
            CALL print(graph, row, col)
            printed ← 1
        ENDIF
        RETURN 1
    ENDIF
END FUNCTION
```

Examines the `graph` array of `node` structures. It counts the number of connections in each direction across all nodes. If the counts for all directions are equal , and if nothing has been printed yet, it calls `print` and sets `printed` to 1, then returns 1, indicating a valid configuration has been found.

* `select`

```pseudocode
FUNCTION select(array, n, count, last, node_number, row, col, graph)
    IF count = n + 1 THEN
        search the next node
        RETURN
    ENDIF

    FOR the nodes in four directions
    	IF the node is connected already THEN
    		select the next one
    	ENDIF
    	IF the node is not connected THEN
    		keep moving upwards/downwards/leftwards/rightwards
    	ENDIF
    ENDFOR

END FUNCTION
```

A recursive function that attempts to set the connection status for a given node in all possible ways that match its number of connections. It makes use of the `search` function to move to the next node once all valid configurations for the current node are exhausted.

* `search`

```pseudocode
FUNCTION search(row,col,graph[],code_number)
    IF run out of the graph
    	judge
    	RETURN
    ENDIF
    ELSE
    	select
    ENDELSE
END FUNCTION
```

 A recursive backtracking function that iterates through all nodes in the graph, calling `select` for each to set up its connections. Once all nodes have been processed, it calls `judge` to check if a valid configuration has been found.

* `test`

```pseudocode
FUNCTION test

	open testfile
	IF file is empty
		print "Failed to open file\n"
	ENDIF
	FOR every test case
		initialize graph[] to 0
		FOR every node in the input
			wright it into graph[]
		ENDFOR

		search
		IF still not printed THEN print "No Solution\n\n"
	ENDFOR
	close testfile
END FUNCTION
```

Opens a file and reads test cases from it. It initializes a graph with given dimensions and connection counts, then calls `search` to start the reconstruction process. It prints whether a solution has been found after each test.

## Chapter3 : Testing Results

| Input                                                        | Expected Output                                              | Actual Output                                                |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 2 2<br/>0 0<br/>0 0<br/>'No Solution' situation              | No Solution                                                  | ![屏幕截图 2024-04-12 210753](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210753.png) |
| 1 4<br/>1 0 0 1<br/>Only one row situation                   | 1 1 0 0 0 1<br/>1 4 0 0 1 0                                  | ![屏幕截图 2024-04-12 210759](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210759.png) |
| 3 3<br/>0 1 0<br/>1 4 1<br/>0 1 0<br/>Simple all four direction situation | 1 2 0 1 0 0<br/>2 1 0 0 0 1<br/>2 2 1 1 1 1<br/>2 3 0 0 1 0<br/>3 2 1 0 0 0 | ![屏幕截图 2024-04-12 210802](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210802.png) |
| 3 3<br/>2 0 2<br/>0 0 0<br/>2 0 2<br/>All the nodes are separated | 1 1 0 1 0 1<br/>1 3 0 1 1 0<br/>3 1 1 0 0 1<br/>3 3 1 0 1 0  | ![屏幕截图 2024-04-12 210806](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210806.png) |
| 3 3<br/>1 1 0<br/>0 0 0<br/>1 2 1<br/>Random common situation | 1 1 0 1 0 0<br/>1 2 0 1 0 0<br/>3 1 1 0 0 0<br/>3 2 1 0 0 1<br/>3 3 0 0 1 0 | ![屏幕截图 2024-04-12 210811](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210811.png) |
| 3 5<br/>1 1 2 0 1<br/>1 0 3 0 2<br/>1 2 1 0 1<br/>Random common situation | 1 1 0 1 0 0<br/>1 2 0 1 0 0<br/>1 3 0 1 0 1<br/>1 5 0 0 1 0<br/>2 1 1 0 0 0<br/>2 3 1 1 0 1<br/>2 5 0 1 1 0<br/>3 1 0 0 0 1<br/>3 2 1 0 1 0<br/>3 3 1 0 0 0<br/>3 5 1 0 0 0 | ![屏幕截图 2024-04-12 210815](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210815.png) |
| 5 6<br/>0 0 2 0 0 2<br/>1 3 3 1 0 0<br/>2 2 1 0 0 2<br/>0 0 0 0 0 1<br/>2 0 2 0 0 2<br/>Random common situation | 1 3 0 1 0 1<br/>1 6 0 1 1 0<br/>2 1 0 0 0 1<br/>2 2 0 1 1 1<br/>2 3 1 0 1 1<br/>2 4 0 0 1 0<br/>3 1 0 1 0 1<br/>3 2 1 0 1 0<br/>3 3 0 0 0 1<br/>3 6 1 0 1 0<br/>4 6 0 1 0 0<br/>5 1 1 0 0 1<br/>5 3 0 0 1 1<br/>5 6 1 0 1 0 | ![屏幕截图 2024-04-12 210819](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210819.png) |
| 15 20 <br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 1 1 2 0 1 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 1 0 3 0 2 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 1 2 1 0 1 0 0 0 0 0 0<br/>max size graph but only a few are valid | 13 10 0 1 0 0<br/>13 11 0 1 0 0<br/>13 12 0 1 0 1<br/>13 14 0 0 1 0<br/>14 10 1 0 0 0<br/>14 12 1 1 0 1<br/>14 14 0 1 1 0<br/>15 10 0 0 0 1<br/>15 11 1 0 1 0<br/>15 12 1 0 0 0<br/>15 14 1 0 0 0 | ![屏幕截图 2024-04-12 210827](D:\HuaweiMoveData\Users\***\Pictures\Screenshots\屏幕截图 2024-04-12 210827.png) |
| 15 20 <br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 1 4 2 2 2 2 0 0 0 0 0 1<br/>0 0 0 0 0 0 0 0 0 2 0 0 0 2 0 0 0 0 0 2<br/>0 0 0 0 0 0 0 0 0 2 0 0 0 2 2 2 2 2 2 3<br/>0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 2<br/>1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2<br/>2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0<br/>Random max size graph | 4 10 0 1 0 0<br/>5 10 1 1 0 0<br/>6 9 0 0 0 1<br/>6 10 1 1 1 1<br/>6 11 0 1 1 0<br/>6 12 0 1 0 1<br/>6 13 0 1 1 0<br/>6 14 0 1 0 1<br/>6 20 0 0 1 0<br/>7 10 1 1 0 0<br/>7 14 1 0 0 1<br/>7 20 0 1 1 0<br/>8 10 1 1 0 0<br/>8 14 0 1 0 1<br/>8 15 0 1 1 0<br/>8 16 0 1 0 1<br/>8 17 0 1 1 0<br/>8 18 0 1 0 1<br/>8 19 0 0 1 1<br/>8 20 1 1 1 0<br/>9 10 1 0 0 0<br/>9 20 1 1 0 0<br/>10 1 0 1 0 0<br/>10 20 1 1 0 0<br/>11 1 1 0 0 1<br/>11 2 0 0 1 1<br/>11 3 0 0 1 1<br/>11 4 0 0 1 1<br/>11 5 0 0 1 1<br/>11 6 0 0 1 1<br/>11 7 0 0 1 1<br/>11 8 0 0 1 1<br/>11 9 0 0 1 1<br/>11 10 0 0 1 1<br/>11 11 1 0 1 0<br/>11 12 1 0 0 1<br/>11 13 1 0 1 0<br/>11 14 1 0 0 1<br/>11 15 1 0 1 0<br/>11 16 1 0 0 1<br/>11 17 1 0 1 0<br/>11 18 1 0 0 1<br/>11 19 0 0 1 1<br/>11 20 1 0 1 0 | ![image-20240414143020340](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240414143020340.png) |

## Chapter4 Analysis and Comments

### Time Complexity

1. **Function `print`**:
   - This function iterates over each node in the graph, printing nodes that have at least one non-zero connection.
   - As it involves a single loop that iterates over all nodes (row x column), the time complexity is **O(row * col)**.
2. **Function `judge`**:
   - This function first iterates over all nodes, counting the number of connections in each of the four directions.
   - It then checks if these counts meet specific conditions.
   - If conditions are satisfied, it calls the `print` function.
   - The primary complexity of this function is defined by the traversal of all nodes, which is **O(row * col)**. However, in the worst case, if the `print` function is called, the complexity can escalate to **O((row * col)^2)**.
3. **Functions `select` and `search`**:
   - These functions constitute the core part of the recursive search. The `search` function calls the `select` function for each node in the graph.
   - The `select` function attempts recursive searches in four directions, which can be quite complex, with complexity depending heavily on the graph structure and the depth of recursion.
   - In the worst case, these functions could reach an exponential time complexity, potentially **O(4^(row * col))**, depending on how recursion branches and depth are managed in the `select` function.
4. **Function `test`**:
   - This function is responsible for reading input from a file and repeatedly invoking the `search` function, as determined by an input parameter.
   - The time complexity here is tied to the complexity of the `search` function, multiplied by the number of test iterations.
5. **Main function `main`**:
   - Calls the `test` function 10 times, with its complexity mirroring that of the `test` function.

In conclusion, the overall worst-case time complexity of the program could be close to exponential, approximating **O(4^(row * col))**.

### Space Complexity

1. **Graph Representation**:
   - The program utilizes an array of `node` structures to represent the graph. Each node stores details such as position (`row`, `col`), connectivity (`connect`), directions (`direct` array), and cross-connections (`cross`). The total memory used by this array is proportional to the number of nodes, which is `row * col`. Therefore, the space required for the graph representation is **O(row * col)**.
2. **Recursive Function Calls**:
   - The `select` and `search` functions employ recursive calls, which can significantly impact the space complexity due to the stack space needed for each recursive call.
   - The depth of recursion in the `select` function depends on the connectivity and possible paths in the graph. In the worst-case scenario, considering a fully connected graph or high connectivity, the maximum recursion depth could potentially reach **O(row * col)** because the recursion could theoretically extend through all nodes in the graph.
3. **Auxiliary Storage**:
   - The `select` function uses an auxiliary array `array[4]` to store temporary states during the recursive exploration of node connections. However, the size of this array is constant **O(1)**.
   - Additional local variables and temporary storage used in functions like `judge`, `print`, and during file reading and processing are minimal and generally considered **O(1)** unless they scale with input size.
4. **Overall Space Complexity**:
   - Combining the above factors, the dominant term in the space complexity is from the graph representation **O(row * col)** and the potential maximum recursion depth **O(row * col)**. Therefore, the overall space complexity of the program is **O(row * col)** due to the graph storage and recursion stack depth. This complexity assumes the worst-case scenario where recursion depth is extensive, potentially reaching the total number of nodes in the graph.

### Analysis

The program presented for graph traversal and node analysis uses a structured approach with a clear modular design, effectively encapsulating functionalities like node printing, judgment, and recursive search within distinct functions. This structuring into functions such as `print`, `judge`, `search`, and `select` not only enhances the readability and maintainability of the code but also facilitates isolated testing and debugging, making each component reusable in different contexts.

However, despite these strengths, the program faces significant challenges, primarily due to its potential exponential time complexity and deep recursion, which can severely affect performance, especially on larger graphs. This complexity arises from the recursive search strategy used to explore node connections in all directions, which, while thorough, can lead to performance bottlenecks and high space consumption as the recursion depth may reach the total number of nodes in the graph
